from __future__ import annotations

from tests.simulation.conversation_simulator import run_simulation

from .intelligence_brief_evaluator import IntelligenceBriefEvaluator


def test_intelligence_brief_quality_contract(monkeypatch):
    monkeypatch.setattr(
        "src.governor.governor.Governor._check_network_budget",
        lambda self, cap_id: None,
    )
    transcript = run_simulation(["research AI regulation trends"])
    response = transcript.turns[-1].nova_response

    grade = IntelligenceBriefEvaluator.evaluate(response)

    assert grade.structure_pass is True
    assert grade.source_coverage_pass is True
    assert grade.confidence_present is True
    assert grade.result.quality_score >= 7.0

