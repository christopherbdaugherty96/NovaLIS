# src/governor/execute_boundary.py

"""
ExecuteBoundary – Governor‑owned execution gate.
Phase‑4 staging: enforces global phase gate and manages execution lifecycle.
Timeouts are delegated to NetworkMediator.
"""

from __future__ import annotations

import time
from typing import Optional

from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult

# Phase‑4 staging flag – True when execution is allowed
GOVERNED_ACTIONS_ENABLED = True

# Resource limits (Phase‑4 defaults)
MAX_EXECUTION_TIME = 10      # seconds (not yet enforced, placeholder)
MAX_MEMORY_MB = 100          # placeholder
MAX_CONCURRENT = 1           # enforced via SingleActionQueue


class ExecuteBoundary:
    """
    Gatekeeper for all execution. Checks the global phase gate and
    provides lifecycle hooks for execution.
    """

    def __init__(self):
        self._start_time: Optional[float] = None

    def allow_execution(self) -> bool:
        """
        Called before any action is attempted.
        Returns True if execution is permitted in the current phase.
        """
        return GOVERNED_ACTIONS_ENABLED

    def enter_execution(self) -> None:
        """Call at the start of an executor to start the timeout timer."""
        self._start_time = time.time()

    def exit_execution(self) -> None:
        """Clean up after execution."""
        self._start_time = None