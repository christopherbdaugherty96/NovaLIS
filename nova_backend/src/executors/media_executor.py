from __future__ import annotations

from src.actions.action_result import ActionResult


class MediaExecutor:
    def execute(self, request) -> ActionResult:
        action = (request.params or {}).get("action", "").strip().lower()
        if action not in {"play", "pause", "resume"}:
            return ActionResult.failure("Invalid media command.", request_id=request.request_id)

        label = "resumed" if action == "resume" else f"{action}ed" if action.endswith("e") else f"{action}"
        if action == "play":
            msg = "Playback started."
        elif action == "pause":
            msg = "Playback paused."
        else:
            msg = "Playback resumed."

        return ActionResult.ok(
            message=msg,
            request_id=request.request_id,
            authority_class="local_effect",
            external_effect=True,
            reversible=True,
        )
