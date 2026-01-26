"""
Confirmation Gate — Phase-3 (Execution-Structurally-Unreachable)

Phase-3 update: Removes all ActionRequest references while maintaining
gate functionality for future phases.
"""

from dataclasses import dataclass
from typing import Optional, Any
import time


@dataclass
class GateResult:
    handled: bool
    # Phase-3: No action reference, execution structurally unreachable
    gate_context: Optional[dict] = None  # Generic context for future phases


class ConfirmationGate:
    def __init__(self, timeout_seconds: int = 30) -> None:
        self._pending_context: Optional[dict] = None
        self._expires_at: Optional[float] = None
        self._timeout = timeout_seconds

    def set_pending(self, context: Optional[dict] = None) -> None:
        """
        Phase-3: Set pending confirmation without ActionRequest.
        context: Generic dictionary for future phase expansion.
        """
        self._pending_context = context or {}
        self._expires_at = time.time() + self._timeout

    def clear(self) -> None:
        self._pending_context = None
        self._expires_at = None

    def try_resolve(self, text: str) -> GateResult:
        """
        Attempt to resolve a pending confirmation.
        Phase-3: Returns generic context, no action reference.
        """
        if not self._pending_context:
            return GateResult(handled=False)

        if self._expires_at and time.time() > self._expires_at:
            self.clear()
            return GateResult(handled=True, gate_context={"reason": "timeout"})

        if text in {"yes", "y"}:
            context = self._pending_context.copy()
            self.clear()
            return GateResult(handled=True, gate_context=context)

        if text in {"no", "n"}:
            self.clear()
            return GateResult(handled=True, gate_context={"reason": "declined"})

        return GateResult(handled=False)


# ------------------------------------------------------------
# Singleton instance
# ------------------------------------------------------------

confirmation_gate = ConfirmationGate()