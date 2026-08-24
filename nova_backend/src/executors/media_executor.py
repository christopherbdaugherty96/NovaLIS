from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class MediaExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    def execute(self, request) -> ActionResult:
        action = (request.params or {}).get("action", "").strip().lower()
        common_meta = {
            "request_id": request.request_id,
            "authority_class": "reversible_local",
            "external_effect": False,
            "reversible": True,
        }
        if action not in {"play", "pause", "resume"}:
            return ActionResult.failure(
                "Invalid media command. Try: play, pause, or resume.",
                request_id=request.request_id,
            )

        if not self.system_control.supports_explicit_media_action(action):
            return ActionResult.failure(
                "Explicit play, pause, and resume are not available on this device yet.",
                data={"action": action},
                **common_meta,
            )

        applied = self.system_control.control_media(action)
        if not applied:
            return ActionResult.failure(
                f"I couldn't {action} media playback on this device right now.",
                data={"action": action},
                **common_meta,
            )

        if action == "play":
            label = "Play"
        elif action == "pause":
            label = "Pause"
        else:
            label = "Resume"

        outcome_reason = (
            "The operating system accepted the media-control request, but "
            "the resulting playback state could not be verified."
        )

        return ActionResult.ok(
            message=(
                f"{label} request sent. "
                "I couldn't verify the resulting playback state."
            ),
            data={
                "action": action,
                "outcome_state": "accepted_unverified",
                "request_accepted": True,
                "effect_verified": False,
            },
            outcome_reason=outcome_reason,
            **common_meta,
        )
