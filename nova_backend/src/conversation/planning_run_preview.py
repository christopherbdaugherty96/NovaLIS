"""Conversation-facing planning run preview helpers.

This module adapts Brain RunManager state for session/UI use. It creates
planning-only runs from Task Understanding plans and returns small preview
payloads. It does not execute, authorize, call capabilities, call the Governor,
or persist runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.brain.run_manager import Run, RunManager
from src.brain.task_understanding import SimpleTaskPlan


_RUN_MANAGER_KEY = "_planning_run_manager"


@dataclass(frozen=True)
class PlanningRunPreview:
    run_id: str
    title: str
    goal: str
    status: str
    current_step: str
    next_step: str
    last_interacted_run_id: str
    focused_run_id: str
    planning_only: bool = True
    authority_effect: str = "none"
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if not self.planning_only:
            raise ValueError("PlanningRunPreview must remain planning-only.")
        if self.authority_effect != "none":
            raise ValueError("PlanningRunPreview is non-authorizing: authority_effect must be 'none'.")
        if self.execution_performed:
            raise ValueError("PlanningRunPreview must not record executed actions.")
        if self.authorization_granted:
            raise ValueError("PlanningRunPreview must not grant authorization.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "title": self.title,
            "goal": self.goal,
            "status": self.status,
            "current_step": self.current_step,
            "next_step": self.next_step,
            "last_interacted_run_id": self.last_interacted_run_id,
            "focused_run_id": self.focused_run_id,
            "planning_only": self.planning_only,
            "authority_effect": self.authority_effect,
            "execution_performed": self.execution_performed,
            "authorization_granted": self.authorization_granted,
        }


def create_planning_run_preview(
    plan: SimpleTaskPlan | None,
    *,
    session_state: dict[str, Any],
    focused_run_id: str = "",
) -> PlanningRunPreview | None:
    """Create a planning-only run preview when a plan exists."""

    if plan is None:
        return None
    if not plan.planning_only or plan.execution_performed or plan.authorization_granted:
        raise ValueError("Planning run previews require non-executing, non-authorizing plans.")

    manager = planning_run_manager(session_state)
    run = manager.update_focus(focused_run_id) if focused_run_id else None
    if run is None:
        run = manager.create_run(plan)
    preview = format_planning_run_preview(run, manager=manager, focused_run_id=run.run_id)
    session_state["planning_run_preview"] = preview.to_dict()
    session_state["last_interacted_run_id"] = manager.last_interacted_run_id
    session_state["focused_run_id"] = preview.focused_run_id
    return preview


def format_planning_run_preview(
    run: Run,
    *,
    manager: RunManager | None = None,
    focused_run_id: str = "",
) -> PlanningRunPreview:
    """Return serializable preview metadata for a planning run."""

    current_step = run.steps[0].description if run.steps else "understand request"
    if len(run.steps) > 1:
        next_step = run.steps[1].description
    else:
        next_step = run.understanding.suggested_next_step or "build task envelope"
    last_interacted = manager.last_interacted_run_id if manager is not None else run.run_id
    focused = focused_run_id or last_interacted or run.run_id
    return PlanningRunPreview(
        run_id=run.run_id,
        title=run.goal,
        goal=run.goal,
        status=run.status.value,
        current_step=current_step,
        next_step=next_step,
        last_interacted_run_id=last_interacted or "",
        focused_run_id=focused,
    )


def planning_run_manager(session_state: dict[str, Any]) -> RunManager:
    """Return the session-local in-memory RunManager."""

    existing = session_state.get(_RUN_MANAGER_KEY)
    if isinstance(existing, RunManager):
        return existing
    manager = RunManager()
    session_state[_RUN_MANAGER_KEY] = manager
    return manager


__all__ = [
    "PlanningRunPreview",
    "create_planning_run_preview",
    "format_planning_run_preview",
    "planning_run_manager",
]
