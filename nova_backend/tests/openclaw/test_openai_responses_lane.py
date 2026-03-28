import importlib

import pytest

from src.providers.openai_responses_lane import OpenAIResponsesLane
from src.settings.runtime_settings_store import RuntimeSettingsStore
from src.usage.provider_usage_store import ProviderUsageStore


def _install_stores(monkeypatch, tmp_path):
    settings_store = RuntimeSettingsStore(tmp_path / "runtime_settings.json")
    usage_store = ProviderUsageStore(
        tmp_path / "provider_usage.json",
        daily_token_budget=4000,
        warning_ratio=0.8,
    )
    lane_module = importlib.import_module("src.providers.openai_responses_lane")
    monkeypatch.setattr(lane_module, "runtime_settings_store", settings_store)
    monkeypatch.setattr(lane_module, "provider_usage_store", usage_store)
    return settings_store, usage_store


def test_openai_lane_blocks_without_key(monkeypatch, tmp_path):
    settings_store, _usage_store = _install_stores(monkeypatch, tmp_path)
    settings_store.set_permission("metered_openai_enabled", True, source="test")
    settings_store.set_provider_policy(routing_mode="budgeted_fallback", source="test")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    lane = OpenAIResponsesLane(network=object())
    plan = lane.plan_for_openclaw_fallback()

    assert plan["allowed"] is False
    assert "OPENAI_API_KEY" in plan["reason"]


def test_openai_lane_allows_budgeted_fallback_when_ready(monkeypatch, tmp_path):
    settings_store, _usage_store = _install_stores(monkeypatch, tmp_path)
    settings_store.set_permission("metered_openai_enabled", True, source="test")
    settings_store.set_provider_policy(
        routing_mode="budgeted_fallback",
        preferred_openai_model="gpt-5.4-mini",
        source="test",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    lane = OpenAIResponsesLane(network=object())
    plan = lane.plan_for_openclaw_fallback()

    assert plan["allowed"] is True
    assert plan["preferred_model"] == "gpt-5.4-mini"


def test_openai_lane_records_usage_from_response_payload(monkeypatch, tmp_path):
    settings_store, usage_store = _install_stores(monkeypatch, tmp_path)
    settings_store.set_permission("metered_openai_enabled", True, source="test")
    settings_store.set_provider_policy(
        routing_mode="budgeted_fallback",
        preferred_openai_model="gpt-5.4-mini",
        source="test",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    class _FakeNetwork:
        def request(self, capability_id, method, url, json_payload=None, headers=None, **_kwargs):
            assert capability_id == 62
            assert method == "POST"
            assert url == "https://api.openai.com/v1/responses"
            assert "Authorization" in (headers or {})
            assert json_payload["model"] == "gpt-5.4-mini"
            return {
                "status_code": 200,
                "data": {
                    "output": [
                        {
                            "content": [
                                {"type": "output_text", "text": "Here is the final task report."}
                            ]
                        }
                    ],
                    "usage": {
                        "input_tokens": 120,
                        "output_tokens": 40,
                        "total_tokens": 160,
                    },
                },
            }

    lane = OpenAIResponsesLane(network=_FakeNetwork())
    result = lane.summarize_task_report(
        prompt="Summarize the morning context.",
        system_prompt="You are Nova.",
        model="gpt-5.4-mini",
        request_id="req-openai-1",
        task_label="Morning Brief",
    )

    assert result["text"] == "Here is the final task report."
    assert result["usage_meta"]["route"] == "openai_metered"
    assert result["usage_meta"]["exact_total_tokens"] == 160
    assert result["usage_meta"]["estimated_cost_usd"] > 0
    assert usage_store.snapshot()["event_count"] == 1
