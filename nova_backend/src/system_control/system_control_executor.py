from __future__ import annotations

import os
import platform
import subprocess
import ctypes
import shutil
from pathlib import Path


class SystemControlExecutor:
    """Single OS-action boundary for local system control operations."""

    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_PLAY_PAUSE = 0xB3
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

    @staticmethod
    def _run(args: list[str], timeout: int = 3) -> bool:
        try:
            completed = subprocess.run(args, check=False, timeout=timeout)
            return completed.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _run_capture(args: list[str], timeout: int = 3) -> str:
        try:
            completed = subprocess.run(args, check=False, timeout=timeout, capture_output=True, text=True)
            if completed.returncode != 0:
                return ""
            return (completed.stdout or "").strip()
        except Exception:
            return ""

    @staticmethod
    def _run_applescript(script: str, timeout: int = 3) -> bool:
        return SystemControlExecutor._run(["osascript", "-e", script], timeout=timeout)

    @classmethod
    def _get_windows_brightness(cls) -> int | None:
        script = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
        output = cls._run_capture(["powershell", "-NoProfile", "-Command", script], timeout=5)
        for line in output.splitlines():
            value = line.strip()
            if value.isdigit():
                return max(0, min(int(value), 100))
        return None

    @classmethod
    def _set_windows_brightness(cls, value: int) -> bool:
        bounded = max(0, min(int(value), 100))
        script = (
            "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
            f".WmiSetBrightness(1,{bounded})"
        )
        return cls._run(["powershell", "-NoProfile", "-Command", script], timeout=5)

    def set_volume(self, action: str, level: int | None = None) -> bool:
        system = platform.system()

        try:
            if system == "Linux":
                if action == "set" and level is not None:
                    return self._run(["amixer", "set", "Master", f"{level}%"])
                elif action == "up":
                    return self._run(["amixer", "set", "Master", "5%+"])
                elif action == "down":
                    return self._run(["amixer", "set", "Master", "5%-"])
                else:
                    return False

            if system == "Darwin":
                if action == "set" and level is not None:
                    script = f"set volume output volume {level}"
                elif action == "up":
                    script = "set volume output volume ((output volume of (get volume settings)) + 5)"
                elif action == "down":
                    script = "set volume output volume ((output volume of (get volume settings)) - 5)"
                else:
                    return False
                return self._run_applescript(script)

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

    def control_media(self, action: str) -> bool:
        command = (action or "").strip().lower()
        if command not in {"play", "pause", "resume"}:
            return False

        system = platform.system()
        try:
            if system == "Linux":
                if shutil.which("playerctl") is None:
                    return False
                mapping = {
                    "play": "play",
                    "pause": "pause",
                    "resume": "play",
                }
                return self._run(["playerctl", mapping[command]])

            if system == "Darwin":
                if command in {"play", "resume"}:
                    if self._run_applescript('tell application "Music" to play'):
                        return True
                elif command == "pause":
                    if self._run_applescript('tell application "Music" to pause'):
                        return True
                # Fallback to media key toggle when app-specific script fails.
                return self._run_applescript('tell application "System Events" to key code 16')

            if system == "Windows":
                return self._send_windows_volume_key(self.VK_MEDIA_PLAY_PAUSE, presses=1)

            return False
        except Exception:
            return False

    def set_brightness(self, action: str, level: int | None = None) -> bool:
        command = (action or "").strip().lower()
        if command not in {"up", "down", "set"}:
            return False

        system = platform.system()
        try:
            if system == "Linux":
                if shutil.which("brightnessctl") is None:
                    return False
                if command == "up":
                    return self._run(["brightnessctl", "set", "+5%"])
                if command == "down":
                    return self._run(["brightnessctl", "set", "5%-"])
                if level is None:
                    return False
                bounded = max(0, min(int(level), 100))
                return self._run(["brightnessctl", "set", f"{bounded}%"])

            if system == "Darwin":
                if command == "up":
                    return self._run_applescript('tell application "System Events" to key code 144')
                if command == "down":
                    return self._run_applescript('tell application "System Events" to key code 145')
                if level is None:
                    return False
                bounded = max(0, min(int(level), 100))
                # Coarse deterministic set: dim low, then step up.
                if not self._run_applescript('tell application "System Events" to key code 145'):
                    return False
                presses = max(1, round(bounded / 10))
                for _ in range(presses):
                    if not self._run_applescript('tell application "System Events" to key code 144'):
                        return False
                return True

            if system == "Windows":
                current = self._get_windows_brightness()
                if command == "up":
                    target = 60 if current is None else current + 10
                    return self._set_windows_brightness(target)
                if command == "down":
                    target = 40 if current is None else current - 10
                    return self._set_windows_brightness(target)
                if level is None:
                    return False
                return self._set_windows_brightness(level)

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
