from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from src.websocket.session_handler import guard_general_chat_action_claim
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


@pytest.mark.parametrize(
    ("claim", "action"),
    [
        ("I saved that for you.", "saved"),
        ("I'll remember that.", "remembered"),
        ("I forgot that memory.", "forgot"),
        ("I deleted it.", "deleted"),
        ("I set a reminder.", "reminder_set"),
        ("I cancelled the reminder.", "cancelled"),
        ("I completed the task.", "completed"),
        ("I emailed the update.", "sent"),
        ("I sent the update.", "sent"),
        ("I scheduled it.", "scheduled"),
    ],
)
def test_action_claim_requires_matching_same_turn_receipt(claim, action):
    guarded = guard_general_chat_action_claim(claim, turn_receipts=[])
    assert guarded == "I didn't do that."

    matching = [{"event_type": "ACTION_COMPLETED", "action_kind": action, "success": True}]
    assert guard_general_chat_action_claim(claim, turn_receipts=matching) == claim

    wrong = [{"event_type": "ACTION_COMPLETED", "action_kind": "different", "success": True}]
    assert guard_general_chat_action_claim(claim, turn_receipts=wrong) == "I didn't do that."


def test_plain_general_chat_answer_passes_unchanged():
    answer = "TCP is connection-oriented, while UDP is datagram-oriented."
    assert guard_general_chat_action_claim(answer, turn_receipts=[]) == answer


def test_unreceipted_model_claim_is_never_streamed(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(["please think about this"])

    with patch("src.skills.general_chat.generate_chat", return_value="I saved that for you."):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert not any(message.get("type") == "chat_stream" for message in ws.sent_messages)
    assert "I didn't do that." in _chat_messages(ws)
