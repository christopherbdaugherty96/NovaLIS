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
    "claim",
    [
        "I saved that for you.",
        "I'll remember that.",
        "I forgot that memory.",
        "I deleted it.",
        "I set a reminder.",
        "I cancelled the reminder.",
        "I completed the task.",
        "I emailed the update.",
        "I sent the update.",
        "I scheduled it.",
        "Yes, I emailed your team this morning.",
        "I've deleted your sister's birthday from memory.",
        "Done! Your reminder is set for 3pm.",
        "Got it, I'll remind you tomorrow at 9.",
        "I've added it to your calendar.",
        "I've forgotten that.",
        "I removed that from your memories.",
        "Sure, I sent your email to John.",
        "All set - reminder created.",
        "Done. I've saved that, set the reminder, and emailed your team.",
    ],
)
def test_general_chat_action_claim_is_always_blocked(claim):
    guarded = guard_general_chat_action_claim(claim, turn_receipts=[])
    assert guarded == "I didn't do that."

    fake_matching_receipt = [
        {"event_type": "ACTION_COMPLETED", "action_kind": "sent", "success": True}
    ]
    assert (
        guard_general_chat_action_claim(claim, turn_receipts=fake_matching_receipt)
        == "I didn't do that."
    )


def test_plain_general_chat_answer_passes_unchanged():
    answer = "TCP is connection-oriented, while UDP is datagram-oriented."
    assert guard_general_chat_action_claim(answer, turn_receipts=[]) == answer


def test_instructional_remember_phrase_is_not_an_action_claim():
    answer = "Remember that TCP retransmits lost packets."
    assert guard_general_chat_action_claim(answer, turn_receipts=[]) == answer


@pytest.mark.parametrize(
    "answer",
    [
        "Rewrite this politely: I sent the report yesterday.",
        "In this example, I set x to 3.",
        'The sentence "I emailed your team" is in the first person.',
        "If I scheduled it tomorrow, the event would conflict.",
    ],
)
def test_quoted_hypothetical_and_explanatory_action_language_passes(answer):
    assert guard_general_chat_action_claim(answer, turn_receipts=[]) == answer


@pytest.mark.parametrize(
    "claim",
    [
        "The reminder has been set for 3 PM.",
        "Done - the email was sent.",
        "Reminder created for tomorrow.",
        "Your task has been completed.",
        "The memory was deleted.",
        "All set - your appointment was scheduled.",
    ],
)
def test_passive_or_subjectless_action_claim_is_blocked(claim):
    assert guard_general_chat_action_claim(claim, turn_receipts=[]) == "I didn't do that."


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
