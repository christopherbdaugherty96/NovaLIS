from copy import deepcopy
from datetime import datetime, timezone

from src.brief.daily_loop import compose_daily_loop_projection, render_daily_loop_answer
from src.conversation.personal_operations_intent import PersonalOperationsIntent

NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)


def test_projection_assembles_existing_state_with_provenance_without_mutation():
    state = {
        "brief_calendar": {
            "connected": True,
            "events": [{"date": "2026-08-29", "time": "01:00 PM", "title": "Review"}],
        },
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
            "outcome_state": "visible_verified",
            "visible_effect_verified": True,
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

    assert projection.next[0].text == "01:00 PM — Review"
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
                "launch_request_accepted": True,
                "success": True,
            }
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.unresolved_outcomes[0].text == "Accepted; outcome unverified: volume_control"
    assert "Completed: volume_control" not in {item.text for item in projection.changed}


def test_successful_user_read_is_changed_but_not_finished_or_unresolved():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-READ",
                "capability_id": 32,
                "capability_name": "system_status",
                "activity_origin": "user_action",
            },
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:01:00Z",
                "request_id": "REQ-READ",
                "capability_id": 32,
                "success": True,
                "status": "completed",
                "authority_class": "read_only_local",
                "external_effect": False,
                "activity_origin": "user_action",
            },
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.unresolved_outcomes == ()
    assert "Read completed: system_status" in {item.text for item in projection.changed}
    assert not any("effect verified" in item.text.lower() for item in projection.changed)


def test_completed_actions_correlate_attempt_receipts_and_remain_distinguishable():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:03:00Z",
                "request_id": "REQ-2",
                "capability_id": 22,
                "status": "completed",
                "outcome_state": "visible_verified",
                "visible_effect_verified": True,
                "success": True,
            },
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T10:02:00Z",
                "request_id": "REQ-2",
                "capability_id": 22,
                "capability_name": "open_file_folder",
            },
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:01:00Z",
                "request_id": "REQ-1",
                "capability_id": 19,
                "status": "completed",
                "outcome_state": "visible_verified",
                "visible_effect_verified": True,
                "success": True,
            },
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-1",
                "capability_id": 19,
                "capability_name": "volume_control",
            },
        ],
        now=NOW,
    )

    assert [item.text for item in projection.completed_today] == [
        "open_file_folder",
        "volume_control",
    ]
    assert {item.text for item in projection.changed} >= {
        "Completed: open_file_folder",
        "Completed: volume_control",
    }


def test_background_reads_are_changes_not_user_completed_work():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-BG",
                "capability_id": 55,
                "activity_origin": "background_read",
                "status": "completed",
                "success": True,
            },
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T09:59:00Z",
                "request_id": "REQ-BG",
                "capability_id": 55,
                "capability_name": "weather_snapshot",
                "activity_origin": "background_read",
            },
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert [item.text for item in projection.changed] == [
        "Background read completed: weather_snapshot"
    ]


def test_daily_brief_support_reads_do_not_become_user_work_or_unresolved_outcomes():
    receipts = []
    for index, (capability_id, capability_name) in enumerate(
        (
            (55, "weather_snapshot"),
            (56, "news_snapshot"),
            (32, "os_diagnostics"),
            (57, "calendar_snapshot"),
        )
    ):
        request_id = f"REQ-BRIEF-{index}"
        receipts.extend(
            [
                {
                    "event_type": "ACTION_ATTEMPTED",
                    "timestamp_utc": f"2026-08-29T10:0{index}:00Z",
                    "request_id": request_id,
                    "capability_id": capability_id,
                    "capability_name": capability_name,
                    "activity_origin": "background_read",
                },
                {
                    "event_type": "ACTION_COMPLETED",
                    "timestamp_utc": f"2026-08-29T10:0{index}:01Z",
                    "request_id": request_id,
                    "capability_id": capability_id,
                    "activity_origin": "background_read",
                    "status": "completed",
                    "success": True,
                },
            ]
        )

    projection = compose_daily_loop_projection(receipts=receipts, now=NOW)

    assert projection.waiting_on == ()
    assert projection.unresolved_outcomes == ()
    assert projection.completed_today == ()
    assert all(item.text.startswith("Background read completed:") for item in projection.changed)


