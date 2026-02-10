"""
ConfirmationGate — Phase-3.5 (Provably Passive)

Constitutional Contract:
- Gate is silent (message=None) when no confirmation pending
- Only speaks when explicitly engaged with pending context
- Binary confirmation: only "yes" or "no" accepted
- No inference, no language normalization
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class GateResult:
    """Phase-3.5: Gate only speaks through message field."""
    message: Optional[str] = None  # None = gate is silent
    confirmed: bool = False  # Always boolean, never None
    gate_context: Optional[dict] = None  # Future Phase-4 use


class ConfirmationGate:
    """Passive gate that only responds when explicitly engaged."""
    
    def __init__(self):
        # Internal state: only set by explicit user commands (Phase-4)
        self._pending_context = None
    
    def has_pending_confirmation(self) -> bool:
        """
        Phase-3.5: Explicit predicate for gate engagement.
        Returns True if and only if a confirmation flow is active.
        """
        return self._pending_context is not None
    
    def try_resolve(self, text: str) -> GateResult:
        """
        Phase-3.5: Gate is provably silent when idle.
        
        Constitutional Proof:
        - Line 33: If no pending context → message=None (silent)
        - Line 39: Only two valid responses: "yes" or "no"
        - Line 45: All other input → message=None (silent)
        """
        if not self.has_pending_confirmation():
            # 🔒 PROOF: Gate is idle → always silent
            return GateResult(message=None)
        
        # Only reachable if confirmation flow was explicitly started
        lowered = text.strip().lower()
        
        # Phase-3.5: Binary confirmation only
        if lowered == "yes":
            self._pending_context = None
            return GateResult(
                message="Okay.",
                confirmed=True,
                gate_context=None
            )
        elif lowered == "no":
            self._pending_context = None
            return GateResult(
                message="Cancelled.",
                confirmed=False,
                gate_context=None
            )
        else:
            # Not a confirmation response → gate is silent
            return GateResult(message=None)
    
    def set_pending(self, context: dict) -> None:
        """
        Phase-4 placeholder: explicit confirmation initiation.
        
        Contract:
        - Only called by future Phase-4 authority boundaries
        - Never called in Phase-3.5
        - Exists to preserve structural honesty
        """
        self._pending_context = context
    
    def clear(self) -> None:
        """Reset to idle state."""
        self._pending_context = None


# Global instance
confirmation_gate = ConfirmationGate()