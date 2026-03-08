from __future__ import annotations

from .conversation_simulator import run_simulation


def test_research_conversation_flow():
    script = [
        "hello nova",
        "research AI regulation",
        "summarize that",
        "shorter version",
    ]

    transcript = run_simulation(script)
    assert len(transcript.turns) == 4

    capabilities = transcript.capability_sequence()
    assert 48 in capabilities

    research_turn = next(turn for turn in transcript.turns if turn.capability_triggered == 48)
    assert "Summary" in research_turn.nova_response
    assert "Key Findings" in research_turn.nova_response

    assert transcript.turns[-1].nova_response
    assert len(transcript.turns[-1].nova_response) <= len(transcript.turns[-2].nova_response)
