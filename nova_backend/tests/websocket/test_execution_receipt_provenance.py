from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from src import brain_server
from src.actions.action_request import ActionRequest
from src.base_skill import SkillResult
from src.conversation.session_router import GateResult
from src.executors.memory_governance_executor import MemoryGovernanceExecutor
from src.memory.governed_memory_store import GovernedMemoryStore
from src.websocket.session_handler import guard_general_chat_action_claim
from tests.phase45._websocket_test_helpers import _ScriptedWebSocket
from tests.websocket.test_commitment_truth_reminder_handoff import (
    _FailingScheduleStore,
    _RecordingScheduleStore,
)
from tests.websocket.test_commitment_truth_reminder_handoff import (
    _run_session as _run_reminder_session,
)

pytestmark = pytest.mark.slow

ACTION_CLAIM_NOTE = "Chat can't take actions. Nothing was saved, sent, scheduled or changed."


def _chat_frames(ws: _ScriptedWebSocket) -> list[dict]:
    return [message for message in ws.sent_messages if message.get("type") == "chat"]


@pytest.mark.parametrize(
    "model_reply",
    (
        "Reminder saved: SCH-FAKE-0001\nText: call mom\nRequested for: Oct 16, 5:00 PM",
        'Saved. Memory MEM-FAKE-0001: "favorite color blue".\nTier: personal',
        "Summary: Reminder saved: SCH-FAKE-0001\nText: call mom",
    ),
)
def test_model_receipt_shapes_are_neutralized(model_reply):
    guarded = guard_general_chat_action_claim(model_reply)

    assert "SCH-FAKE-0001" not in guarded
    assert "MEM-FAKE-0001" not in guarded
    assert ACTION_CLAIM_NOTE in guarded


def test_model_receipt_shape_split_across_lines_is_neutralized():
    guarded = guard_general_chat_action_claim(
        "Your receipt follows:\nSCH-FAKE-0001\nText: call mom"
    )

    assert "SCH-FAKE-0001" not in guarded
    assert ACTION_CLAIM_NOTE in guarded


@pytest.mark.parametrize(
    "model_reply,receipt_id",
    (
        ("Done: SCH-FAKE-0001", "SCH-FAKE-0001"),
        ("All set — MEM-FAKE-0001", "MEM-FAKE-0001"),
    ),
)
def test_model_standalone_receipt_marker_is_neutralized(model_reply, receipt_id):
    guarded = guard_general_chat_action_claim(model_reply)

    assert receipt_id not in guarded
    assert ACTION_CLAIM_NOTE in guarded


