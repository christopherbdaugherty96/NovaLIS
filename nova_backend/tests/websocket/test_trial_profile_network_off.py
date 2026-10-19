from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from src.governor.capability_registry import CapabilityRegistry
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket


TRIAL_UNAVAILABLE_MESSAGE = (
    "Web search and weather are not available in this trial version."
)


def _disable_session_gate(monkeypatch) -> None:
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )


def _forbid_network(monkeypatch) -> list[dict]:
    calls: list[dict] = []

    def _network_spy(self, **kwargs):
        del self
        calls.append(dict(kwargs))
        raise AssertionError("trial-profile chat must not reach the network")

    monkeypatch.setattr(
        "src.governor.network_mediator.NetworkMediator.request",
        _network_spy,
    )
    return calls


@pytest.mark.parametrize(
    "text",
    (
        "hey how are you doing today?",
        "what's up today",
        "how should I plan my day today",
    ),
)
def test_trial_recency_small_talk_stays_in_local_chat(monkeypatch, text):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    _disable_session_gate(monkeypatch)
    network_calls = _forbid_network(monkeypatch)
    model_prompts: list[str] = []

    def _local_chat(prompt: str, **_kwargs):
        model_prompts.append(prompt)
        return "Local trial chat reply."

    ws = _ScriptedWebSocket([text])
    with patch("src.skills.general_chat.generate_chat", side_effect=_local_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert network_calls == []
    assert model_prompts
    assert any("Local trial chat reply." in message for message in _chat_messages(ws))
    assert not any(TRIAL_UNAVAILABLE_MESSAGE in message for message in _chat_messages(ws))


@pytest.mark.parametrize(
    "text",
    (
        "What's the weather tomorrow?",
        "Search the web for the best pizza near me",
        "Google the best pizza near me",
    ),
)
def test_trial_explicit_network_request_is_honestly_unavailable(monkeypatch, text):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    _disable_session_gate(monkeypatch)
    network_calls = _forbid_network(monkeypatch)
    ws = _ScriptedWebSocket([text])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model must not answer disabled search or weather"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert network_calls == []
    messages = _chat_messages(ws)
    assert any(TRIAL_UNAVAILABLE_MESSAGE in message for message in messages)
    assert not any("receipt" in message.lower() for message in messages)


def test_trial_profile_disables_search_and_weather_only(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    trial = CapabilityRegistry()
    assert not trial.is_enabled(16)
    assert not trial.is_enabled(55)

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    default = CapabilityRegistry()
    assert default.is_enabled(16)
    assert default.is_enabled(55)

