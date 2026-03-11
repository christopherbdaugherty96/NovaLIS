from __future__ import annotations

import importlib
from typing import Any, Mapping


def locate_cursor() -> dict[str, Any]:
    """Return cursor and display geometry using optional local dependencies."""
    try:
        pyautogui = importlib.import_module("pyautogui")
        x, y = pyautogui.position()
        size = pyautogui.size()
        return {
            "x": int(x),
            "y": int(y),
            "screen_width": int(getattr(size, "width", 0) or 0),
            "screen_height": int(getattr(size, "height", 0) or 0),
        }
    except Exception:
        return {"x": 0, "y": 0, "screen_width": 0, "screen_height": 0}


def build_cursor_region(cursor: Mapping[str, Any] | None, size: int = 800) -> dict[str, int]:
    """Build a bounded capture region around the cursor position."""
    payload = dict(cursor or {})
    region_size = max(128, min(int(size or 800), 1600))
    x = int(payload.get("x") or 0)
    y = int(payload.get("y") or 0)
    screen_width = int(payload.get("screen_width") or 0)
    screen_height = int(payload.get("screen_height") or 0)

    half = region_size // 2
    left = max(0, x - half)
    top = max(0, y - half)

    width = region_size
    height = region_size

    if screen_width > 0:
        width = min(region_size, screen_width)
        left = min(left, max(0, screen_width - width))
    if screen_height > 0:
        height = min(region_size, screen_height)
        top = min(top, max(0, screen_height - height))

    return {
        "left": int(left),
        "top": int(top),
        "width": int(width),
        "height": int(height),
    }
