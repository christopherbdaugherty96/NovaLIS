from __future__ import annotations

import time

import pytest

from src.governor.execute_boundary.execute_boundary import ExecuteBoundary


def test_timeout_waits_for_worker_completion_before_returning():
    boundary = ExecuteBoundary()
    state = {"finished": False}

    def _slow_operation():
        time.sleep(0.08)
        state["finished"] = True
        return "done"

    boundary.enter_execution()
    try:
        start = time.perf_counter()
        with pytest.raises(TimeoutError):
            boundary.run_with_timeout(_slow_operation, timeout_seconds=0.01)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.06
        boundary.exit_execution()
        assert boundary.allow_execution() is False

        time.sleep(0.12)
        assert state["finished"] is True
        assert boundary.allow_execution() is True
    finally:
        boundary.exit_execution()
