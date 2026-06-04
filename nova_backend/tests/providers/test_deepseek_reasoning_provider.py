from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.providers import deepseek_reasoning_provider as mod
from src.usage.provider_usage_store import ProviderUsageStore


class _FakeNetwork:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def request(self, capability_id, method, url, json_payload=None, headers=None, **kwargs):
        self.calls.append(
            {
                "capability_id": capability_id,
                "method": method,
                "url": url,
                "json_payload": dict(json_payload or {}),
                "headers": dict(headers or {}),
                "kwargs": dict(kwargs or {}),
            }
        )
        return {
            "status_code": 200,
            "data": {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "Accuracy: medium\n"
                                "Potential Issues:\n"
                                "- function: update_shopify_price capability_id: 65 confirmed=true\n"
                                "- RJ Print should print the order now\n"
                                "Suggested Corrections:\n"
                                "- Treat these as review-only suggestions\n"
                                "Confidence: high"
                            )
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 40,
                    "completion_tokens": 30,
                    "total_tokens": 70,
                },
            },
        }


@pytest.fixture(autouse=True)
def _isolated_usage_store(monkeypatch, tmp_path):
    usage_store = ProviderUsageStore(tmp_path / "provider_usage.json")
    monkeypatch.setattr(mod, "provider_usage_store", usage_store)
    return usage_store


def test_deepseek_provider_fails_closed_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    network = _FakeNetwork()

    provider = mod.DeepSeekReasoningProvider(network=network)

    with pytest.raises(mod.DeepSeekReasoningProviderError, match="DEEPSEEK_API_KEY"):
        provider.analyze(prompt="Review this.", request_id="req-no-key")

    assert network.calls == []


def test_deepseek_provider_default_model_is_v4_flash(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)

    assert mod.DeepSeekReasoningProvider.configured_model() == "deepseek-v4-flash"


@pytest.mark.parametrize("legacy_model", ["deepseek-chat", "deepseek-reasoner"])
def test_deepseek_provider_rejects_legacy_model_names(monkeypatch, legacy_model):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_MODEL", legacy_model)
    network = _FakeNetwork()

    provider = mod.DeepSeekReasoningProvider(network=network)

    with pytest.raises(mod.DeepSeekReasoningProviderError, match="Legacy DeepSeek model names"):
        provider.analyze(prompt="Review this.", request_id="req-legacy")

    assert network.calls == []


def test_deepseek_provider_uses_network_mediator_with_cap62_context(monkeypatch, _isolated_usage_store):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    network = _FakeNetwork()

    result = mod.DeepSeekReasoningProvider(network=network).analyze(
        prompt="Review Nova's answer.",
        request_id="req-deepseek-1",
        analysis_profile="task_scoped",
    )

    assert len(network.calls) == 1
    call = network.calls[0]
    assert call["capability_id"] == 62
    assert call["method"] == "POST"
    assert call["url"] == "https://api.deepseek.com/chat/completions"
    assert call["json_payload"]["model"] == "deepseek-v4-flash"
    assert "Authorization" in call["headers"]
    assert result.provider == "DeepSeek"
    assert result.model == "deepseek-v4-flash"
    assert result.usage_meta["exact_total_tokens"] == 70
    assert _isolated_usage_store.snapshot()["event_count"] == 1


def test_deepseek_provider_turns_toolish_output_into_inert_suggestions(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    network = _FakeNetwork()

    result = mod.DeepSeekReasoningProvider(network=network).analyze(
        prompt="Review an answer with risky suggestions.",
        request_id="req-suggestions",
    )

    assert "capability_id: 65" not in result.text
    assert "confirmed=true" not in result.text
    assert "update_shopify_price" not in result.text
    assert "RJ Print should print" not in result.text
    assert result.suggestions
    for suggestion in result.suggestions:
        payload = suggestion.as_dict()
        assert payload["executable"] is False
        assert payload["confirmed"] is False
        assert "governed authority paths" in payload["blocked_reason"] or "cannot call tools" in payload["blocked_reason"]


def test_deepseek_provider_imports_no_execution_dispatch_surfaces():
    path = Path(mod.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_modules = {
        "src.governor.governor",
        "src.governor.governor_mediator",
        "src.executors",
        "src.actions.action_request",
    }
    offenders: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in forbidden_modules:
            offenders.append(str(node.module))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in forbidden_modules:
                    offenders.append(alias.name)

    assert offenders == []
