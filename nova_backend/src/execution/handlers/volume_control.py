"""
NovaLIS — Phase-2 Handler: volume_control

Purpose:
- Adjust system volume deterministically.

LOCKED RULES:
- One action per call
- Explicit level OR explicit delta (not both)
- No tracking, no polling, no background state
- No retries
- No inference
- No chaining
- Return ActionResult only
"""

from __future__ import annotations

from typing import Any, Dict

from ...actions.action_request import ActionRequest
from ...actions.action_result import ActionResult


# ------------------------------------------------------------
# Phase-2 constraints
# ------------------------------------------------------------

_MIN_VOLUME = 0
_MAX_VOLUME = 100


def volume_control(action: ActionRequest) -> ActionResult:
    """
    Execute a volume control action.

    Expected payload (exactly ONE of the following):
      - level: int   (0–100)
      - delta: int   (e.g. +5, -10)

    Examples:
      payload={"level": 30}
      payload={"delta": -5}
    """
    if not isinstance(action, ActionRequest):
        return ActionResult(success=False, message="Invalid action request.")

    payload: Dict[str, Any] = action.payload or {}

    level = payload.get("level")
    delta = payload.get("delta")

    # Enforce exactly one mode
    if (level is None and delta is None) or (level is not None and delta is not None):
        return ActionResult(
            success=False,
            message="Specify either a volume level or a volume change.",
        )

    # --------------------------------------------------------
    # Resolve target volume
    # --------------------------------------------------------

    try:
        if level is not None:
            if not isinstance(level, int):
                return ActionResult(success=False, message="Volume level must be a number.")

            target = max(_MIN_VOLUME, min(_MAX_VOLUME, level))

        else:
            if not isinstance(delta, int):
                return ActionResult(success=False, message="Volume change must be a number.")

            # Phase-2 rule:
            # We do NOT track current volume.
            # We rely on the OS mixer to clamp internally.
            target = delta

    except Exception:
        return ActionResult(success=False, message="Invalid volume parameters.")

    # --------------------------------------------------------
    # Execute (Windows)
    # --------------------------------------------------------

    try:
        # Windows-safe approach using nircmd or similar tool is NOT allowed
        # unless explicitly installed and allowlisted.
        #
        # Phase-2 recommendation:
        # Use pycaw if already installed; otherwise, defer execution.
        #
        # For now, we fail closed if volume backend is unavailable.

        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if level is not None:
            volume.SetMasterVolumeLevelScalar(target / 100.0, None)
            message = f"Volume set to {target}%."
        else:
            current = volume.GetMasterVolumeLevelScalar()
            new_level = max(
                0.0, min(1.0, current + (target / 100.0))
            )
            volume.SetMasterVolumeLevelScalar(new_level, None)
            message = "Volume adjusted."

        return ActionResult(
            success=True,
            message=message,
            data={"mode": "level" if level is not None else "delta"},
        )

    except Exception:
        # Fail closed, calmly
        return ActionResult(
            success=False,
            message="Volume could not be adjusted.",
        )
