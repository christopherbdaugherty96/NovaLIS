from __future__ import annotations

from src.cognition.cognitive_layer_contract import CognitiveMode, CognitiveRequest
from src.cognition.modules import ReportingModule, ResearchModule, VerificationModule


def test_cognition_module_scaffolds_return_contract_compliant_results():
    request = CognitiveRequest(
        user_query="Summarize runtime governance posture.",
        conversation_context=("ctx-1", "ctx-2"),
        source_data={"source_a": "x"},
        mode=CognitiveMode.REPORTING,
        request_id="test-request",
    )
    modules = (ResearchModule(), VerificationModule(), ReportingModule())

    for module in modules:
        result = module.analyze(request)
        assert result.module_name == module.name
        assert result.summary
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.key_points) >= 1
        assert result.diagnostics.get("template") is True
