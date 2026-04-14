from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.llm import llm_gateway
from src.governor.network_mediator import NetworkMediator
from src.openclaw.agent_personality_bridge import (
    OpenClawAgentPersonalityBridge,
    delivery_channels,
)
from src.openclaw.agent_runtime_store import (
    OpenClawAgentRuntimeStore,
    openclaw_agent_runtime_store,
)
from src.openclaw.execution_memory import ExecutionMemory
from src.openclaw.per_tool_budget import PerToolBudgetTracker
from src.openclaw.robust_executor import RetryConfig, RobustExecutor
from src.openclaw.strict_preflight import evaluate_manual_envelope
from src.openclaw.task_envelope import TaskEnvelope
from src.openclaw.thinking_loop import ThinkingLoop
from src.openclaw.tool_registry import get_tool_registry
from src.personality.conversation_personality_agent import ConversationPersonalityAgent
from src.providers.openai_responses_lane import OpenAIResponsesLane, OpenAIResponsesLaneError
from src.skills.calendar import CalendarSkill
from src.skills.news import NewsSkill
from src.tasks.notification_schedule_store import NotificationScheduleStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunCancelledError(RuntimeError):
    """Raised when a cancel request is detected at a checkpoint."""


def _estimate_tokens(text: str) -> int:
    raw = str(text or "").strip()
    if not raw:
        return 0
    return max(1, round(len(raw) / 4))


@dataclass
class RunBudgetMeter:
    envelope: TaskEnvelope
    started_monotonic: float = field(default_factory=time.monotonic)
    steps_used: int = 0
    network_calls_used: int = 0
    files_touched_used: int = 0
    bytes_read_used: int = 0
    bytes_written_used: int = 0
    stage_label: str = "Starting now"
    notes: list[str] = field(default_factory=list)

    def set_stage(self, label: str) -> None:
        self.stage_label = str(label or "").strip() or self.stage_label

    def _raise_if_over_budget(self, key: str, used: int, budget: int) -> None:
        if int(budget) >= 0 and int(used) > int(budget):
            raise RuntimeError(f"Run exceeded envelope {key} budget ({used}/{budget}).")

    def record_step(self, label: str) -> None:
        self.set_stage(label)
        self.steps_used += 1
        self._raise_if_over_budget("step", self.steps_used, int(self.envelope.max_steps))

    def record_network_call(self, url: str) -> None:
        if not self.envelope.url_allowed(url):
            raise RuntimeError(f"Run attempted network access outside the envelope: {url}")
        self.network_calls_used += 1
        self._raise_if_over_budget(
            "network call",
            self.network_calls_used,
            int(self.envelope.max_network_calls),
        )

    def record_network_bytes(self, payload: Any) -> None:
        self.bytes_read_used += _payload_size_bytes(payload)
        self._raise_if_over_budget(
            "bytes read",
            self.bytes_read_used,
            int(self.envelope.max_bytes_read),
        )

    def record_file_read(self, path: Any) -> None:
        self.files_touched_used += 1
        self._raise_if_over_budget(
            "file touch",
            self.files_touched_used,
            int(self.envelope.max_files_touched),
        )
        try:
            self.bytes_read_used += max(0, int(path.stat().st_size))
        except Exception:
            pass
        self._raise_if_over_budget(
            "bytes read",
            self.bytes_read_used,
            int(self.envelope.max_bytes_read),
        )

    def snapshot(self) -> dict[str, Any]:
        duration_seconds = max(0.0, time.monotonic() - self.started_monotonic)
        return {
            "steps_used": int(self.steps_used),
            "steps_budget": int(self.envelope.max_steps),
            "network_calls_used": int(self.network_calls_used),
            "network_calls_budget": int(self.envelope.max_network_calls),
            "files_touched_used": int(self.files_touched_used),
            "files_touched_budget": int(self.envelope.max_files_touched),
            "bytes_read_used": int(self.bytes_read_used),
            "bytes_read_budget": int(self.envelope.max_bytes_read),
            "bytes_written_used": int(self.bytes_written_used),
            "bytes_written_budget": int(self.envelope.max_bytes_written),
            "metering_mode": "measured_narrow_lane",
            "duration_s": round(duration_seconds, 2),
            "summary": (
                f"Used so far: {int(self.steps_used)}/{int(self.envelope.max_steps)} steps, "
                f"{int(self.network_calls_used)}/{int(self.envelope.max_network_calls)} web requests, "
                f"{int(self.files_touched_used)}/{int(self.envelope.max_files_touched)} local files, "
                f"{int(self.bytes_read_used)}/{int(self.envelope.max_bytes_read)} bytes read."
            ),
        }


