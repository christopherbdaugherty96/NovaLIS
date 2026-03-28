from __future__ import annotations

from src.working_context.operational_remembrance import (
    build_operational_context_widget,
    render_operational_context_message,
)
from src.working_context.project_threads import ProjectThreadStore


def test_operational_context_widget_is_session_scoped_and_resettable():
    store = ProjectThreadStore(session_id="sess-op", ledger=None)
    store.ensure_thread("Nova Runtime", goal="Finish operational remembrance")

    payload = build_operational_context_widget(
        session_state={
            "turn_count": 5,
            "active_topic": "nova operational remembrance",
            "general_chat_context": [{"role": "user", "content": "help"}],
        },
        working_context_snapshot={
            "task_type": "work",
            "task_goal": "Finish operational remembrance visibility",
            "current_step": "Build the trust panel",
            "selected_file": "nova_backend/static/dashboard.js",
            "last_relevant_object": "trust-center-operational-grid",
            "recent_relevant_turns": ["Create the widget", "Add reset flow"],
        },
        project_threads=store,
        trust_snapshot={
            "recent_runtime_activity": [{"title": "Workspace refresh", "detail": "Visible continuity refresh"}],
            "blocked_conditions": [{"label": "Autonomy", "status": "disabled", "reason": "Invocation-bound"}],
        },
    )

    assert payload["type"] == "operational_context"
    assert payload["active_thread"] == "Nova Runtime"
    assert payload["resettable"] is True
    assert payload["memory_preserved_on_reset"] is True
    assert payload["recent_relevant_turns"]


def test_operational_context_message_stays_plain_language():
    message = render_operational_context_message(
        {
            "summary": "Current goal: Finish operational remembrance visibility.",
            "continuity_note": "Reset clears session continuity but preserves durable memory.",
            "active_thread": "Nova Runtime",
            "task_goal": "Finish operational remembrance visibility",
            "current_step": "Wire trust page",
        }
    )

    assert "Operational Context" in message
    assert "Nova Runtime" in message
    assert "Wire trust page" in message
