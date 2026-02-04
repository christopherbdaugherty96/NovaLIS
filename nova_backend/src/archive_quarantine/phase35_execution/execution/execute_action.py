"""
NovaLIS Action Execution Boundary — GOVERNOR PRIVATE

⚠️ Phase-3.5 Status:
- This module MUST NOT be imported outside the Governor
- Direct execution is DISABLED
- Any call here is a constitutional violation
"""

from typing import Callable, Dict

from ..actions.action_request import ActionRequest
from ..actions.action_types import ActionType
from ..actions.action_result import ActionResult

# Handler Imports (preserved for Phase-4 compatibility)
from .handlers.open_app import open_app as handle_open_app
from .handlers.open_folder import open_folder as handle_open_folder
from .handlers.open_view import open_view as handle_open_view
from .handlers.volume_control import volume_control as handle_volume_control

# ⚠️ GOVERNOR-ONLY
# Handler registry must only be accessed by Governor-owned execution
# Any external import is a constitutional violation
_HANDLER_MAP: Dict[ActionType, Callable[[ActionRequest], ActionResult]] = {
    ActionType.OPEN_APP: handle_open_app,
    ActionType.OPEN_FOLDER: handle_open_folder,
    ActionType.OPEN_VIEW: handle_open_view,
    ActionType.VOLUME_CONTROL: handle_volume_control,
}


class ExecuteBoundary:
    """
    Execution boundary for confirmed actions.
    Canonical entrypoint for all action execution.
    """

    def __init__(self, config=None):
        """Initialize the execution boundary."""
        self.config = config

    def execute(self, action: ActionRequest) -> ActionResult:
        """
        Execute a confirmed action.
        Returns ActionResult with outcome.
        
        Phase-3.5: Execution disabled, Governor enforcement active.
        Phase-4: Governor will re-enable via structural token.
        """
        return ActionResult(
            success=False,
            message="Execution is disabled in Phase 3.5 (Governor enforcement active)."
        )

    def reset(self):
        """
        Reset boundary-local state (no-op for Phase-3.5).
        """
        pass


# ⚠️ CRITICAL: Free function execute_action REMOVED for Phase-3.5
# This ensures no execution bypass exists outside Governor control
# Phase-4 may reintroduce this via Governor mediation only