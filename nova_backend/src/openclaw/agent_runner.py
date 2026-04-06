from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from src.llm import llm_gateway
from src.openclaw.agent_personality_bridge import (
    OpenClawAgentPersonalityBridge,
    delivery_channels,
)
from src.openclaw.agent_runtime_store import (
    OpenClawAgentRuntimeStore,
    openclaw_agent_runtime_store,
)
from src.openclaw.strict_preflight import evaluate_manual_envelope
from src.openclaw.task_envelope import TaskEnvelope
from src.personality.conversation_personality_agent import ConversationPersonalityAgent
from src.providers.openai_responses_lane import OpenAIResponsesLane, OpenAIResponsesLaneError
from src.skills.calendar import CalendarSkill
from src.skills.news import NewsSkill
from src.skills.weather import WeatherSkill
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
    ) -> None:
        self._store = store or openclaw_agent_runtime_store
        self._network = network
        self._personality_bridge = OpenClawAgentPersonalityBridge(presenter=presenter)
        self._openai_lane = openai_lane or OpenAIResponsesLane(network=network)

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
                "summary": "Collecting sources and preparing a governed briefing.",
                "scope_summary": scope_summary,
                "budget_summary": budget_summary,
                "budget_usage": {},
            }
        )
        try:
            payload = await self._collect_payload(template_id)
            self._check_cancel(envelope.id)
            budget_usage = self._estimate_budget_usage(template_id, envelope, payload)
            prompt = self._build_summary_prompt(template, payload)
            fallback = self._fallback_summary(template_id, payload)
            usage_meta: dict[str, Any] = {}
            summary_model = ""
            summary_route = "deterministic_fallback"
            summarized = ""

            if template_id != "morning_brief":
                summarized = self._summarize_with_local_model(template, prompt)
                if summarized:
                    summary_model = "Local summarizer"
                    summary_route = "local_model"
                    usage_meta = self._local_usage_meta(prompt=prompt, summary=summarized)

            if template_id != "morning_brief" and not summarized:
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
            presented_message = self._personality_bridge.present_result(envelope, raw_summary)
            completed_at = _utc_now_iso()

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
                    "summary": "Run was cancelled before it completed.",
                    "started_at": started_at,
                    "completed_at": _utc_now_iso(),
                    "llm_summary_used": False,
                    "scope_summary": scope_summary,
                    "budget_summary": budget_summary,
                    "budget_usage": {},
                    "strict_preflight": strict_preflight.to_dict(),
                }
            )
            raise
        except Exception as exc:
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
                    "budget_usage": {},
                    "strict_preflight": strict_preflight.to_dict(),
                }
            )
            raise
        finally:
            self._store.clear_active_run(envelope.id)

    def _check_cancel(self, envelope_id: str) -> None:
        if self._store.is_cancel_requested(envelope_id):
            raise RunCancelledError("Run cancelled by user request.")

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
        return await self._collect_morning_brief_payload()

    async def _collect_morning_brief_payload(self) -> dict[str, Any]:
        weather_result = await self._call_skill(WeatherSkill(network=self._network), "weather", self.WEATHER_TIMEOUT_SECONDS)
        calendar_result = await self._call_skill(CalendarSkill(), "calendar", self.CALENDAR_TIMEOUT_SECONDS)
        news_result = await self._call_skill(NewsSkill(network=self._network), "news", self.NEWS_TIMEOUT_SECONDS)
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
        calendar_result = await self._call_skill(CalendarSkill(), "calendar", self.CALENDAR_TIMEOUT_SECONDS)
        news_result = await self._call_skill(NewsSkill(network=self._network), "news", self.NEWS_TIMEOUT_SECONDS)
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
        news_result = await self._call_skill(NewsSkill(network=self._network), "market news", self.NEWS_TIMEOUT_SECONDS)
        widget_data = dict(getattr(news_result, "widget_data", {}) or {})
        categories = dict(widget_data.get("categories") or {})
        crypto_bucket = dict(categories.get("crypto") or {})
        market_summary = str(
            crypto_bucket.get("summary")
            or widget_data.get("summary")
            or getattr(news_result, "message", "")
            or ""
        ).strip() or "Market research is unavailable right now."
        items = list(crypto_bucket.get("items") or widget_data.get("items") or [])
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

    async def _call_skill(self, skill: Any, query: str, timeout_seconds: float) -> Any | None:
        try:
            return await asyncio.wait_for(skill.handle(query), timeout=timeout_seconds)
        except Exception:
            return None

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
            _wline = _wline.replace("Â°F", "°F")
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
            _weather_line = _weather_line.replace("Â°F", "°F")
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

    def _estimate_budget_usage(
        self,
        template_id: str,
        envelope: TaskEnvelope,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        source_notes = dict(payload.get("source_notes") or {})
        uses_weather = "weather" in envelope.tools_allowed
        uses_calendar = "calendar" in envelope.tools_allowed
        uses_news = "news" in envelope.tools_allowed
        uses_schedules = "schedules" in envelope.tools_allowed
        uses_summarize = "summarize" in envelope.tools_allowed

        steps_used = sum(
            1
            for flag in (uses_weather, uses_calendar, uses_news, uses_schedules, uses_summarize)
            if flag
        )
        network_calls_estimated = 0
        if uses_weather:
            network_calls_estimated += 1
        if uses_news:
            network_calls_estimated += 3 if template_id == "market_watch" else 4
        files_touched_estimated = (
            1 if uses_calendar and str(source_notes.get("calendar") or "").strip() == "available" else 0
        )
        bytes_read_estimated = 0
        if uses_weather:
            bytes_read_estimated += 25_000
        if uses_news:
            bytes_read_estimated += 220_000 if template_id == "market_watch" else 350_000
        if files_touched_estimated:
            bytes_read_estimated += 25_000

        return {
            "steps_used": steps_used,
            "steps_budget": int(envelope.max_steps),
            "network_calls_estimated": network_calls_estimated,
            "network_calls_budget": int(envelope.max_network_calls),
            "files_touched_estimated": files_touched_estimated,
            "files_touched_budget": int(envelope.max_files_touched),
            "bytes_read_estimated": bytes_read_estimated,
            "bytes_read_budget": int(envelope.max_bytes_read),
            "bytes_written_estimated": 0,
            "bytes_written_budget": int(envelope.max_bytes_written),
            "metering_mode": "estimated",
            "summary": (
                f"Estimated usage: {steps_used}/{int(envelope.max_steps)} steps, "
                f"{network_calls_estimated}/{int(envelope.max_network_calls)} network calls, "
                f"{files_touched_estimated}/{int(envelope.max_files_touched)} file touches. "
                "Byte usage is estimated for now."
            ),
        }


openclaw_agent_runner = OpenClawAgentRunner(store=openclaw_agent_runtime_store)
