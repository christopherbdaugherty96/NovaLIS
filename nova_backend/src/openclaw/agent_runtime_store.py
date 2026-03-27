"""
AgentRuntimeStore — in-memory store for active and recently completed TaskEnvelopes.

Thread-safe. Holds up to MAX_RECENT_COMPLETED completed envelopes.
No persistence — store is ephemeral and resets on process restart by design.
"""
from __future__ import annotations

import threading
from collections import deque
from typing import Optional

from src.openclaw.task_envelope import TaskEnvelope, EnvelopeStatus

MAX_RECENT_COMPLETED = 50


class AgentRuntimeStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active: dict[str, TaskEnvelope] = {}
        self._recent: deque[TaskEnvelope] = deque(maxlen=MAX_RECENT_COMPLETED)

    def register(self, envelope: TaskEnvelope) -> None:
        with self._lock:
            self._active[envelope.id] = envelope

    def update_status(self, envelope_id: str, status: EnvelopeStatus, result_text: Optional[str] = None) -> None:
        with self._lock:
            env = self._active.get(envelope_id)
            if env is None:
                return
            env.status = status
            if result_text is not None:
                env.result_text = result_text
            if status in ("complete", "failed", "stopped"):
                self._recent.appendleft(env)
                del self._active[envelope_id]

    def get_active(self) -> list[TaskEnvelope]:
        with self._lock:
            return list(self._active.values())

    def get_recent(self) -> list[TaskEnvelope]:
        with self._lock:
            return list(self._recent)

    def stop_all(self) -> int:
        with self._lock:
            count = len(self._active)
            for env in list(self._active.values()):
                env.mark_stopped()
                self._recent.appendleft(env)
            self._active.clear()
            return count

    def stop_by_id(self, envelope_id: str) -> bool:
        with self._lock:
            env = self._active.get(envelope_id)
            if env is None:
                return False
            env.mark_stopped()
            self._recent.appendleft(env)
            del self._active[envelope_id]
            return True


# Singleton store for use across the runtime
_default_store = AgentRuntimeStore()


def get_default_store() -> AgentRuntimeStore:
    return _default_store
