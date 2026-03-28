from __future__ import annotations

from typing import Any

from src.working_context.project_threads import ProjectThreadStore


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _clip(value: Any, *, limit: int = 180) -> str:
    text = _clean(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_operational_context_widget(
    *,
    session_state: dict[str, Any] | None,
    working_context_snapshot: dict[str, Any] | None,
    project_threads: ProjectThreadStore,
    trust_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = dict(session_state or {})
    context = dict(working_context_snapshot or state.get("working_context") or {})
    trust = dict(trust_snapshot or {})

    focus_thread = _clean(project_threads.active_thread_name() or state.get("project_thread_active"))
    thread_count = len(project_threads.list_summaries())
    turn_count = int(state.get("turn_count") or 0)
    recent_turns = [
        _clip(item, limit=120)
        for item in list(context.get("recent_relevant_turns") or [])[:4]
        if _clean(item)
    ]
    recent_activity = [
        {
            "title": _clean(item.get("title") or "Runtime event"),
            "detail": _clean(item.get("detail") or item.get("kind") or ""),
            "outcome": _clean(item.get("outcome") or "info"),
            "timestamp": _clean(item.get("timestamp") or ""),
        }
        for item in list(trust.get("recent_runtime_activity") or [])[:3]
        if isinstance(item, dict)
    ]
    blocked_conditions = [
        {
            "label": _clean(item.get("label") or item.get("area") or "Condition"),
            "status": _clean(item.get("status") or ""),
            "reason": _clean(item.get("reason") or ""),
        }
        for item in list(trust.get("blocked_conditions") or [])[:3]
        if isinstance(item, dict)
    ]

    task_goal = _clean(context.get("task_goal"))
    current_step = _clean(context.get("current_step"))
    task_type = _clean(context.get("task_type"))
    selected_file = _clean(context.get("selected_file"))
    last_object = _clean(context.get("last_relevant_object"))
    open_report_id = _clean(context.get("open_report_id"))
    active_topic = _clean(state.get("active_topic"))
    active_window = _clean(context.get("active_window"))
    active_app = _clean(context.get("active_app"))
    active_url = _clean(context.get("active_url"))
    general_chat_context = list(state.get("general_chat_context") or [])
    general_chat_turns = len(general_chat_context)

    summary_parts: list[str] = []
    if task_goal:
        summary_parts.append(f"Current goal: {task_goal}")
    elif focus_thread:
        summary_parts.append(f"Current focus thread: {focus_thread}")
    else:
        summary_parts.append("No strong continuity anchor is active right now.")

    if current_step:
        summary_parts.append(f"Current step: {current_step}")
    if selected_file:
        summary_parts.append(f"Selected file: {selected_file}")
    elif last_object:
        summary_parts.append(f"Latest object: {last_object}")

    summary = " ".join(summary_parts).strip()
    if not summary:
        summary = "Operational context is visible here so session continuity stays inspectable."

    recommended_actions = [
        {"label": "Refresh continuity", "command": "operational context"},
        {"label": "Reset continuity", "command": "reset operational context"},
        {"label": "Workspace Home", "command": "workspace home"},
        {"label": "Trust Center", "command": "trust center"},
    ]

    return {
        "type": "operational_context",
        "summary": summary,
        "continuity_note": (
            "This is session continuity, not durable personal memory. Reset clears the session context but preserves governed memory."
        ),
        "task_type": task_type,
        "task_goal": task_goal,
        "current_step": current_step,
        "selected_file": selected_file,
        "last_relevant_object": last_object,
        "open_report_id": open_report_id,
        "active_topic": active_topic,
        "active_thread": focus_thread,
        "thread_count": thread_count,
        "turn_count": turn_count,
        "general_chat_turns": general_chat_turns,
        "recent_relevant_turns": recent_turns,
        "active_app": active_app,
        "active_window": active_window,
        "active_url": active_url,
        "recent_activity": recent_activity,
        "blocked_conditions": blocked_conditions,
        "resettable": True,
        "memory_preserved_on_reset": True,
        "recommended_actions": recommended_actions,
    }


def render_operational_context_message(widget: dict[str, Any] | None) -> str:
    payload = dict(widget or {})
    lines = ["Operational Context", ""]
    lines.append(_clean(payload.get("summary")) or "Operational context is visible here.")
    lines.append("")
    lines.append(_clean(payload.get("continuity_note")) or "Session continuity is visible and resettable here.")

    detail_pairs = [
        ("Focus thread", payload.get("active_thread")),
        ("Goal", payload.get("task_goal")),
        ("Current step", payload.get("current_step")),
        ("Active topic", payload.get("active_topic")),
        ("Selected file", payload.get("selected_file")),
        ("Latest object", payload.get("last_relevant_object")),
        ("Open report", payload.get("open_report_id")),
    ]
    detail_lines = [f"{label}: {_clean(value)}" for label, value in detail_pairs if _clean(value)]
    if detail_lines:
        lines.append("")
        lines.extend(detail_lines[:6])

    return "\n".join(lines).strip()
