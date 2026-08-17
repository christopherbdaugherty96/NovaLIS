from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


class _RecordingScheduleStore:
    def __init__(self) -> None:
        self.created: list[dict] = []

    def create_schedule(self, **kwargs) -> dict:
        self.created.append(dict(kwargs))
        return {
            "id": "SCH-TEST-0001",
            "kind": kwargs["kind"],
            "recurrence": kwargs["recurrence"],
        }

    def summarize(self) -> dict:
        upcoming_items = [
            {
                "id": "SCH-TEST-0001",
                "kind": str(item["kind"]),
                "title": str(item["title"]),
                "body": str(item["body"]),
                "recurrence": str(item["recurrence"]),
                "next_run_at": item["next_run_at"].isoformat(),
                "active": True,
            }
            for item in self.created
        ]
        return {
            "summary": f"0 due | {len(self.created)} upcoming",
            "active_count": len(self.created),
            "due_count": 0,
            "upcoming_count": len(self.created),
            "due_items": [],
            "upcoming_items": upcoming_items,
            "policy_summary": "",
        }

    def get_schedule(self, schedule_id: str) -> dict | None:
        if schedule_id != "SCH-TEST-0001" or not self.created:
            return None
        return {
            "id": schedule_id,
            "body": str(self.created[-1]["body"]),
            "active": True,
        }


class _FailingScheduleStore(_RecordingScheduleStore):
    def create_schedule(self, **kwargs) -> dict:
        raise OSError("simulated persistence failure")


class _SummaryFailingScheduleStore(_RecordingScheduleStore):
    def summarize(self) -> dict:
        raise OSError("simulated summary failure after persistence")


class _TimeoutScheduleStore(_RecordingScheduleStore):
    def create_schedule(self, **kwargs) -> dict:
        raise TimeoutError("simulated persistence timeout")


class _ReadFailingScheduleStore(_RecordingScheduleStore):
    def get_schedule(self, schedule_id: str) -> dict | None:
        raise OSError("simulated reminder verification failure")


def _run_session(monkeypatch, prompts: list[str], store: _RecordingScheduleStore) -> _ScriptedWebSocket:
    monkeypatch.setattr(brain_server, "NotificationScheduleStore", lambda: store)
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(prompts)
    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("GeneralChat must not run for reminder handoff"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))
    return ws


def test_calendar_offer_preserves_subject_then_persists_real_reminder(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_session(
        monkeypatch,
        [
            "add to my calendar to complete onboarding for work at 3:00 PM",
            "yes, set a reminder",
            "remind me at two pm",
        ],
        store,
    )

    assert len(store.created) == 1
    created = store.created[0]
    assert created["kind"] == "reminder"
    assert created["body"] == "complete onboarding for work"
    assert created["recurrence"] == "once"
    assert created["next_run_at"].hour == 14

    messages = _chat_messages(ws)
    assert any("Calendar writing isn't enabled" in message for message in messages)
    assert any("No calendar event was created" in message for message in messages)
    assert any("What time should Nova save this reminder for?" in message for message in messages)
    assert any("Reminder saved: SCH-TEST-0001" in message for message in messages)
    assert any("Text: complete onboarding for work" in message for message in messages)
    assert any("does not have background reminder delivery" in message for message in messages)
    assert any("will not fire automatically" in message for message in messages)


@pytest.mark.parametrize(
    "management_command",
    ["show schedules", "reminders", "are there any reminders today?"],
)
def test_notification_management_command_displays_persisted_reminder(
    monkeypatch,
    management_command: str,
):
    store = _RecordingScheduleStore()
    ws = _run_session(
        monkeypatch,
        [
            "add to my calendar to complete onboarding for work at 3:00 PM",
            "yes, set a reminder",
            "remind me at two pm",
            management_command,
        ],
        store,
    )

    assert len(store.created) == 1
    messages = _chat_messages(ws)
    assert any("Reminder saved: SCH-TEST-0001" in message for message in messages)
    assert any("Scheduled Updates" in message for message in messages)

    schedule_widgets = [
        message for message in ws.sent_messages if message.get("type") == "notification_schedule"
    ]
    assert len(schedule_widgets) == 2
    assert schedule_widgets[-1]["active_count"] == 1
    assert schedule_widgets[-1]["upcoming_items"][0]["id"] == "SCH-TEST-0001"
    assert schedule_widgets[-1]["upcoming_items"][0]["body"] == "complete onboarding for work"
    assert not any(message.get("type") == "calendar" for message in ws.sent_messages)


@pytest.mark.parametrize(
    "phrase",
    [
        "what's my schedule today?",
        "show my calendar",
        "what do I have scheduled tomorrow?",
    ],
)
def test_calendar_awareness_queries_remain_calendar_queries(monkeypatch, phrase: str):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, [phrase], store)

    assert store.created == []
    assert any(message.get("type") == "calendar" for message in ws.sent_messages)
    assert not any(message.get("type") == "notification_schedule" for message in ws.sent_messages)


