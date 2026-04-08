from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.working_context.project_threads import ProjectThreadStore


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _parse_ts(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


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

MODE_NOTICE_TYPES = {
    "silent": {"blocked_without_next_step", "repeated_runtime_issue"},
    "suggestive": {"blocked_without_next_step", "repeated_runtime_issue"},
    "workflow_assist": {
        "blocked_without_next_step",
        "repeated_runtime_issue",
        "missing_continuity_anchor",
    },
    "high_awareness": {
        "blocked_without_next_step",
        "repeated_runtime_issue",
        "missing_continuity_anchor",
        "active_trust_condition",
    },
}

MODE_AUTO_SURFACE_COOLDOWN_SECONDS = {
    "silent": 24 * 60 * 60,
    "suggestive": 12 * 60,
    "workflow_assist": 6 * 60,
    "high_awareness": 3 * 60,
}

NOTICE_TYPE_AUTO_SURFACE_COOLDOWN_SECONDS = {
    "blocked_without_next_step": 20 * 60,
    "repeated_runtime_issue": 15 * 60,
    "missing_continuity_anchor": 8 * 60,
    "active_trust_condition": 5 * 60,
}

NOTICE_STATUS_ACTIVE = "active"
NOTICE_STATUS_DISMISSED = "dismissed"
NOTICE_STATUS_RESOLVED = "resolved"
VALID_NOTICE_STATUSES = {
    NOTICE_STATUS_ACTIVE,
    NOTICE_STATUS_DISMISSED,
    NOTICE_STATUS_RESOLVED,
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


def _notice_signature(notice: dict[str, Any]) -> str:
    return "|".join(
        [
            _clean(notice.get("id")),
            _clean(notice.get("type")),
            _clean(notice.get("summary")),
            _clean(notice.get("why_now")),
        ]
    ).lower()


def _normalize_notice_state(value: Any) -> dict[str, Any]:
    raw = dict(value or {}) if isinstance(value, dict) else {}
    items = {}
    for notice_id, item in dict(raw.get("items") or {}).items():
        key = _clean(notice_id)
        if not key or not isinstance(item, dict):
            continue
        status = _clean(item.get("status")).lower()
        if status not in VALID_NOTICE_STATUSES:
            status = NOTICE_STATUS_ACTIVE
        items[key] = {
            "status": status,
            "signature": _clean(item.get("signature")),
            "type": _clean(item.get("type")),
            "title": _clean(item.get("title")),
            "summary": _clean(item.get("summary")),
            "updated_at": _clean(item.get("updated_at")),
            "last_auto_surface_at": _clean(item.get("last_auto_surface_at")),
        }
    return {"items": items}


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


def _active_trust_condition_notice(
    *,
    blocked_conditions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not blocked_conditions:
        return None
    first = dict(blocked_conditions[0] or {})
    label = _clean(first.get("label") or first.get("area") or "Trust condition")
    status = _clean(first.get("status"))
    reason = _clean(first.get("reason") or "A trust condition is currently restricting part of the runtime.")
    summary = label if not status else f"{label}: {status}"
    return {
        "id": f"active_trust_condition::{label.lower().replace(' ', '_')}",
        "type": "active_trust_condition",
        "title": "A trust condition needs review",
        "summary": summary,
        "why_now": reason,
        "risk_level": "medium",
        "requires_permission": False,
        "suggested_actions": [
            {"label": "Trust center", "command": "trust center"},
            {"label": "Connection status", "command": "connection status"},
            {"label": "System status", "command": "system status"},
        ],
    }


def _decorate_notice(notice: dict[str, Any]) -> dict[str, Any]:
    payload = dict(notice)
    payload["dismiss_command"] = f"dismiss assistive notice {_clean(payload.get('id'))}"
    payload["resolve_command"] = f"resolve assistive notice {_clean(payload.get('id'))}"
    payload["signature"] = _notice_signature(payload)
    return payload


def apply_assistive_notice_feedback(
    notice_state: dict[str, Any] | None,
    *,
    notice: dict[str, Any],
    status: str,
) -> dict[str, Any]:
    normalized = _normalize_notice_state(notice_state)
    target_status = _clean(status).lower()
    if target_status not in {NOTICE_STATUS_DISMISSED, NOTICE_STATUS_RESOLVED}:
        raise ValueError(f"Unsupported assistive notice status: {status}")
    notice_id = _clean(notice.get("id"))
    if not notice_id:
        raise ValueError("Assistive notice id is required.")
    normalized["items"][notice_id] = {
        "status": target_status,
        "signature": _notice_signature(notice),
        "type": _clean(notice.get("type")),
        "title": _clean(notice.get("title")),
        "summary": _clean(notice.get("summary")),
        "updated_at": _utc_now_iso(),
        "last_auto_surface_at": _clean(
            dict(normalized["items"].get(notice_id) or {}).get("last_auto_surface_at")
        ),
    }
    return normalized


def record_auto_surfaced_notices(
    notice_state: dict[str, Any] | None,
    *,
    notices: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized = _normalize_notice_state(notice_state)
    timestamp = _utc_now_iso()
    for notice in notices:
        notice_id = _clean(notice.get("id"))
        if not notice_id:
            continue
        signature = _notice_signature(notice)
        existing = dict(normalized["items"].get(notice_id) or {})
        if _clean(existing.get("signature")) != signature:
            existing["status"] = NOTICE_STATUS_ACTIVE
        existing["signature"] = signature
        existing["type"] = _clean(notice.get("type"))
        existing["title"] = _clean(notice.get("title"))
        existing["summary"] = _clean(notice.get("summary"))
        existing["last_auto_surface_at"] = timestamp
        existing.setdefault("updated_at", "")
        normalized["items"][notice_id] = existing
    return normalized


def _auto_surface_ready(
    *,
    notice: dict[str, Any],
    state_item: dict[str, Any],
    assistive_notice_mode: str,
    now: datetime,
) -> bool:
    last_surface = _parse_ts(state_item.get("last_auto_surface_at"))
    if last_surface is None:
        return True
    notice_type = _clean(notice.get("type"))
    cooldown_seconds = NOTICE_TYPE_AUTO_SURFACE_COOLDOWN_SECONDS.get(
        notice_type,
        MODE_AUTO_SURFACE_COOLDOWN_SECONDS.get(
            assistive_notice_mode,
            MODE_AUTO_SURFACE_COOLDOWN_SECONDS["suggestive"],
        ),
    )
    return now - last_surface >= timedelta(seconds=cooldown_seconds)


def build_assistive_notices_widget(
    *,
    session_state: dict[str, Any] | None,
    working_context_snapshot: dict[str, Any] | None,
    project_threads: ProjectThreadStore,
    trust_snapshot: dict[str, Any] | None = None,
    assistive_notice_mode: str = "suggestive",
    explicit_request: bool = False,
    permission_granted: bool = True,
) -> dict[str, Any]:
    state = dict(session_state or {})
    working_context = dict(working_context_snapshot or state.get("working_context") or {})
    trust = dict(trust_snapshot or {})
    mode = _clean(assistive_notice_mode).lower() or "suggestive"
    if mode not in MODE_LABELS:
        mode = "suggestive"
    mode_label = MODE_LABELS[mode]

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
    blocked_conditions = [
        dict(item or {})
        for item in list(trust.get("blocked_conditions") or [])[:4]
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
        _active_trust_condition_notice(blocked_conditions=blocked_conditions),
    ]
    allowed_types = MODE_NOTICE_TYPES.get(mode, MODE_NOTICE_TYPES["suggestive"])
    candidate_notices = [
        _decorate_notice(item)
        for item in notices
        if isinstance(item, dict)
        and _clean(item.get("type")) in allowed_types
        and (permission_granted or not item.get("requires_permission"))
    ]

    notice_state = _normalize_notice_state(state.get("assistive_notice_state"))
    now = _utc_now()
    hidden_count = 0
    dismissed_count = 0
    suppressed_count = 0
    surfaced_notices: list[dict[str, Any]] = []
    active_notices: list[dict[str, Any]] = []
    handled_notices: list[dict[str, Any]] = []

    for notice in candidate_notices:
        notice_id = _clean(notice.get("id"))
        state_item = dict(notice_state["items"].get(notice_id) or {})
        signature = _notice_signature(notice)
        status = _clean(state_item.get("status")).lower() or NOTICE_STATUS_ACTIVE
        signature_matches = _clean(state_item.get("signature")) == signature
        if signature_matches and status in {NOTICE_STATUS_DISMISSED, NOTICE_STATUS_RESOLVED}:
            dismissed_count += 1
            handled_notices.append(
                {
                    "id": notice_id,
                    "type": _clean(state_item.get("type") or notice.get("type")),
                    "title": _clean(state_item.get("title") or notice.get("title") or "Handled notice"),
                    "summary": _clean(state_item.get("summary") or notice.get("summary")),
                    "status": status,
                    "updated_at": _clean(state_item.get("updated_at")),
                }
            )
            continue

        active_notices.append(notice)
        if mode == "silent" and not explicit_request:
            hidden_count += 1
            continue
        if not explicit_request and not _auto_surface_ready(
            notice=notice,
            state_item=state_item,
            assistive_notice_mode=mode,
            now=now,
        ):
            suppressed_count += 1
            continue
        surfaced_notices.append(notice)

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
            {"label": "Assistive notices", "command": "assistive notices"},
        ]
    )

    if mode == "silent" and not explicit_request:
        summary = "Silent mode is active. Nova is not surfacing assistive notices automatically right now."
    elif surfaced_notices:
        summary = (
            f"{len(surfaced_notices)} assistive notice{'s' if len(surfaced_notices) != 1 else ''} "
            "are worth a quick review."
        )
    elif suppressed_count:
        summary = (
            "No new assistive notices are active right now. "
            f"{suppressed_count} notice{'s are' if suppressed_count != 1 else ' is'} cooling down."
        )
    elif dismissed_count:
        summary = (
            "No active assistive notices are surfaced right now. "
            f"{dismissed_count} handled notice{'s remain hidden until conditions change.' if dismissed_count != 1 else ' remains hidden until conditions change.'}"
        )
    else:
        summary = "No bounded assistive notices are active right now."

    return {
        "type": "assistive_notices",
        "summary": summary,
        "assistive_notice_mode": mode,
        "assistive_notice_mode_label": mode_label,
        "explicit_request": bool(explicit_request),
        "active_notice_count": len(active_notices),
        "notice_count": len(surfaced_notices),
        "hidden_notice_count": hidden_count,
        "suppressed_notice_count": suppressed_count,
        "dismissed_notice_count": dismissed_count,
        "notices": surfaced_notices[:4],
        "handled_notices": handled_notices[:4],
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
