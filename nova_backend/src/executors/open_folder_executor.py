from __future__ import annotations

import ctypes
import platform
import time
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
    _VISIBLE_WINDOW_ATTEMPTS = 6
    _VISIBLE_WINDOW_POLL_SECONDS = 0.2

    def __init__(self) -> None:
        self.system_control = SystemControlExecutor()

    @staticmethod
    def _visible_explorer_titles() -> tuple[str, ...]:
        """Return visible Windows File Explorer titles without assuming pywin32."""
        if platform.system() != "Windows":
            return ()

        try:
            user32 = ctypes.windll.user32  # type: ignore[attr-defined]
            callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            titles: list[str] = []

            @callback_type
            def _collect(hwnd, _lparam):
                if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                    return True

                class_name = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_name, len(class_name))
                if class_name.value != "CabinetWClass":
                    return True

                title_length = int(user32.GetWindowTextLengthW(hwnd) or 0)
                if title_length <= 0:
                    return True
                title = ctypes.create_unicode_buffer(title_length + 1)
                user32.GetWindowTextW(hwnd, title, len(title))
                if title.value.strip():
                    titles.append(title.value.strip())
                return True

            user32.EnumWindows(_collect, 0)
            return tuple(titles)
        except Exception:
            return ()

    def _visible_folder_verified(self, folder: Path) -> bool:
        """Conservatively verify that an Explorer window for the folder is visible."""
        if platform.system() != "Windows" or not folder.is_dir():
            return False

        target_name = folder.name.strip().casefold()
        if not target_name:
            return False

        for attempt in range(self._VISIBLE_WINDOW_ATTEMPTS):
            titles = self._visible_explorer_titles()
            if any(title.casefold() == target_name for title in titles):
                return True
            if attempt + 1 < self._VISIBLE_WINDOW_ATTEMPTS:
                time.sleep(self._VISIBLE_WINDOW_POLL_SECONDS)
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
