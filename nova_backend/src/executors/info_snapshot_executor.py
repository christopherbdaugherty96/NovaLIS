from __future__ import annotations

import asyncio
import inspect
from typing import Any

from src.actions.action_result import ActionResult
from src.skills.calendar import CalendarSkill
from src.skills.news import NewsSkill
from src.skills.weather import WeatherSkill


def _run_skill(skill: Any, query: str) -> Any:
    result = skill.handle(query)
    if inspect.isawaitable(result):
        return asyncio.run(result)
    return result


def _fallback_widget(capability_id: int) -> dict[str, Any]:
    if capability_id == 55:
        return {
            "type": "weather",
            "data": {
                "summary": "Weather is currently unavailable.",
                "temperature": None,
                "condition": "Unavailable",
                "location": "Local",
                "forecast": "",
                "alerts": [],
            },
        }
    if capability_id == 56:
        return {
            "type": "news",
            "items": [],
            "summary": "News is currently unavailable.",
            "categories": {},
        }
    return {
        "type": "calendar",
        "summary": "Unavailable.",
        "events": [],
    }


def _follow_up_prompts(capability_id: int) -> list[str]:
    if capability_id == 55:
        return [
            "weather forecast",
            "today's news",
            "morning brief",
        ]
    if capability_id == 56:
        return [
            "summarize headline 1",
            "daily brief",
            "more on story 1",
        ]
    return [
        "today's schedule",
        "morning brief",
        "system status",
    ]


def _build_snapshot_message(capability_id: int, widget: dict[str, Any], fallback: str) -> str:
    if capability_id == 55:
        data = dict(widget.get("data") or {})
        summary = str(data.get("summary") or "").strip()
        location = str(data.get("location") or "").strip()
        forecast = str(data.get("forecast") or "").strip()
        alerts = list(data.get("alerts") or [])
        lines = [summary or fallback]
        if location:
            lines.append(f"Location: {location}")
        if forecast:
            lines.append(f"Forecast: {forecast}")
        if alerts:
            lines.append(f"Alerts: {len(alerts)} active")
        lines.append("Try next: weather forecast, today's news, or morning brief.")
        return "\n".join(lines)

    if capability_id == 56:
        items = list(widget.get("items") or [])
        summary = str(widget.get("summary") or "").strip()
        lines = [summary or fallback]
        if items:
            lines.append(f"Loaded {len(items)} headline(s) for follow-up.")
            lines.append("Try next: summarize headline 1, more on story 1, or daily brief.")
        return "\n".join(lines)

    events = list(widget.get("events") or [])
    summary = str(widget.get("summary") or "").strip()
    lines = [summary or fallback]
    if events:
        lines.append(f"Upcoming events loaded: {len(events)}")
    lines.append("Try next: today's schedule, morning brief, or system status.")
    return "\n".join(lines)


class WeatherSnapshotExecutor:
    def __init__(self, network: Any | None = None) -> None:
        self._skill = WeatherSkill(network=network)

    def execute(self, request) -> ActionResult:
        result = _run_skill(self._skill, "weather")
        if result is None:
            return ActionResult.failure(
                "Weather is currently unavailable.",
                data={"widget": _fallback_widget(55), "follow_up_prompts": _follow_up_prompts(55)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        widget = getattr(result, "widget_data", None)
        safe_widget = widget if isinstance(widget, dict) else _fallback_widget(55)
        fallback_message = str(getattr(result, "message", "") or "Weather is currently unavailable.").strip()
        message = _build_snapshot_message(55, safe_widget, fallback_message)
        if getattr(result, "success", False):
            return ActionResult.ok(
                message=message,
                data={"widget": safe_widget, "follow_up_prompts": _follow_up_prompts(55)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        return ActionResult.failure(
            message=message or "Weather is currently unavailable.",
            data={"widget": safe_widget, "follow_up_prompts": _follow_up_prompts(55)},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )


class NewsSnapshotExecutor:
    def __init__(self, network: Any | None = None) -> None:
        self._skill = NewsSkill(network=network)

    def execute(self, request) -> ActionResult:
        result = _run_skill(self._skill, "news")
        if result is None:
            return ActionResult.failure(
                "News is currently unavailable.",
                data={"widget": _fallback_widget(56), "follow_up_prompts": _follow_up_prompts(56)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        widget = getattr(result, "widget_data", None)
        safe_widget = widget if isinstance(widget, dict) else _fallback_widget(56)
        fallback_message = str(getattr(result, "message", "") or "News is currently unavailable.").strip()
        message = _build_snapshot_message(56, safe_widget, fallback_message)
        if getattr(result, "success", False):
            return ActionResult.ok(
                message=message,
                data={"widget": safe_widget, "follow_up_prompts": _follow_up_prompts(56)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        return ActionResult.failure(
            message=message or "News is currently unavailable.",
            data={"widget": safe_widget, "follow_up_prompts": _follow_up_prompts(56)},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )


class CalendarSnapshotExecutor:
    def __init__(self) -> None:
        self._skill = CalendarSkill()

    def execute(self, request) -> ActionResult:
        result = _run_skill(self._skill, "calendar")
        if result is None:
            return ActionResult.failure(
                "Calendar is currently unavailable.",
                data={"widget": _fallback_widget(57), "follow_up_prompts": _follow_up_prompts(57)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        widget = getattr(result, "widget_data", None)
        safe_widget = widget if isinstance(widget, dict) else _fallback_widget(57)
        fallback_message = str(getattr(result, "message", "") or "Calendar is currently unavailable.").strip()
        message = _build_snapshot_message(57, safe_widget, fallback_message)
        if getattr(result, "success", False):
            return ActionResult.ok(
                message=message,
                data={"widget": safe_widget, "follow_up_prompts": _follow_up_prompts(57)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        return ActionResult.failure(
            message=message or "Calendar is currently unavailable.",
            data={"widget": safe_widget, "follow_up_prompts": _follow_up_prompts(57)},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
