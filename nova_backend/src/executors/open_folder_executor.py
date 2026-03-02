from __future__ import annotations

from pathlib import Path

from src.actions.action_result import ActionResult


PRESET_FOLDERS = {
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
    "desktop": Path.home() / "Desktop",
    "pictures": Path.home() / "Pictures",
}


class OpenFolderExecutor:
    def execute(self, request) -> ActionResult:
        target = ((request.params or {}).get("target") or "").strip().lower()
        folder = PRESET_FOLDERS.get(target)
        if folder is None:
            return ActionResult.failure("Preset folder not available.", request_id=request.request_id)

        return ActionResult.ok(
            message=f"Opened {target}.",
            data={"path": str(folder)},
            request_id=request.request_id,
            authority_class="local_effect",
            external_effect=True,
            reversible=True,
        )
