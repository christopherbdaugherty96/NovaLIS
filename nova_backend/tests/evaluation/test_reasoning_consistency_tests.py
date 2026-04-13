from __future__ import annotations

from tests.simulation.conversation_simulator import run_simulation

from .cognitive_evaluator import CognitiveEvaluator


def test_reasoning_consistency_between_full_and_shorter_versions(monkeypatch):
    monkeypatch.setattr(
        "src.governor.governor.Governor._check_network_budget",
        lambda self, cap_id: None,
    )
    transcript = run_simulation(
        [
            "research robotics policy shifts",
            "shorter version",
        ]
    )
    full_text = transcript.turns[0].nova_response
    short_text = transcript.turns[1].nova_response

    full_eval = CognitiveEvaluator.evaluate_intelligence_brief(full_text)

    # Shorter follow-up should compress output but preserve core framing.
    assert len(short_text) <= len(full_text)
    assert "summary" in short_text.lower() or "governments" in short_text.lower()
    assert full_eval.has_summary is True
    assert full_eval.coherence_pass is True

