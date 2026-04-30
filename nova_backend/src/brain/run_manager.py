"""Planning-only Brain run manager.

This module tracks non-executing planning runs in memory. It does not call the
Governor, capabilities, OpenClaw, browser tools, file tools, email, calendar, or
account systems. A run is continuity state, not permission.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

from src.brain.task_understanding import SimpleTaskPlan, TaskEnvelope, TaskUnderstanding


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class RunStatus(_StringEnum):
    PLANNING = "planning"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class RunStep:
    step_id: str
    description: str
    status: str = "planned"
    authority_effect: str = "none"
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_effect != "none":
            raise ValueError("RunStep is non-authorizing: authority_effect must be 'none'.")
        if self.execution_performed:
            raise ValueError("RunStep must not record executed actions.")
        if self.authorization_granted:
            raise ValueError("RunStep must not grant authorization.")


@dataclass(frozen=True)
class Run:
    run_id: str
    goal: str
    status: RunStatus
    created_at: str
    updated_at: str
    understanding: TaskUnderstanding
    envelope: TaskEnvelope
    steps: tuple[RunStep, ...] = field(default_factory=tuple)
    planning_only: bool = True
    authority_effect: str = "none"
    execution_performed: bool = False
    authorization_granted: bool = False
    pause_reason: str = ""
    cancel_reason: str = ""

    def __post_init__(self) -> None:
        if not self.planning_only:
            raise ValueError("Run must remain planning-only.")
        if self.authority_effect != "none":
            raise ValueError("Run is non-authorizing: authority_effect must be 'none'.")
        if self.execution_performed:
            raise ValueError("Run must not record executed actions.")
        if self.authorization_granted:
            raise ValueError("Run must not grant authorization.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


class RunManager:
    """In-memory manager for planning-only Brain runs."""

    def __init__(
        self,
        *,
        id_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._runs: dict[str, Run] = {}
        self._last_interacted_run_id: str | None = None
        self._id_factory = id_factory or (lambda: f"run_{uuid4().hex}")
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @property
    def last_interacted_run_id(self) -> str | None:
        return self._last_interacted_run_id

    def create_run(self, plan: SimpleTaskPlan) -> Run:
        if not plan.planning_only or plan.execution_performed or plan.authorization_granted:
            raise ValueError("RunManager only accepts planning-only, non-authorizing plans.")

        now = self._now()
        run = Run(
            run_id=self._id_factory(),
            goal=plan.understanding.goal,
            status=RunStatus.PLANNING,
            created_at=now,
            updated_at=now,
            understanding=plan.understanding,
            envelope=plan.envelope,
            steps=tuple(
                RunStep(step_id=f"step_{index}", description=description)
                for index, description in enumerate(plan.plan_steps, start=1)
            ),
        )
        self._runs[run.run_id] = run
        self._last_interacted_run_id = run.run_id
        return run

    def get_run(self, run_id: str) -> Run | None:
        return self._runs.get(str(run_id or "").strip())

    def list_runs(self) -> tuple[Run, ...]:
        return tuple(self._runs.values())

    def pause_run(self, run_id: str, reason: str = "") -> Run | None:
        run = self.get_run(run_id)
        if run is None:
            return None
        updated = replace(
            run,
            status=RunStatus.PAUSED,
            updated_at=self._now(),
            pause_reason=str(reason or "").strip(),
        )
        self._runs[run.run_id] = updated
        self._last_interacted_run_id = run.run_id
        return updated

    def cancel_run(self, run_id: str, reason: str = "") -> Run | None:
        run = self.get_run(run_id)
        if run is None:
            return None
        updated = replace(
            run,
            status=RunStatus.CANCELLED,
            updated_at=self._now(),
            cancel_reason=str(reason or "").strip(),
        )
        self._runs[run.run_id] = updated
        self._last_interacted_run_id = run.run_id
        return updated

    def update_focus(self, run_id: str) -> Run | None:
        run = self.get_run(run_id)
        if run is None:
            return None
        self._last_interacted_run_id = run.run_id
        return run

    def last_interacted_run(self) -> Run | None:
        if self._last_interacted_run_id is None:
            return None
        return self.get_run(self._last_interacted_run_id)

    def _now(self) -> str:
        value = self._clock()
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    return value


__all__ = [
    "Run",
    "RunManager",
    "RunStatus",
    "RunStep",
]
