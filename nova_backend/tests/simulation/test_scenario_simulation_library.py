from __future__ import annotations

from pathlib import Path

from .conversation_runner import run_scenario_library


def test_scenario_simulation_library_executes_all_workflows():
    scenario_dir = Path(__file__).resolve().parent / "scenarios"
    runs = run_scenario_library(scenario_dir)

    assert len(runs) >= 4

    for scenario, transcript in runs:
        assert len(transcript.turns) == len(scenario["script"])
        for turn in transcript.turns:
            assert turn.execution_time_ms >= 0
            assert turn.governor_decision

    assert any(transcript.capability_sequence() for _scenario, transcript in runs)
