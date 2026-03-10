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


class WeatherSnapshotExecutor:
    def __init__(self, network: Any | None = None) -> None:
        self._skill = WeatherSkill(network=network)

    def execute(self, request) -> ActionResult:
        result = _run_skill(self._skill, "weather")
        if result is None:
            return ActionResult.failure(
                "Weather is currently unavailable.",
                data={"widget": _fallback_widget(55)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        message = str(getattr(result, "message", "") or "Weather is currently unavailable.").strip()
        widget = getattr(result, "widget_data", None)
        if getattr(result, "success", False):
            return ActionResult.ok(
                message=message,
                data={"widget": widget if isinstance(widget, dict) else _fallback_widget(55)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        return ActionResult.failure(
            message=message or "Weather is currently unavailable.",
            data={"widget": widget if isinstance(widget, dict) else _fallback_widget(55)},
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
                data={"widget": _fallback_widget(56)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        message = str(getattr(result, "message", "") or "News is currently unavailable.").strip()
        widget = getattr(result, "widget_data", None)
        if getattr(result, "success", False):
            return ActionResult.ok(
                message=message,
                data={"widget": widget if isinstance(widget, dict) else _fallback_widget(56)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        return ActionResult.failure(
            message=message or "News is currently unavailable.",
            data={"widget": widget if isinstance(widget, dict) else _fallback_widget(56)},
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
                data={"widget": _fallback_widget(57)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        message = str(getattr(result, "message", "") or "Calendar is currently unavailable.").strip()
        widget = getattr(result, "widget_data", None)
        if getattr(result, "success", False):
            return ActionResult.ok(
                message=message,
                data={"widget": widget if isinstance(widget, dict) else _fallback_widget(57)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        return ActionResult.failure(
            message=message or "Calendar is currently unavailable.",
            data={"widget": widget if isinstance(widget, dict) else _fallback_widget(57)},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

