"""
TaskEnvelope — the governed contract for every OpenClaw task.

Every task MUST be wrapped in a TaskEnvelope before execution.
No raw task execution is permitted outside this contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
import uuid

EnvelopeStatus = Literal["pending", "running", "complete", "stopped", "failed"]
EnvelopeTrigger = Literal["user", "schedule", "bridge"]
EnvelopeType = Literal["morning_brief", "evening_digest", "inbox_check", "task_run", "default"]


@dataclass
class TaskEnvelope:
    title: str
    tools_allowed: list[str] = field(default_factory=list)
    max_steps: int = 5
    max_duration_s: int = 60
    envelope_type: EnvelopeType = "default"
    triggered_by: EnvelopeTrigger = "user"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: EnvelopeStatus = "pending"
    result_text: str | None = None

    def mark_running(self) -> None:
        self.status = "running"

    def mark_complete(self, result: str) -> None:
        self.status = "complete"
        self.result_text = result

    def mark_failed(self, reason: str) -> None:
        self.status = "failed"
        self.result_text = reason

    def mark_stopped(self) -> None:
        self.status = "stopped"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "envelope_type": self.envelope_type,
            "tools_allowed": self.tools_allowed,
            "max_steps": self.max_steps,
            "max_duration_s": self.max_duration_s,
            "triggered_by": self.triggered_by,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "result_text": self.result_text,
        }
