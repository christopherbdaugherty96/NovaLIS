from __future__ import annotations

import asyncio
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


def _failed_search() -> ActionResult:
    return ActionResult.failure(
        "I'm checking online. I couldn't complete the search due to a network issue.",
        capability_id=16,
        authority_class="read_only_network",
    )


def _successful_search(query: str, source: str = "Reuters") -> ActionResult:
    return ActionResult.ok(
        f"Retrieved one result for {query}.",
        capability_id=16,
        authority_class="read_only_network",
        data={
            "widget": {
                "type": "search",
                "data": {
                    "query": query,
                    "results": [
                        {
                            "title": f"Verified report about {query}",
                            "source": source,
                            "url": "https://example.test/report",
                            "description": "A retrieved source summary.",
                        }
                    ],
                },
            }
        },
    )


def test_failed_news_search_blocks_unsupported_followup_claims(monkeypatch):
    _disable_unrelated_gate(monkeypatch)

    async def _invoke(*args, **kwargs):
        return _failed_search()

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "Tell me more about that.",
            "What are other sources reporting?",
            "Do those sources agree?",
            "Explain why this matters.",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Failed-retrieval follow-ups must not reach GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat = _chat_messages(ws)
    assert any("couldn't complete the search" in message for message in chat)
    assert any("can't add verified current details" in message for message in chat)
    assert any("no additional sources were retrieved" in message.lower() for message in chat)
    assert any("can't say whether sources agree" in message.lower() for message in chat)
    assert any("general background" in message.lower() for message in chat)
    assert not any("Reuters" in message or "BBC" in message for message in chat)


def test_failed_news_evidence_does_not_capture_explicit_unrelated_topic(monkeypatch):
    _disable_unrelated_gate(monkeypatch)

    async def _invoke(*args, **kwargs):
        return _failed_search()

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "Tell me more about photosynthesis.",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="Photosynthesis converts light energy into chemical energy.",
    ) as model:
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert model.call_count == 1
    assert any("Photosynthesis converts" in message for message in _chat_messages(ws))


def test_successful_retrieval_replaces_failure_with_actual_source_evidence(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    results = [_failed_search(), _successful_search("Ukraine", "Reuters")]

    async def _invoke(*args, **kwargs):
        return results.pop(0)

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "What's happening with Ukraine?",
            "What are other sources reporting?",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Source follow-up must use retrieved evidence"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    final = _chat_messages(ws)[-1]
    assert "Reuters" in final
    assert "Verified report about Ukraine" in final
    assert "no additional sources were retrieved" not in final.lower()


def test_new_failed_topic_does_not_reuse_stale_successful_sources(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    results = [_successful_search("Russia", "Reuters"), _failed_search()]

    async def _invoke(*args, **kwargs):
        return results.pop(0)

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "What's happening with Mars?",
            "Do those sources agree?",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Failed-retrieval comparison must not reach GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    final = _chat_messages(ws)[-1]
    assert "can't say whether sources agree" in final.lower()
    assert "Reuters" not in final
