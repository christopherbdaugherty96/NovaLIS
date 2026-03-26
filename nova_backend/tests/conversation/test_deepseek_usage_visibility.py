from __future__ import annotations

from src.conversation.deepseek_bridge import DeepSeekBridge
from src.usage.provider_usage_store import ProviderUsageStore


def test_deepseek_bridge_records_usage_event(monkeypatch, tmp_path):
    import src.conversation.deepseek_bridge as mod

    usage_store = ProviderUsageStore(tmp_path / "provider_usage.json")
    monkeypatch.setattr(mod, "provider_usage_store", usage_store)
    monkeypatch.setattr(
        mod.llm_gateway,
        "generate_chat",
        lambda *args, **kwargs: "Core answer: Version locking preserves trusted model behavior.",
    )

    result = DeepSeekBridge().analyze(
        "Why does version locking matter?",
        [],
        analysis_profile="deep_reason",
    )

    snapshot = usage_store.snapshot()
    assert "Core answer:" in result
    assert snapshot["event_count"] == 1
    assert snapshot["recent_events"][0]["analysis_profile"] == "deep_reason"
