# src/governor/governor.py

"""
Governor – constitutional authority spine.
Phase‑4 integration: owns all execution‑related components, but they are lazily loaded
to preserve Phase‑3.5 safety until the unlock.
"""

from __future__ import annotations

from typing import Optional, Dict, Any

from src.actions.action_result import ActionResult
from src.governor.execute_boundary import ExecuteBoundary
from src.governor.single_action_queue import SingleActionQueue
from src.governor.exceptions import (
    CapabilityRegistryError,
    NetworkMediatorError,
    LedgerWriteFailed,
)
from src.actions.action_request import ActionRequest


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
        """
        Lazy load LedgerWriter.
        Dynamically imported to allow test monkeypatching and to avoid binding
        authority surfaces at module load time.
        """
        if self._ledger is None:
            import src.ledger.writer as ledger_mod
            self._ledger = ledger_mod.LedgerWriter()
        return self._ledger

    # ---- Phase‑4 entrypoint (called by mediator) ----

    def handle_governed_invocation(
        self,
        capability_id: int,
        params: Dict[str, Any],
    ) -> ActionResult:
        """
        Receives a parsed governed invocation from GovernorMediator.
        This method is the ONLY place that can attempt to create an ActionRequest.
        Returns an ActionResult (structured, may contain widget data).
        """
        # 1) Capability identity + enable gate (per‑capability)
        try:
            cap = self.registry.get(capability_id)
            print(f"[DEBUG] Capability {capability_id} found: {cap.name}, enabled={self.registry.is_enabled(capability_id)}")
        except CapabilityRegistryError as e:
            print(f"[DEBUG] Capability {capability_id} not found: {e}")
            return ActionResult.failure(f"I can’t do that. {e}")

        if not self.registry.is_enabled(capability_id):
            print(f"[DEBUG] Capability {capability_id} is disabled")
            # Policy denial → refusal
            return ActionResult.refusal("I can’t do that yet.")

        # 2) Global phase gate (fail‑closed) – single check
        if not self._execute_boundary.allow_execution():
            print("[DEBUG] Phase gate blocked execution")
            # Policy denial → refusal
            return ActionResult.refusal("That requires a specific action, which I can’t perform right now.")

        # 3) Single pending action boundary (MUST be checked before any ledger write)
        print(f"[DEBUG] Queue has pending: {self._queue.has_pending()}")
        if self._queue.has_pending():
            # Policy denial → refusal (queue busy)
            return ActionResult.refusal("I can’t do that right now.")

        # 4) Ledger must be writable BEFORE any effect (but after queue check)
        try:
            self.ledger.log_event(
                "ACTION_ATTEMPTED",
                {"capability_id": capability_id, "capability_name": cap.name},
            )
            print("[DEBUG] ACTION_ATTEMPTED logged")
        except Exception:
            # Any failure to write to the ledger denies the action
            print("[DEBUG] Ledger write FAILED")
            return ActionResult.failure("I can’t do that right now.")

        # 5) Create ActionRequest
        req = ActionRequest(capability_id=capability_id, params=params)
        print(f"[DEBUG] ActionRequest created: {req.request_id}")

        # 6) Execute (routed to appropriate executor)
        try:
            result = self._execute(req)
            return result
        except (NetworkMediatorError, LedgerWriteFailed) as e:
            print(f"[DEBUG] Execution exception (Network/Ledger): {e}")
            return ActionResult.failure("I can’t do that right now.", request_id=req.request_id)
        except Exception as e:
            print(f"[DEBUG] Unexpected exception: {e}")
            return ActionResult.failure("I can’t do that right now.", request_id=req.request_id)

    def _execute(self, req: ActionRequest) -> ActionResult:
        """
        Internal execution router.
        This is the ONLY place executors are instantiated.
        The Governor manages the entire boundary lifecycle; executors receive only
        the network client and the request, never the boundary object.
        """
        print(f"[DEBUG] _execute called for capability {req.capability_id}")

        self._queue.set_pending(req.request_id)
        self._execute_boundary.enter_execution()

        result = None
        error_type = None

        try:
            # --- Log search query if this is a web search (capability 16) ---
            if req.capability_id == 16:
                query = req.params.get("query")
                if query:
                    try:
                        self.ledger.log_event("SEARCH_QUERY", {"query": query})
                    except LedgerWriteFailed:
                        # Non‑blocking; failure is logged by ledger itself
                        pass

            # ---- Prepare params with capability_id injected (executors need it) ----
            params = {
                **req.params,
                "capability_id": req.capability_id,
            }

            # ---- Route by capability_id ----
            if req.capability_id == 16:
                from src.executors.web_search_executor import WebSearchExecutor
                executor = WebSearchExecutor(self.network)  # No boundary injected
                result = executor.execute(req.request_id, params)

            elif req.capability_id == 17:
                from src.executors.webpage_launch_executor import WebpageLaunchExecutor
                executor = WebpageLaunchExecutor()  # no dependencies
                result = executor.execute(req.request_id, params)

            else:
                result = ActionResult.refusal(
                    "Execution path not implemented yet.",
                    request_id=req.request_id
                )

        except TimeoutError:
            error_type = "timeout"
            result = ActionResult.refusal(
                "The request took too long and was cancelled.",
                request_id=req.request_id
            )
        except Exception as e:
            print(f"[DEBUG] Exception inside _execute routing: {e}")
            error_type = "exception"
            result = ActionResult.refusal(
                "I can’t do that right now.",
                request_id=req.request_id
            )
        finally:
            # Completion logging (best effort) – MUST run for all paths
            if result is not None:
                try:
                    payload = {
                        "capability_id": req.capability_id,
                        "request_id": req.request_id,
                        "success": bool(result.success),
                    }
                    if error_type:
                        payload["error_type"] = error_type
                    self.ledger.log_event("ACTION_COMPLETED", payload)
                except LedgerWriteFailed:
                    pass

            self._execute_boundary.exit_execution()
            self._queue.clear()

        return result