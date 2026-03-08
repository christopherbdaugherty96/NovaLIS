from __future__ import annotations

from .conversation_simulator import run_simulation


def test_cognitive_trace_layer_is_opt_in_and_structured():
    transcript = run_simulation(
        [
            "research AI chips",
            "shorter version",
        ],
        include_trace=True,
    )

    assert len(transcript.turns) == 2
    for turn in transcript.turns:
        assert turn.trace_id
        assert isinstance(turn.trace_steps, list)
        assert turn.trace_steps
        assert "stage" in turn.trace_steps[0]
        assert "data" in turn.trace_steps[0]

    first_stages = [step["stage"] for step in transcript.turns[0].trace_steps]
    assert "input_normalizer" in first_stages
    assert "governor_mediator.parse" in first_stages
    assert "governor_invocation" in first_stages

