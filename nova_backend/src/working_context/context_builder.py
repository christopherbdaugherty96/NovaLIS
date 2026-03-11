from __future__ import annotations

from typing import Any

from src.working_context.context_pruner import prune_context
from src.working_context.context_signals import (
    infer_goal_from_turn,
    infer_step,
    infer_task_type,
)
from src.working_context.context_state import WorkingContextState


class WorkingContextBuilder:
    """Build and update session-local context from explicit signals."""

    def from_payload(self, payload: dict[str, Any] | None) -> dict[str, Any]:
        state = WorkingContextState.from_dict(payload)
        pruned, _changed = prune_context(state.to_dict())
        return pruned

    def update_for_user_turn(
        self,
        context: dict[str, Any] | None,
        *,
        text: str,
        channel: str,
        intent_family: str = "",
    ) -> tuple[dict[str, Any], list[str], bool]:
        data = self.from_payload(context)
        updated_fields: list[str] = []

        if channel:
            notes = dict(data.get("confidence_notes") or {})
            if notes.get("last_channel") != channel:
                notes["last_channel"] = channel
                data["confidence_notes"] = notes
                updated_fields.append("confidence_notes.last_channel")

        task_type = infer_task_type(text, intent_family=intent_family)
        if task_type and data.get("task_type") != task_type:
            data["task_type"] = task_type
            updated_fields.append("task_type")

        goal = infer_goal_from_turn(text)
        if goal and data.get("task_goal") != goal:
            data["task_goal"] = goal
            updated_fields.append("task_goal")

        step = infer_step(text)
        if step and data.get("current_step") != step:
            data["current_step"] = step
            updated_fields.append("current_step")

        turns = list(data.get("recent_relevant_turns") or [])
        if goal:
            turns.append(goal)
            data["recent_relevant_turns"] = turns
            updated_fields.append("recent_relevant_turns")

        pruned, pruned_changed = prune_context(data)
        changed = bool(updated_fields or pruned_changed)
        return pruned, updated_fields, changed

    def update_from_snapshot(
        self,
        context: dict[str, Any] | None,
        *,
        snapshot: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], list[str], bool]:
        data = self.from_payload(context)
        payload = dict(snapshot or {})
        updated_fields: list[str] = []

        active_window = dict(payload.get("active_window") or {})
        browser = dict(payload.get("browser") or {})
        system = dict(payload.get("system") or {})

        mappings = {
            "active_app": str(active_window.get("app") or "").strip(),
            "active_window": str(active_window.get("title") or "").strip(),
            "active_url": str(browser.get("url") or "").strip(),
            "selected_text": str(browser.get("selected_text") or "").strip(),
        }
        for key, value in mappings.items():
            if value and data.get(key) != value:
                data[key] = value
                updated_fields.append(key)

        page_title = str(browser.get("page_title") or "").strip()
        if page_title and data.get("cursor_target") != page_title:
            data["cursor_target"] = page_title
            updated_fields.append("cursor_target")

        system_context = dict(data.get("system_context") or {})
        os_name = str(system.get("os") or "").strip()
        os_release = str(system.get("os_release") or "").strip()
        hostname = str(system.get("hostname") or "").strip()
        if os_name:
            system_context["os"] = os_name
        if os_release:
            system_context["os_release"] = os_release
        if hostname:
            system_context["hostname"] = hostname
        if system_context != dict(data.get("system_context") or {}):
            data["system_context"] = system_context
            updated_fields.append("system_context")

        pruned, pruned_changed = prune_context(data)
        changed = bool(updated_fields or pruned_changed)
        return pruned, updated_fields, changed

    def apply_patch(
        self,
        context: dict[str, Any] | None,
        *,
        patch: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], list[str], bool]:
        data = self.from_payload(context)
        delta = dict(patch or {})
        updated_fields: list[str] = []

        for key, value in delta.items():
            if key == "system_context":
                merged = dict(data.get("system_context") or {})
                merged.update(
                    {
                        str(k): str(v)
                        for k, v in dict(value or {}).items()
                        if str(k).strip() and str(v).strip()
                    }
                )
                if merged != dict(data.get("system_context") or {}):
                    data["system_context"] = merged
                    updated_fields.append("system_context")
                continue
            if key == "confidence_notes":
                merged = dict(data.get("confidence_notes") or {})
                merged.update(
                    {
                        str(k): str(v)
                        for k, v in dict(value or {}).items()
                        if str(k).strip() and str(v).strip()
                    }
                )
                if merged != dict(data.get("confidence_notes") or {}):
                    data["confidence_notes"] = merged
                    updated_fields.append("confidence_notes")
                continue
            if key == "recent_relevant_turns":
                turns = [str(item).strip() for item in list(value or []) if str(item).strip()]
                if turns:
                    existing = list(data.get("recent_relevant_turns") or [])
                    data["recent_relevant_turns"] = existing + turns
                    updated_fields.append("recent_relevant_turns")
                continue
            text = str(value or "").strip()
            if text and data.get(key) != text:
                data[key] = text
                updated_fields.append(key)

        pruned, pruned_changed = prune_context(data)
        changed = bool(updated_fields or pruned_changed)
        return pruned, updated_fields, changed
