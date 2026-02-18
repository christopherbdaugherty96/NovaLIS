# src/governor/execute_boundary.py

"""
ExecuteBoundary – Governor‑owned execution gate.
Phase‑3.5 / Phase‑4 locked: checks global flag and enforces resource limits.
"""

from __future__ import annotations

import time
from typing import Optional

from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult

# This should match the global phase gate in nova_config.py
# For now, we keep it False; it will be flipped to True after admission.
GOVERNED_ACTIONS_ENABLED = False

# Resource limits (Phase‑4 defaults)
MAX_EXECUTION_TIME = 10      # seconds
MAX_MEMORY_MB = 100          # not enforced here, but placeholder
MAX_CONCURRENT = 1           # enforced via SingleActionQueue


class ExecuteBoundary:
    """
    Gatekeeper for all execution. In Phase‑3.5 it always fails closed.
    In Phase‑4 it enforces the global phase gate and resource limits.
    """

    def __init__(self):
        self._start_time: Optional[float] = None

    def allow_execution(self) -> bool:
        """
        Called before any action is attempted.
        Returns True if execution is permitted in the current phase.
        """
        # Global phase gate
        if not GOVERNED_ACTIONS_ENABLED:
            return False
        # Additional pre‑flight checks can be added here
        return True

    def evaluate(self, request: ActionRequest) -> ActionResult:
        """
        Legacy method for Phase‑3.5 – always refuses.
        In Phase‑4 this will be replaced by a call to the executor.
        """
        if not GOVERNED_ACTIONS_ENABLED:
            return ActionResult.refusal(
                "That action requires execution, which is not available in the current phase.",
                request_id=request.request_id
            )
        # Phase‑4 path will go here eventually
        return ActionResult.refusal("Execution not yet implemented.", request_id=request.request_id)

    def enter_execution(self) -> None:
        """Call at the start of an executor to start the timeout timer."""
        self._start_time = time.time()

    def check_timeout(self) -> None:
        """Raise an exception if execution time exceeds limit."""
        if self._start_time and (time.time() - self._start_time) > MAX_EXECUTION_TIME:
            raise TimeoutError("Execution timeout exceeded.")

    def exit_execution(self) -> None:
        """Clean up after execution."""
        self._start_time = None