def test_model_fake_receipt_has_no_execution_provenance(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    fake = (
        "Reminder saved: SCH-FAKE-0001\n"
        "Text: call mom\n"
        'receipt: {"kind": "reminder", "id": "SCH-FAKE-0001"}'
    )
    ws = _ScriptedWebSocket(["what should I remember to do tomorrow?"])

    with patch("src.skills.general_chat.generate_chat", return_value=fake):
        asyncio.run(brain_server.websocket_endpoint(ws))

    final = _chat_frames(ws)[-1]
    assert "receipt" not in final
    assert "SCH-FAKE-0001" not in final["message"]
    assert ACTION_CLAIM_NOTE in final["message"]


def test_plain_model_reply_has_no_execution_provenance(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(["explain TCP"])

    with patch("src.skills.general_chat.generate_chat", return_value="TCP is connection-oriented."):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert "receipt" not in _chat_frames(ws)[-1]


def test_confirmed_escalation_model_receipt_is_neutralized(monkeypatch):
    async def _ask_for_escalation(*args, **kwargs):
        del args, kwargs
        return SkillResult(
            success=True,
            message="Would you like me to go deeper?",
            skill="general_chat",
            data={
                "escalation": {
                    "ask_user": True,
                    "original_query": "please think about this",
                    "context_snapshot": [],
                    "heuristic_result": {},
                }
            },
        )

    async def _confirm_escalation(*args, **kwargs):
        del args
        kwargs["session_state"]["pending_escalation"] = None
        return SimpleNamespace(
            handled=True,
            message="",
            context_entries=[],
            skill_result=SkillResult(
                success=True,
                message="Reminder saved: SCH-FAKE-ESCALATION",
                skill="general_chat",
            ),
        )

    monkeypatch.setattr(brain_server, "run_general_chat_fallback", _ask_for_escalation)
    monkeypatch.setattr(brain_server, "resolve_pending_escalation_reply", _confirm_escalation)
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(GovernedMemoryStore, "list_items", lambda self, **kwargs: [])
    ws = _ScriptedWebSocket(["please think about this", "yes"])

    asyncio.run(brain_server.websocket_endpoint(ws))

    final = _chat_frames(ws)[-1]
    assert "receipt" not in final
    assert "SCH-FAKE-ESCALATION" not in final["message"]
    assert ACTION_CLAIM_NOTE in final["message"]


def test_real_reminder_save_carries_execution_provenance(monkeypatch):
    store = _RecordingScheduleStore()
    ws = _run_reminder_session(
        monkeypatch,
        ["remind me to call mom tomorrow at 9am"],
        store,
    )

    frame = next(
        message
        for message in _chat_frames(ws)
        if "Reminder saved: SCH-TEST-0001" in message.get("message", "")
    )
    assert frame["receipt"] == {"kind": "reminder", "id": "SCH-TEST-0001"}
    assert store.get_schedule(frame["receipt"]["id"])["id"] == frame["receipt"]["id"]


def test_real_memory_save_carries_execution_provenance(monkeypatch, tmp_path):
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(["remember this: favorite color blue"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model must not handle an explicit memory save"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    frame = next(
        message
        for message in _chat_frames(ws)
        if "Saved. Memory MEM-" in message.get("message", "")
    )
    receipt = frame["receipt"]
    assert receipt["kind"] == "memory"
    assert GovernedMemoryStore().get_item(receipt["id"])["id"] == receipt["id"]


class _UnverifiableReminderStore(_RecordingScheduleStore):
    def get_schedule(self, schedule_id: str) -> None:
        del schedule_id
        return None


def test_unverifiable_reminder_write_has_no_receipt_or_success_wording(monkeypatch):
    store = _UnverifiableReminderStore()
    ws = _run_reminder_session(
        monkeypatch,
        ["remind me to call mom tomorrow at 9am"],
        store,
    )

    assert len(store.created) == 1
    frames = _chat_frames(ws)
    assert all("receipt" not in frame for frame in frames)
    assert all("Reminder saved:" not in frame.get("message", "") for frame in frames)


def test_failed_reminder_write_has_no_receipt_or_success_wording(monkeypatch):
    ws = _run_reminder_session(
        monkeypatch,
        ["remind me to call mom tomorrow at 9am"],
        _FailingScheduleStore(),
    )

    frames = _chat_frames(ws)
    assert all("receipt" not in frame for frame in frames)
    assert all("Reminder saved:" not in frame.get("message", "") for frame in frames)


def test_unverifiable_memory_write_has_no_receipt_or_success_wording(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr(GovernedMemoryStore, "get_item", lambda self, item_id: None)
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(GovernedMemoryStore, "list_items", lambda self, **kwargs: [])
    ws = _ScriptedWebSocket(["remember this: favorite color blue"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model must not handle an explicit memory save"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    frames = _chat_frames(ws)
    assert all("receipt" not in frame for frame in frames)
    assert all("Saved. Memory" not in frame.get("message", "") for frame in frames)


def test_unverifiable_memory_write_preserves_accepted_unknown_outcome(monkeypatch, tmp_path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    monkeypatch.setattr(store, "get_item", lambda item_id: None)
    result = MemoryGovernanceExecutor(store=store).execute(
        ActionRequest(
            capability_id=61,
            params={"action": "save", "title": "Private note", "body": "Keep this."},
        )
    )

    assert result.success is True
    assert result.status == "completed"
    assert result.outcome_reason == "memory_read_back_failed"
    assert (result.data or {}).get("outcome_state") == "accepted_unverified"
    assert "memory_item" not in (result.data or {})
    assert "saved" not in result.message.lower()


def test_failed_memory_write_has_no_receipt_or_success_wording(monkeypatch, tmp_path):
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))

    def _fail_save(self, **kwargs):
        del self, kwargs
        raise OSError("simulated memory write failure")

    monkeypatch.setattr(GovernedMemoryStore, "save_item", _fail_save)
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(GovernedMemoryStore, "list_items", lambda self, **kwargs: [])
    ws = _ScriptedWebSocket(["remember this: favorite color blue"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model must not handle an explicit memory save"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    frames = _chat_frames(ws)
    assert all("receipt" not in frame for frame in frames)
    assert all("Saved. Memory" not in frame.get("message", "") for frame in frames)
