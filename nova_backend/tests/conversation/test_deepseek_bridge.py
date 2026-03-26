from __future__ import annotations

import pytest

from src.conversation import prompts
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.usage.provider_usage_store import ProviderUsageStore


@pytest.fixture(autouse=True)
def _isolated_usage_store(monkeypatch, tmp_path):
    import src.conversation.deepseek_bridge as mod

    monkeypatch.setattr(mod, "provider_usage_store", ProviderUsageStore(tmp_path / "provider_usage.json"))


def test_deepseek_bridge_normalizes_plain_deep_reason_output(monkeypatch):
    import src.conversation.deepseek_bridge as mod

    monkeypatch.setattr(
        mod.llm_gateway,
        "generate_chat",
        lambda *args, **kwargs: (
            "Inference demand is shifting toward inference-heavy workloads. "
            "Power and cooling constraints matter. Supply visibility remains uneven."
        ),
    )

    bridge = DeepSeekBridge()
    result = bridge.analyze(
        "Explain the long-term implications of inference-heavy workloads.",
        [{"role": "assistant", "content": "Earlier discussion about GPUs."}],
        analysis_profile="deep_reason",
    )

    assert "Core answer:" in result
    assert "Key drivers:" in result
    assert "Risks and uncertainties:" in result
    assert "What to verify next:" in result
    assert "Power and cooling constraints matter." in result


def test_deepseek_bridge_strips_duplicate_core_answer_prefix(monkeypatch):
    import src.conversation.deepseek_bridge as mod

    monkeypatch.setattr(
        mod.llm_gateway,
        "generate_chat",
        lambda *args, **kwargs: "Core answer: Version locking preserves trusted model behavior.",
    )

    result = mod.DeepSeekBridge().analyze(
        "Why does version locking matter?",
        [],
        analysis_profile="deep_reason",
    )

    assert result.startswith("Core answer:\nVersion locking preserves trusted model behavior.")
    assert "Core answer:\nCore answer:" not in result


def test_task_scoped_prompt_preserves_requested_format_contract():
    prompt = prompts.build_analysis_prompt(
        "Return exactly these sections: Accuracy, Potential Issues, Suggested Corrections, Confidence.",
        [],
        profile="task_scoped",
    )

    assert "Task-scoped reasoning contract:" in prompt
    assert "Follow the requested format exactly." in prompt
    assert "Core answer:" not in prompt


def test_deepseek_bridge_requests_extended_timeout(monkeypatch):
    import src.conversation.deepseek_bridge as mod

    captured = {}

    def _fake_generate_chat(*args, **kwargs):
        captured.update(kwargs)
        return "Core answer: Version locking preserves trusted model behavior."

    monkeypatch.setattr(mod.llm_gateway, "generate_chat", _fake_generate_chat)

    result = mod.DeepSeekBridge().analyze(
        "Why does model version locking matter?",
        [],
        suggested_max_tokens=180,
        analysis_profile="deep_reason",
    )

    assert "Core answer:" in result
    assert captured.get("timeout") == mod.ANALYSIS_TIMEOUT_SECONDS


def test_deepseek_bridge_allows_timeout_override(monkeypatch):
    import src.conversation.deepseek_bridge as mod

    captured = {}

    def _fake_generate_chat(*args, **kwargs):
        captured.update(kwargs)
        return "Structured analysis is available."

    monkeypatch.setattr(mod.llm_gateway, "generate_chat", _fake_generate_chat)

    result = mod.DeepSeekBridge().analyze(
        "Create a structured analysis document.",
        [],
        analysis_profile="task_scoped",
        timeout_seconds=150.0,
    )

    assert result == "Structured analysis is available."
    assert captured.get("timeout") == 150.0
