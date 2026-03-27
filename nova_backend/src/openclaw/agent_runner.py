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
from src.openclaw.task_envelope import TaskEnvelope
from src.personality.conversation_personality_agent import ConversationPersonalityAgent
from src.skills.calendar import CalendarSkill
from src.skills.news import NewsSkill
from src.skills.weather import WeatherSkill
from src.tasks.notification_schedule_store import NotificationScheduleStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    ) -> None:
        self._store = store or openclaw_agent_runtime_store
        self._network = network
        self._personality_bridge = OpenClawAgentPersonalityBridge(presenter=presenter)

    async def run_template(self, template_id: str, *, triggered_by: str = "dashboard") -> dict[str, Any]:
        template = self._store.get_template(template_id)
        if template is None:
            raise KeyError(template_id)
        if not bool(template.get("manual_run_available")):
            raise RuntimeError(str(template.get("availability_reason") or "This template is not ready yet.").strip())

        envelope = TaskEnvelope.from_template(template, triggered_by=triggered_by)
        started_at = _utc_now_iso()
        payload = await self._collect_payload(template_id)
        prompt = self._build_summary_prompt(template, payload)
        summarized = self._summarize_with_local_model(template, prompt)
        fallback = self._fallback_summary(template_id, payload)
        raw_summary = summarized or fallback
        presented_message = self._personality_bridge.present_result(envelope, raw_summary)
        channels = delivery_channels(template_id, template.get("delivery_mode"))
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
                "source_notes": dict(payload.get("source_notes") or {}),
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
            "source_notes": dict(payload.get("source_notes") or {}),
            "run_record": run_record,
        }

    async def _collect_payload(self, template_id: str) -> dict[str, Any]:
        if template_id == "evening_digest":
            return await self._collect_evening_digest_payload()
        return await self._collect_morning_brief_payload()

    async def _collect_morning_brief_payload(self) -> dict[str, Any]:
        weather_result = await self._call_skill(WeatherSkill(network=self._network), "weather", self.WEATHER_TIMEOUT_SECONDS)
        calendar_result = await self._call_skill(CalendarSkill(), "calendar", self.CALENDAR_TIMEOUT_SECONDS)
        news_result = await self._call_skill(NewsSkill(network=self._network), "news", self.NEWS_TIMEOUT_SECONDS)
        schedules = NotificationScheduleStore().summarize()

        weather_summary = self._weather_summary(weather_result)
        calendar_summary = self._calendar_summary(calendar_result)
        news_summary = self._news_summary(news_result)
        headlines = self._headline_list(news_result)

        return {
            "weather_summary": weather_summary,
            "calendar_summary": calendar_summary,
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

    def _build_summary_prompt(self, template: dict[str, Any], payload: dict[str, Any]) -> str:
        title = str(template.get("title") or "Briefing").strip()
        lines = [
            f"Create a calm Nova task report for '{title}'.",
            "Keep it to 2-4 sentences.",
            "Lead with the useful thing.",
            "Do not mention internal tools, workers, or envelopes.",
        ]
        for key in ("weather_summary", "calendar_summary", "news_summary", "schedule_summary"):
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

    def _fallback_summary(self, template_id: str, payload: dict[str, Any]) -> str:
        schedule_summary = str(payload.get("schedule_summary") or "").strip()
        if template_id == "evening_digest":
            parts = [
                str(payload.get("calendar_summary") or "").strip(),
                str(payload.get("news_summary") or "").strip(),
            ]
            if schedule_summary:
                parts.append(f"Scheduled updates: {schedule_summary}.")
            return " ".join(part for part in parts if part).strip() or "Evening digest is ready."

        parts = [
            str(payload.get("weather_summary") or "").strip(),
            str(payload.get("calendar_summary") or "").strip(),
            str(payload.get("news_summary") or "").strip(),
        ]
        if schedule_summary:
            parts.append(f"Scheduled updates: {schedule_summary}.")
        return " ".join(part for part in parts if part).strip() or "Morning brief is ready."


openclaw_agent_runner = OpenClawAgentRunner(store=openclaw_agent_runtime_store)
