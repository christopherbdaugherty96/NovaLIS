from __future__ import annotations

from src.usage.provider_usage_store import ProviderUsageStore


def test_provider_usage_store_records_estimated_reasoning_usage(tmp_path):
    store = ProviderUsageStore(tmp_path / "provider_usage.json", daily_token_budget=1000, warning_ratio=0.8)

    snapshot = store.record_reasoning_event(
        provider="DeepSeek reasoning lane",
        route="DeepSeekBridge -> llm_gateway",
        analysis_profile="task_scoped",
        prompt_text="Explain this error and tell me what to try next.",
        response_text="The import path is wrong. Try checking your module root first.",
    )

    assert snapshot["event_count"] == 1
    assert snapshot["estimated_total_tokens"] > 0
    assert snapshot["budget_state"] == "normal"
    assert snapshot["recent_events"][0]["provider"] == "DeepSeek reasoning lane"


def test_provider_usage_store_enters_warning_state_when_usage_is_high(tmp_path):
    store = ProviderUsageStore(tmp_path / "provider_usage.json", daily_token_budget=50, warning_ratio=0.5)

    snapshot = store.record_reasoning_event(
        provider="DeepSeek reasoning lane",
        route="DeepSeekBridge -> llm_gateway",
        analysis_profile="task_scoped",
        prompt_text="x" * 120,
        response_text="y" * 120,
    )

    assert snapshot["budget_state"] in {"warning", "limit"}
    assert snapshot["budget_state_label"] in {"Budget low", "Budget reached"}


def test_provider_usage_store_can_record_exact_usage_and_cost(tmp_path):
    store = ProviderUsageStore(tmp_path / "provider_usage.json", daily_token_budget=1000, warning_ratio=0.8)

    snapshot = store.record_reasoning_event(
        provider="OpenAI",
        route="Nova -> OpenAI optional lane",
        analysis_profile="coding_agent",
        prompt_text="help me finish this feature",
        response_text="here is the patch plan",
        exact_usage_available=True,
        exact_input_tokens=120,
        exact_output_tokens=40,
        estimated_cost_usd=0.0184,
    )

    assert snapshot["exact_total_tokens"] == 160
    assert snapshot["estimated_cost_usd"] == 0.0184
    assert snapshot["cost_tracking_label"] == "Estimated cost visibility is live for supported providers"
    assert snapshot["recent_events"][0]["usage_measurement"] == "exact"
