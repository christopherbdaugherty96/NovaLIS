from __future__ import annotations

import os
import platform
import subprocess
import ctypes
import shutil
import re
from pathlib import Path


class SystemControlExecutor:
    """Single OS-action boundary for local system control operations."""

    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_PLAY_PAUSE = 0xB3
    KEYEVENTF_KEYUP = 0x0002

    @staticmethod
    def _workspace_path_roots() -> tuple[Path, ...]:
        roots: list[Path] = []
        seen: set[str] = set()

        def _add(path_value: Path | None) -> None:
            if path_value is None:
                return
            try:
                resolved = path_value.resolve()
            except Exception:
                return
            key = str(resolved).lower()
            if key in seen or not resolved.exists():
                return
            seen.add(key)
            roots.append(resolved)

        try:
            cwd = Path.cwd().resolve()
        except Exception:
            cwd = None

        if cwd is None:
            return ()

        _add(cwd)
        for candidate in [cwd, *cwd.parents]:
            try:
                if (candidate / ".git").exists():
                    _add(candidate)
                    break
            except Exception:
                continue

        return tuple(roots)

    @staticmethod
    def _allowed_path_roots() -> tuple[Path, ...]:
        home = Path.home().resolve()
        return (
            home,
            (home / "Documents").resolve(),
            (home / "Downloads").resolve(),
            (home / "Desktop").resolve(),
            (home / "Pictures").resolve(),
            *SystemControlExecutor._workspace_path_roots(),
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

    @staticmethod
    def _parse_float(text: str) -> float | None:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text or "")
        if not match:
            return None
        try:
            return float(match.group(1))
        except Exception:
            return None

    @staticmethod
    def _clamp_percent(value: int) -> int:
        return max(0, min(int(value), 100))

    @classmethod
    def _set_volume_linux(cls, action: str, level: int | None = None) -> bool:
        if action == "set" and level is not None:
            bounded = cls._clamp_percent(level)
            if shutil.which("amixer") is not None and cls._run(["amixer", "set", "Master", f"{bounded}%"]):
                return True
            if shutil.which("pactl") is not None and cls._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{bounded}%"]):
                return True
            return False

        if action == "up":
            if shutil.which("amixer") is not None and cls._run(["amixer", "set", "Master", "5%+"]):
                return True
            if shutil.which("pactl") is not None and cls._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"]):
                return True
            return False

        if action == "down":
            if shutil.which("amixer") is not None and cls._run(["amixer", "set", "Master", "5%-"]):
                return True
            if shutil.which("pactl") is not None and cls._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"]):
                return True
            return False

        if action == "mute":
            if shutil.which("amixer") is not None and cls._run(["amixer", "set", "Master", "mute"]):
                return True
            if shutil.which("pactl") is not None and cls._run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"]):
                return True
            return False

        if action == "unmute":
            if shutil.which("amixer") is not None and cls._run(["amixer", "set", "Master", "unmute"]):
                return True
            if shutil.which("pactl") is not None and cls._run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"]):
                return True
            return False

        return False

    @classmethod
    def _set_volume_macos(cls, action: str, level: int | None = None) -> bool:
        if action == "set" and level is not None:
            bounded = cls._clamp_percent(level)
            return cls._run_applescript(f"set volume output volume {bounded}")
        if action == "up":
            return cls._run_applescript("set volume output volume ((output volume of (get volume settings)) + 5)")
        if action == "down":
            return cls._run_applescript("set volume output volume ((output volume of (get volume settings)) - 5)")
        if action == "mute":
            return cls._run_applescript("set volume with output muted")
        if action == "unmute":
            return cls._run_applescript("set volume without output muted")
        return False

    @classmethod
    def _get_xrandr_primary_display(cls) -> str | None:
        output = cls._run_capture(["xrandr", "--listmonitors"], timeout=3)
        for line in output.splitlines():
            line = line.strip()
            if not line or ":" not in line or line.lower().startswith("monitors:"):
                continue
            parts = line.split()
            if parts:
                return parts[-1]
        return None

    @classmethod
    def _get_xrandr_brightness(cls, display: str) -> float | None:
        output = cls._run_capture(["xrandr", "--verbose"], timeout=3)
        if not output:
            return None

        in_display = False
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if raw_line and not raw_line.startswith(" "):
                in_display = raw_line.startswith(display + " ")
                continue
            if in_display and line.lower().startswith("brightness:"):
                value = cls._parse_float(line)
                if value is not None:
                    return max(0.1, min(value, 1.0))
        return None

    @classmethod
    def _set_xrandr_brightness(cls, display: str, percent_value: int) -> bool:
        bounded = cls._clamp_percent(percent_value)
        scaled = max(0.1, min(bounded / 100.0, 1.0))
        return cls._run(["xrandr", "--output", display, "--brightness", f"{scaled:.2f}"], timeout=3)

    @classmethod
    def _get_macos_brightness_tool_value(cls) -> float | None:
        if shutil.which("brightness") is None:
            return None
        output = cls._run_capture(["brightness", "-l"], timeout=3)
        # Typical output includes "brightness 0.500000"
        match = re.search(r"brightness\s+([0-9]*\.[0-9]+|[0-9]+)", output, re.IGNORECASE)
        if not match:
            return None
        try:
            value = float(match.group(1))
        except Exception:
            return None
        return max(0.0, min(value, 1.0))

    @classmethod
    def _set_macos_brightness_tool(cls, percent_value: int) -> bool:
        if shutil.which("brightness") is None:
            return False
        bounded = cls._clamp_percent(percent_value)
        scaled = max(0.0, min(bounded / 100.0, 1.0))
        return cls._run(["brightness", f"{scaled:.2f}"], timeout=3)

    def set_volume(self, action: str, level: int | None = None) -> bool:
        system = platform.system()
        command = (action or "").strip().lower()

        try:
            if system == "Linux":
                return self._set_volume_linux(command, level)

            if system == "Darwin":
                return self._set_volume_macos(command, level)

            if system == "Windows":
                if command == "up":
                    return self._send_windows_volume_key(self.VK_VOLUME_UP, presses=2)
                if command == "down":
                    return self._send_windows_volume_key(self.VK_VOLUME_DOWN, presses=2)
                if command == "mute":
                    # Windows exposes a generic toggle key here; fail closed until
                    # a state-aware mute implementation exists.
                    return False
                if command == "unmute":
                    # Windows media key is a toggle; fail closed until
                    # unmute can be implemented explicitly.
                    return False
                if command == "set" and level is not None:
                    bounded = self._clamp_percent(level)
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
                # Windows only exposes a generic play/pause toggle through this
                # path. Fail closed instead of pretending play, pause, and resume
                # are explicit commands.
                return False

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
                    if shutil.which("xrandr") is None:
                        return False
                    display = self._get_xrandr_primary_display()
                    if not display:
                        return False
                    if command == "set":
                        if level is None:
                            return False
                        return self._set_xrandr_brightness(display, level)
                    current = self._get_xrandr_brightness(display)
                    if current is None:
                        current = 0.5
                    step = 0.08
                    next_value = current + step if command == "up" else current - step
                    return self._run(
                        ["xrandr", "--output", display, "--brightness", f"{max(0.1, min(next_value, 1.0)):.2f}"],
                        timeout=3,
                    )
                if command == "up":
                    return self._run(["brightnessctl", "set", "+7%"])
                if command == "down":
                    return self._run(["brightnessctl", "set", "7%-"])
                if level is None:
                    return False
                bounded = self._clamp_percent(level)
                return self._run(["brightnessctl", "set", f"{bounded}%"])

            if system == "Darwin":
                if shutil.which("brightness") is not None:
                    current = self._get_macos_brightness_tool_value()
                    if command == "set":
                        if level is None:
                            return False
                        return self._set_macos_brightness_tool(level)
                    if current is None:
                        current = 0.5
                    delta = 8
                    target = round((current * 100) + (delta if command == "up" else -delta))
                    return self._set_macos_brightness_tool(target)

                if command == "up":
                    return self._run_applescript('tell application "System Events" to key code 144')
                if command == "down":
                    return self._run_applescript('tell application "System Events" to key code 145')
                if level is None:
                    return False
                bounded = self._clamp_percent(level)
                # Coarse deterministic set: dim low, then step up.
                for _ in range(16):
                    self._run_applescript('tell application "System Events" to key code 145')
                presses = max(0, min(16, round(bounded / 6.25)))
                for _ in range(presses):
                    if not self._run_applescript('tell application "System Events" to key code 144'):
                        return False
                return True

            if system == "Windows":
                current = self._get_windows_brightness()
                if command == "up":
                    target = 55 if current is None else current + 10
                    return self._set_windows_brightness(target)
                if command == "down":
                    target = 45 if current is None else current - 10
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
                completed = subprocess.run(["open", str(path)], check=False, timeout=3)
                return completed.returncode == 0
            if system == "Linux":
                completed = subprocess.run(["xdg-open", str(path)], check=False, timeout=3)
                return completed.returncode == 0
            return False
        except Exception:
            return False
