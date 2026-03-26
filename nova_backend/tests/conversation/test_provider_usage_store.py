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
