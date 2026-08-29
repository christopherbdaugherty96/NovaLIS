from copy import deepcopy
from datetime import datetime, timezone

from src.brief.daily_loop import compose_daily_loop_projection, render_daily_loop_answer
from src.conversation.personal_operations_intent import PersonalOperationsIntent

NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)


def test_projection_assembles_existing_state_with_provenance_without_mutation():
    state = {
        "brief_calendar": {"connected": True, "events": [{"time": "09:00", "title": "Review"}]},
        "brief_weather": {"connected": True, "summary": "Rain after 3 PM"},
        "news_cache": [{"title": "Relevant local update"}],
        "working_context": {"task_goal": "Finish beta review"},
    }
    memory = [
        {"title": "Waiting: vendor reply", "content_raw": "Vendor reply", "tags": ["waiting"]},
        {"title": "Next: send summary", "content_raw": "Send summary", "tags": ["next_action"]},
    ]
    reminders = [{"active": True, "body": "Submit report", "next_run_at": "2026-08-29T14:00:00Z"}]
    receipts = [
        {
            "event_type": "ACTION_COMPLETED",
            "timestamp_utc": "2026-08-29T10:00:00Z",
            "capability_name": "calendar_snapshot",
            "outcome_state": "completed",
            "success": True,
        }
    ]
    originals = deepcopy((state, memory, reminders, receipts))

    projection = compose_daily_loop_projection(
        session_state=state,
        memory_items=memory,
        reminders=reminders,
        receipts=receipts,
        now=NOW,
    )

    assert projection.next[0].text == "09:00 — Review"
    assert {item.source for item in projection.next} >= {"calendar", "governed_memory", "local_reminders"}
    assert projection.waiting_on[0].text == "Vendor reply"
    assert projection.completed_today[0].text == "calendar_snapshot"
    assert projection.context_today[0].source == "weather"
    assert projection.recommended_next is not None
    assert projection.recommended_next.source == "recommendation_from:calendar"
    assert projection.execution_performed is False
    assert projection.authorization_granted is False
    assert (state, memory, reminders, receipts) == originals


def test_accepted_unverified_receipt_is_unresolved_never_completed():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "capability_name": "volume_control",
                "outcome_state": "accepted_unverified",
                "success": True,
            }
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.unresolved_outcomes[0].text == "Accepted; outcome unverified: volume_control"
    assert "Completed: volume_control" not in {item.text for item in projection.changed}


def test_projection_excludes_verified_completions_from_other_days():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-28T10:00:00Z",
                "capability_name": "old_action",
                "outcome_state": "completed",
            }
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.changed == ()


def test_empty_projection_reports_missing_sources_and_no_fabricated_items():
    projection = compose_daily_loop_projection(now=NOW)
    answer = render_daily_loop_answer(PersonalOperationsIntent.WAITING_ON, projection)

    assert projection.waiting_on == ()
    assert "No matching items are present" in answer
    assert "Calendar is not loaded in this session" in answer
    assert "Weather is not loaded in this session" in answer
    assert "News is not loaded in this session" in answer
    assert "Google Tasks is not connected" in answer
    assert "No action was executed" in answer


def test_recommendation_is_clearly_distinguished_from_evidence():
    projection = compose_daily_loop_projection(
        memory_items=[{"content_raw": "Call supplier", "tags": ["waiting"]}],
        now=NOW,
    )

    answer = render_daily_loop_answer(PersonalOperationsIntent.RECOMMENDED_NEXT, projection)

    assert "Recommendation (derived, not an instruction)" in answer
    assert "recommendation_from:governed_memory" in answer


def test_noncurrent_memory_cannot_enter_projection_or_recommendation():
    projection = compose_daily_loop_projection(
        memory_items=[
            {"content_raw": "Current task", "tags": ["next"], "tier": "active"},
            {"content_raw": "Deferred task", "tags": ["next"], "tier": "deferred"},
            {
                "content_raw": "Superseded task",
                "tags": ["next"],
                "tier": "active",
                "lock": {"superseded_by": "MEM-new"},
            },
            {
                "content_raw": "Private internal task",
                "tags": ["next"],
                "tier": "active",
                "user_visible": False,
            },
        ],
        now=NOW,
    )

    assert [item.text for item in projection.next] == ["Current task"]
    assert projection.recommended_next is not None
    assert projection.recommended_next.text == "Current task"


def test_calendar_requires_positive_connection_evidence():
    projection = compose_daily_loop_projection(
        session_state={
            "brief_calendar": {
                "status": "unavailable",
                "events": [{"time": "09:00", "title": "Stale event"}],
            }
        },
        now=NOW,
    )

    assert projection.next == ()
    calendar = next(source for source in projection.sources if source.source == "calendar")
    assert calendar.status == "not_loaded"
    assert calendar.detail == "Calendar is not loaded in this session."


def test_weather_requires_positive_connection_evidence():
    projection = compose_daily_loop_projection(
        session_state={
            "brief_weather": {
                "summary": "Weather is currently unavailable.",
                "condition": "Unavailable",
                "status": "unavailable",
                "connected": False,
            }
        },
        now=NOW,
    )

    assert not any(item.source == "weather" for item in projection.context_today)
    weather = next(source for source in projection.sources if source.source == "weather")
    assert weather.status == "not_loaded"
    assert weather.detail == "Weather is not loaded in this session."


def test_waiting_answer_counts_unresolved_outcomes_separately():
    projection = compose_daily_loop_projection(
        memory_items=[{"content_raw": "Approval", "tags": ["waiting"]}],
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "outcome_state": "unknown_unverified",
                "capability_name": "external_action",
            }
        ],
        now=NOW,
    )

    answer = render_daily_loop_answer(PersonalOperationsIntent.WAITING_ON, projection)
    assert "Approval [source: governed_memory]" in answer
    assert "Unresolved action outcomes: 1" in answer
