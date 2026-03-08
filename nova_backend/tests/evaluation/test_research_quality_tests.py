from __future__ import annotations

from tests.simulation.conversation_simulator import run_simulation

from .cognitive_evaluator import CognitiveEvaluator


def test_research_quality_metrics_present():
    transcript = run_simulation(["create an intelligence brief on lithium supply chains"])
    response = transcript.turns[-1].nova_response
    result = CognitiveEvaluator.evaluate_intelligence_brief(response)

    assert result.has_summary is True
    assert result.has_key_findings is True
    assert result.has_sources is True
    assert result.source_count >= 2
    assert result.summary_compression_ratio > 0