@pytest.mark.parametrize(
    "phrase",
    [
        "add this to my calendar",
        "put this on my calendar",
        "schedule this event",
        "create a calendar event",
        "block this time on my calendar",
        "add an event",
        "add a dentist appointment tomorrow at 3 PM",
        "put dinner on my calendar at 7",
        "schedule a meeting tomorrow at noon",
        "add this to Google Calendar",
    ],
)
def test_calendar_write_forms_are_blocked_before_general_chat(monkeypatch, phrase: str):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, [phrase], store)

    assert store.created == []
    messages = _chat_messages(ws)
    assert any("Calendar writing isn't enabled" in message for message in messages)
    assert any("No calendar event was created" in message for message in messages)


def test_google_calendar_boundary_hands_off_to_local_reminder_without_claiming_write(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_session(
        monkeypatch,
        [
            "add this to Google Calendar",
            "yes, set a reminder",
            "dentist appointment",
            "tomorrow at 3 PM",
        ],
        store,
    )

    assert len(store.created) == 1
    assert store.created[0]["body"] == "dentist appointment"
    messages = _chat_messages(ws)
    assert any("Google Calendar writing isn't enabled" in message for message in messages)
    assert any("No calendar event was created" in message for message in messages)
    assert any("Reminder saved: SCH-TEST-0001" in message for message in messages)
    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)


@pytest.mark.parametrize(
    "prompts, expected_body",
    [
        (["remind me to call mom", "2 PM"], "call mom"),
        (["remind me at 2 PM", "call mom"], "call mom"),
        (["remind me at 2 PM to complete onboarding"], "complete onboarding"),
        (["set a reminder tomorrow at 2 PM to test Nova"], "test Nova"),
    ],
)
def test_reminder_slots_are_preserved_until_persistence(monkeypatch, prompts, expected_body):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, prompts, store)

    assert len(store.created) == 1
    assert store.created[0]["body"] == expected_body
    assert store.created[0]["next_run_at"].hour == 14
    assert any("Reminder saved: SCH-TEST-0001" in message for message in _chat_messages(ws))


def test_natural_tomorrow_reminder_never_streams_a_prepersistence_promise(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, ["remind me tomorrow at 2 PM to test Nova"], store)

    assert len(store.created) == 1
    assert store.created[0]["body"] == "test Nova"
    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)
    messages = _chat_messages(ws)
    assert any("Reminder saved: SCH-TEST-0001" in message for message in messages)
    assert any("will not fire automatically" in message for message in messages)


