from __future__ import annotations

import importlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CAPTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "captures"


class ScreenCaptureEngine:
    """Invocation-time region capture with safe dependency fallback."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or DEFAULT_CAPTURE_DIR

    def capture_region(self, bounds: Mapping[str, Any]) -> dict[str, Any]:
        left = int(bounds.get("left") or 0)
        top = int(bounds.get("top") or 0)
        width = int(bounds.get("width") or 0)
        height = int(bounds.get("height") or 0)
        if width <= 0 or height <= 0:
            return {
                "ok": False,
                "error": "Capture bounds must include positive width and height.",
                "failure_kind": "invalid_bounds",
            }

        try:
            pyautogui = importlib.import_module("pyautogui")
        except ModuleNotFoundError as error:
            return {
                "ok": False,
                "error": f"Capture dependency unavailable: {error}",
                "failure_kind": "missing_dependency",
                "missing_dependency": str(getattr(error, "name", "") or "pyautogui").strip(),
            }
        except Exception as error:
            return {
                "ok": False,
                "error": f"Capture dependency unavailable: {error}",
                "failure_kind": "dependency_unavailable",
            }

        try:
            image = pyautogui.screenshot(region=(left, top, width, height))
            image_path = self._save_image(image)
            return {
                "ok": True,
                "image_path": str(image_path),
                "bounds": {"left": left, "top": top, "width": width, "height": height},
            }
        except Exception as error:
            return {
                "ok": False,
                "error": f"Screen capture failed: {error}",
                "failure_kind": "capture_failed",
            }

    def _save_image(self, image: Any) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        image_path = self.output_dir / f"screen_capture_{timestamp}.png"
        image.save(image_path)
        return image_path
