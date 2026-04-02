from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class BrightnessExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

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

        if action in {"up", "down"}:
            applied = self.system_control.set_brightness(action, None)
            if not applied:
                return ActionResult.failure(
                    message="I couldn't adjust brightness on this device right now.",
                    **common_meta,
                )
            message = "Turned the brightness up." if action == "up" else "Turned the brightness down."
            return ActionResult.ok(message=message, data={"action": action}, **common_meta)

        if action == "set":
            try:
                value = int(level)
            except (TypeError, ValueError):
                return ActionResult.failure("Brightness level must be a number.", request_id=request.request_id)
            if value < 0 or value > 100:
                return ActionResult.failure("Brightness must be between 0 and 100.", request_id=request.request_id)
            applied = self.system_control.set_brightness("set", value)
            if not applied:
                return ActionResult.failure(
                    message="I couldn't set brightness on this device right now.",
                    **common_meta,
                )
            return ActionResult.ok(message=f"Set brightness to {value}%.", data={"action": "set", "level": value}, **common_meta)

        return ActionResult.failure(
            "Invalid brightness command. Try: brightness up, brightness down, or set brightness to 65.",
            request_id=request.request_id,
        )
