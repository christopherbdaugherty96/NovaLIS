from __future__ import annotations

import src.working_context.assistive_noticing as assistive_noticing
from src.working_context.assistive_noticing import (
    apply_assistive_notice_feedback,
    build_assistive_notices_widget,
    record_auto_surfaced_notices,
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


def test_suggestive_mode_does_not_surface_continuity_anchor_notice():
    store = ProjectThreadStore(session_id="assistive-4", ledger=None)

    payload = build_assistive_notices_widget(
        session_state={"turn_count": 5},
        working_context_snapshot={
            "task_goal": "Resume the same work",
            "recent_relevant_turns": ["Continue the same thread", "Resume the same task"],
        },
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=True,
    )

    assert payload["notice_count"] == 0
    assert payload["active_notice_count"] == 0


def test_workflow_assist_mode_surfaces_continuity_anchor_notice():
    store = ProjectThreadStore(session_id="assistive-5", ledger=None)

    payload = build_assistive_notices_widget(
        session_state={"turn_count": 5},
        working_context_snapshot={
            "task_goal": "Resume the same work",
            "recent_relevant_turns": ["Continue the same thread", "Resume the same task"],
        },
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="workflow_assist",
        explicit_request=True,
    )

    assert any(item["type"] == "missing_continuity_anchor" for item in payload["notices"])


def test_high_awareness_mode_surfaces_trust_condition_notice():
    store = ProjectThreadStore(session_id="assistive-6", ledger=None)

    payload = build_assistive_notices_widget(
        session_state={"turn_count": 1},
        working_context_snapshot={},
        project_threads=store,
        trust_snapshot={
            "recent_runtime_activity": [],
            "blocked_conditions": [
                {
                    "label": "Remote bridge",
                    "status": "paused",
                    "reason": "Paused in settings for review.",
                }
            ],
        },
        assistive_notice_mode="high_awareness",
        explicit_request=True,
    )

    assert any(item["type"] == "active_trust_condition" for item in payload["notices"])


def test_dismissed_notice_stays_hidden_until_conditions_change():
    store = ProjectThreadStore(session_id="assistive-7", ledger=None)
    store.ensure_thread("Nova Runtime", goal="Finish bounded noticing")
    store.attach_update(
        thread_name="Nova Runtime",
        summary="Runtime truth drift is still unresolved.",
        category="blocker",
    )

    first_payload = build_assistive_notices_widget(
        session_state={"turn_count": 4},
        working_context_snapshot={"task_goal": "Finish bounded noticing"},
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=True,
    )
    notice = first_payload["notices"][0]
    notice_state = apply_assistive_notice_feedback({}, notice=notice, status="dismissed")

    second_payload = build_assistive_notices_widget(
        session_state={"turn_count": 4, "assistive_notice_state": notice_state},
        working_context_snapshot={"task_goal": "Finish bounded noticing"},
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=True,
    )

    assert second_payload["notice_count"] == 0
    assert second_payload["dismissed_notice_count"] == 1
    assert second_payload["handled_notices"][0]["status"] == "dismissed"
    assert second_payload["handled_notices"][0]["title"] == notice["title"]


def test_auto_surface_cooldown_hides_recently_shown_notice_but_explicit_view_can_still_open_it():
    store = ProjectThreadStore(session_id="assistive-8", ledger=None)
    store.ensure_thread("Nova Runtime", goal="Finish bounded noticing")
    store.attach_update(
        thread_name="Nova Runtime",
        summary="Runtime truth drift is still unresolved.",
        category="blocker",
    )

    first_payload = build_assistive_notices_widget(
        session_state={"turn_count": 4},
        working_context_snapshot={"task_goal": "Finish bounded noticing"},
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=False,
    )
    notice_state = record_auto_surfaced_notices({}, notices=list(first_payload["notices"]))

    auto_payload = build_assistive_notices_widget(
        session_state={"turn_count": 4, "assistive_notice_state": notice_state},
        working_context_snapshot={"task_goal": "Finish bounded noticing"},
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=False,
    )
    explicit_payload = build_assistive_notices_widget(
        session_state={"turn_count": 4, "assistive_notice_state": notice_state},
        working_context_snapshot={"task_goal": "Finish bounded noticing"},
        project_threads=store,
        trust_snapshot={"recent_runtime_activity": [], "blocked_conditions": []},
        assistive_notice_mode="suggestive",
        explicit_request=True,
    )

    assert auto_payload["notice_count"] == 0
    assert auto_payload["suppressed_notice_count"] == 1
    assert explicit_payload["notice_count"] == 1


def test_notice_type_specific_cooldown_overrides_mode_baseline(monkeypatch):
    store = ProjectThreadStore(session_id="assistive-9", ledger=None)
    monkeypatch.setattr(
        assistive_noticing,
        "_utc_now",
        lambda: assistive_noticing.datetime(2026, 3, 27, 12, 0, 0, tzinfo=assistive_noticing.timezone.utc),
    )

    first_payload = build_assistive_notices_widget(
        session_state={"turn_count": 1},
        working_context_snapshot={},
        project_threads=store,
        trust_snapshot={
            "recent_runtime_activity": [],
            "blocked_conditions": [
                {
                    "label": "Remote bridge",
                    "status": "paused",
                    "reason": "Paused in settings for review.",
                }
            ],
        },
        assistive_notice_mode="high_awareness",
        explicit_request=False,
    )
    notice_state = record_auto_surfaced_notices({}, notices=list(first_payload["notices"]))

    updated_item = dict(notice_state["items"]["active_trust_condition::remote_bridge"])
    updated_item["last_auto_surface_at"] = "2026-03-27T11:56:00+00:00"
    notice_state["items"]["active_trust_condition::remote_bridge"] = updated_item

    auto_payload = build_assistive_notices_widget(
        session_state={"turn_count": 1, "assistive_notice_state": notice_state},
        working_context_snapshot={},
        project_threads=store,
        trust_snapshot={
            "recent_runtime_activity": [],
            "blocked_conditions": [
                {
                    "label": "Remote bridge",
                    "status": "paused",
                    "reason": "Paused in settings for review.",
                }
            ],
        },
        assistive_notice_mode="high_awareness",
        explicit_request=False,
    )

    assert auto_payload["notice_count"] == 0
    assert auto_payload["suppressed_notice_count"] == 1


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
