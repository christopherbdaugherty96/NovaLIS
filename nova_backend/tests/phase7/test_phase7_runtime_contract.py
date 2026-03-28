from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_STATE_PATH = PROJECT_ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"
REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "config" / "registry.json"


def _request(text: str) -> SimpleNamespace:
    return SimpleNamespace(capability_id=62, params={"text": text}, request_id="phase7-req")


def test_phase7_runtime_truth_reports_complete_bounded_reasoning_lane():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")

    assert "| Phase 7 | COMPLETE |" in content
    assert "explicit second-opinion capability" in content
    assert "provider transparency" in content
    assert "advisory-only trust explanation" in content


def test_phase7_registry_keeps_external_reasoning_bounded():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    capability = next(item for item in registry["capabilities"] if int(item["id"]) == 62)

    assert capability["name"] == "external_reasoning_review"
    assert capability["phase_introduced"] == "7"
    assert capability["enabled"] is True
    assert capability["authority_class"] == "read_only_local"
    assert capability["external_effect"] is False
    assert capability["reversible"] is True


def test_phase7_external_reasoning_executor_stays_advisory_only(monkeypatch):
    from src.executors import external_reasoning_executor as mod

    monkeypatch.setattr(
        mod.ResponseVerificationExecutor,
        "execute",
        lambda self, request: mod.ActionResult.ok(
            "DeepSeek Second Opinion\nAgreement Level: High (0.91)",
            structured_data={
                "verification_text": "Accuracy: high\nPotential Issues:\n- none\nSuggested Corrections:\n- none\nConfidence: high",
                "verification_accuracy_label": "High",
                "verification_accuracy_score": 0.91,
                "verification_confidence_label": "High",
                "verification_confidence_score": 0.95,
                "verification_recommended": False,
                "issue_count": 0,
                "correction_count": 0,
                "follow_up_prompts": ["return to Nova's original answer"],
            },
            speakable_text="DeepSeek second opinion ready.",
            request_id=request.request_id,
        ),
    )

    result = mod.ExternalReasoningExecutor().execute(_request("Review this answer for gaps."))

    assert result.success is True
    assert result.authority_class == "read_only"
    assert result.external_effect is False
    assert "Provider: DeepSeek" in result.message
    assert result.structured_data["reasoning_provider"] == "DeepSeek"
    assert result.structured_data["reasoning_authority"] == "analysis_only"
    assert "cannot take actions" in result.structured_data["reasoning_governance_note"]


def test_phase7_provider_usage_store_surfaces_budget_and_measurement_truth(tmp_path):
    from src.usage.provider_usage_store import ProviderUsageStore

    store = ProviderUsageStore(tmp_path / "provider_usage.json", daily_token_budget=120, warning_ratio=0.5)
    snapshot = store.record_reasoning_event(
        provider="DeepSeek reasoning lane",
        route="DeepSeekBridge -> llm_gateway",
        analysis_profile="task_scoped",
        prompt_text="x" * 160,
        response_text="y" * 160,
    )

    assert snapshot["event_count"] == 1
    assert snapshot["measurement_label"] == "Estimated tokens"
    assert snapshot["budget_state"] in {"warning", "limit"}
    assert snapshot["recent_events"][0]["usage_measurement"] == "estimated"
