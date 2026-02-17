test_phase35_execution_gate.py

"""
Phase 3.5 constitutional test: prove execution gate refuses any ActionRequest.

Run with: pytest tests/
(Assumes nova_backend/ is in Python path, or run from project root with PYTHONPATH=.)
"""

import pytest
from src.actions.action_request import ActionRequest
from src.actions.action_types import ActionType
from src.governor.execution_gate import GovernorExecutionGate, EXECUTION_ENABLED


def test_execution_gate_refuses_all_actions():
    """Any ActionRequest → success=False, non‑empty message."""
    request = ActionRequest(
        action_type=ActionType.GET_TIME,
        title="Test action"
    )

    result = GovernorExecutionGate.evaluate(request)

    assert result.success is False
    assert "execution" in result.message.lower()
    assert "not available" in result.message.lower()


def test_execution_flag_is_false():
    """Phase 3.5 guarantee: EXECUTION_ENABLED is False."""
    assert EXECUTION_ENABLED is False