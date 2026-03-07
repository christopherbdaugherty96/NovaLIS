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
        lambda self, user_message, context, suggested_max_tokens=800: (
            "Accuracy: medium\nPotential Issues:\n- claim may be outdated\n"
            "Suggested Corrections:\n- use the latest source\nConfidence: medium"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "GDP grew by 9% yesterday"}))
    assert result.success is True
    assert "Verification Report" in result.message
    assert "Verification Confidence: Medium (0.65)" in result.message
    assert "Accuracy:" in result.message
    assert isinstance(result.data, dict)
    assert "verification_text" in result.data
    assert result.data["verification_confidence_label"] == "Medium"
    assert result.data["verification_confidence_score"] == 0.65
    assert result.data["verification_recommended"] is True


def test_response_verification_high_confidence_not_flagged(monkeypatch):
    from src.executors import response_verification_executor as mod

    monkeypatch.setattr(
        mod.DeepSeekBridge,
        "analyze",
        lambda self, user_message, context, suggested_max_tokens=800: (
            "Accuracy: high\nPotential Issues:\n- none noted\n"
            "Suggested Corrections:\n- none\nConfidence: high"
        ),
    )

    result = mod.ResponseVerificationExecutor().execute(_request({"text": "Water boils near 100 C at sea level"}))
    assert result.success is True
    assert result.data["verification_confidence_label"] == "High"
    assert result.data["verification_confidence_score"] == 0.9
    assert result.data["verification_recommended"] is False
