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


@pytest.mark.parametrize(
    "followup, expected",
    [
        ("What are other sources saying?", "no additional sources were retrieved"),
        ("What do the other sources say?", "no additional sources were retrieved"),
        ("Are those sources in agreement?", "can't say whether sources agree"),
    ],
)
def test_failed_news_search_blocks_source_reporting_paraphrase(monkeypatch, followup, expected):
    _disable_unrelated_gate(monkeypatch)

    async def _invoke(*args, **kwargs):
        return _failed_search()

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            followup,
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Source-reporting paraphrase must not reach GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    final = _chat_messages(ws)[-1]
    assert expected in final.lower()


def test_explicit_topic_switch_retires_prior_news_evidence(monkeypatch):
    _disable_unrelated_gate(monkeypatch)

    async def _invoke(*args, **kwargs):
        return _failed_search()

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "Tell me more about photosynthesis.",
            "Tell me more about that.",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=[
            "Photosynthesis converts light energy into chemical energy.",
            "Plants use that chemical energy to make sugars.",
        ],
    ) as model:
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert model.call_count == 2
    assert "Plants use that chemical energy" in _chat_messages(ws)[-1]
    assert "retrieval did not succeed" not in _chat_messages(ws)[-1]


def test_generic_clarification_preserves_failed_news_evidence(monkeypatch):
    _disable_unrelated_gate(monkeypatch)

    async def _invoke(*args, **kwargs):
        return _failed_search()

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(
        [
            "What's happening with Russia?",
            "Can you elaborate?",
            "What are other sources saying?",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="I can only offer unverified general context.",
    ) as model:
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert model.call_count == 1
    assert "no additional sources were retrieved" in _chat_messages(ws)[-1].lower()


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



def test_unavailable_news_does_not_hijack_a_new_project_topic(monkeypatch):
    async def unavailable_news(*_args, **_kwargs):
        return None, ActionResult.failure(
            "News unavailable right now.",
            capability_id=56,
            data={"widget": {"type": "news", "items": [], "categories": {"world": []}}},
        )

    monkeypatch.setattr(brain_server, "invoke_governed_text_command", unavailable_news)
    prompts = [
        "Show me the news.",
        "Tell me more about the first story.",
        "What do I have coming up?",
        "Project Cedar has seven amber tags.",
        "How many tags does it have?",
        "Actually, I meant eight tags, not seven.",
        "Tell me a joke.",
        "Back to Cedar, how many tags does it have now?",
    ]
    ws = _ScriptedWebSocket([
        {"type": "chat", "text": text, "turn_id": str(i)}
        for i, text in enumerate(prompts)
    ])
    with patch("src.skills.general_chat.generate_chat", return_value=None):
        asyncio.run(brain_server.websocket_endpoint(ws))

    replies = {
        frame.get("turn_id"): frame["message"]
        for frame in ws.sent_messages if frame["type"] == "chat"
    }
    assert "headline" in replies["1"].lower()
    assert "What you have next:" in replies["2"]
    for turn in ("4", "5", "7"):
        assert "headline" not in replies[turn].lower(), replies[turn]



async def _sourced_news(*_args, **_kwargs):
    return None, ActionResult.ok(
        "One sourced headline.",
        capability_id=56,
        data={"widget": {"type": "news", "items": [{
            "title": "Synthetic ocean research headline",
            "source": "Synthetic newsroom",
            "url": "https://example.test/ocean",
            "summary": "Researchers published a survey.",
        }]}},
    )


@pytest.mark.parametrize("followup", ["Why does that matter?", "Tell me more about ocean research"])
def test_selected_headline_followup_survives_silent_refresh(monkeypatch, followup):
    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _sourced_news)
    ws = _ScriptedWebSocket([
        "news",
        "Why is the first story important?",
        {"type": "chat", "text": "news", "silent_widget_refresh": True},
        followup,
    ])
    with patch("src.skills.general_chat.generate_chat", return_value=None) as generate:
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert "Synthetic ocean research headline" in _chat_messages(ws)[-1]
    assert "Synthetic newsroom" in _chat_messages(ws)[-1]
    generate.assert_not_called()



@pytest.mark.parametrize("query", ["Why does Cedar matter?", "Tell me more about Cedar", "Why is Cedar important?", "Why does Cedar have seven tags?"])
def test_explicit_new_subject_does_not_use_selected_headline(monkeypatch, query):
    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _sourced_news)
    ws = _ScriptedWebSocket(["news", "Why is the first story important?", query])
    with patch("src.skills.general_chat.generate_chat", return_value="Cedar answer.") as generate:
        asyncio.run(brain_server.websocket_endpoint(ws))

    replies = _chat_messages(ws)
    assert "Synthetic ocean research headline" in replies[-2]
    assert replies[-1] == "Cedar answer."
    generate.assert_called_once()


@pytest.mark.parametrize("change_topic", [False, True])
def test_legacy_more_only_uses_a_current_story_index(monkeypatch, change_topic):
    calls = []

    async def summarize_story(_governor, capability_id, params, **_kwargs):
        assert capability_id == 49
        calls.append(dict(params))
        return ActionResult.ok("Story action result.", capability_id=49, data={"story_index": 1})

    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _sourced_news)
    monkeypatch.setattr(brain_server, "invoke_governed_capability", summarize_story)
    prompts = ["news", "summarize story 1"]
    if change_topic:
        prompts.append("Project Cedar has seven tags.")
    prompts.append("more")
    ws = _ScriptedWebSocket(prompts)
    with patch("src.skills.general_chat.generate_chat", return_value="Ordinary chat."):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls and len(calls) == (1 if change_topic else 2)
    if not change_topic:
        assert calls[-1]["action"] == "story_page_summary"
