"""Morning Brief handler — governed brief via RoutineGraph.

Extracts the morning brief path from session_handler into a clean
module. Uses run_daily_brief_routine() to produce a RoutineRun and
RoutineReceipt alongside the brief text.

Non-authorizing: the brief is read-only synthesis. It does not
execute capabilities, grant authority, or modify state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.routine.daily_brief_routine import run_daily_brief_routine
from src.routine.routine_graph import RoutineReceipt, RoutineRun
from src.trust.receipt_store import get_recent_receipts


MORNING_BRIEF_TRIGGERS = frozenset({
    "morning",
    "morning brief",
    "brief",
    "brief me",
    "what did i miss",
    "catch me up",
})


@dataclass(frozen=True)
class MorningBriefResult:
    """Result of assembling a governed morning brief."""
    text: str
    run: RoutineRun
    receipt: RoutineReceipt
    brief_dict: dict[str, Any]

    @property
    def has_content(self) -> bool:
        return bool(self.brief_dict.get("sections"))


def is_morning_brief_request(lowered: str) -> bool:
    return lowered in MORNING_BRIEF_TRIGGERS


def compose_governed_morning_brief(
    *,
    session_state: dict[str, Any],
    memory_items: list[dict[str, Any]] | None = None,
    weather_data: dict[str, Any] | None = None,
    calendar_data: dict[str, Any] | None = None,
) -> MorningBriefResult:
    """Assemble a governed morning brief using the RoutineGraph engine.

    Returns a MorningBriefResult containing:
    - text: speakable brief summary
    - run: RoutineRun with full outputs
    - receipt: RoutineReceipt for ledger
    - brief_dict: structured brief data for widgets

    The caller is responsible for fetching weather/calendar data
    through governed capability calls and passing the results here.
    """
    recent_receipts = get_recent_receipts(limit=10)

    run, receipt = run_daily_brief_routine(
        session_state=session_state,
        memory_items=memory_items,
        recent_receipts=recent_receipts,
        weather_data=weather_data,
        calendar_data=calendar_data,
    )

    brief_dict = run.outputs.get("daily_brief", {})
    text = brief_dict.get("summary") or "Morning brief assembled."

    sections = brief_dict.get("sections") or []
    if sections:
        parts: list[str] = []
        for section in sections:
            title = section.get("title", "")
            items = section.get("items", [])
            if items:
                parts.append(f"**{title}**: {', '.join(str(i) for i in items[:3])}")
        if parts:
            text = "\n\n".join(parts)

    return MorningBriefResult(
        text=text,
        run=run,
        receipt=receipt,
        brief_dict=brief_dict,
    )


def weather_result_to_brief_data(
    weather_result: Any,
    weather_summary: str,
) -> dict[str, Any] | None:
    """Convert a governed weather result to the format compose_daily_brief expects."""
    if weather_result is None or not getattr(weather_result, "success", False):
        return None
    data = getattr(weather_result, "data", None) or {}
    widget = data.get("widget", {}) if isinstance(data, dict) else {}
    widget_data = widget.get("data", {}) if isinstance(widget, dict) else {}
    return {
        "connected": True,
        "status": "ok",
        "summary": weather_summary,
        "temperature": widget_data.get("temperature") if isinstance(widget_data, dict) else None,
        "condition": widget_data.get("condition") if isinstance(widget_data, dict) else None,
    }


def calendar_result_to_brief_data(
    session_state: dict[str, Any],
) -> dict[str, Any] | None:
    """Extract calendar data from session state for the brief engine."""
    events = session_state.get("last_calendar_events")
    if not isinstance(events, list) or not events:
        return None
    return {
        "connected": True,
        "status": "ok",
        "events": [
            {"title": str(e.get("title", "")), "time": str(e.get("time", ""))}
            for e in events[:5]
            if isinstance(e, dict)
        ],
        "scope": "today",
    }
