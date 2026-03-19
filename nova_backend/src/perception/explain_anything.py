from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ExplainRoute:
    kind: str
    reason: str
    file_path: str = ""


class ExplainAnythingRouter:
    """
    Lightweight read-only routing for "explain this" interactions.

    This router chooses context source only. It does not execute actions.
    """

    @staticmethod
    def _looks_like_path(value: str) -> bool:
        text = str(value or "").strip()
        if not text:
            return False
        if "/" in text or "\\" in text:
            return True
        if "." in text and len(text.rsplit(".", 1)[-1]) <= 6:
            return True
        return False

    @staticmethod
    def _extract_file_path(params: Mapping[str, Any] | None) -> str:
        payload = dict(params or {})
        working_context = dict(payload.get("working_context") or {})
        candidates = (
            payload.get("file_path"),
            payload.get("selected_file"),
            payload.get("path"),
            working_context.get("selected_file"),
        )
        for item in candidates:
            value = str(item or "").strip()
            if value and ExplainAnythingRouter._looks_like_path(value):
                return value
        return ""

    @staticmethod
    def _query_prefers_file(query_text: str) -> bool:
        lowered = str(query_text or "").strip().lower()
        if not lowered:
            return False
        file_markers = (
            "this file",
            "this document",
            "this doc",
            "this code",
            "this error log",
            "in the file",
            "from the file",
        )
        return any(marker in lowered for marker in file_markers)

    @staticmethod
    def _query_prefers_screen(query_text: str) -> bool:
        lowered = str(query_text or "").strip().lower()
        if not lowered:
            return False
        screen_markers = (
            "what am i looking at",
            "what i'm looking at",
            "what is on my screen",
            "what's on my screen",
            "view screen",
            "view the screen",
            "view this screen",
            "this screen",
            "on my screen",
        )
        return any(marker in lowered for marker in screen_markers)

    def decide(self, *, params: Mapping[str, Any] | None, context_snapshot: Mapping[str, Any] | None) -> ExplainRoute:
        file_path = self._extract_file_path(params)
        if file_path:
            return ExplainRoute(kind="file", reason="file_selected", file_path=file_path)

        snapshot = dict(context_snapshot or {})
        payload = dict(params or {})
        working_context = dict(payload.get("working_context") or {})
        query_text = str(payload.get("query") or "").strip()
        task_type = str(working_context.get("task_type") or "").strip().lower()
        selected_file = str(working_context.get("selected_file") or "").strip()
        followup = bool(payload.get("followup"))

        if selected_file and (self._query_prefers_file(query_text) or task_type in {"document_review", "code_analysis", "error_debugging"}):
            return ExplainRoute(kind="file", reason="working_context_file", file_path=selected_file)
        if selected_file and followup and not str(working_context.get("active_url") or "").strip():
            return ExplainRoute(kind="file", reason="followup_file", file_path=selected_file)

        browser = dict(snapshot.get("browser") or {})
        if bool(browser.get("is_browser")) or str(working_context.get("active_url") or "").strip():
            return ExplainRoute(kind="webpage", reason="browser_active")

        cursor = dict(snapshot.get("cursor") or {})
        if (
            int(cursor.get("screen_width") or 0) > 0
            and int(cursor.get("screen_height") or 0) > 0
        ) or str(working_context.get("active_window") or "").strip():
            return ExplainRoute(kind="screen", reason="cursor_region_available")

        if self._query_prefers_screen(query_text):
            return ExplainRoute(kind="screen", reason="explicit_screen_query")

        if selected_file:
            return ExplainRoute(kind="file", reason="fallback_file_context", file_path=selected_file)

        return ExplainRoute(kind="clarify", reason="insufficient_context")

    @staticmethod
    def clarification_message() -> str:
        return (
            "I need a target to explain. You can say 'explain this' while your screen is visible, "
            "or provide a file path."
        )

    @staticmethod
    def is_supported_file(path_text: str) -> bool:
        path = Path(path_text)
        suffix = path.suffix.lower()
        return suffix in {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".xml",
            ".csv",
            ".log",
            ".ini",
            ".cfg",
        }