class MeteredNetworkProxy:
    def __init__(self, *, delegate: NetworkMediator | None, meter: RunBudgetMeter) -> None:
        self._delegate = delegate or NetworkMediator()
        self._meter = meter

    def request(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        url = str(kwargs.get("url") or "").strip()
        self._meter.record_network_call(url)
        response = self._delegate.request(*args, **kwargs)
        if kwargs.get("as_json", True):
            self._meter.record_network_bytes(response.get("data"))
        else:
            self._meter.record_network_bytes(response.get("text"))
        return response


def _payload_size_bytes(payload: Any) -> int:
    if payload is None:
        return 0
    if isinstance(payload, bytes):
        return len(payload)
    if isinstance(payload, str):
        return len(payload.encode("utf-8", errors="ignore"))
    try:
        return len(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    except Exception:
        return len(str(payload).encode("utf-8", errors="ignore"))


class OpenClawAgentRunner:
    """Manual first foundation for low-token home-agent briefing runs."""

    WEATHER_TIMEOUT_SECONDS = 8.0
    CALENDAR_TIMEOUT_SECONDS = 3.0
    NEWS_TIMEOUT_SECONDS = 10.0
    SUMMARY_TIMEOUT_SECONDS = 30.0

    def __init__(
        self,
        *,
        store: OpenClawAgentRuntimeStore | None = None,
        network: Any = None,
        presenter: ConversationPersonalityAgent | None = None,
        openai_lane: OpenAIResponsesLane | None = None,
        execution_memory: ExecutionMemory | None = None,
    ) -> None:
        self._store = store or openclaw_agent_runtime_store
        self._network = network
        self._personality_bridge = OpenClawAgentPersonalityBridge(presenter=presenter)
        self._openai_lane = openai_lane or OpenAIResponsesLane(network=network)
        self._active_budget_meter: RunBudgetMeter | None = None
        self._active_envelope: TaskEnvelope | None = None
        self._robust_executor = RobustExecutor(retry_config=RetryConfig(max_retries=1))
        self._execution_memory = execution_memory or ExecutionMemory()
        self._tool_registry = get_tool_registry()
        self._per_tool_budget = PerToolBudgetTracker()

    async def run_template(self, template_id: str, *, triggered_by: str = "dashboard") -> dict[str, Any]:
        template = self._store.get_template(template_id)
        if template is None:
            raise KeyError(template_id)
        if not bool(template.get("manual_run_available")):
            raise RuntimeError(str(template.get("availability_reason") or "This template is not ready yet.").strip())

        envelope = TaskEnvelope.from_template(template, triggered_by=triggered_by)
        strict_preflight = evaluate_manual_envelope(envelope)
        if not strict_preflight.allowed:
            raise RuntimeError(strict_preflight.reason)
        started_at = _utc_now_iso()
        channels = delivery_channels(template_id, template.get("delivery_mode"))
        scope_summary = envelope.scope_summary()
        budget_summary = envelope.budget_summary()
        budget_meter = RunBudgetMeter(envelope)
        self._active_budget_meter = budget_meter
        self._active_envelope = envelope
        self._store.set_active_run(
            {
                "envelope_id": envelope.id,
                "template_id": template_id,
                "title": str(template.get("title") or "").strip(),
                "status": "running",
                "status_label": "Running now",
                "triggered_by": triggered_by,
                "delivery_mode": str(template.get("delivery_mode") or "widget").strip(),
                "delivery_channels": channels,
                "started_at": started_at,
                "summary": "Gathering what this task needs and preparing your result.",
                "scope_summary": scope_summary,
                "budget_summary": budget_summary,
                "budget_usage": budget_meter.snapshot(),
            }
        )
        try:
            self._update_run_progress(
                envelope,
                status_label="Collecting sources",
                summary="Gathering the approved information for this task.",
            )
            payload = await self._collect_payload(template_id)
            self._check_cancel(envelope.id)
            prompt = self._build_summary_prompt(template, payload)
            fallback = self._fallback_summary(template_id, payload)
            usage_meta: dict[str, Any] = {}
            summary_model = ""
            summary_route = "deterministic_fallback"
            summarized = ""
            budget_meter.record_step("Summarizing")
            self._update_run_progress(
                envelope,
                status_label="Summarizing",
                summary="Turning the collected information into a clear result.",
            )

            if template_id != "morning_brief":
                summarized = self._summarize_with_local_model(template, prompt)
                if summarized:
                    summary_model = "Local summarizer"
                    summary_route = "local_model"
                    usage_meta = self._local_usage_meta(prompt=prompt, summary=summarized)

            if template_id not in {"morning_brief", "project_snapshot"} and not summarized:
                openai_result = self._summarize_with_metered_openai(template, prompt)
                if openai_result:
                    summarized = str(openai_result.get("text") or "").strip()
                    usage_meta = dict(openai_result.get("usage_meta") or {})
                    summary_model = str(usage_meta.get("model_label") or "OpenAI").strip() or "OpenAI"
                    summary_route = "openai_metered"

            self._check_cancel(envelope.id)
            raw_summary = summarized or fallback
            if not usage_meta:
                usage_meta = self._fallback_usage_meta(
                    template=template,
                    prompt=prompt,
                    summary=raw_summary,
                    openai_attempted=not bool(summarized),
                )
            self._update_run_progress(
                envelope,
                status_label="Delivering",
                summary="Handing the finished result back through Nova.",
            )
            presented_message = self._personality_bridge.present_result(envelope, raw_summary)
            completed_at = _utc_now_iso()
            budget_usage = budget_meter.snapshot()
            budget_usage["per_tool"] = self._per_tool_budget.snapshot()

            run_record = self._store.record_run(
                {
                    "envelope_id": envelope.id,
                    "template_id": template_id,
                    "title": str(template.get("title") or "").strip(),
                    "status": "completed",
                    "triggered_by": triggered_by,
                    "delivery_mode": str(template.get("delivery_mode") or "widget").strip(),
                    "delivery_channels": channels,
                    "presented_message": presented_message,
                    "summary": raw_summary,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "llm_summary_used": bool(summarized),
                    "estimated_input_tokens": _estimate_tokens(prompt) if summarized else 0,
                    "estimated_output_tokens": _estimate_tokens(summarized) if summarized else 0,
                    "estimated_total_tokens": (_estimate_tokens(prompt) + _estimate_tokens(summarized)) if summarized else 0,
                    "summary_route": summary_route,
                    "summary_model": summary_model,
                    "scope_summary": scope_summary,
                    "budget_summary": budget_summary,
                    "budget_usage": budget_usage,
                    "source_notes": dict(payload.get("source_notes") or {}),
                    "strict_preflight": strict_preflight.to_dict(),
                    "usage_meta": usage_meta,
                }
            )

            return {
                "envelope": envelope.to_dict(),
                "template": template,
                "summary": raw_summary,
                "presented_message": presented_message,
                "delivery_channels": channels,
                "llm_summary_used": bool(summarized),
                "estimated_input_tokens": _estimate_tokens(prompt) if summarized else 0,
                "estimated_output_tokens": _estimate_tokens(summarized) if summarized else 0,
                "estimated_total_tokens": (_estimate_tokens(prompt) + _estimate_tokens(summarized)) if summarized else 0,
                "summary_route": summary_route,
                "summary_model": summary_model,
                "source_notes": dict(payload.get("source_notes") or {}),
                "strict_preflight": strict_preflight.to_dict(),
                "usage_meta": usage_meta,
                "scope_summary": scope_summary,
                "budget_summary": budget_summary,
                "budget_usage": budget_usage,
                "run_record": run_record,
            }
        except RunCancelledError:
            budget_usage = budget_meter.snapshot()
            self._store.record_run(
                {
                    "envelope_id": envelope.id,
                    "template_id": template_id,
                    "title": str(template.get("title") or "").strip(),
                    "status": "cancelled",
                    "triggered_by": triggered_by,
                    "delivery_mode": str(template.get("delivery_mode") or "widget").strip(),
                    "delivery_channels": {"widget": False, "chat": False},
                    "presented_message": "",
                    "summary": "This task was cancelled before it finished.",
                    "started_at": started_at,
                    "completed_at": _utc_now_iso(),
                    "llm_summary_used": False,
                    "scope_summary": scope_summary,
                    "budget_summary": budget_summary,
                    "budget_usage": budget_usage,
                    "strict_preflight": strict_preflight.to_dict(),
                }
            )
            raise
        except Exception as exc:
            budget_usage = budget_meter.snapshot()
            self._store.record_run(
                {
                    "envelope_id": envelope.id,
                    "template_id": template_id,
                    "title": str(template.get("title") or "").strip(),
                    "status": "failed",
                    "triggered_by": triggered_by,
                    "delivery_mode": str(template.get("delivery_mode") or "widget").strip(),
                    "delivery_channels": {"widget": False, "chat": False},
                    "presented_message": "",
                    "summary": f"Run failed: {str(exc)[:120]}",
                    "started_at": started_at,
                    "completed_at": _utc_now_iso(),
                    "llm_summary_used": False,
                    "scope_summary": scope_summary,
                    "budget_summary": budget_summary,
                    "budget_usage": budget_usage,
                    "strict_preflight": strict_preflight.to_dict(),
                }
            )
            raise
        finally:
            self._active_budget_meter = None
            self._active_envelope = None
            self._store.clear_active_run(envelope.id)

    def _check_cancel(self, envelope_id: str) -> None:
        if self._store.is_cancel_requested(envelope_id):
            raise RunCancelledError("Run cancelled by user request.")

    def _update_run_progress(
        self,
        envelope: TaskEnvelope,
        *,
        status_label: str,
        summary: str,
    ) -> None:
        meter = self._active_budget_meter
        if meter:
            meter.set_stage(status_label)
        self._store.update_active_run(
            envelope.id,
            {
                "status": "running",
                "status_label": str(status_label or "Running now").strip() or "Running now",
                "summary": str(summary or "").strip(),
                "budget_usage": meter.snapshot() if meter else {},
            },
        )

    def _network_for_run(self) -> Any:
        meter = self._active_budget_meter
        if not meter:
            return self._network
        return MeteredNetworkProxy(delegate=self._network, meter=meter)

    async def _collect_payload(self, template_id: str) -> dict[str, Any]:
        if template_id == "inbox_check":
            # inbox_check has no payload collector. The email connector is not yet available.
            # This template is intentionally not runnable (manual_run_available: False).
            # run_template() enforces that guard before reaching here, but this explicit
            # check prevents silent fallthrough to the morning_brief collector if that
            # guard is ever bypassed in tests or future code paths.
            raise RuntimeError(
                "inbox_check cannot be run yet. The email connector is not part of the active runtime."
            )
        if template_id == "evening_digest":
            return await self._collect_evening_digest_payload()
        if template_id == "market_watch":
            return await self._collect_market_watch_payload()
        if template_id == "project_snapshot":
            return await self._collect_project_snapshot_payload()
        return await self._collect_morning_brief_payload()

    async def _collect_project_snapshot_payload(self) -> dict[str, Any]:
        meter = self._active_budget_meter
        envelope = self._active_envelope
        root = self._project_root()
        readme_path = root / "README.md"
        repo_map_path = root / "REPO_MAP.md"

        if meter:
            meter.record_step("Reading project overview")
        if envelope:
            self._update_run_progress(
                envelope,
                status_label="Reading project overview",
                summary="Reading the current workspace overview and repo map.",
            )

        readme_text = ""
        repo_map_text = ""
        if readme_path.exists():
            if meter:
                meter.record_file_read(readme_path)
            readme_text = readme_path.read_text(encoding="utf-8", errors="ignore")
        if repo_map_path.exists():
            if meter:
                meter.record_file_read(repo_map_path)
            repo_map_text = repo_map_path.read_text(encoding="utf-8", errors="ignore")

        if meter:
            meter.record_step("Mapping project surfaces")
        if envelope:
            self._update_run_progress(
                envelope,
                status_label="Mapping project surfaces",
                summary="Reviewing the major folders and user-facing surfaces in the workspace.",
            )

        top_folders = [
            item.name
            for item in sorted(root.iterdir(), key=lambda entry: entry.name.lower())
            if item.is_dir() and not item.name.startswith(".")
        ][:8]
        top_files = [
            item.name
            for item in sorted(root.iterdir(), key=lambda entry: entry.name.lower())
            if item.is_file() and not item.name.startswith(".")
        ][:8]
        docs_surfaces = [
            label
            for label, path in (
                ("Human guides", root / "docs" / "reference" / "HUMAN_GUIDES"),
                ("Runtime truth", root / "docs" / "current_runtime"),
                ("Design roadmap", root / "docs" / "design"),
                ("Proof packets", root / "docs" / "PROOFS"),
            )
            if path.exists()
        ]

        if meter:
            meter.record_step("Preparing snapshot")
        if envelope:
            self._update_run_progress(
                envelope,
                status_label="Preparing snapshot",
                summary="Turning the workspace review into a bounded project snapshot.",
            )

        return {
            "project_name": root.name,
            "target_path": str(root),
            "project_summary": self._extract_first_paragraph(readme_text)
            or "The current workspace is available, but the README summary is limited.",
            "repo_orientation": self._extract_first_paragraph(repo_map_text),
            "top_folders": top_folders,
            "top_files": top_files,
            "docs_surfaces": docs_surfaces,
            "source_notes": {
                "workspace": "available",
                "readme": "available" if readme_text else "limited",
                "repo_map": "available" if repo_map_text else "limited",
                "docs": "available" if docs_surfaces else "limited",
            },
        }

    async def _collect_morning_brief_payload(self) -> dict[str, Any]:
        network = self._network_for_run()
        meter = self._active_budget_meter
        envelope = self._active_envelope

        # Record budget steps for all three skills up front
        for label in ("Collecting weather", "Collecting calendar", "Collecting news"):
            if meter:
                meter.record_step(label)

        if envelope:
            self._update_run_progress(
                envelope,
                status_label="Collecting sources",
                summary="Gathering weather, calendar, and news in parallel.",
            )

        # Build parallel call list using the tool registry
        calls = [
            {
                "skill": self._tool_registry.create("weather", network=network),
                "query": "weather",
                "timeout": self.WEATHER_TIMEOUT_SECONDS,
                "tool_name": "weather",
                "is_network_tool": True,
            },
            {
                "skill": self._tool_registry.create("calendar"),
                "query": "calendar",
                "timeout": self.CALENDAR_TIMEOUT_SECONDS,
                "tool_name": "calendar",
                "is_network_tool": False,
            },
            {
                "skill": self._tool_registry.create("news", network=network),
                "query": "news",
                "timeout": self.NEWS_TIMEOUT_SECONDS,
                "tool_name": "news",
                "is_network_tool": True,
            },
        ]

        budget_remaining = None
        if meter:
            budget_remaining = max(
                0,
                int(meter.envelope.max_network_calls) - int(meter.network_calls_used),
            )

        results = await self._robust_executor.call_many_parallel(
            calls,
            max_concurrent=3,
            budget_network_remaining=budget_remaining,
        )

        weather_result = results.get("weather")
        calendar_result = results.get("calendar")
        news_result = results.get("news")

        # Record side-effects for metering
        if weather_result and meter:
            meter.record_network_call("https://weather.visualcrossing.com/forecast")
            meter.record_network_bytes(weather_result)
        if calendar_result:
            self._record_skill_side_effects(CalendarSkill(), calendar_result)
        if news_result and meter:
            # News typically hits multiple RSS feeds
            for _url in ("https://www.reuters.com/rssFeed",
                         "https://feeds.apnews.com/apnews",
                         "https://feeds.npr.org/1001/rss.xml",
                         "https://feeds.bbci.co.uk/news/rss.xml"):
                try:
                    meter.record_network_call(_url)
                except RuntimeError:
                    break  # budget exceeded

        # Record to execution memory and per-tool budget
        for tool_name, result in results.items():
            rec = next(
                (r for r in self._robust_executor.call_log
                 if r.tool_name == tool_name),
                None,
            )
            duration = rec.duration_seconds if rec else 0.0
            success = result is not None
            self._execution_memory.record(
                tool_name=tool_name,
                task_type="morning_brief",
                success=success,
                duration_seconds=duration,
                error=rec.error if rec and not rec.success else None,
            )
            is_net = tool_name in ("weather", "news")
            self._per_tool_budget.record_call(
                tool_name,
                duration_seconds=duration,
                success=success,
                network_calls=1 if (is_net and success) else 0,
            )
        if self._active_budget_meter:
            self._active_budget_meter.record_step("Reviewing reminders")
        if self._active_envelope:
            self._update_run_progress(
                self._active_envelope,
                status_label="Reviewing reminders",
                summary="Checking local schedules and assembling the governed briefing.",
            )
        schedules = NotificationScheduleStore().summarize()

        weather_summary = self._weather_summary(weather_result)
        weather_detail = self._weather_detail(weather_result)
        calendar_summary = self._calendar_summary(calendar_result)
        calendar_events = self._calendar_events(calendar_result)
        news_summary = self._news_summary(news_result)
        headlines = self._headline_list(news_result)

        return {
            "weather_summary": weather_summary,
            "weather_detail": weather_detail,
            "calendar_summary": calendar_summary,
            "calendar_events": calendar_events,
            "news_summary": news_summary,
            "headline_titles": headlines,
            "schedule_summary": str(schedules.get("summary") or "").strip(),
            "source_notes": {
                "weather": "available" if weather_summary and "unavailable" not in weather_summary.lower() else "limited",
                "calendar": "available" if "not connected" not in calendar_summary.lower() and "unavailable" not in calendar_summary.lower() else "limited",
                "news": "available" if headlines else "limited",
                "schedules": "available",
            },
        }

    async def _collect_evening_digest_payload(self) -> dict[str, Any]:
        calendar_result = await self._call_skill(
            CalendarSkill(),
            "calendar",
            self.CALENDAR_TIMEOUT_SECONDS,
            stage_label="Collecting calendar",
        )
        news_result = await self._call_skill(
            NewsSkill(network=self._network_for_run()),
            "news",
            self.NEWS_TIMEOUT_SECONDS,
            stage_label="Collecting news",
        )
        if self._active_budget_meter:
            self._active_budget_meter.record_step("Reviewing reminders")
        if self._active_envelope:
            self._update_run_progress(
                self._active_envelope,
                status_label="Reviewing reminders",
                summary="Checking local schedules and assembling the governed digest.",
            )
        schedules = NotificationScheduleStore().summarize()

        calendar_summary = self._calendar_summary(calendar_result)
        news_summary = self._news_summary(news_result)
        headlines = self._headline_list(news_result)

        return {
            "calendar_summary": calendar_summary,
            "news_summary": news_summary,
            "headline_titles": headlines,
            "schedule_summary": str(schedules.get("summary") or "").strip(),
            "source_notes": {
                "calendar": "available" if "not connected" not in calendar_summary.lower() and "unavailable" not in calendar_summary.lower() else "limited",
                "news": "available" if headlines else "limited",
                "schedules": "available",
            },
        }

    async def _collect_market_watch_payload(self) -> dict[str, Any]:
        meter = self._active_budget_meter
        envelope = self._active_envelope
        if meter:
            meter.record_step("Collecting market news")
        if envelope:
            self._update_run_progress(
                envelope,
                status_label="Collecting market news",
                summary="Reading the bounded market-news sources for this run.",
            )

        skill = NewsSkill(network=self._network_for_run())
        crypto_group = next(
            (group for group in list(skill.CATEGORY_GROUPS) if str(group.get("key") or "").strip() == "crypto"),
            {},
        )
        sources = list(crypto_group.get("sources") or [])
        try:
            items = await skill._fetch_many(
                sources,
                semaphore=asyncio.Semaphore(skill.MAX_CONCURRENT_FEEDS),
            )
        except Exception:
            items = []
        market_summary = skill._summarize_headlines(items)
        headlines = [
            str(item.get("title") or "").strip()
            for item in items[:3]
            if isinstance(item, dict) and str(item.get("title") or "").strip()
        ]

        return {
            "market_summary": market_summary,
            "headline_titles": headlines,
            "source_notes": {
                "markets": "available" if headlines else "limited",
            },
        }

    async def _call_skill(
        self,
        skill: Any,
        query: str,
        timeout_seconds: float,
        *,
        stage_label: str,
    ) -> Any | None:
        envelope = self._active_envelope
        meter = self._active_budget_meter
        if meter:
            meter.record_step(stage_label)
        if envelope:
            self._update_run_progress(
                envelope,
                status_label=stage_label,
                summary=f"{stage_label}.",
            )
        result = await self._robust_executor.call_skill(
            skill,
            query,
            timeout_seconds=timeout_seconds,
            tool_name=stage_label,
        )
        if result is not None:
            self._record_skill_side_effects(skill, result)
        return result

    def _record_skill_side_effects(self, skill: Any, result: Any | None) -> None:
        meter = self._active_budget_meter
        if not meter:
            return
        if isinstance(skill, CalendarSkill):
            calendar_path = CalendarSkill._calendar_path()
            if calendar_path is not None:
                meter.record_file_read(calendar_path)

    @staticmethod
    def _weather_summary(result: Any | None) -> str:
        if not result:
            return "Weather is unavailable right now."
        widget_data = dict(getattr(result, "widget_data", {}) or {})
        data = dict(widget_data.get("data") or {})
        summary = str(data.get("summary") or getattr(result, "message", "") or "").strip()
        return summary or "Weather is unavailable right now."

    @staticmethod
    def _calendar_summary(result: Any | None) -> str:
        if not result:
            return "Calendar is unavailable right now."
        widget_data = dict(getattr(result, "widget_data", {}) or {})
        summary = str(widget_data.get("summary") or getattr(result, "message", "") or "").strip()
        return summary or "Calendar is unavailable right now."

    @staticmethod
    def _news_summary(result: Any | None) -> str:
        if not result:
            return "News is unavailable right now."
        widget_data = dict(getattr(result, "widget_data", {}) or {})
        summary = str(widget_data.get("summary") or getattr(result, "message", "") or "").strip()
        return summary or "News is unavailable right now."

    @staticmethod
    def _headline_list(result: Any | None) -> list[str]:
        if not result:
            return []
        widget_data = dict(getattr(result, "widget_data", {}) or {})
        items = list(widget_data.get("items") or [])
        return [
            str(item.get("title") or "").strip()
            for item in items[:3]
            if str(item.get("title") or "").strip()
        ]

    @staticmethod
    def _weather_detail(result: Any | None) -> dict[str, str]:
        """Extract temp, condition, location, forecast from weather widget data."""
        if not result:
            return {}
        widget_data = dict(getattr(result, "widget_data", {}) or {})
        data = dict(widget_data.get("data") or {})
        return {
            "temp": str(data.get("temperature") or "").strip(),
            "condition": str(data.get("condition") or "").strip(),
            "location": str(data.get("location") or "").strip(),
            "forecast": str(data.get("forecast") or "").strip(),
        }

    @staticmethod
    def _calendar_events(result: Any | None) -> list[dict[str, str]]:
        """Extract individual today events from calendar widget."""
        if not result:
            return []
        widget_data = dict(getattr(result, "widget_data", {}) or {})
        events = list(widget_data.get("events") or [])
        return [
            {
                "title": str(ev.get("title") or "").strip(),
                "time": str(ev.get("time") or "").strip(),
            }
            for ev in events[:5]
            if str(ev.get("title") or "").strip()
        ]

    def _build_summary_prompt(self, template: dict[str, Any], payload: dict[str, Any]) -> str:
        template_id = str(template.get("id") or "").strip()
        if template_id == "project_snapshot":
            lines = [
                "Create a calm Nova read-only project snapshot.",
                "Keep it to 4-6 sentences.",
                "Lead with what the project appears to be.",
                "Name the most important visible surfaces.",
                "End with the safest next improvement or review direction.",
                "Do not claim hidden certainty or mention internal workers or envelopes.",
                f"Project: {str(payload.get('project_name') or '').strip()}",
                f"Path: {str(payload.get('target_path') or '').strip()}",
                f"Project summary: {str(payload.get('project_summary') or '').strip()}",
            ]
            repo_orientation = str(payload.get("repo_orientation") or "").strip()
            if repo_orientation:
                lines.append(f"Repo orientation: {repo_orientation}")
            top_folders = [str(item).strip() for item in list(payload.get("top_folders") or []) if str(item).strip()]
            if top_folders:
                lines.append("Top folders: " + ", ".join(top_folders[:6]))
            docs_surfaces = [str(item).strip() for item in list(payload.get("docs_surfaces") or []) if str(item).strip()]
            if docs_surfaces:
                lines.append("Doc layers: " + ", ".join(docs_surfaces[:4]))
            top_files = [str(item).strip() for item in list(payload.get("top_files") or []) if str(item).strip()]
            if top_files:
                lines.append("Key files: " + ", ".join(top_files[:6]))
            return "\n".join(lines).strip()

        title = str(template.get("title") or "Briefing").strip()
        lines = [
            f"Create a calm Nova task report for '{title}'.",
            "Keep it to 2-4 sentences.",
            "Lead with the useful thing.",
            "Do not mention internal tools, workers, or envelopes.",
        ]
        # Weather — prefer structured detail over summary text
        weather_detail = dict(payload.get("weather_detail") or {})
        if weather_detail.get("temp") and weather_detail.get("condition"):
            _wtemp = weather_detail["temp"]
            _wcond = weather_detail["condition"]
            _wloc = weather_detail.get("location") or ""
            _wfcast = weather_detail.get("forecast") or ""
            _wline = f"{_wtemp}°F, {_wcond}"
            if _wloc:
                _wline += f" in {_wloc}"
            if _wfcast:
                _wline += f". {_wfcast}"
            lines.append(f"Weather: {_wline}")
        else:
            weather_summary = str(payload.get("weather_summary") or "").strip()
            if weather_summary:
                lines.append(f"Weather Summary: {weather_summary}")
        # Calendar — prefer individual events over summary text
        cal_events = list(payload.get("calendar_events") or [])
        if cal_events:
            event_strs = [
                f"{ev.get('time', '')} {ev.get('title', '')}".strip()
                for ev in cal_events
            ]
            lines.append("Today's schedule: " + "; ".join(event_strs))
        else:
            calendar_summary = str(payload.get("calendar_summary") or "").strip()
            if calendar_summary:
                lines.append(f"Calendar Summary: {calendar_summary}")
        # News, market, schedules
        for key in ("news_summary", "market_summary", "schedule_summary"):
            value = str(payload.get(key) or "").strip()
            if value:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        headlines = [str(item).strip() for item in list(payload.get("headline_titles") or []) if str(item).strip()]
        if headlines:
            lines.append("Headlines: " + "; ".join(headlines[:3]))
        return "\n".join(lines).strip()

    def _summarize_with_local_model(self, template: dict[str, Any], prompt: str) -> str:
        if not prompt:
            return ""
        title = str(template.get("title") or "briefing").strip().lower()
        system_prompt = (
            "You are Nova. Write a calm, direct household task report. "
            "Be useful first. Keep the tone warm without sounding eager."
        )
        result = llm_gateway.generate_chat(
            prompt,
            mode="task_report",
            safety_profile="local_task_report",
            request_id=f"openclaw_{str(template.get('id') or 'task').strip()}",
            system_prompt=system_prompt,
            max_tokens=220,
            temperature=0.55,
            timeout=self.SUMMARY_TIMEOUT_SECONDS,
        )
        if not result:
            return ""
        clean = str(result).strip()
        if clean.lower().startswith(title):
            return clean
        return clean

    def _summarize_with_metered_openai(self, template: dict[str, Any], prompt: str) -> dict[str, Any] | None:
        plan = self._openai_lane.plan_for_openclaw_fallback()
        if not bool(plan.get("allowed")):
            return None

        request_id = f"openclaw_{str(template.get('id') or 'task').strip()}_openai"
        try:
            return self._openai_lane.summarize_task_report(
                prompt=prompt,
                system_prompt=(
                    "You are Nova. Write a calm, direct household task report. "
                    "Be useful first. Keep the tone warm without sounding eager."
                ),
                model=str(plan.get("preferred_model") or "gpt-5.4-mini").strip() or "gpt-5.4-mini",
                request_id=request_id,
                max_output_tokens=220,
                task_label=str(template.get("title") or "OpenClaw task report").strip() or "OpenClaw task report",
            )
        except OpenAIResponsesLaneError:
            return None

    @staticmethod
    def _local_usage_meta(*, prompt: str, summary: str) -> dict[str, Any]:
        return {
            "route": "local_model",
            "route_label": "Local summarizer",
            "provider_label": "Local model",
            "model_label": "Local summarizer",
            "metered": False,
            "local_only": True,
            "measurement_label": "Estimated tokens",
            "estimated_input_tokens": _estimate_tokens(prompt),
            "estimated_output_tokens": _estimate_tokens(summary),
            "estimated_total_tokens": _estimate_tokens(prompt) + _estimate_tokens(summary),
            "exact_input_tokens": 0,
            "exact_output_tokens": 0,
            "exact_total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "budget_state": "normal",
            "budget_state_label": "Normal",
            "summary": "This run stayed local. Nova used the local summarizer and spent no metered OpenAI tokens.",
        }

    @staticmethod
    def _fallback_usage_meta(
        *,
        template: dict[str, Any],
        prompt: str,
        summary: str,
        openai_attempted: bool,
    ) -> dict[str, Any]:
        title = str(template.get("title") or "This run").strip() or "This run"
        detail = (
            "Nova stayed off the metered lane and returned a deterministic fallback summary."
            if openai_attempted
            else "Nova stayed local and returned a deterministic fallback summary."
        )
        return {
            "route": "deterministic_fallback",
            "route_label": "Deterministic fallback",
            "provider_label": "Deterministic fallback",
            "model_label": "No model",
            "metered": False,
            "local_only": True,
            "measurement_label": "Estimated tokens",
            "estimated_input_tokens": _estimate_tokens(prompt),
            "estimated_output_tokens": _estimate_tokens(summary),
            "estimated_total_tokens": _estimate_tokens(prompt) + _estimate_tokens(summary),
            "exact_input_tokens": 0,
            "exact_output_tokens": 0,
            "exact_total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "budget_state": "normal",
            "budget_state_label": "Normal",
            "summary": f"{title} used a deterministic local fallback. {detail}",
        }

    def _fallback_summary(self, template_id: str, payload: dict[str, Any]) -> str:
        if template_id == "project_snapshot":
            project_name = str(payload.get("project_name") or "This workspace").strip() or "This workspace"
            project_summary = str(payload.get("project_summary") or "").strip()
            repo_orientation = str(payload.get("repo_orientation") or "").strip()
            top_folders = [str(item).strip() for item in list(payload.get("top_folders") or []) if str(item).strip()]
            docs_surfaces = [str(item).strip() for item in list(payload.get("docs_surfaces") or []) if str(item).strip()]
            lines = [f"Project Snapshot: {project_name}"]
            if project_summary:
                lines.extend(["", project_summary])
            if repo_orientation:
                lines.extend(["", f"Repo orientation: {repo_orientation}"])
            if top_folders:
                lines.extend(["", "Main surfaces: " + ", ".join(top_folders[:6])])
            if docs_surfaces:
                lines.append("Docs layers: " + ", ".join(docs_surfaces[:4]))
            lines.extend(
                [
                    "",
                    "Suggested next step: review the biggest gap or request the safest focused improvement before any write-capable flow is added.",
                ]
            )
            return "\n".join(lines).strip()

        if template_id == "market_watch":
            parts = [
                str(payload.get("market_summary") or "").strip(),
            ]
            return " ".join(part for part in parts if part).strip() or "Market watch is ready."
        schedule_summary = str(payload.get("schedule_summary") or "").strip()
        if template_id == "evening_digest":
            parts = [
                str(payload.get("calendar_summary") or "").strip(),
                str(payload.get("news_summary") or "").strip(),
            ]
            if schedule_summary:
                parts.append(f"Scheduled updates: {schedule_summary}.")
            return " ".join(part for part in parts if part).strip() or "Evening digest is ready."

        # Structured morning brief — matches the chat-command brief format
        _now = datetime.now()
        _day_str = f"{_now.strftime('%A, %B')} {_now.day}"
        _time_str = _now.strftime("%I:%M %p").lstrip("0")

        weather_detail = dict(payload.get("weather_detail") or {})
        _temp = weather_detail.get("temp") or ""
        _cond = weather_detail.get("condition") or ""
        _loc = weather_detail.get("location") or ""
        _fcast = weather_detail.get("forecast") or ""
        if _temp and _cond:
            _weather_line = f"{_temp}°F, {_cond}"
            if _loc:
                _weather_line += f" in {_loc}"
            _weather_line += "."
            if _fcast:
                _weather_line += f" {_fcast}"
        else:
            _weather_line = str(payload.get("weather_summary") or "Weather unavailable.").strip()

        _cal_events = list(payload.get("calendar_events") or [])
        if _cal_events:
            _event_lines = "\n".join(
                f"  {ev.get('time', ''):<12}{ev.get('title', '')}"
                for ev in _cal_events
            )
            _cal_section = f"Schedule:\n{_event_lines}"
        else:
            _cal_section = f"Schedule: {str(payload.get('calendar_summary') or 'No events today.').strip()}"

        _headlines = [
            str(h).strip()
            for h in list(payload.get("headline_titles") or [])
            if str(h).strip()
        ]

        _parts = [f"Morning Brief — {_day_str} at {_time_str}", ""]
        _parts.append(f"Weather: {_weather_line}")
        _parts.append("")
        _parts.append(_cal_section)
        if _headlines:
            _parts.append("")
            _parts.append("News: " + _headlines[0])
            for _h in _headlines[1:]:
                _parts.append(f"  Also: {_h}")
        elif payload.get("news_summary") and "unavailable" not in str(payload.get("news_summary") or "").lower():
            _parts.append("")
            _parts.append(f"News: {payload['news_summary']}")
        if schedule_summary:
            _parts.append("")
            _parts.append(f"Schedules: {schedule_summary}")
        return "\n".join(_parts)

    @staticmethod
    def _project_root() -> Path:
        return Path(__file__).resolve().parents[3]

    @staticmethod
    def _extract_first_paragraph(text: str) -> str:
        paragraphs: list[str] = []
        current: list[str] = []
        for raw_line in str(text or "").splitlines():
            line = str(raw_line or "").strip()
            if not line:
                if current:
                    paragraphs.append(" ".join(current).strip())
                    current = []
                continue
            if line.startswith("#") or line.startswith("- ") or line.startswith("* "):
                if current:
                    paragraphs.append(" ".join(current).strip())
                    current = []
                continue
            if "." in line:
                prefix, _rest = line.split(".", 1)
                if prefix.isdigit():
                    if current:
                        paragraphs.append(" ".join(current).strip())
                        current = []
                    continue
            current.append(line)
        if current:
            paragraphs.append(" ".join(current).strip())
        for paragraph in paragraphs:
            if paragraph:
                return paragraph
        return ""

    # ------------------------------------------------------------------
    # Goal-based execution (ThinkingLoop path)
    # ------------------------------------------------------------------

    async def run_goal(self, goal: str, *, triggered_by: str = "user") -> dict[str, Any]:
        """Run a freeform goal through the LLM-guided thinking loop.

        Unlike run_template() which executes a fixed template, this accepts
        any natural language goal and lets the ThinkingLoop reason about
        which tools to use and in what order.

        Returns the full execution record from ThinkingLoop.run() plus
        a presentable summary.
        """
        if not (goal or "").strip():
            raise ValueError("Goal cannot be empty")

        t0 = time.monotonic()

        loop = ThinkingLoop(
            registry=self._tool_registry,
            executor=self._robust_executor,
            network=self._network,
            execution_memory=self._execution_memory,
        )

        # Track active run for progress/cancellation
        goal_id = f"goal_{int(t0 * 1000)}"
        self._store.set_active_run({
            "envelope_id": goal_id,
            "template_id": "goal",
            "title": goal[:80],
            "status": "running",
            "status_label": "Thinking",
            "triggered_by": triggered_by,
            "delivery_mode": "widget",
            "delivery_channels": ["widget"],
            "started_at": _utc_now_iso(),
            "summary": f"Working on: {goal}",
        })

        def _on_step_progress(step_num: int, status: str, tools: list[str]) -> None:
            if self._store.is_cancel_requested(goal_id):
                raise RunCancelledError("Goal cancelled by user request.")
            self._store.update_active_run(goal_id, {
                "status_label": f"Step {step_num}: {', '.join(tools)}",
                "summary": f"Step {step_num}/{loop.MAX_STEPS} — {status}",
            })

        loop.set_progress_callback(_on_step_progress)

        try:
            result = await loop.run(goal.strip())
        except RunCancelledError:
            self._store.clear_active_run(goal_id)
            return {
                "goal": goal,
                "triggered_by": triggered_by,
                "success": False,
                "steps": len(loop.thoughts),
                "summary": "Goal was cancelled before completion.",
                "thoughts": loop.thoughts,
                "total_duration_seconds": round(time.monotonic() - t0, 3),
                "cancelled": True,
            }
        finally:
            self._store.clear_active_run(goal_id)

        # Record execution stats to memory
        for thought in result.get("thoughts", []):
            for tool_name in thought.selected_tools:
                tool_result = thought.results.get(tool_name)
                self._execution_memory.record(
                    tool_name=tool_name,
                    task_type="goal",
                    success=tool_result is not None and not (
                        isinstance(tool_result, dict) and tool_result.get("error")
                    ),
                    duration_seconds=thought.duration_seconds,
                )
                self._per_tool_budget.record_call(
                    tool_name,
                    duration_seconds=thought.duration_seconds,
                    success=tool_result is not None,
                )

        # Use LLM synthesis if available, fall back to static extraction
        summary = result.get("synthesis") or self._summarize_goal_result(goal, result)

        total_duration = time.monotonic() - t0

        return {
            "goal": goal,
            "triggered_by": triggered_by,
            "success": result.get("success", False),
            "steps": result.get("steps", 0),
            "summary": summary,
            "thoughts": result.get("thoughts", []),
            "total_duration_seconds": round(total_duration, 3),
            "per_tool_budget": self._per_tool_budget.snapshot(),
        }

    @staticmethod
    def _summarize_goal_result(goal: str, result: dict[str, Any]) -> str:
        """Extract a human-readable summary from thinking loop results."""
        thoughts = result.get("thoughts", [])
        if not thoughts:
            return f"I wasn't able to make progress on: {goal}"

        # Collect successful results
        summaries: list[str] = []
        for thought in thoughts:
            for tool_name, tool_result in thought.results.items():
                if tool_result is None:
                    continue
                if isinstance(tool_result, dict) and tool_result.get("error"):
                    continue
                msg = getattr(tool_result, "message", None)
                if msg:
                    summaries.append(str(msg).strip())

        if summaries:
            return " ".join(summaries[:3])

        if result.get("success"):
            return f"Completed goal: {goal}"
        return f"Attempted but could not fully complete: {goal}"


openclaw_agent_runner = OpenClawAgentRunner(store=openclaw_agent_runtime_store)
