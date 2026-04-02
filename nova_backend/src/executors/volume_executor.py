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
            "authority_class": "reversible_local",
            "external_effect": False,
            "reversible": True,
        }

        if action and not self.system_control.supports_explicit_volume_action(action):
            if action in {"mute", "unmute"}:
                return ActionResult.failure(
                    "Explicit mute and unmute are not available on this device yet. Try volume up, volume down, or set volume to a level.",
                    **common_meta,
                )
            return ActionResult.failure(
                "That volume command is not available on this device right now.",
                **common_meta,
            )

        if action in {"up", "down"}:
            applied = self._apply_volume(action, None)
            if not applied:
                return ActionResult.failure(
                    message="I couldn't adjust volume on this device right now.",
                    **common_meta,
                )
            message = "Turned the volume up." if action == "up" else "Turned the volume down."
            return ActionResult.ok(message=message, data={"action": action}, **common_meta)

        if action in {"mute", "unmute"}:
            applied = self._apply_volume(action, None)
            if not applied:
                return ActionResult.failure(
                    message=f"I couldn't {action} audio on this device right now.",
                    **common_meta,
                )
            message = "Audio muted." if action == "mute" else "Audio unmuted."
            return ActionResult.ok(message=message, data={"action": action}, **common_meta)

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
            return ActionResult.ok(message=f"Set volume to {value}%.", data={"action": "set", "level": value}, **common_meta)

        return ActionResult.failure(
            "Invalid volume command. Try: volume up, volume down, mute, unmute, or set volume to 40.",
            request_id=request.request_id,
        )
