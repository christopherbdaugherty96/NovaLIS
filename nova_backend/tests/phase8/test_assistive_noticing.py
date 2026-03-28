from __future__ import annotations

from src.working_context.assistive_noticing import (
    build_assistive_notices_widget,
    render_assistive_notices_message,
)
from src.working_context.project_threads import ProjectThreadStore


def test_assistive_notices_detect_blocker_without_next_step():
    store = ProjectThreadStore(session_id="assistive-1", ledger=None)
    store.ensure_thread("Nova Runtime", goal="Finish bounded noticing")
    store.attach_update(
        thread_name="Nova Runtime",
        summary="Runtime truth drift is still unresolved.",
        category="blocker",
    )

    payload = build_assistive_notices_widget(
        session_state={"turn_count": 4},
        working_context_snapshot={"task_goal": "Finish bounded noticing"},
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=False,
    )

    assert payload["type"] == "assistive_notices"
    assert payload["notice_count"] >= 1
    assert any(item["type"] == "blocked_without_next_step" for item in payload["notices"])


def test_assistive_notices_hide_unsolicited_results_in_silent_mode():
    store = ProjectThreadStore(session_id="assistive-2", ledger=None)

    payload = build_assistive_notices_widget(
        session_state={"turn_count": 5},
        working_context_snapshot={
            "task_goal": "Stabilize the workspace flow",
            "recent_relevant_turns": ["Fix the same issue", "Fix it again"],
        },
        project_threads=store,
        trust_snapshot={
            "recent_runtime_activity": [
                {"title": "Action needs attention", "detail": "Calendar unavailable", "outcome": "issue"},
                {"title": "Action needs attention", "detail": "Weather unavailable", "outcome": "issue"},
            ],
            "blocked_conditions": [],
        },
        assistive_notice_mode="silent",
        explicit_request=False,
    )

    assert payload["notice_count"] == 0
    assert payload["hidden_notice_count"] >= 1
    assert "Silent mode is active" in payload["summary"]


def test_assistive_notices_explicit_view_can_show_silent_mode_findings():
    store = ProjectThreadStore(session_id="assistive-3", ledger=None)

    payload = build_assistive_notices_widget(
        session_state={"turn_count": 5},
        working_context_snapshot={"task_goal": "Resume the same work"},
        project_threads=store,
        trust_snapshot={
            "recent_runtime_activity": [
                {"title": "Action needs attention", "detail": "Calendar unavailable", "outcome": "issue"},
                {"title": "Action needs attention", "detail": "Weather unavailable", "outcome": "issue"},
            ],
            "blocked_conditions": [],
        },
        assistive_notice_mode="silent",
        explicit_request=True,
    )

    assert payload["notice_count"] >= 1
    assert any(item["type"] == "repeated_runtime_issue" for item in payload["notices"])


def test_assistive_notices_message_stays_plain_language():
    message = render_assistive_notices_message(
        {
            "summary": "2 assistive notices are worth a quick review.",
            "governance_note": "Notice, ask, then assist.",
            "notices": [
                {
                    "title": "A blocker is recorded without a next step",
                    "summary": "Nova Runtime is blocked on: Runtime truth drift",
                    "why_now": "Nova can see a blocker, but there is no follow-up step recorded yet.",
                }
            ],
        }
    )

    assert "Assistive Notices" in message
    assert "Why now:" in message
    assert "Notice, ask, then assist." in message
