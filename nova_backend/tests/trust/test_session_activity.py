from __future__ import annotations

import pytest
from src.trust.session_activity import (
    ActivityOrigin,
    activity_origin_for_request,
    normalize_activity_origin,
    record_rejected_or_unsupported,
    render_session_activity_recap,
)


def _receipt(event_type: str, request_id: str, **metadata) -> dict:
    return {
        "event_type": event_type,
        "timestamp_utc": metadata.pop("timestamp_utc", "2026-08-12T12:00:00+00:00"),
        "session_id": metadata.pop("session_id", "session-current"),
        "request_id": request_id,
        "activity_origin": metadata.pop("activity_origin", "user_action"),
        "capability_id": metadata.pop("capability_id", 19),
        "capability_name": metadata.pop("capability_name", "volume_up_down"),
        **metadata,
    }


def _pair(request_id: str, **completion) -> list[dict]:
    common = {
        key: completion[key]
        for key in ("activity_origin", "capability_id", "capability_name")
        if key in completion
    }
    return [
        _receipt("ACTION_ATTEMPTED", request_id, **common),
        _receipt("ACTION_COMPLETED", request_id, **completion),
    ]


def test_mixed_recap_uses_correlated_evidence_and_outcome_semantics():
    receipts = [
        *_pair(
            "background-news",
            activity_origin="background_read",
            capability_id=56,
            capability_name="news_update",
            success=True,
            status="completed",
        ),
        *_pair(
            "verified-volume",
            success=True,
            status="completed",
            outcome_state="visible_verified",
            visible_effect_verified=True,
            launch_request_accepted=True,
        ),
        *_pair(
            "unverified-folder",
            capability_id=22,
            capability_name="open_file_folder",
            success=True,
            status="completed",
            outcome_state="accepted_unverified",
            launch_request_accepted=True,
            visible_effect_verified=False,
        ),
        *_pair(
            "failed-action",
            success=False,
            status="failed",
            outcome_state="failed",
            failure_reason="device refused the command",
        ),
        _receipt("ACTION_ATTEMPTED", "unknown-action"),
    ]
    session_state = {"session_id": "session-current"}
    record_rejected_or_unsupported(
        session_state,
        label="Google Calendar write",
        reason="Calendar writing is not enabled.",
    )

    recap = render_session_activity_recap(
        session_id="session-current",
        activity_facts=session_state["session_activity_facts"],
        receipts=receipts,
    )

    assert "News update (Cap 56): background read completed" in recap
    assert "Volume up down (Cap 19): effect verified" in recap
    assert "Open file folder (Cap 22): request accepted; visible effect was not verified" in recap
    assert "Volume up down (Cap 19): failed" in recap
    assert "outcome unknown or unverified" in recap
    assert "Google Calendar write: rejected or unsupported; no action was attempted" in recap
    assert "did not infer actions from the conversation transcript" in recap


def test_user_read_success_is_distinct_from_effect_verified_action():
    recap = render_session_activity_recap(
        session_id="session-current",
        receipts=_pair(
            "system-status",
            capability_id=32,
            capability_name="system_status",
            success=True,
            status="completed",
            authority_class="read_only_local",
            external_effect=False,
        ),
    )

    assert "System status (Cap 32): read completed successfully" in recap
    assert "no external effect is claimed" in recap
    assert "effect verified" not in recap


def test_empty_and_legacy_receipts_never_create_current_session_history():
    receipts = [
        _receipt("ACTION_COMPLETED", "", success=True, status="completed"),
        {
            "event_type": "ACTION_COMPLETED",
            "timestamp_utc": "2026-08-12T12:00:00+00:00",
            "request_id": "legacy",
            "success": True,
            "status": "completed",
        },
        _receipt(
            "ACTION_COMPLETED",
            "other-session",
            session_id="session-other",
            success=True,
            status="completed",
        ),
    ]

    recap = render_session_activity_recap(
        session_id="session-current",
        receipts=receipts,
    )

    assert "do not have correlated action evidence for this session" in recap
    assert "will not infer actions from the conversation transcript" in recap


def test_conversation_mentions_are_not_an_activity_source():
    recap = render_session_activity_recap(
        session_id="session-current",
        activity_facts=[],
        receipts=[],
    )

    assert "opened" not in recap.lower()
    assert "performed" not in recap.lower()


def test_mismatched_origin_within_request_downgrades_to_unknown():
    receipts = [
        _receipt("ACTION_ATTEMPTED", "req-mismatch", activity_origin="user_action"),
        _receipt(
            "ACTION_COMPLETED",
            "req-mismatch",
            activity_origin="background_read",
            success=True,
            status="completed",
        ),
    ]

    recap = render_session_activity_recap(
        session_id="session-current",
        receipts=receipts,
    )

    assert "outcome unknown or unverified" in recap
    assert "disagree about activity origin" in recap


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("background_read", "background_read"),
        (ActivityOrigin.BACKGROUND_READ, "background_read"),
        ("user_action", "user_action"),
        ("client_claimed_verified", "user_action"),
        (None, "user_action"),
    ],
)
def test_activity_origin_is_allowlisted(raw, expected):
    assert normalize_activity_origin(raw) == expected


@pytest.mark.parametrize(
    ("silent", "command", "expected"),
    [
        (True, "weather", "background_read"),
        (True, "news", "background_read"),
        (True, "calendar", "background_read"),
        (True, "awareness brief", "background_read"),
        (True, "volume up", "user_action"),
        (True, "open documents", "user_action"),
        (False, "weather", "user_action"),
    ],
)
def test_background_origin_requires_silent_and_allowlisted_read_command(
    silent,
    command,
    expected,
):
    assert (
        activity_origin_for_request(
            silent_widget_refresh=silent,
            command_text=command,
        )
        == expected
    )