def test_failed_background_read_is_never_described_as_completed():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-BG-FAIL",
                "capability_id": 55,
                "activity_origin": "background_read",
                "status": "failed",
                "success": False,
            },
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T09:59:00Z",
                "request_id": "REQ-BG-FAIL",
                "capability_id": 55,
                "capability_name": "weather_snapshot",
                "activity_origin": "background_read",
            },
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.waiting_on == ()
    assert projection.unresolved_outcomes == ()
    assert [item.text for item in projection.changed] == [
        "Background read failed: weather_snapshot"
    ]
    assert not any("completed" in item.text.lower() for item in projection.changed)


def test_correlated_attempt_and_completion_produce_one_change_entry():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-ONE",
                "capability_id": 19,
                "activity_origin": "user_action",
                "status": "completed",
                "outcome_state": "visible_verified",
                "visible_effect_verified": True,
                "success": True,
            },
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T09:59:00Z",
                "request_id": "REQ-ONE",
                "capability_id": 19,
                "capability_name": "volume_control",
                "activity_origin": "user_action",
            },
        ],
        now=NOW,
    )

    assert [item.text for item in projection.changed] == ["Completed: volume_control"]


def test_changed_merges_all_receipt_types_by_timestamp_before_limit():
    receipts = [
        {
            "event_type": "ACTION_COMPLETED",
            "timestamp_utc": f"2026-08-29T{hour:02d}:00:00Z",
            "request_id": f"REQ-{hour}",
            "capability_name": f"action_{hour}",
            "activity_origin": "user_action",
            "status": "completed",
            "outcome_state": "visible_verified",
            "visible_effect_verified": True,
            "success": True,
        }
        for hour in range(13, 19)
    ]
    receipts.append(
        {
            "event_type": "MEMORY_ITEM_SAVED",
            "timestamp_utc": "2026-08-29T19:00:00Z",
            "message": "Newest memory change",
        }
    )

    projection = compose_daily_loop_projection(receipts=receipts, now=NOW)

    assert [item.text for item in projection.changed] == [
        "Newest memory change",
        "Completed: action_18",
        "Completed: action_17",
        "Completed: action_16",
        "Completed: action_15",
    ]


def test_orphan_attempt_is_preserved_once_as_unknown_unverified():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-INTERRUPTED",
                "capability_id": 19,
                "capability_name": "volume_control",
                "activity_origin": "user_action",
            }
        ],
        now=NOW,
    )

    expected = "Outcome unknown; not verified: volume_control"
    assert [item.text for item in projection.unresolved_outcomes] == [expected]
    assert [item.text for item in projection.changed] == [expected]
    assert projection.completed_today == ()


def test_partial_failure_uses_canonical_failed_outcome_semantics():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:01:00Z",
                "request_id": "REQ-PARTIAL",
                "capability_id": 22,
                "activity_origin": "user_action",
                "status": "completed_degraded",
                "outcome_state": "partial_failure",
                "partial_failure": True,
                "success": False,
            },
            {
                "event_type": "ACTION_ATTEMPTED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-PARTIAL",
                "capability_id": 22,
                "capability_name": "open_file_folder",
                "activity_origin": "user_action",
            },
        ],
        now=NOW,
    )

    assert [item.text for item in projection.changed] == ["Failed: open_file_folder"]
    assert projection.completed_today == ()
    assert projection.unresolved_outcomes == ()


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


def test_projection_excludes_verified_completion_with_malformed_timestamp():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "bad",
                "request_id": "REQ-UNDATED",
                "capability_name": "undated_action",
                "activity_origin": "user_action",
                "status": "completed",
                "outcome_state": "visible_verified",
                "visible_effect_verified": True,
                "success": True,
            }
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.changed == ()


def test_projection_excludes_non_action_change_with_missing_timestamp():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "MEMORY_ITEM_SAVED",
                "message": "Undated memory change",
            }
        ],
        now=NOW,
    )

    assert projection.changed == ()


