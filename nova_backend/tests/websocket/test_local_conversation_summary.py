from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


def _disable_unrelated_gate(monkeypatch) -> None:
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )


@pytest.mark.parametrize(
    "phrase",
    [
        "Summarize our discussion.",
        "Recap what we discussed.",
        "Summarize our conversation so far.",
    ],
)
def test_conversation_summary_is_local_and_does_not_promote_model_text(monkeypatch, phrase):
    _disable_unrelated_gate(monkeypatch)
    invoked: list[int] = []

    async def _invoke(_governor, capability_id, params, **kwargs):
        invoked.append(capability_id)
        return ActionResult.failure("External research must not run.", capability_id=capability_id)

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(["Photosynthesis is interesting.", phrase])

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="Reuters verified a fabricated photosynthesis claim.",
    ) as model:
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert model.call_count == 1
    assert 48 not in invoked
    summary = _chat_messages(ws)[-1]
    assert "history currently available" in summary.lower()
    assert "photosynthesis" in summary.lower()
    assert "Reuters verified" not in summary
    assert "not independently verified" in summary.lower()


def test_conversation_summary_without_history_reports_insufficient_context(monkeypatch):
    _disable_unrelated_gate(monkeypatch)

    async def _must_not_invoke(*args, **kwargs):
        raise AssertionError("Empty local summary must not invoke a capability.")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _must_not_invoke)
    ws = _ScriptedWebSocket(["Summarize our discussion."])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Empty local summary must not invoke GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert "do not have enough prior conversation" in _chat_messages(ws)[-1].lower()


def test_failed_news_retrieval_is_preserved_in_local_summary(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    invoked: list[int] = []

    async def _invoke(_governor, capability_id, params, **kwargs):
        invoked.append(capability_id)
        if capability_id == 16:
            return ActionResult.failure(
                "I'm checking online. I couldn't complete the search due to a network issue.",
                capability_id=16,
                authority_class="read_only_network",
            )
        return ActionResult.failure("Unexpected capability.", capability_id=capability_id)

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "Tell me more about that.",
            "What are other sources reporting?",
            "Do those sources agree?",
            "Explain why this matters.",
            "Summarize our discussion.",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Grounded failure workflow must not invoke GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert invoked == [16]
    summary = _chat_messages(ws)[-1].lower()
    assert "russia" in summary
    assert "retrieval failed" in summary
    assert "no current sources were retrieved" in summary
    assert "source agreement" in summary
    assert "unverified" in summary
    assert "\n- - " not in summary


def test_seven_turn_news_workflow_ends_in_local_evidence_aware_summary(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    invoked: list[int] = []

    async def _invoke(_governor, capability_id, params, **kwargs):
        invoked.append(capability_id)
        if capability_id == 16:
            return ActionResult.failure(
                "I'm checking online. I couldn't complete the search due to a network issue.",
                capability_id=16,
                authority_class="read_only_network",
            )
        return ActionResult.failure("Unexpected capability.", capability_id=capability_id)

    async def _unavailable_read(*args, **kwargs):
        return None, None

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _unavailable_read)

    brief = SimpleNamespace(
        text="Weather unavailable. News unavailable. Calendar unavailable.",
        run=SimpleNamespace(run_id="run_summary_acceptance", outputs={}),
        receipt=SimpleNamespace(
            receipt_id="receipt_summary_acceptance",
            graph_name="daily_brief",
            sources_consulted=frozenset({"session_state"}),
        ),
        has_content=False,
    )
    ws = _ScriptedWebSocket(
        [
            "Give me my daily briefing.",
            "What's happening with Russia?",
            "Tell me more about that.",
            "What are other sources reporting?",
            "Do those sources agree?",
            "Explain why this matters.",
            "Summarize our discussion.",
        ]
    )

    with (
        patch(
            "src.conversation.morning_brief_handler.compose_governed_morning_brief",
            return_value=brief,
        ),
        patch(
            "src.skills.general_chat.generate_chat",
            side_effect=AssertionError("The governed seven-turn workflow must not use GeneralChat"),
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert invoked == [16]
    summary = _chat_messages(ws)[-1].lower()
    assert "history currently available" in summary
    assert "russia" in summary
    assert "retrieval failed" in summary
    assert "no current sources were retrieved" in summary
    assert "source agreement" in summary
    assert "unverified" in summary
    assert "\n- - " not in summary
