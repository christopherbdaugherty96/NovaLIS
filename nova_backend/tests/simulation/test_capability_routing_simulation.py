from __future__ import annotations

from .conversation_simulator import run_simulation


def test_capability_routing_simulation():
    script = [
        "search for nuclear energy",
        "research nuclear energy",
        "create an intelligence brief on nuclear energy",
    ]

    transcript = run_simulation(script)
    sequence = transcript.capability_sequence()
    assert sequence == [16, 48, 48]
    executors = [turn.capability_executor for turn in transcript.turns if turn.capability_triggered is not None]
    assert executors == [
        "web_search_executor",
        "multi_source_reporting_executor",
        "multi_source_reporting_executor",
    ]
