from __future__ import annotations

import re
from typing import Any, Mapping


class VisionAnalyzer:
    """Read-only screen interpretation scaffold."""

    @staticmethod
    def _snippet(text: str, limit: int = 220) -> str:
        clean = re.sub(r"\s+", " ", str(text or "")).strip()
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    def analyze(
        self,
        *,
        image_path: str,
        ocr_text: str,
        context_snapshot: Mapping[str, Any] | None = None,
        user_query: str = "",
    ) -> dict[str, Any]:
        snapshot = dict(context_snapshot or {})
        active_window = dict(snapshot.get("active_window") or {})
        browser = dict(snapshot.get("browser") or {})
        system = dict(snapshot.get("system") or {})

        page_title = str(browser.get("page_title") or active_window.get("title") or "").strip()
        os_name = str(system.get("os") or "").strip()
        text_snippet = self._snippet(ocr_text, limit=240)
        query = str(user_query or "").strip()

        summary_lines = []
        if page_title:
            summary_lines.append(f"You appear to be viewing: {page_title}.")
        if os_name:
            summary_lines.append(f"Detected environment: {os_name}.")
        if text_snippet:
            summary_lines.append(f"Visible text signal: {text_snippet}")
        else:
            summary_lines.append("I captured the region, but OCR text is limited.")
        if query:
            summary_lines.append(f"Request interpreted as: {query}.")

        return {
            "summary": " ".join(summary_lines),
            "confidence": 0.55 if text_snippet else 0.30,
            "signals": {
                "page_title": page_title,
                "ocr_snippet": text_snippet,
                "os": os_name,
                "image_path": str(image_path or ""),
            },
        }
