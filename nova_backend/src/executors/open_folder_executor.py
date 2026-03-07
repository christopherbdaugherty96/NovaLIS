from __future__ import annotations

from pathlib import Path

from src.actions.action_result import ActionResult
from src.system_control.system_control_executor import SystemControlExecutor


PRESET_FOLDERS = {
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
    "desktop": Path.home() / "Desktop",
    "pictures": Path.home() / "Pictures",
}


class OpenFolderExecutor:
    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    def execute(self, request) -> ActionResult:
        params = request.params or {}
        explicit_path = str(params.get("path") or "").strip()
        if explicit_path:
            candidate = Path(explicit_path).expanduser()
            if not candidate.exists():
                return ActionResult.failure("File not found.", request_id=request.request_id)
            if not self.system_control.open_path(candidate):
                return ActionResult.failure("I couldn't open that path on this system.", request_id=request.request_id)
            return ActionResult.ok(
                message=f"Opened path: {candidate}",
                data={"path": str(candidate)},
                request_id=request.request_id,
                authority_class="local_effect",
                external_effect=True,
                reversible=True,
            )

        target = str(params.get("target") or "").strip().lower()
        folder = PRESET_FOLDERS.get(target)
        if folder is None:
            return ActionResult.failure("Preset folder not available.", request_id=request.request_id)
        if not folder.exists():
            return ActionResult.failure(f"The {target} folder was not found on this system.", request_id=request.request_id)
        if not self.system_control.open_path(folder):
            return ActionResult.failure("I couldn't open that folder on this system.", request_id=request.request_id)

        return ActionResult.ok(
            message=f"Opened {target}: {folder}",
            data={"path": str(folder)},
            request_id=request.request_id,
            authority_class="local_effect",
            external_effect=True,
            reversible=True,
        )
