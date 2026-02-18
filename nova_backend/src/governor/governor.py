# src/governor/governor.py

"""
Governor – constitutional authority spine.
Phase‑4 integration: owns all execution‑related components, but they are lazily loaded
to preserve Phase‑3.5 safety until the unlock.
"""

from __future__ import annotations

from typing import Optional, Dict, Any

from src.governor.execute_boundary import ExecuteBoundary
from src.governor.single_action_queue import SingleActionQueue
from src.ledger.writer import LedgerWriter
from src.governor.exceptions import (
    CapabilityRegistryError,
    NetworkMediatorError,
    LedgerWriteFailed,
)
from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult

# Phase‑4 components are imported only when needed (lazy loading)
# This avoids crashes if configuration files aren't ready during Phase‑3.5.


class Governor:
    """
    Single authority choke point.
    - Owns execute boundary and queue unconditionally.
    - Lazily loads registry, network mediator, ledger on first use.
    """

    def __init__(self):
        self._execute_boundary = ExecuteBoundary()
        self._queue = SingleActionQueue()

        # Lazy‑loaded Phase‑4 components (initially None)
        self._registry = None
        self._network = None
        self._ledger = None

    @property
    def execute_boundary(self) -> ExecuteBoundary:
        return self._execute_boundary

    @property
    def registry(self):
        """Lazy load CapabilityRegistry."""
        if self._registry is None:
            from src.governor.capability_registry import CapabilityRegistry
            self._registry = CapabilityRegistry()
        return self._registry

    @property
    def network(self):
        """Lazy load NetworkMediator."""
        if self._network is None:
            from src.governor.network_mediator import NetworkMediator
            self._network = NetworkMediator()
        return self._network

    @property
    def ledger(self):
        """Lazy load LedgerWriter."""
        if self._ledger is None:
            self._ledger = LedgerWriter()
        return self._ledger

    # ---- Phase‑4 entrypoint (called by mediator) ----

    def handle_governed_invocation(
        self,
        capability_id: int,
        params: Dict[str, Any],
    ) -> str:
        """
        Receives a parsed governed invocation from GovernorMediator.
        This method is the ONLY place that can attempt to create an ActionRequest.
        Returns a user‑facing message (success or refusal).
        """
        # 1) Capability identity + enable gate (per‑capability)
        try:
            cap = self.registry.get(capability_id)
        except CapabilityRegistryError as e:
            return f"I can’t do that. {e}"

        if not self.registry.is_enabled(capability_id):
            # Enabled flag is separate from phase gate.
            return "I can’t do that yet."

        # 2) Global phase gate (fail‑closed)
        if not self._execute_boundary.allow_execution():
            return "That requires a specific action, which I can’t perform right now."

        # 3) Ledger must be writable BEFORE any effect
        try:
            self.ledger.log_event(
                "ACTION_ATTEMPTED",
                {"capability_id": capability_id, "capability_name": cap.name},
            )
        except LedgerWriteFailed:
            # Fail closed: no ledger, no action
            return "I can’t do that right now."

        # 4) Single pending action boundary
        if self._queue.has_pending():
            return "I can’t do that right now."

        # 5) ExecuteBoundary pre‑flight (resource checks)
        if not self._execute_boundary.allow_execution():
            return "I can’t do that right now."

        # 6) Create ActionRequest
        req = ActionRequest(capability_id=capability_id, params=params)

        # 7) Execute (routed to appropriate executor)
        try:
            result = self._execute(req)
            # Convert ActionResult to user message
            if result.success:
                return result.message
            else:
                # For failures, return the error message or a generic refusal
                return result.message or "I can’t do that right now."
        except (NetworkMediatorError, LedgerWriteFailed) as e:
            # These are expected failures; log and return a calm refusal.
            # (The ledger event was already logged by the callee.)
            return "I can’t do that right now."
        except Exception:
            # Unexpected error – log and fail closed.
            # In a real system you'd also write a CONSTITUTIONAL_VIOLATION event.
            return "I can’t do that right now."

    def _execute(self, req: ActionRequest) -> ActionResult:
        """
        Route to the appropriate executor.
        Executors must use self.network for any outbound calls.
        """
        # Mark action as pending to enforce concurrency
        self._queue.set_pending(f"cap_{req.capability_id}")

        try:
            # Start execution timer
            self._execute_boundary.enter_execution()

            # ---- Route by capability_id ----
            if req.capability_id == 16:
                from src.executors.web_search_executor import WebSearchExecutor
                executor = WebSearchExecutor(self.network, self._execute_boundary)
                result = executor.execute(req)

            # Add other capabilities here (17, 18, etc.)

            else:
                result = ActionResult.refusal(
                    "Execution path not implemented yet.",
                    request_id=req.request_id
                )

            # Completion logging must never change outcome.
            try:
                self.ledger.log_event(
                    "ACTION_COMPLETED",
                    {
                        "capability_id": req.capability_id,
                        "request_id": req.request_id,
                        "success": result.success,
                    },
                )
            except LedgerWriteFailed:
                # Fail closed for *effects* is already enforced by ACTION_ATTEMPTED pre-check.
                # Completion logging is best-effort.
                pass

            return result

        except TimeoutError:
            return ActionResult.refusal(
                "The request took too long and was cancelled.",
                request_id=req.request_id
            )
        except Exception:
            # Unexpected error – log and fail closed.
            return ActionResult.refusal(
                "I can’t do that right now.",
                request_id=req.request_id
            )
        finally:
            # Always clean up
            self._execute_boundary.exit_execution()
            self._queue.clear()