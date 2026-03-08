from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class CognitiveTrace:
    """Per-request debug trace for simulation/testing only."""

    trace_id: str = field(default_factory=lambda: uuid4().hex[:12])
    steps: list[dict[str, Any]] = field(default_factory=list)

    def record(self, stage: str, data: dict[str, Any] | None = None) -> None:
        self.steps.append(
            {
                "stage": str(stage),
                "data": dict(data or {}),
            }
        )

    def to_payload(self) -> dict[str, Any]:
        return {"trace_id": self.trace_id, "trace_steps": list(self.steps)}

