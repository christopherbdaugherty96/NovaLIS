from __future__ import annotations

from types import SimpleNamespace


def _request(params: dict):
    return SimpleNamespace(capability_id=31, params=params, request_id="verify-req")


def test_response_verification_requires_text():
    from src.executors.response_verification_executor import ResponseVerificationExecutor

    result = ResponseVerificationExecutor().execute(_request({"text": ""}))
    assert result.success is False
    assert "I need text to verify" in result.message


def test_response_verification_returns_report(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "Accuracy: medium\nPotential Issues:\n- claim may be outdated\n"
            "Suggested Corrections:\n- use the latest source\nConfidence: medium"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "GDP grew by 9% yesterday"}))
    assert result.success is True
    assert "Verification Report" in result.message
    assert "Claim Reliability: Medium (0.65)" in result.message
    assert "Report Confidence: Medium (0.65)" in result.message
    assert "Accuracy:" in result.message
    assert isinstance(result.data, dict)
    assert result.speakable_text.startswith("Verification complete.")
    assert isinstance(result.structured_data, dict)
    assert result.structured_data["verification_accuracy_label"] == "Medium"
    assert "verification_text" in result.data
    assert result.data["verification_accuracy_label"] == "Medium"
    assert result.data["verification_accuracy_score"] == 0.65
    assert result.data["verification_confidence_label"] == "Medium"
    assert result.data["verification_confidence_score"] == 0.65
    assert result.data["verification_recommended"] is True
    assert result.data["issue_count"] == 1
    assert result.data["correction_count"] == 1
    assert result.data["follow_up_prompts"]


def test_response_verification_high_confidence_not_flagged(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "Accuracy: high\nPotential Issues:\n- none noted\n"
            "Suggested Corrections:\n- none\nConfidence: high"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "Water boils near 100 C at sea level"}))
    assert result.success is True
    assert result.data["verification_accuracy_label"] == "High"
    assert result.data["verification_confidence_label"] == "High"
    assert result.data["verification_confidence_score"] == 0.9
    assert result.data["verification_recommended"] is False


def test_response_verification_uses_accuracy_for_recommendation_and_counts_inline_sections(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "Accuracy: Low\n"
            "Potential Issues: The statement conflicts with well-established lunar science.\n"
            "Suggested Corrections: State that the moon has no substantial atmosphere like Earth's.\n"
            "Confidence: High"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "The moon has a thick atmosphere like Earth."}))

    assert result.success is True
    assert "Claim Reliability: Low (0.40)" in result.message
    assert "Report Confidence: High (0.90)" in result.message
    assert result.data["verification_accuracy_label"] == "Low"
    assert result.data["verification_confidence_label"] == "High"
    assert result.data["verification_recommended"] is True
    assert result.data["issue_count"] == 1
    assert result.data["correction_count"] == 1


def test_response_verification_returns_truthful_failure_when_analysis_is_unavailable(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "I can provide structured analysis, but it is currently unavailable."
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "The moon has an atmosphere"}))
    assert result.success is False
    assert "structured analysis is currently blocked or unavailable" in result.message.lower()
    assert result.outcome_reason
    assert result.structured_data["failure_kind"] == "analysis_unavailable"


def test_response_verification_rejects_incomplete_report(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: "Confidence: medium\nJust trust me.",
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "A claim"}))
    assert result.success is False
    assert "incomplete report" in result.message.lower()


def test_response_verification_supports_second_opinion_mode(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
            "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(
        _request({"text": "Recent exchange for second opinion review:\nUser: What changed?\nNova: Prices moved.", "review_mode": "second_opinion"})
    )
    assert result.success is True
    assert "DeepSeek Second Opinion" in result.message
    assert "Agreement Level: Medium (0.65)" in result.message
    assert "Bottom line:" in result.message
    assert "Main gap: the answer needs a clearer caveat" in result.message
    assert result.data["verification_mode"] == "second_opinion"
    assert result.data["verification_summary_line"].startswith("Bottom line:")
    assert result.data["top_issue"] == "the answer needs a clearer caveat"
    assert result.data["follow_up_prompts"][0] == "ask Nova to revise the answer"
    assert result.speakable_text.startswith("DeepSeek second opinion ready.")


def test_response_verification_normalizes_markdownish_structured_output(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800, **_kwargs: (
            "```markdown\n"
            "**Accuracy** - medium\n"
            "**Potential Issues** - the answer needs a clearer caveat\n"
            "**Suggested Corrections** - explain the uncertainty in one sentence\n"
            "**Confidence** - high\n"
            "```"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(
        _request({"text": "A draft answer that needs review", "review_mode": "second_opinion"})
    )

    assert result.success is True
    assert "Accuracy: medium" in result.data["verification_text"]
    assert "Potential Issues:" in result.data["verification_text"]
    assert result.data["top_issue"] == "the answer needs a clearer caveat"
