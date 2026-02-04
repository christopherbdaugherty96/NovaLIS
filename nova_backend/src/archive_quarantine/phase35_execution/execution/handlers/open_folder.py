"""
NovaLIS — Phase-2 Handler: open_folder

Purpose:
- Open a single, explicitly approved folder in the OS file explorer
- Enforce strict allowlist behavior
- Execute exactly one OS action
- Fail closed on any violation

PHASE-2 RULES:
- Deterministic only
- No discovery
- No retries
- No background supervision
- One action per call
"""

import os
import subprocess
from typing import Dict, Any

from ...actions.action_request import ActionRequest
from ...actions.action_result import ActionResult
from ...actions.action_types import ActionType


# ----------------------------------------------------------
# LOCAL ALLOWLIST (Phase-2 V1)
# ----------------------------------------------------------

def _allowed_folders() -> Dict[str, Dict[str, Any]]:
    """
    Return the Phase-2 approved folder allowlist.

    NOTE:
    - Absolute paths only
    - No filesystem traversal
    - No dynamic discovery
    - May move to nova_config.py in Phase-3+
    """
    return {
        "documents": {
            "name": "Documents",
            "path": r"C:\Users\Chris\Documents",
        },
        "downloads": {
            "name": "Downloads",
            "path": r"C:\Users\Chris\Downloads",
        },
    }


# ----------------------------------------------------------
# EXECUTION HANDLER
# ----------------------------------------------------------

def open_folder(action: ActionRequest) -> ActionResult:
    """
    Execute a Phase-2 OPEN_FOLDER action.

    This handler:
    - Assumes confirmation has already occurred
    - Executes immediately
    - Returns exactly one ActionResult
    """

    # Defensive type check (execution boundary invariant)
    if not isinstance(action, ActionRequest):
        return ActionResult(
            success=False,
            message="Invalid action request.",
        )

    # Explicit ActionType guard
    if action.action_type is not ActionType.OPEN_FOLDER:
        return ActionResult(
            success=False,
            message="Invalid action type.",
        )

    payload = action.payload or {}
    folder_id = (payload.get("folder_id") or "").strip().lower()

    if not folder_id:
        return ActionResult(
            success=False,
            message="No folder specified.",
        )

    allowlist = _allowed_folders()
    spec = allowlist.get(folder_id)

    if not spec:
        return ActionResult(
            success=False,
            message="That folder is not approved to open.",
            data={"folder_id": folder_id},
        )

    path = spec.get("path")
    name = spec.get("name", folder_id)

    # Absolute path enforcement
    if not path or not os.path.isabs(path):
        return ActionResult(
            success=False,
            message="That folder path is not allowed.",
        )

    # Existence check (fail calm, no filesystem leakage)
    if not os.path.exists(path):
        return ActionResult(
            success=False,
            message=f"{name} could not be opened.",
        )

    try:
        # Windows Explorer open (detached, no supervision)
        subprocess.Popen(
            ["explorer", path],
            shell=False,
            close_fds=True,
            creationflags=(
                subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            ),
        )

        return ActionResult(
            success=True,
            message=f"Opened {name}.",
            data={"folder_id": folder_id},
        )

    except Exception:
        return ActionResult(
            success=False,
            message=f"{name} could not be opened.",
        )
