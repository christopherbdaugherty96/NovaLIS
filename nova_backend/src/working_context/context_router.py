from __future__ import annotations

from typing import Any


class WorkingContextRouter:
    """Returns bounded context slices for specific downstream consumers."""

    @staticmethod
    def for_explain(context: dict[str, Any] | None) -> dict[str, Any]:
        data = dict(context or {})
        return {
            "task_type": str(data.get("task_type") or ""),
            "task_goal": str(data.get("task_goal") or ""),
            "active_app": str(data.get("active_app") or ""),
            "active_window": str(data.get("active_window") or ""),
            "active_url": str(data.get("active_url") or ""),
            "selected_file": str(data.get("selected_file") or ""),
            "cursor_target": str(data.get("cursor_target") or ""),
            "current_step": str(data.get("current_step") or ""),
            "last_relevant_object": str(data.get("last_relevant_object") or ""),
            "recent_relevant_turns": list(data.get("recent_relevant_turns") or []),
            "system_context": dict(data.get("system_context") or {}),
        }

    @staticmethod
    def followup_target(context: dict[str, Any] | None) -> str:
        data = dict(context or {})
        for key in ("last_relevant_object", "cursor_target", "selected_file", "task_goal"):
            value = str(data.get(key) or "").strip()
            if value:
                return value
        return ""
