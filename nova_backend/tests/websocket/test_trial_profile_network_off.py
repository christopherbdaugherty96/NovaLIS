from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from src.governor.capability_registry import CapabilityRegistry
from src.governor.governor_mediator import GovernorMediator, Invocation
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

TRIAL_UNAVAILABLE_MESSAGE = (
    "Web search and weather are not available in this trial version."
)
TRIAL_NO_LIVE_DATA_INSTRUCTION = (
    "You have no internet or live data in this version. If asked about current events, "
    "prices, scores, news or weather, say you can't check them here."
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
        "how are you doing today?",
        "how's your day going today?",
        "how do I tell my boss I'm sick today",
        "what should I cook for dinner today?",
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
    assert model_prompts, _chat_messages(ws)
    assert any("Local trial chat reply." in message for message in _chat_messages(ws))
    assert not any(TRIAL_UNAVAILABLE_MESSAGE in message for message in _chat_messages(ws))


@pytest.mark.parametrize(
    "text",
    (
        "weather",
        "weather update",
        "current weather",
        "weather in Boston",
        "What's the weather tomorrow?",
        "Search the web for the best pizza near me",
        "Google the best pizza near me",
        "Give me the latest on quantum computing",
        "Find current information about quantum computing",
        "Latest quantum computing news",
        "Did quantum computing stocks rise today?",
        "What's the price of Bitcoin today?",
        "What happened today?",
        "What changed since yesterday?",
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


@pytest.mark.parametrize(
    "text",
    (
        "what's new in AI today?",
        "What's going on with AI today?",
        "What's happening today?",
    ),
)
def test_trial_current_info_chat_gets_no_live_data_instruction(monkeypatch, text):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    _disable_session_gate(monkeypatch)
    network_calls = _forbid_network(monkeypatch)
    model_messages: list[dict] = []

    def _local_chat(_prompt: str, **kwargs):
        model_messages.extend(kwargs.get("messages") or [])
        return "Local current-info chat reply."

    ws = _ScriptedWebSocket([text])
    with patch("src.skills.general_chat.generate_chat", side_effect=_local_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert network_calls == []
    assert any(TRIAL_NO_LIVE_DATA_INSTRUCTION in row.get("content", "") for row in model_messages)
    assert any("Local current-info chat reply." in message for message in _chat_messages(ws))


def test_default_general_chat_omits_trial_no_live_data_instruction(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    _disable_session_gate(monkeypatch)
    model_messages: list[dict] = []

    def _local_chat(_prompt: str, **kwargs):
        model_messages.extend(kwargs.get("messages") or [])
        return "Default local chat reply."

    ws = _ScriptedWebSocket(["Explain photosynthesis simply"])
    with patch("src.skills.general_chat.generate_chat", side_effect=_local_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert model_messages
    assert not any(TRIAL_NO_LIVE_DATA_INSTRUCTION in row.get("content", "") for row in model_messages)


@pytest.mark.parametrize(
    ("text", "capability_id"),
    (
        ("What's on today?", 57),
        ("What's the news today?", 56),
        ("Why is service status down?", 48),
    ),
)
def test_trial_broad_current_info_guard_preserves_specific_governed_intents(
    monkeypatch, text, capability_id
):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")

    result = GovernorMediator.parse_governed_invocation(text)

    assert isinstance(result, Invocation)
    assert result.capability_id == capability_id


def test_trial_personal_appointments_question_stays_behind_schedule_truth_guard(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    _disable_session_gate(monkeypatch)
    network_calls = _forbid_network(monkeypatch)
    ws = _ScriptedWebSocket(["What appointments do I have happening today?"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("schedule questions must not reach the model"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert network_calls == []
    messages = _chat_messages(ws)
    assert any("don't have your calendar loaded" in message.lower() for message in messages)
    assert any("won't guess" in message.lower() for message in messages)


def test_trial_profile_disables_search_and_weather_only(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    trial = CapabilityRegistry()
    assert not trial.is_enabled(16)
    assert not trial.is_enabled(55)

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    default = CapabilityRegistry()
    assert default.is_enabled(16)
    assert default.is_enabled(55)

