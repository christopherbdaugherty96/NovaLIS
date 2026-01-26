"""
NovaLIS — Phase-2 Handler: open_app

Purpose:
- Launch a single, explicitly approved application
- Enforce strict allowlist behavior
- Execute exactly one OS action
- Fail closed on any violation

PHASE-2 RULES:
- Deterministic only
- No discovery
- No retries
- No background supervision
- No user-supplied arguments
- One action per call
"""

import os
import subprocess
import logging
from typing import Dict, Any, Optional

from ...actions.action_request import ActionRequest
from ...actions.action_result import ActionResult
from ...actions.action_types import ActionType

logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# LOCAL ALLOWLIST (Phase-2 V1)
# ----------------------------------------------------------

def _allowed_apps() -> Dict[str, Dict[str, Any]]:
    """
    Return the Phase-2 approved application allowlist.
    
    RULES:
    - Absolute paths only
    - No PATH lookup
    - No dynamic discovery
    - May move to nova_config.py in Phase-3+
    """
    return {
        "chrome": {
            "name": "Google Chrome",
            "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        },
        "notepad": {
            "name": "Notepad",
            "path": r"C:\Windows\System32\notepad.exe",
        },
        "calculator": {
            "name": "Calculator",
            "path": r"C:\Windows\System32\calc.exe",
        },
    }


# ----------------------------------------------------------
# EXECUTION HANDLER
# ----------------------------------------------------------

def open_app(action: ActionRequest) -> ActionResult:
    """
    Execute a Phase-2 OPEN_APP action.
    
    This handler:
    - Assumes confirmation has already occurred
    - Executes immediately
    - Returns exactly one ActionResult
    """
    
    # Defensive type check (execution boundary invariant)
    if not isinstance(action, ActionRequest):
        logger.warning("Invalid action request type")
        return ActionResult(
            success=False,
            message="Invalid action request.",
        )

    # ✅ CORRECTED: Changed from LAUNCH_APP to OPEN_APP
    if action.action_type is not ActionType.OPEN_APP:
        logger.warning(f"Wrong action type: {action.action_type}")
        return ActionResult(
            success=False,
            message="Invalid action type.",
        )

    payload = action.payload or {}
    app_id = (payload.get("app_id") or "").strip().lower()

    if not app_id:
        logger.warning("No application specified in payload")
        return ActionResult(
            success=False,
            message="No application specified.",
        )

    allowlist = _allowed_apps()
    spec = allowlist.get(app_id)

    if not spec:
        logger.info(f"App not in allow-list: {app_id}")
        return ActionResult(
            success=False,
            message="I can't launch that app right now.",
            data={"app_id": app_id},
        )

    path = spec.get("path")
    name = spec.get("name", app_id)

    # Absolute path enforcement
    if not path or not os.path.isabs(path):
        logger.warning(f"Path not absolute: {path}")
        return ActionResult(
            success=False,
            message="That app path is not allowed.",
        )

    # ✅ ADDED: Chrome path fallback (bounded, deterministic)
    if app_id == "chrome" and not os.path.exists(path):
        logger.info(f"Chrome not found at primary path: {path}")
        alt_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        if os.path.exists(alt_path):
            path = alt_path
            logger.info(f"Using alternative Chrome path: {path}")
        else:
            logger.warning("Chrome not found at any known location")
            return ActionResult(
                success=False,
                message="Google Chrome could not be found on your system.",
            )

    # Existence check (fail calm, no filesystem leakage)
    if not os.path.exists(path):
        logger.warning(f"App not found: {path}")
        return ActionResult(
            success=False,
            message=f"{name} could not be launched.",
        )

    try:
        # Build command — no user-supplied args allowed
        cmd = [path]
        
        logger.info(f"Launching app: {name} from {path}")
        
        subprocess.Popen(
            cmd,
            shell=False,
            close_fds=True,
            creationflags=(
                subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            ),
        )

        logger.info(f"Successfully launched: {name}")
        return ActionResult(
            success=True,
            message=f"Opened {name}.",
            data={"app_id": app_id},
        )

    except Exception as e:
        logger.exception(f"Failed to launch {name}: {e}")
        return ActionResult(
            success=False,
            message=f"{name} could not be launched.",
        )