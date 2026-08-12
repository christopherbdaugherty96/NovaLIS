from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class VolumeExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    def _apply_volume(self, action: str, level: int | None) -> bool:
        return self.system_control.set_volume(action=action, level=level)

    @staticmethod
    def _accepted_unverified_result(
        *,
        request_id: str | None,
        action: str,
        message: str,
        level: int | None = None,
    ) -> ActionResult:
        outcome_reason = (
            "The operating system accepted the volume control request, but "
            "the resulting system volume could not be verified."
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
            direction = "up" if action == "up" else "down"
            return self._accepted_unverified_result(
                request_id=request.request_id,
                action=action,
                message=(
                    f"Volume-{direction} request sent. "
                    "I couldn't verify the resulting system volume."
                ),
            )

        if action in {"mute", "unmute"}:
            applied = self._apply_volume(action, None)
            if not applied:
                return ActionResult.failure(
                    message=f"I couldn't {action} audio on this device right now.",
                    **common_meta,
                )
            label = "Mute" if action == "mute" else "Unmute"
            return self._accepted_unverified_result(
                request_id=request.request_id,
                action=action,
                message=(
                    f"{label} request sent. "
                    "I couldn't verify the resulting system audio state."
                ),
            )

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
            return self._accepted_unverified_result(
                request_id=request.request_id,
                action="set",
                level=value,
                message=(
                    f"Volume-level request sent for {value}%. "
                    "I couldn't verify the resulting system volume."
                ),
            )

        return ActionResult.failure(
            "Invalid volume command. Try: volume up, volume down, mute, unmute, or set volume to 40.",
            request_id=request.request_id,
        )
