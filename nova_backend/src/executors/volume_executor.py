from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class VolumeExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    def _apply_volume(self, action: str, level: int | None) -> bool:
        return self.system_control.set_volume(action=action, level=level)

    def execute(self, request) -> ActionResult:
        params = request.params or {}
        action = (params.get("action") or "").strip().lower()
        level = params.get("level")
        common_meta = {
            "request_id": request.request_id,
            "authority_class": "local_effect",
            "external_effect": True,
            "reversible": True,
        }

        if action in {"up", "down"}:
            applied = self._apply_volume(action, None)
            if not applied:
                return ActionResult.failure(
                    message="I couldn't adjust volume on this device right now.",
                    **common_meta,
                )
            return ActionResult.ok(message=f"Volume {action}.", **common_meta)

        if action in {"mute", "unmute"}:
            applied = self._apply_volume(action, None)
            if not applied:
                return ActionResult.failure(
                    message=f"I couldn't {action} audio on this device right now.",
                    **common_meta,
                )
            return ActionResult.ok(message=f"Audio {action}d." if action == "mute" else "Audio unmuted.", **common_meta)

        if action == "set":
            try:
                value = int(level)
            except (TypeError, ValueError):
                return ActionResult.failure("Volume level must be a number.", request_id=request.request_id)
            if value < 0 or value > 100:
                return ActionResult.failure("Volume level must be between 0 and 100.", request_id=request.request_id)
            applied = self._apply_volume("set", value)
            if not applied:
                return ActionResult.failure(
                    message="I couldn't set volume on this device right now.",
                    **common_meta,
                )
            return ActionResult.ok(message=f"Volume set to {value}.", **common_meta)

        return ActionResult.failure("Invalid volume command.", request_id=request.request_id)
