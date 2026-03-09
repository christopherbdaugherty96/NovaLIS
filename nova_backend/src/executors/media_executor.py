from __future__ import annotations

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


class MediaExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    def execute(self, request) -> ActionResult:
        action = (request.params or {}).get("action", "").strip().lower()
        if action not in {"play", "pause", "resume"}:
            return ActionResult.failure("Invalid media command.", request_id=request.request_id)

        applied = self.system_control.control_media(action)
        if action == "play":
            msg = "Playback started." if applied else "Playback start requested."
        elif action == "pause":
            msg = "Playback paused." if applied else "Playback pause requested."
        else:
            msg = "Playback resumed." if applied else "Playback resume requested."

        return ActionResult.ok(
            message=msg,
            request_id=request.request_id,
            authority_class="local_effect",
            external_effect=True,
            reversible=True,
        )
