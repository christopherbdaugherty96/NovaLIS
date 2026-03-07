from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


class SystemControlExecutor:
    """Single OS-action boundary for local system control operations."""

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
                # No built-in zero-dependency volume setter is guaranteed.
                # Keep fail-closed and return unsupported for now.
                return False

            return False
        except Exception:
            return False

    def open_path(self, path: Path) -> bool:
        try:
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
