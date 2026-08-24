from __future__ import annotations

import asyncio
import inspect
import re
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
            "daily brief",
        ]
    if capability_id == 56:
        return [
            "summarize headline 1",
            "daily brief",
            "more on story 1",
        ]
    return [
        "today's schedule",
        "tomorrow's schedule",
        "upcoming events",
        "daily brief",
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
        lines.append("Try next: weather forecast, today's news, or daily brief.")
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
    lines.append("Try next: today's schedule, tomorrow's schedule, what's coming up, or daily brief.")
    return "\n".join(lines)


class WeatherSnapshotExecutor:
    def __init__(self, network: Any | None = None) -> None:
        self._network = network

    def execute(self, request) -> ActionResult:
        requested_location = re.sub(
            r"\s+",
            " ",
            str(request.params.get("location") or ""),
        ).strip(" ,.")[:120]
        requested_scope = str(request.params.get("scope") or "today").strip().lower()
        if requested_scope not in {"today", "tomorrow"}:
            requested_scope = "today"
        skill = WeatherSkill(
            network=self._network,
            location=requested_location or None,
            scope=requested_scope,
        )
        result = _run_skill(skill, "weather tomorrow" if requested_scope == "tomorrow" else "weather")
        if result is None:
            widget = _fallback_widget(55)
            if requested_location:
                widget["data"]["location"] = requested_location
            return ActionResult.failure(
                (
                    f"Weather for {requested_location} is currently unavailable."
                    if requested_location
                    else "Weather is currently unavailable."
                ),
                data={"widget": widget, "follow_up_prompts": _follow_up_prompts(55)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        widget = getattr(result, "widget_data", None)
        safe_widget = widget if isinstance(widget, dict) else _fallback_widget(55)
        if requested_location:
            safe_widget.setdefault("data", {}).setdefault("location", requested_location)
        fallback_message = str(
            getattr(result, "message", "")
            or (
                f"Weather for {requested_location} is currently unavailable."
                if requested_location
                else "Weather is currently unavailable."
            )
        ).strip()
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
    _SCOPE_QUERIES = {
        "today": "calendar",
        "tomorrow": "tomorrow's schedule",
        "upcoming": "upcoming events",
    }

    def __init__(self) -> None:
        self._skill = CalendarSkill()

    def execute(self, request) -> ActionResult:
        requested_scope = str((request.params or {}).get("scope") or "today").strip().lower()
        query = self._SCOPE_QUERIES.get(requested_scope, self._SCOPE_QUERIES["today"])
        result = _run_skill(self._skill, query)
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
