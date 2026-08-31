"""One-turn grounding for follow-ups to Personal Operations answers."""

from __future__ import annotations

import re
from typing import Any

from src.brief.daily_loop import DailyLoopItem, DailyLoopProjection
from src.conversation.personal_operations_intent import PersonalOperationsIntent

_FOLLOWUP_RE = re.compile(
    r"^(?:why|why this recommendation|tell me more|tell me more about that|"
    r"the second one|tell me more about the second one)\??$",
    re.IGNORECASE,
)


def is_personal_operations_followup(text: str) -> bool:
    canonical = " ".join(str(text or "").strip().split())
    return bool(_FOLLOWUP_RE.fullmatch(canonical))


def take_personal_operations_surface(
    session_state: dict[str, Any],
    *,
    silent_widget_refresh: bool,
) -> Any:
    """Consume the surface on a real user turn; preserve it across UI hydration."""

    if silent_widget_refresh:
        return None
    return session_state.pop("active_personal_operations_surface", None)


def build_personal_operations_surface(
    intent: PersonalOperationsIntent,
    projection: DailyLoopProjection,
    answer: str,
) -> dict[str, Any]:
    selected = {
        PersonalOperationsIntent.NEXT: projection.next,
        PersonalOperationsIntent.CHANGED: projection.changed,
        PersonalOperationsIntent.WAITING_ON: projection.waiting_on + projection.unresolved_outcomes,
        PersonalOperationsIntent.NEED_TO_FINISH: projection.open_loops,
        PersonalOperationsIntent.COMPLETED_TODAY: projection.completed_today,
        PersonalOperationsIntent.MATTERS_TODAY: (
            projection.next + projection.waiting_on + projection.context_today
        ),
    }.get(intent, ())
    if intent == PersonalOperationsIntent.RECOMMENDED_NEXT:
        selected = (projection.recommended_next,) if projection.recommended_next else ()
    items = [
        {"text": item.text, "source": item.source}
        for item in selected
        if isinstance(item, DailyLoopItem)
    ][:5]
    missing = [source.detail for source in projection.sources if source.status != "available"]
    return {
        "surface_type": "personal_operations",
        "intent": intent.value,
        "answer": str(answer or ""),
        "items": items,
        "missing_sources": missing,
    }


def answer_personal_operations_followup(text: str, surface: Any) -> str:
    if not isinstance(surface, dict) or surface.get("surface_type") != "personal_operations":
        return (
            "I don't have a reliable immediately prior personal-operations answer to refer to. "
            "Ask the full question again so I can ground the answer in current evidence."
        )
    items = [item for item in list(surface.get("items") or []) if isinstance(item, dict)]
    lowered = " ".join(str(text or "").strip().lower().split()).rstrip("?")
    if "second one" in lowered:
        if len(items) < 2:
            return "I don't have a reliable second item in the immediately prior answer."
        item = items[1]
        return f"The second item was: {item.get('text')} [source: {item.get('source')}]"
    if lowered.startswith("why"):
        if not items:
            return (
                "The prior answer did not contain a supported recommendation or evidence item, "
                "so I can't give a grounded reason for it."
            )
        item = items[0]
        prefix = (
            "I made that recommendation because this was the first supported next item"
            if surface.get("intent") == PersonalOperationsIntent.RECOMMENDED_NEXT.value
            else "That answer was grounded first in this current item"
        )
        return f"{prefix}: {item.get('text')} [source: {item.get('source')}]. No action was executed."
    if items:
        lines = ["More from the immediately prior grounded answer:"]
        lines.extend(f"- {item.get('text')} [source: {item.get('source')}]" for item in items[:3])
    else:
        lines = ["The immediately prior answer had no supported personal-state items."]
    missing = [str(item) for item in list(surface.get("missing_sources") or []) if str(item).strip()]
    if missing:
        lines.append("Missing-source truth:")
        lines.extend(f"- {item}" for item in missing[:3])
    lines.append("No action was executed.")
    return "\n".join(lines)
