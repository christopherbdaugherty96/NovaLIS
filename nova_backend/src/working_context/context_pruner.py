from __future__ import annotations

from typing import Any


MAX_TURN_HISTORY = 2
MAX_TEXT_VALUE = 240
MAX_LONG_TEXT_VALUE = 400


def _clamp(value: str, limit: int) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def prune_context(payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Clamp size and keep only bounded session-focused fields."""
    data = dict(payload or {})
    changed = False

    for key in (
        "task_type",
        "task_goal",
        "active_app",
        "active_window",
        "active_url",
        "selected_file",
        "selected_text",
        "cursor_target",
        "current_step",
        "last_relevant_object",
        "open_report_id",
    ):
        old = str(data.get(key) or "")
        limit = MAX_LONG_TEXT_VALUE if key in {"task_goal", "selected_text"} else MAX_TEXT_VALUE
        new = _clamp(old, limit)
        if old != new:
            changed = True
        data[key] = new

    turns = [str(item).strip() for item in list(data.get("recent_relevant_turns") or []) if str(item).strip()]
    if len(turns) > MAX_TURN_HISTORY:
        turns = turns[-MAX_TURN_HISTORY:]
        changed = True
    turns = [_clamp(turn, MAX_TEXT_VALUE) for turn in turns]
    data["recent_relevant_turns"] = turns

    system_context = dict(data.get("system_context") or {})
    clean_system: dict[str, str] = {}
    for key, value in system_context.items():
        label = _clamp(str(key), 64)
        text = _clamp(str(value), 120)
        if not label:
            continue
        clean_system[label] = text
    if system_context != clean_system:
        changed = True
    data["system_context"] = clean_system

    confidence = dict(data.get("confidence_notes") or {})
    clean_confidence: dict[str, str] = {}
    for key, value in confidence.items():
        label = _clamp(str(key), 64)
        text = _clamp(str(value), 120)
        if not label:
            continue
        clean_confidence[label] = text
    if confidence != clean_confidence:
        changed = True
    data["confidence_notes"] = clean_confidence

    return data, changed
