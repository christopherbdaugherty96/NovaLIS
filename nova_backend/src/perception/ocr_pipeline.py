from __future__ import annotations

import importlib


class OCRPipeline:
    """Optional OCR extraction helper for screen captures."""

    def extract_text(self, image_path: str) -> str:
        path = str(image_path or "").strip()
        if not path:
            return ""

        try:
            pytesseract = importlib.import_module("pytesseract")
            image_module = importlib.import_module("PIL.Image")
        except Exception:
            return ""

        try:
            with image_module.open(path) as image:
                return str(pytesseract.image_to_string(image) or "").strip()
        except Exception:
            return ""
