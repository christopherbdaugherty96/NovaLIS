from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_envelope_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"ENV-{stamp}-{uuid4().hex[:6].upper()}"


@dataclass
class TaskEnvelope:
    id: str
    title: str
    template_id: str
    tools_allowed: list[str]
    max_steps: int
    max_duration_s: int
    triggered_by: str = "user"
    delivery_mode: str = "widget"
    status: str = "pending"
    created_at: str = field(default_factory=_utc_now_iso)
    result_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_template(
        cls,
        template: dict[str, Any],
        *,
        triggered_by: str = "user",
    ) -> "TaskEnvelope":
        return cls(
            id=_new_envelope_id(),
            title=str(template.get("title") or "OpenClaw Task").strip(),
            template_id=str(template.get("id") or "").strip(),
            tools_allowed=[
                str(item).strip()
                for item in list(template.get("tools_allowed") or [])
                if item is not None and str(item).strip()
            ],
            max_steps=max(1, int(template.get("max_steps") or 1)),
            max_duration_s=max(15, int(template.get("max_duration_s") or 60)),
            triggered_by=str(triggered_by or "user").strip() or "user",
            delivery_mode=str(template.get("delivery_mode") or "widget").strip() or "widget",
            metadata={
                "category": str(template.get("category") or "").strip(),
                "schedule_label": str(template.get("schedule_label") or "").strip(),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "template_id": self.template_id,
            "tools_allowed": list(self.tools_allowed),
            "max_steps": int(self.max_steps),
            "max_duration_s": int(self.max_duration_s),
            "triggered_by": self.triggered_by,
            "delivery_mode": self.delivery_mode,
            "status": self.status,
            "created_at": self.created_at,
            "result_text": self.result_text,
            "metadata": dict(self.metadata),
        }
