import pytest

from src.openclaw.per_tool_budget import (
    PerToolBudgetExceeded,
    PerToolBudgetTracker,
    ToolBudgetConfig,
)


def test_record_and_usage():
    tracker = PerToolBudgetTracker()
    tracker.record_call("weather", duration_seconds=1.5, success=True, network_calls=1)
    tracker.record_call("weather", duration_seconds=2.0, success=False, network_calls=0)

    u = tracker.usage("weather")
    assert u["calls"] == 2
    assert u["successes"] == 1
    assert u["failures"] == 1
    assert u["network_calls"] == 1
    assert abs(u["total_duration_seconds"] - 3.5) < 0.01


def test_no_limits_means_unlimited():
    tracker = PerToolBudgetTracker()
    for _ in range(100):
        tracker.record_call("weather", duration_seconds=1.0)
    assert tracker.can_call("weather") is True


def test_call_limit_enforced():
    tracker = PerToolBudgetTracker()
    tracker.set_limit("weather", ToolBudgetConfig(max_calls=2))

    tracker.record_call("weather")
    tracker.record_call("weather")
    with pytest.raises(PerToolBudgetExceeded, match="calls"):
        tracker.record_call("weather")


def test_duration_limit_enforced():
    tracker = PerToolBudgetTracker()
    tracker.set_limit("weather", ToolBudgetConfig(max_duration_seconds=5.0))

    tracker.record_call("weather", duration_seconds=3.0)
    with pytest.raises(PerToolBudgetExceeded, match="duration"):
        tracker.record_call("weather", duration_seconds=3.0)


def test_network_limit_enforced():
    tracker = PerToolBudgetTracker()
    tracker.set_limit("weather", ToolBudgetConfig(max_network_calls=1))

    tracker.record_call("weather", network_calls=1)
    with pytest.raises(PerToolBudgetExceeded, match="network"):
        tracker.record_call("weather", network_calls=1)


def test_can_call_respects_limits():
    tracker = PerToolBudgetTracker()
    tracker.set_limit("weather", ToolBudgetConfig(max_calls=1))

    assert tracker.can_call("weather") is True
    tracker.record_call("weather")
    assert tracker.can_call("weather") is False


def test_can_call_unknown_tool():
    tracker = PerToolBudgetTracker()
    assert tracker.can_call("nonexistent") is True


def test_empty_usage():
    tracker = PerToolBudgetTracker()
    assert tracker.usage("nonexistent") == {}


def test_snapshot():
    tracker = PerToolBudgetTracker()
    tracker.set_limit("weather", ToolBudgetConfig(max_calls=1))
    tracker.record_call("weather")
    tracker.record_call("news")

    snap = tracker.snapshot()
    assert snap["tools_tracked"] == 2
    assert "weather" in snap["tools_over_budget"]
    assert "news" not in snap["tools_over_budget"]


def test_set_limits_batch():
    tracker = PerToolBudgetTracker()
    tracker.set_limits({
        "weather": ToolBudgetConfig(max_calls=3),
        "news": ToolBudgetConfig(max_calls=5),
    })
    assert tracker.can_call("weather") is True
    assert tracker.can_call("news") is True
