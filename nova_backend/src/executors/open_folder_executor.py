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

    @staticmethod
    def _trusted_visible_explorer_paths() -> tuple[Path, ...]:
        """Return path-bound Explorer evidence from a trusted observer.

        The current runtime has no reliable path-bound Windows observer. An
        empty result keeps launch outcomes accepted-unverified instead of using
        a window title as evidence for a specific filesystem path.
        """
        return ()

    @staticmethod
    def _normalized_path(path: Path) -> str:
        try:
            resolved = path.expanduser().resolve(strict=False)
        except Exception:
            return ""
        return str(resolved).rstrip("\\/").casefold()

    def _visible_folder_verified(self, folder: Path) -> bool:
        """Require exact normalized-path evidence before claiming visible success."""
        requested_path = self._normalized_path(folder)
        if not requested_path:
            return False

        for visible_path in self._trusted_visible_explorer_paths():
            if self._normalized_path(visible_path) == requested_path:
                return True
        return False

    @staticmethod
    def _rejected_data(*, requested_path: str = "") -> dict:
        data = {
            "outcome_state": "rejected",
            "launch_request_accepted": False,
            "visible_effect_verified": False,
        }
        if requested_path:
            data["requested_path"] = requested_path
        return data

    def _accepted_result(self, request, *, candidate: Path, item_label: str, target: str = "") -> ActionResult:
        # Presets have a bounded user-facing target name that can be matched to
        # an Explorer title. Arbitrary explicit paths remain accepted-unverified.
        visible_verified = bool(target) and self._visible_folder_verified(candidate)
        outcome_state = "visible_verified" if visible_verified else "accepted_unverified"
        data = {
            "path": str(candidate),
            "opened_kind": item_label,
            "outcome_state": outcome_state,
            "launch_request_accepted": True,
            "visible_effect_verified": visible_verified,
        }

        if visible_verified:
            message = (
                f"Opened your {target} folder: {candidate}"
                if target
                else f"Opened {item_label}: {candidate}"
            )
            outcome_reason = "A visible File Explorer window matching the requested folder was verified."
        else:
            display_name = target.title() if target else str(candidate)
            if candidate.is_dir():
                message = (
                    f"Open request sent for {display_name}. "
                    "I couldn't verify that File Explorer became visible."
                )
                outcome_reason = (
                    "The operating system accepted the open request, but a visible File Explorer "
                    "window could not be verified."
                )
            else:
                message = (
                    f"Open request sent for {display_name}. "
                    "I couldn't verify that the requested item became visible."
                )
                outcome_reason = (
                    "The operating system accepted the open request, but the requested item "
                    "could not be verified as visible."
                )

        return ActionResult.ok(
            message=message,
            data=data,
            request_id=request.request_id,
            authority_class="reversible_local",
            external_effect=False,
            reversible=True,
            outcome_reason=outcome_reason,
        )

    def execute(self, request) -> ActionResult:
        params = request.params or {}
        explicit_path = str(params.get("path") or "").strip()
        if explicit_path:
            candidate = Path(explicit_path).expanduser()
            if not candidate.exists():
                return ActionResult.failure(
                    f"I couldn't find that path: {candidate}",
                    data=self._rejected_data(requested_path=str(candidate)),
                    request_id=request.request_id,
                )
            if not self.system_control.open_path(candidate):
                return ActionResult.failure(
                    "I couldn't open that path on this system.",
                    data=self._rejected_data(requested_path=str(candidate)),
                    request_id=request.request_id,
                )
            item_label = "folder" if candidate.is_dir() else "path"
            return self._accepted_result(request, candidate=candidate, item_label=item_label)

        target = str(params.get("target") or "").strip().lower()
        folder = PRESET_FOLDERS.get(target)
        if folder is None:
            available = ", ".join(sorted(PRESET_FOLDERS.keys()))
            return ActionResult.failure(
                f"I couldn't match that preset folder. Try one of: {available}.",
                data=self._rejected_data(),
                request_id=request.request_id,
            )
        if not folder.exists():
            return ActionResult.failure(
                f"The {target} folder was not found on this system.",
                data=self._rejected_data(requested_path=str(folder)),
                request_id=request.request_id,
            )
        if not self.system_control.open_path(folder):
            return ActionResult.failure(
                "I couldn't open that folder on this system.",
                data=self._rejected_data(requested_path=str(folder)),
                request_id=request.request_id,
            )

        return self._accepted_result(
            request,
            candidate=folder,
            item_label="folder",
            target=target,
        )
