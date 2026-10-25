from __future__ import annotations

import pytest
from src.connectors import shopify_connector
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.providers.deepseek_reasoning_provider import (
    DeepSeekReasoningProvider,
    DeepSeekReasoningProviderError,
)
from src.providers.openai_responses_lane import OpenAIResponsesLane, OpenAIResponsesLaneError


class _NoNetwork:
    def request(self, *_args, **_kwargs):
        raise AssertionError("trial profile must not attempt provider network access")


def test_trial_profile_disables_openai_plan_even_when_configured(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setenv("OPENAI_API_KEY", "configured-test-key")

    plan = OpenAIResponsesLane(network=_NoNetwork()).plan_for_openclaw_fallback()

    assert plan["allowed"] is False
    assert plan["reason"] == "OpenAI isn't available in this trial version."


def test_trial_profile_blocks_direct_openai_execution_before_network(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setenv("OPENAI_API_KEY", "configured-test-key")

    with pytest.raises(OpenAIResponsesLaneError, match="isn't available in this trial version"):
        OpenAIResponsesLane(network=_NoNetwork()).summarize_task_report(
            prompt="private prompt",
            system_prompt="system",
            model="gpt-5.4-mini",
            request_id="trial-test",
        )


def test_trial_profile_blocks_direct_deepseek_execution_before_network(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "configured-test-key")

    with pytest.raises(DeepSeekReasoningProviderError, match="isn't available in this trial version"):
        DeepSeekReasoningProvider(network=_NoNetwork()).analyze(prompt="private prompt")


def test_trial_profile_blocks_deepseek_bridge_by_profile_not_key(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "configured-test-key")

    response = DeepSeekBridge().analyze("private prompt", [])

    assert response == "External reasoning isn't available in this trial version."


def test_trial_profile_does_not_bootstrap_shopify_even_when_configured(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    monkeypatch.setenv("NOVA_SHOPIFY_SHOP_DOMAIN", "example.myshopify.com")
    monkeypatch.setenv("NOVA_SHOPIFY_ACCESS_TOKEN", "configured-test-token")
    installed = []
    monkeypatch.setattr(shopify_connector, "set_shopify_connector", installed.append)

    shopify_connector.bootstrap_shopify_connector()

    assert installed == []
