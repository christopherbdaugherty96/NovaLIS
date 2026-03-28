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


MODE_LABELS = {
    "silent": "Silent",
    "suggestive": "Suggestive",
    "workflow_assist": "Workflow Assist",
    "high_awareness": "High Awareness",
}


def _dedupe_actions(items: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen_commands: set[str] = set()
    for item in items:
        label = _clean(item.get("label"))
        command = _clean(item.get("command"))
        if not label or not command or command in seen_commands:
            continue
        deduped.append({"label": label, "command": command})
        seen_commands.add(command)
    return deduped[:6]


def _blocked_without_next_step_notice(
    *,
    focus_thread: dict[str, Any],
) -> dict[str, Any] | None:
    thread_name = _clean(focus_thread.get("name"))
    blocker = _clean(focus_thread.get("latest_blocker"))
    next_action = _clean(focus_thread.get("latest_next_action"))
    if not thread_name or not blocker or next_action:
        return None
    return {
        "id": f"blocked_without_next_step::{thread_name.lower()}",
        "type": "blocked_without_next_step",
        "title": "A blocker is recorded without a next step",
        "summary": f"{thread_name} is blocked on: {blocker}",
        "why_now": "Nova can see a blocker, but there is no follow-up step recorded yet.",
        "risk_level": "low",
        "requires_permission": True,
        "suggested_actions": [
            {"label": "Project status", "command": f"project status {thread_name}"},
            {"label": "Biggest blocker", "command": f"biggest blocker in {thread_name}"},
            {"label": "Continue thread", "command": f"continue my {thread_name}"},
        ],
    }


def _repeated_runtime_issue_notice(
    *,
    recent_activity: list[dict[str, Any]],
) -> dict[str, Any] | None:
    issue_rows = [
        dict(item or {})
        for item in recent_activity
        if _clean(item.get("outcome")).lower() == "issue"
    ]
    if len(issue_rows) < 2:
        return None
    latest = issue_rows[0]
    repeated_titles = ", ".join(
        [
            _clean(item.get("title") or "Runtime issue")
            for item in issue_rows[:2]
            if _clean(item.get("title") or "Runtime issue")
        ]
    )
    detail = _clean(latest.get("detail") or latest.get("reason") or "A recent runtime issue needs attention.")
    return {
        "id": "repeated_runtime_issue",
        "type": "repeated_runtime_issue",
        "title": "Recent runtime issues are repeating",
        "summary": repeated_titles or "Multiple recent runtime issues were detected.",
        "why_now": detail,
        "risk_level": "low",
        "requires_permission": False,
        "suggested_actions": [
            {"label": "Trust center", "command": "trust center"},
            {"label": "System status", "command": "system status"},
            {"label": "Operational context", "command": "operational context"},
        ],
    }


def _continuity_anchor_notice(
    *,
    session_state: dict[str, Any],
    working_context_snapshot: dict[str, Any],
    thread_count: int,
) -> dict[str, Any] | None:
    if thread_count > 0:
        return None
    turn_count = int(session_state.get("turn_count") or 0)
    task_goal = _clean(working_context_snapshot.get("task_goal"))
    recent_turns = [
        _clean(item)
        for item in list(working_context_snapshot.get("recent_relevant_turns") or [])[:3]
        if _clean(item)
    ]
    if turn_count < 3 and not task_goal and len(recent_turns) < 2:
        return None
    summary = task_goal or (recent_turns[0] if recent_turns else "You appear to be working through an ongoing topic.")
    return {
        "id": "missing_continuity_anchor",
        "type": "missing_continuity_anchor",
        "title": "This work does not have a continuity anchor yet",
        "summary": _clip(summary, limit=140),
        "why_now": "Nova can see ongoing work signals, but there is no active project thread yet to hold continuity.",
        "risk_level": "low",
        "requires_permission": True,
        "suggested_actions": [
            {"label": "Show threads", "command": "show threads"},
            {"label": "Workspace home", "command": "workspace home"},
            {"label": "Create thread", "command": "create thread current project"},
        ],
    }


def build_assistive_notices_widget(
    *,
    session_state: dict[str, Any] | None,
    working_context_snapshot: dict[str, Any] | None,
    project_threads: ProjectThreadStore,
    trust_snapshot: dict[str, Any] | None = None,
    assistive_notice_mode: str = "suggestive",
    explicit_request: bool = False,
) -> dict[str, Any]:
    state = dict(session_state or {})
    working_context = dict(working_context_snapshot or state.get("working_context") or {})
    trust = dict(trust_snapshot or {})
    mode = _clean(assistive_notice_mode).lower() or "suggestive"
    mode_label = MODE_LABELS.get(mode, MODE_LABELS["suggestive"])

    thread_summaries = [dict(item or {}) for item in project_threads.list_summaries()]
    focus_thread_name = _clean(project_threads.active_thread_name() or state.get("project_thread_active"))
    focus_thread = {}
    if focus_thread_name:
        focus_thread = next(
            (
                row
                for row in thread_summaries
                if _clean(row.get("name")).lower() == focus_thread_name.lower()
            ),
            {},
        )
    if not focus_thread and thread_summaries:
        focus_thread = dict(thread_summaries[0])

    recent_activity = [
        dict(item or {})
        for item in list(trust.get("recent_runtime_activity") or [])[:6]
        if isinstance(item, dict)
    ]
    notices = [
        _blocked_without_next_step_notice(focus_thread=focus_thread),
        _repeated_runtime_issue_notice(recent_activity=recent_activity),
        _continuity_anchor_notice(
            session_state=state,
            working_context_snapshot=working_context,
            thread_count=len(thread_summaries),
        ),
    ]
    notices = [item for item in notices if isinstance(item, dict)]
    surfaced_notices = notices if explicit_request or mode != "silent" else []

    recommended_actions = _dedupe_actions(
        [
            action
            for item in surfaced_notices
            for action in list(item.get("suggested_actions") or [])
            if isinstance(action, dict)
        ]
        + [
            {"label": "Open settings", "command": "settings"},
            {"label": "Operational context", "command": "operational context"},
        ]
    )

    if mode == "silent" and not explicit_request:
        summary = (
            "Silent mode is active. Nova is not surfacing assistive notices automatically right now."
        )
    elif surfaced_notices:
        summary = (
            f"{len(surfaced_notices)} assistive notice{'s' if len(surfaced_notices) != 1 else ''} "
            "are worth a quick review."
        )
    else:
        summary = "No bounded assistive notices are active right now."

    return {
        "type": "assistive_notices",
        "summary": summary,
        "assistive_notice_mode": mode,
        "assistive_notice_mode_label": mode_label,
        "explicit_request": bool(explicit_request),
        "notice_count": len(surfaced_notices),
        "hidden_notice_count": max(0, len(notices) - len(surfaced_notices)),
        "notices": surfaced_notices[:4],
        "recommended_actions": recommended_actions,
        "governance_note": (
            "Notice, ask, then assist. Nova may surface low-risk suggestions here, but it should not silently decide or act."
        ),
    }


def render_assistive_notices_message(widget: dict[str, Any] | None) -> str:
    payload = dict(widget or {})
    lines = ["Assistive Notices", ""]
    lines.append(_clean(payload.get("summary")) or "No assistive notices are active right now.")
    lines.append("")
    lines.append(_clean(payload.get("governance_note")) or "Notice, ask, then assist remains the governing rule.")
    notices = [dict(item or {}) for item in list(payload.get("notices") or [])[:3]]
    if notices:
        lines.append("")
        for item in notices:
            title = _clean(item.get("title") or "Notice")
            summary = _clean(item.get("summary"))
            why_now = _clean(item.get("why_now"))
            lines.append(f"- {title}")
            if summary:
                lines.append(f"  {summary}")
            if why_now:
                lines.append(f"  Why now: {why_now}")
    return "\n".join(lines).strip()
