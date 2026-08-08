from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from src import brain_server
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages


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
        return {
            "summary": f"0 due | {len(self.created)} upcoming",
            "active_count": len(self.created),
            "due_count": 0,
            "upcoming_count": len(self.created),
            "due_items": [],
            "upcoming_items": [],
            "policy_summary": "",
        }


class _FailingScheduleStore(_RecordingScheduleStore):
    def create_schedule(self, **kwargs) -> dict:
        raise OSError("simulated persistence failure")


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
    "phrase",
    [
        "add this to my calendar",
        "put this on my calendar",
        "schedule this event",
        "create a calendar event",
        "block this time on my calendar",
        "add an event",
    ],
)
def test_calendar_write_forms_are_blocked_before_general_chat(monkeypatch, phrase: str):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, [phrase], store)

    assert store.created == []
    messages = _chat_messages(ws)
    assert any("Calendar writing isn't enabled" in message for message in messages)
    assert any("No calendar event was created" in message for message in messages)


@pytest.mark.parametrize(
    "prompts, expected_body",
    [
        (["remind me to call mom", "2 PM"], "call mom"),
        (["remind me at 2 PM", "call mom"], "call mom"),
        (["remind me at 2 PM to complete onboarding"], "complete onboarding"),
    ],
)
def test_reminder_slots_are_preserved_until_persistence(monkeypatch, prompts, expected_body):
    store = _RecordingScheduleStore()
    ws = _run_session(monkeypatch, prompts, store)

    assert len(store.created) == 1
    assert store.created[0]["body"] == expected_body
    assert store.created[0]["next_run_at"].hour == 14
    assert any("Reminder saved: SCH-TEST-0001" in message for message in _chat_messages(ws))


def test_persistence_failure_never_claims_success(monkeypatch):
    store = _FailingScheduleStore()
    ws = _run_session(monkeypatch, ["remind me at 2 PM to call mom"], store)

    messages = _chat_messages(ws)
    assert any("No reminder was created" in message for message in messages)
    assert not any("Reminder saved:" in message for message in messages)
    assert not any("SCH-" in message for message in messages)
    assert not any("scheduled" in message.lower() for message in messages)
    assert not any("done" in message.lower() for message in messages)
