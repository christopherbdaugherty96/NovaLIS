"""Slice 0 red baselines promoted to Slice 3A provider-off regressions."""

from __future__ import annotations

import pytest
from src.conversation import deepseek_bridge as bridge_mod
from src.providers import deepseek_reasoning_provider as provider_mod
from src.settings.runtime_settings_store import runtime_settings_store
from src.usage.provider_usage_store import ProviderUsageStore


class _TransportSpy:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def request(self, capability_id, method, url, **kwargs):
        self.calls.append(
            {
                "capability_id": capability_id,
                "method": method,
                "url": url,
                "kwargs": dict(kwargs),
            }
        )
        return {
            "status_code": 200,
            "data": {
                "choices": [{"message": {"content": "Bounded advisory response."}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        }


def test_red_baseline_provider_off_does_not_reach_deepseek_transport(monkeypatch, tmp_path):
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "slice0-fake-key")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    monkeypatch.setattr(runtime_settings_store, "is_permission_enabled", lambda _name: False)
    monkeypatch.setattr(
        provider_mod,
        "provider_usage_store",
        ProviderUsageStore(tmp_path / "provider_usage.json"),
    )
    monkeypatch.setattr(provider_mod, "_check_budget_gate", lambda **_kwargs: "normal")
    monkeypatch.setattr(provider_mod, "_log_budget_event", lambda **_kwargs: "normal")
    transport = _TransportSpy()

    with pytest.raises(
        provider_mod.DeepSeekReasoningProviderError,
        match="paused in Settings",
    ):
        provider_mod.DeepSeekReasoningProvider(network=transport).analyze(
            prompt="Private Slice 0 prompt",
            request_id="slice0-provider-off",
        )

    assert transport.calls == []


def test_red_baseline_provider_off_stops_bridge_before_provider(monkeypatch):
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    monkeypatch.setattr(runtime_settings_store, "is_permission_enabled", lambda _name: False)
    monkeypatch.setattr(
        bridge_mod.CapabilityRegistry,
        "is_enabled",
        lambda _self, capability_id: capability_id == 62,
    )
    provider_calls: list[dict] = []

    def _provider_call(_self, **kwargs):
        provider_calls.append(dict(kwargs))
        return type(
            "Result",
            (),
            {"text": "Analysis complete.", "route": "slice0-provider-spy"},
        )()

    monkeypatch.setattr(bridge_mod.DeepSeekReasoningProvider, "analyze", _provider_call)

    result = bridge_mod.DeepSeekBridge().analyze(
        "Private Slice 0 prompt",
        [],
        analysis_profile="task_scoped",
    )

    assert provider_calls == []
    assert result == "External reasoning is paused in Settings."
