from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorkingContextState:
    """Session-scoped task context model (non-persistent)."""

    task_type: str = ""
    task_goal: str = ""
    active_app: str = ""
    active_window: str = ""
    active_url: str = ""
    selected_file: str = ""
    selected_text: str = ""
    cursor_target: str = ""
    current_step: str = ""
    last_relevant_object: str = ""
    recent_relevant_turns: list[str] = field(default_factory=list)
    open_report_id: str = ""
    system_context: dict[str, str] = field(default_factory=dict)
    confidence_notes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type,
            "task_goal": self.task_goal,
            "active_app": self.active_app,
            "active_window": self.active_window,
            "active_url": self.active_url,
            "selected_file": self.selected_file,
            "selected_text": self.selected_text,
            "cursor_target": self.cursor_target,
            "current_step": self.current_step,
            "last_relevant_object": self.last_relevant_object,
            "recent_relevant_turns": list(self.recent_relevant_turns),
            "open_report_id": self.open_report_id,
            "system_context": dict(self.system_context),
            "confidence_notes": dict(self.confidence_notes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "WorkingContextState":
        data = dict(payload or {})
        return cls(
            task_type=str(data.get("task_type") or "").strip(),
            task_goal=str(data.get("task_goal") or "").strip(),
            active_app=str(data.get("active_app") or "").strip(),
            active_window=str(data.get("active_window") or "").strip(),
            active_url=str(data.get("active_url") or "").strip(),
            selected_file=str(data.get("selected_file") or "").strip(),
            selected_text=str(data.get("selected_text") or "").strip(),
            cursor_target=str(data.get("cursor_target") or "").strip(),
            current_step=str(data.get("current_step") or "").strip(),
            last_relevant_object=str(data.get("last_relevant_object") or "").strip(),
            recent_relevant_turns=[str(item).strip() for item in list(data.get("recent_relevant_turns") or []) if str(item).strip()],
            open_report_id=str(data.get("open_report_id") or "").strip(),
            system_context={
                str(k): str(v)
                for k, v in dict(data.get("system_context") or {}).items()
                if str(k).strip()
            },
            confidence_notes={
                str(k): str(v)
                for k, v in dict(data.get("confidence_notes") or {}).items()
                if str(k).strip()
            },
        )
