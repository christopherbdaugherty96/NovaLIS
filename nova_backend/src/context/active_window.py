from __future__ import annotations

import importlib
from typing import Any


def get_active_window() -> dict[str, Any]:
    """
    Return a best-effort snapshot of the current active window.

    This module is read-only and intentionally tolerant of missing platform
    dependencies so Phase-4.5 scaffolding can run on any developer machine.
    """
    try:
        pygetwindow = importlib.import_module("pygetwindow")
    except Exception:
        return {
            "title": "",
            "app": "",
            "bounds": None,
        }

    try:
        window = pygetwindow.getActiveWindow()
        if window is None:
            return {"title": "", "app": "", "bounds": None}

        title = str(getattr(window, "title", "") or "").strip()
        left = int(getattr(window, "left", 0) or 0)
        top = int(getattr(window, "top", 0) or 0)
        width = int(getattr(window, "width", 0) or 0)
        height = int(getattr(window, "height", 0) or 0)
        return {
            "title": title,
            "app": "",
            "bounds": {
                "left": left,
                "top": top,
                "width": max(0, width),
                "height": max(0, height),
            },
        }
    except Exception:
        return {
            "title": "",
            "app": "",
            "bounds": None,
        }
