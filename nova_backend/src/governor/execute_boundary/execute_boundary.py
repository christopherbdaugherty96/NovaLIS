"""
ExecuteBoundary – Governor‑owned execution gate.
Phase‑3.5 / Phase‑4 locked: always fails closed, no latent toggle.
"""
from __future__ import annotations

from src.actions.action_request import ActionRequest

from src.actions.action_result import ActionResult

class ExecuteBoundary:
    """
    The only place where execution could ever be initiated.
    In locked phases, it unconditionally returns a refusal.
    No constructor parameter – execution_enabled is hardcoded to False
    until Phase‑4 unlock, at which point this class will be structurally modified.
    """

    def evaluate(self, request: ActionRequest) -> ActionResult:
        """
        Evaluate an action request.
        In Phase‑3.5 this always fails closed with a canonical refusal message.
        """
        return ActionResult.refusal(
            "That action requires execution, which is not available in the current phase.",
            request_id=request.id
        )