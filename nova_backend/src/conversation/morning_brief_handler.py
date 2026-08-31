"""Daily Brief handler — governed brief via RoutineGraph.

Single source of truth for the user-facing Daily Brief trigger and the
governed brief assembly path. Uses run_daily_brief_routine() to produce
a RoutineRun and RoutineReceipt alongside the brief text.

One user-facing brief: every phrasing variant ("daily brief",
"morning brief", "brief me", "what matters today", a quick-action
button) must resolve through is_daily_brief_request() to this one
governed path. Do not add brief trigger sets elsewhere.

Non-authorizing: the brief is read-only synthesis. It does not
execute capabilities, grant authority, or modify state.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.brief.daily_loop import DailyLoopProjection
from src.routine.daily_brief_routine import run_daily_brief_routine
from src.routine.routine_graph import RoutineReceipt, RoutineRun
from src.trust.receipt_store import get_recent_receipts

DAILY_BRIEF_TRIGGERS = frozenset({
    "daily brief",
    "morning brief",
    "morning",
    "brief",
    "brief me",
    "what did i miss",
    "catch me up",
    "plan my day",
    "what matters today",
})

# Natural phrasings that don't reduce to a fixed trigger string.
_DAILY_BRIEF_PATTERNS = (
    re.compile(r"^what(?:'?s| is| does) (?:my |the )?day look(?:ing)? like(?: today)?$"),
    re.compile(r"^what should i focus on(?: today| this morning)?$"),
)

# Courtesy words stripped from the edges before trigger matching, so
# "give me my daily brief please" resolves to "daily brief".
_COURTESY_EDGE_WORDS = frozenset({
    "hey", "hi", "nova", "please", "thanks", "can", "could", "you",
    "give", "show", "run", "start", "me", "my", "the", "a",
})


def normalize_brief_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse spaces, trim courtesy words."""
    lowered = str(text or "").lower()
    lowered = re.sub(r"[^a-z' ]+", " ", lowered)
    words = lowered.split()
    while words and words[0] in _COURTESY_EDGE_WORDS:
        words.pop(0)
    while words and words[-1] in _COURTESY_EDGE_WORDS:
        words.pop()
    return " ".join(words)


def is_daily_brief_request(text: str) -> bool:
    """True when the message asks for the Daily Brief, in any phrasing."""
    lowered = str(text or "").strip().lower()
    if lowered in DAILY_BRIEF_TRIGGERS:
        return True
    normalized = normalize_brief_text(text)
    if normalized in DAILY_BRIEF_TRIGGERS:
        return True
    return any(p.match(normalized) for p in _DAILY_BRIEF_PATTERNS)


# Backwards-compatible aliases (older call sites and tests).
MORNING_BRIEF_TRIGGERS = DAILY_BRIEF_TRIGGERS
is_morning_brief_request = is_daily_brief_request


@dataclass(frozen=True)
class MorningBriefResult:
    """Result of assembling a governed daily brief."""
    text: str
    run: RoutineRun
    receipt: RoutineReceipt
    brief_dict: dict[str, Any]

    @property
    def has_content(self) -> bool:
        return bool(self.brief_dict.get("sections"))


def compose_governed_morning_brief(
    *,
    session_state: dict[str, Any],
    memory_items: list[dict[str, Any]] | None = None,
    weather_data: dict[str, Any] | None = None,
    calendar_data: dict[str, Any] | None = None,
    daily_loop_projection: DailyLoopProjection | None = None,
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
    if daily_loop_projection is not None:
        text = _render_daily_loop_guidance(daily_loop_projection)
    elif sections:
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


def _render_daily_loop_guidance(projection: DailyLoopProjection) -> str:
    """Prioritize the user's operating day while preserving source truth."""

    lines = ["**What matters today**"]
    if projection.next:
        item = projection.next[0]
        lines.append(f"- Next: {item.text} [source: {item.source}]")
    else:
        lines.append("- Next: No upcoming item is known from the available state.")

    waiting_item = (
        projection.waiting_on[0]
        if projection.waiting_on
        else projection.unresolved_outcomes[0]
        if projection.unresolved_outcomes
        else None
    )
    if waiting_item is not None:
        lines.append(f"- Waiting on: {waiting_item.text} [source: {waiting_item.source}]")
    else:
        lines.append("- Waiting on: No waiting item is known from the available state.")

    meaningful_change = next(
        (
            item
            for item in projection.changed
            if not item.text.casefold().startswith("background read ")
        ),
        None,
    )
    if meaningful_change is not None:
        lines.append(
            f"- Meaningful change: {meaningful_change.text} [source: {meaningful_change.source}]"
        )
    else:
        lines.append("- Meaningful change: No meaningful user-facing change is known.")

    if projection.recommended_next is not None:
        lines.append(
            "- Recommendation (derived, not an instruction): "
            f"{projection.recommended_next.text} [source: {projection.recommended_next.source}]"
        )
    else:
        lines.append("- Recommendation: No recommendation is supported by the available state.")

    supporting_context = next(
        (item for item in projection.context_today if item.source == "weather"),
        projection.context_today[0] if projection.context_today else None,
    )
    if supporting_context is not None:
        lines.append(
            f"- Supporting context: {supporting_context.text} [source: {supporting_context.source}]"
        )

    missing = [
        source.detail
        for source in projection.sources
        if source.status in {"not_connected", "not_loaded", "unavailable"}
    ]
    if missing:
        lines.append("\n**Missing-source truth**")
        lines.extend(f"- {detail}" for detail in missing)
    lines.append("\nNo action was executed.")
    return "\n".join(lines)


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