def test_saved_reminder_followup_uses_persisted_session_evidence(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_session(
        monkeypatch,
        [
            "remind me tomorrow at 2 PM to test Nova",
            "show schedules",
            "did you save that reminder?",
        ],
        store,
    )

    assert len(store.created) == 1
    messages = _chat_messages(ws)
    assert any(
        'Yes. Nova saved reminder SCH-TEST-0001: "test Nova"' in message
        for message in messages
    )
    assert any("will not fire automatically while Nova is closed" in message for message in messages)


def test_failed_reminder_followup_never_claims_persistence(monkeypatch):
    store = _FailingScheduleStore()
    ws = _run_session(
        monkeypatch,
        ["remind me at 2 PM to call mom", "did you save that reminder?"],
        store,
    )

    messages = _chat_messages(ws)
    assert any("did not save the most recent reminder request" in message for message in messages)
    assert not any("Yes. Nova saved reminder" in message for message in messages)


def test_unparsed_reminder_followup_does_not_inherit_prior_success(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_session(
        monkeypatch,
        [
            "remind me tomorrow at 2 PM to test Nova",
            "remind me on August 13 at 2 PM to test Nova",
            "did you save that reminder?",
        ],
        store,
    )

    messages = _chat_messages(ws)
    assert len(store.created) == 1
    assert any("no reminder was saved" in message for message in messages)
    assert any("did not save the most recent reminder request" in message for message in messages)
    assert sum("Yes. Nova saved reminder" in message for message in messages) == 0


def test_reminder_followup_fails_conservatively_when_store_cannot_be_verified(monkeypatch):
    store = _ReadFailingScheduleStore()
    ws = _run_session(
        monkeypatch,
        ["remind me tomorrow at 2 PM to test Nova", "did you save that reminder?"],
        store,
    )

    messages = _chat_messages(ws)
    assert len(store.created) == 1
    assert any("couldn't verify the reminder store" in message for message in messages)
    assert not any("Yes. Nova saved reminder" in message for message in messages)


def test_unparsed_reminder_action_fails_truthfully_without_general_chat_stream(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, ["remind me on August 13 at 2 PM to test Nova"], store)

    assert store.created == []
    messages = _chat_messages(ws)
    assert any("no reminder was saved" in message for message in messages)
    assert not any("Reminder saved:" in message for message in messages)
    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)


def test_persistence_failure_never_claims_success(monkeypatch):
    store = _FailingScheduleStore()
    ws = _run_session(monkeypatch, ["remind me at 2 PM to call mom"], store)

    messages = _chat_messages(ws)
    assert any("No reminder was created" in message for message in messages)
    assert not any("Reminder saved:" in message for message in messages)
    assert not any("SCH-" in message for message in messages)
    assert not any("scheduled" in message.lower() for message in messages)
    assert not any("done" in message.lower() for message in messages)
    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)


def test_persistence_timeout_reports_unknown_without_streaming_success(monkeypatch):
    store = _TimeoutScheduleStore()
    ws = _run_session(monkeypatch, ["remind me tomorrow at 2 PM to test Nova"], store)

    messages = _chat_messages(ws)
    assert any("persistence timed out" in message for message in messages)
    assert any("won't claim one was created" in message for message in messages)
    assert not any("Reminder saved:" in message for message in messages)
    assert not any("I'll remind" in message for message in messages)
    assert not any("done" in message.lower() for message in messages)
    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)


@pytest.mark.parametrize(
    "question",
    [
        "can reminders alert me while Nova is closed?",
        "will you notify me tomorrow if Nova is closed?",
    ],
)
def test_background_delivery_questions_never_claim_closed_app_alerts(monkeypatch, question):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, [question], store)

    messages = _chat_messages(ws)
    assert any("cannot alert you while Nova is closed" in message for message in messages)
    assert any("do not run in the background" in message for message in messages)
    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)


def test_summary_failure_does_not_retract_successful_persistence(monkeypatch):
    store = _SummaryFailingScheduleStore()
    ws = _run_session(monkeypatch, ["remind me at 2 PM to call mom"], store)

    assert len(store.created) == 1
    messages = _chat_messages(ws)
    assert any("Reminder saved: SCH-TEST-0001" in message for message in messages)
    assert any("Text: call mom" in message for message in messages)
    assert any("Schedule overview is temporarily unavailable" in message for message in messages)
    assert not any("No reminder was created" in message for message in messages)
