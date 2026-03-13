from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class MediaExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    def execute(self, request) -> ActionResult:
        action = (request.params or {}).get("action", "").strip().lower()
        if action not in {"play", "pause", "resume"}:
            return ActionResult.failure(
                "Invalid media command. Try: play, pause, or resume.",
                request_id=request.request_id,
            )

        applied = self.system_control.control_media(action)
        if not applied:
            return ActionResult.failure(
                f"I couldn't {action} media playback on this device right now.",
                data={"action": action},
                request_id=request.request_id,
                authority_class="local_effect",
                external_effect=True,
                reversible=True,
            )

        if action == "play":
            msg = "Playback started."
        elif action == "pause":
            msg = "Playback paused."
        else:
            msg = "Playback resumed."

        return ActionResult.ok(
            message=msg,
            data={"action": action},
            request_id=request.request_id,
            authority_class="local_effect",
            external_effect=True,
            reversible=True,
        )
