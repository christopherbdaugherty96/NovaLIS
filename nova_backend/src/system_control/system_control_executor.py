from __future__ import annotations

import os
import platform
import subprocess
import ctypes
from pathlib import Path


class SystemControlExecutor:
    """Single OS-action boundary for local system control operations."""

    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    KEYEVENTF_KEYUP = 0x0002

    @staticmethod
    def _allowed_path_roots() -> tuple[Path, ...]:
        home = Path.home().resolve()
        return (
            home,
            (home / "Documents").resolve(),
            (home / "Downloads").resolve(),
            (home / "Desktop").resolve(),
            (home / "Pictures").resolve(),
        )

    @classmethod
    def _is_allowed_path(cls, path: Path) -> bool:
        try:
            resolved = path.expanduser().resolve()
        except Exception:
            return False

        for root in cls._allowed_path_roots():
            try:
                if resolved == root or resolved.is_relative_to(root):
                    return True
            except Exception:
                continue
        return False

    @classmethod
    def _send_windows_volume_key(cls, vk_code: int, presses: int = 1) -> bool:
        try:
            user32 = ctypes.windll.user32  # type: ignore[attr-defined]
            for _ in range(max(1, presses)):
                user32.keybd_event(vk_code, 0, 0, 0)
                user32.keybd_event(vk_code, 0, cls.KEYEVENTF_KEYUP, 0)
            return True
        except Exception:
            return False

    def set_volume(self, action: str, level: int | None = None) -> bool:
        system = platform.system()

        try:
            if system == "Linux":
                if action == "set" and level is not None:
                    subprocess.run(["amixer", "set", "Master", f"{level}%"], check=False, timeout=3)
                elif action == "up":
                    subprocess.run(["amixer", "set", "Master", "5%+"], check=False, timeout=3)
                elif action == "down":
                    subprocess.run(["amixer", "set", "Master", "5%-"], check=False, timeout=3)
                else:
                    return False
                return True

            if system == "Darwin":
                if action == "set" and level is not None:
                    script = f"set volume output volume {level}"
                elif action == "up":
                    script = "set volume output volume ((output volume of (get volume settings)) + 5)"
                elif action == "down":
                    script = "set volume output volume ((output volume of (get volume settings)) - 5)"
                else:
                    return False
                subprocess.run(["osascript", "-e", script], check=False, timeout=3)
                return True

            if system == "Windows":
                if action == "up":
                    return self._send_windows_volume_key(self.VK_VOLUME_UP, presses=2)
                if action == "down":
                    return self._send_windows_volume_key(self.VK_VOLUME_DOWN, presses=2)
                if action == "set" and level is not None:
                    bounded = max(0, min(int(level), 100))
                    # Coarse deterministic set: drive down to floor, then step up.
                    if not self._send_windows_volume_key(self.VK_VOLUME_DOWN, presses=60):
                        return False
                    up_presses = max(0, round(bounded / 2))
                    return self._send_windows_volume_key(self.VK_VOLUME_UP, presses=up_presses)
                return False

            return False
        except Exception:
            return False

    def open_path(self, path: Path) -> bool:
        try:
            if not self._is_allowed_path(path):
                return False
            system = platform.system()
            if system == "Windows":
                os.startfile(str(path))  # type: ignore[attr-defined]
                return True
            if system == "Darwin":
                subprocess.run(["open", str(path)], check=False, timeout=3)
                return True
            if system == "Linux":
                subprocess.run(["xdg-open", str(path)], check=False, timeout=3)
                return True
            return False
        except Exception:
            return False
