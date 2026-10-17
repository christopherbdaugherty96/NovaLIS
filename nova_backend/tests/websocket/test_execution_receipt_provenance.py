from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult
from src.websocket.session_handler import guard_general_chat_action_claim
from tests.phase45._websocket_test_helpers import _ScriptedWebSocket
from tests.websocket.test_commitment_truth_reminder_handoff import (
    _RecordingScheduleStore,
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


def test_real_reminder_save_carries_execution_provenance(monkeypatch):
    ws = _run_reminder_session(
        monkeypatch,
        ["remind me to call mom tomorrow at 9am"],
        _RecordingScheduleStore(),
    )

    frame = next(
        message
        for message in _chat_frames(ws)
        if "Reminder saved: SCH-TEST-0001" in message.get("message", "")
    )
    assert frame["receipt"] == {"kind": "reminder", "id": "SCH-TEST-0001"}


def test_real_memory_save_carries_execution_provenance(monkeypatch):
    async def _save_memory(*args, **kwargs):
        del args, kwargs
        return ActionResult.ok(
            'Saved. Memory MEM-TEST-0001: "favorite color blue".',
            data={
                "memory_item": {
                    "id": "MEM-TEST-0001",
                    "title": "Favorite color",
                    "content_raw": "favorite color blue",
                }
            },
            capability_id=61,
        )

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _save_memory)
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
        if "Saved. Memory MEM-TEST-0001" in message.get("message", "")
    )
    assert frame["receipt"] == {"kind": "memory", "id": "MEM-TEST-0001"}
