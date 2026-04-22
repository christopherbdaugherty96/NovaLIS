from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


RUN_PENDING = "pending"
RUN_RUNNING = "running"
RUN_SUCCEEDED = "succeeded"
RUN_FAILED = "failed"
RUN_CANCELLED = "cancelled"

TERMINAL_RUN_STATES = {RUN_SUCCEEDED, RUN_FAILED, RUN_CANCELLED}
ACTIVE_RUN_STATES = {RUN_PENDING, RUN_RUNNING}

_STATUS_ALIASES = {
    "": RUN_RUNNING,
    "completed": RUN_SUCCEEDED,
    "complete": RUN_SUCCEEDED,
    "success": RUN_SUCCEEDED,
    "successful": RUN_SUCCEEDED,
    "interrupted": RUN_FAILED,
    "error": RUN_FAILED,
    "canceled": RUN_CANCELLED,
}

_ALLOWED_TRANSITIONS = {
    "": {RUN_PENDING, RUN_RUNNING},
    RUN_PENDING: {RUN_PENDING, RUN_RUNNING, RUN_CANCELLED, RUN_FAILED},
    RUN_RUNNING: {RUN_RUNNING, RUN_SUCCEEDED, RUN_FAILED, RUN_CANCELLED},
    RUN_SUCCEEDED: set(),
    RUN_FAILED: set(),
    RUN_CANCELLED: set(),
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_run_status(value: Any) -> str:
    raw = str(value or "").strip().lower()
    return _STATUS_ALIASES.get(raw, raw if raw in _ALLOWED_TRANSITIONS else RUN_RUNNING)


@dataclass(frozen=True)
class RunStateEvent:
    event: str
    run: dict[str, Any] | None
    previous_status: str
    status: str
    emitted_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "run": dict(self.run or {}) if self.run else None,
            "previous_status": self.previous_status,
            "status": self.status,
            "emitted_at": self.emitted_at,
        }


class RunStateMachine:
    """Normalizes OpenClaw run lifecycle transitions for every execution path."""

    def transition(
        self,
        current: dict[str, Any] | None,
        payload: dict[str, Any] | None,
        *,
        next_status: str,
    ) -> tuple[dict[str, Any] | None, RunStateEvent]:
        previous_status = normalize_run_status((current or {}).get("status")) if current else ""
        status = normalize_run_status(next_status)
        allowed = _ALLOWED_TRANSITIONS.get(previous_status, set())
        if status not in allowed and previous_status:
            raise RuntimeError(f"Invalid run transition: {previous_status} -> {status}")

        payload_dict = dict(payload or {})
        merged = dict(current or {})
        merged.update(payload_dict)
        merged["status"] = status
        if "status_label" not in payload_dict:
            if status == RUN_PENDING:
                merged["status_label"] = "Pending"
            elif status == RUN_RUNNING:
                merged["status_label"] = "Running now"
            elif status == RUN_SUCCEEDED:
                merged["status_label"] = "Succeeded"
            elif status == RUN_FAILED:
                merged["status_label"] = "Failed"
            elif status == RUN_CANCELLED:
                merged["status_label"] = "Cancelled"

        run = merged if status in ACTIVE_RUN_STATES else None
        event = RunStateEvent(
            event="run_status_changed",
            run=dict(merged),
            previous_status=previous_status,
            status=status,
            emitted_at=_utc_now_iso(),
        )
        return run, event

    def running_now(self, snapshot: dict[str, Any]) -> dict[str, Any] | None:
        active = snapshot.get("active_run")
        if not isinstance(active, dict):
            return None
        status = normalize_run_status(active.get("status"))
        if status not in ACTIVE_RUN_STATES:
            return None
        return dict(active)


class RunEventHub:
    """Small in-process broadcaster for WebSocket run status push events."""

    def __init__(self) -> None:
        self._queues: set[asyncio.Queue[dict[str, Any]]] = set()

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=20)
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._queues.discard(queue)

    def emit(self, event: RunStateEvent | dict[str, Any]) -> None:
        payload = event.to_dict() if isinstance(event, RunStateEvent) else dict(event or {})
        if not payload:
            return
        for queue in list(self._queues):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                    queue.put_nowait(payload)
                except Exception:
                    pass


run_state_machine = RunStateMachine()
run_event_hub = RunEventHub()
