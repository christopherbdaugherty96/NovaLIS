from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class BrightnessExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    @staticmethod
    def _accepted_unverified_result(
        *,
        request_id: str | None,
        action: str,
        message: str,
        level: int | None = None,
    ) -> ActionResult:
        outcome_reason = (
            "The operating system accepted the brightness control request, but "
            "the resulting display brightness could not be verified."
        )
        structured_data = {
            "action": action,
            "outcome_state": "accepted_unverified",
            "request_accepted": True,
            "effect_verified": False,
        }
        if level is not None:
            structured_data["level"] = level
        return ActionResult.ok(
            message=message,
            data=structured_data,
            request_id=request_id,
            authority_class="reversible_local",
            external_effect=False,
            reversible=True,
            outcome_reason=outcome_reason,
        )

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
            direction = "up" if action == "up" else "down"
            return self._accepted_unverified_result(
                request_id=request.request_id,
                action=action,
                message=(
                    f"Brightness-{direction} request sent. "
                    "I couldn't verify the resulting display brightness."
                ),
            )

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
            return self._accepted_unverified_result(
                request_id=request.request_id,
                action="set",
                level=value,
                message=(
                    f"Brightness-level request sent for {value}%. "
                    "I couldn't verify the resulting display brightness."
                ),
            )

        return ActionResult.failure(
            "Invalid brightness command. Try: brightness up, brightness down, or set brightness to 65.",
            request_id=request.request_id,
        )
