from __future__ import annotations

import pytest

from src.cognition.cognitive_layer_contract import (
    CognitiveMode,
    CognitiveRequest,
    CognitiveResult,
    validate_cognitive_result,
)


def test_cognitive_request_defaults_are_analysis_only():
    request = CognitiveRequest(user_query="Explain governor boundary.")
    assert request.mode == CognitiveMode.ANALYSIS
    assert request.conversation_context == ()
    assert request.source_data == {}


def test_validate_cognitive_result_accepts_well_formed_payload():
    result = CognitiveResult(
        summary="Boundary remains governed.",
        key_points=("All actions route through Governor.",),
        supporting_sources=("CURRENT_RUNTIME_STATE.md",),
        confidence=0.9,
        module_name="verification_engine",
    )
    validate_cognitive_result(result)


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_validate_cognitive_result_rejects_out_of_range_confidence(confidence: float):
    bad = CognitiveResult(summary="x", confidence=confidence)
    with pytest.raises(ValueError):
        validate_cognitive_result(bad)


def test_validate_cognitive_result_rejects_blank_summary():
    with pytest.raises(ValueError):
        validate_cognitive_result(CognitiveResult(summary="   "))
