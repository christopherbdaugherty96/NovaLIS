from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


async def _no_governed_result(*args, **kwargs):
    return None, None


def _disable_unrelated_routes(monkeypatch) -> None:
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "invoke_governed_text_command",
        _no_governed_result,
    )
    monkeypatch.setattr(
        "src.connectors.shopify_connector.get_shopify_connector",
        lambda: None,
    )


class _SourcedAwarenessBrief:
    greeting = "Good morning"

    def to_dict(self) -> dict:
        return {
            "type": "awareness_brief",
            "greeting": self.greeting,
            "sections": [
                {
                    "key": "weather",
                    "title": "Weather",
                    "items": ["Distinctive sourced fact: rain starts after 3 PM."],
                    "status": "ok",
                    "source": "weather",
                },
                {
                    "key": "news",
                    "title": "News",
                    "items": ["Secondary sourced fact."],
                    "status": "ok",
                    "source": "news",
                },
            ],
            "available_count": 2,
            "total_count": 2,
        }


class _DecisionAwarenessBrief:
    greeting = "Good morning"

    def to_dict(self) -> dict:
        return {
            "type": "awareness_brief",
            "greeting": self.greeting,
            "sections": [
                {
                    "key": "weather",
                    "title": "Weather",
                    "items": ["Distinctive weather fact."],
                    "status": "ok",
                    "source": "weather",
                },
                {
                    "key": "auralis_today",
                    "title": "Auralis Today",
                    "items": [
                        "Store live.",
                        "Owner blocker: Meta business verification",
                        "Best move: Open Meta Business Suite and click Verify account",
                        "Watch: July 9 Google Merchant review",
                    ],
                    "status": "ok",
                    "source": "auralis:inputs_partial",
                },
            ],
            "available_count": 2,
            "total_count": 2,
        }


def test_daily_awareness_request_routes_at_websocket_boundary_and_grounds_followup(monkeypatch):
    _disable_unrelated_routes(monkeypatch)
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(
        [
            "Give me my Daily Awareness Brief.",
            "What matters most?",
        ]
    )

    with (
        patch(
            "src.brief.awareness_brief.compose_awareness_brief",
            return_value=_SourcedAwarenessBrief(),
        ),
        patch(
            "src.skills.general_chat.generate_chat",
            side_effect=AssertionError("GeneralChat must not run for the brief or its follow-up"),
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert any(message.get("type") == "awareness_brief" for message in ws.sent_messages)
    chat_messages = _chat_messages(ws)
    assert any("daily awareness brief is ready" in message.lower() for message in chat_messages)
    assert any("Distinctive sourced fact: rain starts after 3 PM." in message for message in chat_messages)
    assert any("source: weather" in message for message in chat_messages)
    assert not any("@auralis_digital" in message for message in chat_messages)


def test_active_awareness_decision_followup_is_grounded_at_websocket_boundary(monkeypatch):
    _disable_unrelated_routes(monkeypatch)
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(
        [
            "Give me my Daily Awareness Brief.",
            "What decision requires my attention?",
        ]
    )

    with (
        patch(
            "src.brief.awareness_brief.compose_awareness_brief",
            return_value=_DecisionAwarenessBrief(),
        ),
        patch(
            "src.skills.general_chat.generate_chat",
            side_effect=AssertionError("GeneralChat must not run for the decision follow-up"),
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    decision_answer = next(
        message for message in chat_messages if "Displayed Auralis Today decision items:" in message
    )
    assert "Owner blocker: Meta business verification" in decision_answer
    assert "Best move: Open Meta Business Suite and click Verify account" in decision_answer
    assert "Watch: July 9 Google Merchant review" not in decision_answer
    assert "source: auralis:inputs_partial" in decision_answer
    assert "not approval or permission to act" in decision_answer


def test_auralis_today_request_routes_and_degrades_honestly_without_inputs(monkeypatch):
    _disable_unrelated_routes(monkeypatch)
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    ws = _ScriptedWebSocket(["Show me Auralis Today"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("GeneralChat must not run for Auralis Today"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert any(message.get("type") == "awareness_brief" for message in ws.sent_messages)
    chat_messages = _chat_messages(ws)
    assert any("trusted Auralis inputs are not available" in message for message in chat_messages)
    assert any("I won't invent business context" in message for message in chat_messages)
    assert not any("@auralis_digital" in message for message in chat_messages)


def test_ambiguous_surface_request_is_clarified_before_general_chat(monkeypatch):
    _disable_unrelated_routes(monkeypatch)
    ws = _ScriptedWebSocket(["Give me the Auralis Today report"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("GeneralChat must not run for an ambiguous surface request"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert any("Which one did you mean?" in message for message in _chat_messages(ws))


def test_surface_mentions_stay_in_general_chat(monkeypatch):
    _disable_unrelated_routes(monkeypatch)
    ws = _ScriptedWebSocket(
        [
            "I mentioned Auralis Today in the meeting",
            "Let's discuss the awareness brief design",
        ]
    )
    generated_prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        generated_prompts.append(prompt)
        return "Normal conversational response."

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(generated_prompts) == 2
    assert _chat_messages(ws).count("Normal conversational response.") == 2
