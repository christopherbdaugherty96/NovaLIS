"""
ConfirmationGate — Provably Passive

Constitutional Contract:
- Gate is silent (message=None) when no confirmation pending
- Only speaks when explicitly engaged with pending context
- Binary confirmation: only "yes" or "no" accepted
- No inference, no language normalization

Current runtime note:
  The live confirmation flow for governed actions (e.g. cap 22 open_file_folder)
  is handled directly by session_handler.py via pending_governed_confirm state.
  This gate class is retained for structural completeness. It is not on the active
  websocket path. Any future confirmation surface should wire through the session
  handler's existing pending_governed_confirm flow.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GateResult:
    """Gate only speaks through message field. None = gate is silent."""
    message: Optional[str] = None
    confirmed: bool = False


class ConfirmationGate:
    """Passive gate that only responds when explicitly engaged."""

    def __init__(self):
        self._pending_context = None

    def has_pending_confirmation(self) -> bool:
        """
        Explicit predicate for gate engagement.
        Returns True if and only if a confirmation flow is active.
        """
        return self._pending_context is not None

    def try_resolve(self, text: str) -> GateResult:
        """
        Gate is provably silent when idle.

        Constitutional Proof:
        - If no pending context → message=None (silent)
        - Only two valid responses: "yes" or "no"
        - All other input → message=None (silent)
        """
        if not self.has_pending_confirmation():
            return GateResult(message=None)

        lowered = text.strip().lower()

        if lowered == "yes":
            self._pending_context = None
            return GateResult(message="Okay.", confirmed=True)
        elif lowered == "no":
            self._pending_context = None
            return GateResult(message="Cancelled.", confirmed=False)
        else:
            return GateResult(message=None)

    def clear(self) -> None:
        """Reset to idle state."""
        self._pending_context = None


# Global instance retained for structural completeness.
# Not on the active websocket path — see session_handler.py pending_governed_confirm.
confirmation_gate = ConfirmationGate()
