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

    with pytest.raises(TimeoutError):
        boundary.run_with_timeout(_slow_operation, timeout_seconds=0.01)

    # Timeout should not leave the worker running in background.
    assert state["finished"] is True
