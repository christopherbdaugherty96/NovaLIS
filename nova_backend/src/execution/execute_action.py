"""
NovaLIS Action Execution Boundary (Phase-2)
"""

from typing import Callable, Dict

from ..actions.action_request import ActionRequest
from ..actions.action_types import ActionType
from ..actions.action_result import ActionResult

# Handler Imports
from .handlers.open_app import open_app as handle_open_app
from .handlers.open_folder import open_folder as handle_open_folder
from .handlers.open_view import open_view as handle_open_view
from .handlers.volume_control import volume_control as handle_volume_control

# Handler Registry
_HANDLER_MAP: Dict[ActionType, Callable[[ActionRequest], ActionResult]] = {
    # ✅ FIX 2: Changed LAUNCH_APP to OPEN_APP
    ActionType.OPEN_APP: handle_open_app,
    ActionType.OPEN_FOLDER: handle_open_folder,
    ActionType.OPEN_VIEW: handle_open_view,
    ActionType.VOLUME_CONTROL: handle_volume_control,
}

def execute_action(action: ActionRequest) -> ActionResult:
    """
    Execute a confirmed action.
    """
    if not isinstance(action, ActionRequest):
        return ActionResult(
            success=False,
            message="Invalid action request.",
        )

    action_type = action.action_type
    handler = _HANDLER_MAP.get(action_type)

    if not handler:
        return ActionResult(
            success=False,
            message=f"Action '{action_type}' is not supported.",
        )

    try:
        return handler(action)
    except Exception:
        return ActionResult(
            success=False,
            message="The action could not be completed.",
        )