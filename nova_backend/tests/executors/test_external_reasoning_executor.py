from __future__ import annotations

from types import SimpleNamespace


def _request(params: dict):
    return SimpleNamespace(capability_id=62, params=params, request_id="reason-req")


def test_external_reasoning_requires_text():
    from src.executors.external_reasoning_executor import ExternalReasoningExecutor

    result = ExternalReasoningExecutor().execute(_request({"text": ""}))
    assert result.success is False
    assert "I need an answer or exchange to review" in result.message
    assert result.structured_data["failure_kind"] == "missing_text"


def test_external_reasoning_returns_governed_second_opinion(monkeypatch):
    from src.executors import external_reasoning_executor as mod

    monkeypatch.setattr(
        mod.ResponseVerificationExecutor,
        "execute",
        lambda self, request: mod.ActionResult.ok(
            "DeepSeek Second Opinion\nAgreement Level: Medium (0.65)",
            data={
                "verification_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "verification_accuracy_label": "Medium",
                "verification_accuracy_score": 0.65,
                "verification_confidence_label": "High",
                "verification_confidence_score": 0.9,
                "verification_recommended": True,
                "issue_count": 1,
                "correction_count": 1,
                "verification_summary_line": "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat.",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "follow_up_prompts": [
                    "nova final answer",
                    "summarize the gaps only",
                    "return to Nova's original answer",
                ],
            },
            structured_data={
                "verification_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "verification_accuracy_label": "Medium",
                "verification_accuracy_score": 0.65,
                "verification_confidence_label": "High",
                "verification_confidence_score": 0.9,
                "verification_recommended": True,
                "issue_count": 1,
                "correction_count": 1,
                "verification_summary_line": "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat.",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "follow_up_prompts": [
                    "nova final answer",
                    "summarize the gaps only",
                    "return to Nova's original answer",
                ],
            },
            speakable_text="DeepSeek second opinion ready.",
            request_id=request.request_id,
        ),
    )

    result = mod.ExternalReasoningExecutor().execute(
        _request({"text": "Recent exchange for second opinion review:\nUser: What changed?\nNova: Prices moved."})
    )

    assert result.success is True
    assert "Governed Second Opinion" in result.message
    assert "Provider: DeepSeek" in result.message
    assert "Bottom line:" in result.message
    assert "Main gap: the answer needs a clearer caveat" in result.message
    assert result.structured_data["reasoning_provider"] == "DeepSeek"
    assert result.structured_data["reasoning_authority"] == "analysis_only"
    assert result.structured_data["reasoning_confidence_label"] == "High"
    assert result.structured_data["reasoning_summary_line"].startswith("Bottom line:")
    assert result.speakable_text.startswith("Second opinion ready.")
