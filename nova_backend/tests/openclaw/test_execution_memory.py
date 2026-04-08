import json

import pytest

from src.openclaw.execution_memory import ExecutionMemory


@pytest.fixture
def memory(tmp_path):
    return ExecutionMemory(path=tmp_path / "mem.json")


def test_record_and_stats(memory):
    memory.record("weather", "brief", success=True, duration_seconds=1.5)
    memory.record("weather", "brief", success=True, duration_seconds=2.0)
    memory.record("weather", "brief", success=False, duration_seconds=0.5, error="timeout")
    stats = memory.stats("weather")
    assert stats["total_calls"] == 3
    assert stats["successes"] == 2
    assert stats["failures"] == 1
    assert abs(stats["success_rate"] - 0.667) < 0.01


def test_reliability_insufficient_data(memory):
    memory.record("news", "brief", success=True, duration_seconds=1.0)
    assert memory.reliability("news", "brief", min_samples=3) == -1.0


def test_reliability_with_data(memory):
    for _ in range(5):
        memory.record("cal", "brief", success=True, duration_seconds=1.0)
    memory.record("cal", "brief", success=False, duration_seconds=0.5)
    rel = memory.reliability("cal", "brief")
    assert abs(rel - 5 / 6) < 0.01


def test_optimal_order(memory):
    # weather: 100% success, 2s avg
    for _ in range(3):
        memory.record("weather", "brief", success=True, duration_seconds=2.0)
    # news: 66% success, 3s avg
    for _ in range(2):
        memory.record("news", "brief", success=True, duration_seconds=3.0)
    memory.record("news", "brief", success=False, duration_seconds=3.0)

    order = memory.optimal_order(["news", "weather"], "brief")
    assert order == ["weather", "news"]


def test_persistence(tmp_path):
    path = tmp_path / "mem.json"
    mem1 = ExecutionMemory(path=path)
    mem1.record("weather", "brief", success=True, duration_seconds=1.0)
    mem1.record("news", "brief", success=False, duration_seconds=2.0, error="fail")

    # Load into a new instance
    mem2 = ExecutionMemory(path=path)
    stats = mem2.stats("weather")
    assert stats["total_calls"] == 1
    assert stats["successes"] == 1


def test_empty_stats(memory):
    assert memory.stats("nonexistent") == {}