def test_malformed_receipt_capability_id_fails_closed_as_unavailable():
    projection = compose_daily_loop_projection(
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-CORRUPT",
                "capability_id": "abc",
                "activity_origin": "user_action",
                "outcome_state": "visible_verified",
                "visible_effect_verified": True,
            }
        ],
        now=NOW,
    )

    assert projection.completed_today == ()
    assert projection.changed == ()
    receipts = next(source for source in projection.sources if source.source == "receipts")
    assert receipts.status == "unavailable"


def test_failed_news_refresh_preserves_unavailable_source_truth():
    projection = compose_daily_loop_projection(
        session_state={"news_cache": []},
        receipts=[
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-08-29T10:00:00Z",
                "request_id": "REQ-NEWS-FAIL",
                "capability_id": 56,
                "capability_name": "news_snapshot",
                "activity_origin": "background_read",
                "status": "failed",
                "outcome_state": "failed",
                "success": False,
            }
        ],
        now=NOW,
    )

    news = next(source for source in projection.sources if source.source == "news")
    assert news.status == "unavailable"
    assert "attempted news refresh failed" in news.detail


def test_ambient_working_context_is_not_promoted_to_open_loop_or_recommendation():
    projection = compose_daily_loop_projection(
        session_state={"working_context": {"task_goal": "What is the weather today?"}},
        now=NOW,
    )

    assert projection.open_loops == ()
    assert projection.recommended_next is None


def test_answered_conversation_question_is_not_promoted_to_open_loop():
    projection = compose_daily_loop_projection(
        session_state={
            "conversation_context": {
                "open_loops": ["Why does local inference matter?"],
                "open_question": "Why does local inference matter?",
                "last_answer_kind": "explanation",
            }
        },
        now=NOW,
    )

    assert projection.open_loops == ()
    assert projection.recommended_next is None


def test_only_explicitly_unresolved_session_evidence_becomes_open_loop():
    projection = compose_daily_loop_projection(
        session_state={
            "conversation_context": {
                "open_loops": [
                    {"text": "Confirm deployment window", "status": "unresolved"},
                    {"text": "Answered question", "status": "resolved"},
                ]
            }
        },
        now=NOW,
    )

    assert [item.text for item in projection.open_loops] == ["Confirm deployment window"]


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


def test_automatic_daily_brief_schedule_is_not_user_work_or_recommendation():
    projection = compose_daily_loop_projection(
        reminders=[
            {
                "kind": "daily_brief",
                "active": True,
                "title": "Daily brief",
                "body": "Run your scheduled daily brief.",
                "next_run_at": "2026-08-30T08:00:00Z",
            }
        ],
        now=NOW,
    )

    assert projection.next == ()
    assert projection.open_loops == ()
    assert projection.recommended_next is None


def test_malformed_memory_fields_fail_closed_as_unavailable():
    projection = compose_daily_loop_projection(
        memory_items=[{"content_raw": "Damaged memory", "tags": 42}],
        now=NOW,
    )

    assert projection.next == ()
    assert projection.open_loops == ()
    memory = next(source for source in projection.sources if source.source == "governed_memory")
    assert memory.status == "unavailable"


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
            {
                "content_raw": "Deleted task",
                "tags": ["next", "open_loop"],
                "tier": "active",
                "deleted": True,
            },
        ],
        now=NOW,
    )

    assert [item.text for item in projection.next] == ["Current task"]
    assert "Deleted task" not in [item.text for item in projection.open_loops]
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


def test_elapsed_calendar_events_are_not_next_or_recommended():
    projection = compose_daily_loop_projection(
        session_state={
            "brief_calendar": {
                "connected": True,
                "status": "ok",
                "events": [
                    {"date": "2026-08-29", "time": "7:00 AM", "title": "Past meeting"},
                    {"date": "2026-08-29", "time": "4:00 PM", "title": "Future meeting"},
                ],
            }
        },
        now=NOW,
    )

    assert [item.text for item in projection.next] == ["4:00 PM — Future meeting"]
    assert projection.recommended_next is not None
    assert projection.recommended_next.text == "4:00 PM — Future meeting"


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
