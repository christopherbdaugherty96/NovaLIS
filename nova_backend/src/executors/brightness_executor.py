from __future__ import annotations

from src.actions.action_result import ActionResult


class BrightnessExecutor:
    def execute(self, request) -> ActionResult:
        params = request.params or {}
        action = (params.get("action") or "").strip().lower()
        level = params.get("level")

        if action in {"up", "down"}:
            return ActionResult.ok(
                message=f"Brightness {action}.",
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
            return ActionResult.ok(
                message=f"Brightness set to {value}.",
                request_id=request.request_id,
                authority_class="local_effect",
                external_effect=True,
                reversible=True,
            )

        return ActionResult.failure("Invalid brightness command.", request_id=request.request_id)
