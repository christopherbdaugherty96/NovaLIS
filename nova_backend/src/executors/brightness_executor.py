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

        if action in {"up", "down"}:
            applied = self.system_control.set_brightness(action, None)
            return ActionResult.ok(
                message=f"Brightness {action}." if applied else f"Brightness {action} requested.",
                request_id=request.request_id,
                authority_class="local_effect",
                external_effect=True,
                reversible=True,
            )

        if action == "set":
            try:
                value = int(level)
            except (TypeError, ValueError):
                return ActionResult.failure("Brightness level must be a number.", request_id=request.request_id)
            if value < 0 or value > 100:
                return ActionResult.failure("Brightness must be between 0 and 100.", request_id=request.request_id)
            applied = self.system_control.set_brightness("set", value)
            return ActionResult.ok(
                message=f"Brightness set to {value}." if applied else f"Brightness set requested: {value}.",
                request_id=request.request_id,
                authority_class="local_effect",
                external_effect=True,
                reversible=True,
            )

        return ActionResult.failure("Invalid brightness command.", request_id=request.request_id)
