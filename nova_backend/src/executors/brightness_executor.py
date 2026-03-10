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
            "authority_class": "local_effect",
            "external_effect": True,
            "reversible": True,
        }

        if action in {"up", "down"}:
            applied = self.system_control.set_brightness(action, None)
            if not applied:
                return ActionResult.failure(
                    message="I couldn't adjust brightness on this device right now.",
                    **common_meta,
                )
            return ActionResult.ok(message=f"Brightness {action}.", **common_meta)

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
            return ActionResult.ok(message=f"Brightness set to {value}.", **common_meta)

        return ActionResult.failure("Invalid brightness command.", request_id=request.request_id)
