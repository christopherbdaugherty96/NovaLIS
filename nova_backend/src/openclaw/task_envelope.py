from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_envelope_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"ENV-{stamp}-{uuid4().hex[:6].upper()}"


def _normalize_unique_strings(values: list[Any] | None) -> list[str]:
    cleaned: list[str] = []
    for item in list(values or []):
        text = str(item or "").strip()
        if not text or text in cleaned:
            continue
        cleaned.append(text)
    return cleaned


@dataclass
class TaskEnvelope:
    id: str
    title: str
    template_id: str
    tools_allowed: list[str]
    allowed_hostnames: list[str]
    max_steps: int
    max_duration_s: int
    max_network_calls: int
    max_files_touched: int
    max_bytes_read: int
    max_bytes_written: int
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
            tools_allowed=_normalize_unique_strings(list(template.get("tools_allowed") or [])),
            allowed_hostnames=_normalize_unique_strings(list(template.get("allowed_hostnames") or [])),
            max_steps=max(1, int(template.get("max_steps") or 1)),
            max_duration_s=max(15, int(template.get("max_duration_s") or 60)),
            max_network_calls=max(0, int(template.get("max_network_calls") or 0)),
            max_files_touched=max(0, int(template.get("max_files_touched") or 0)),
            max_bytes_read=max(0, int(template.get("max_bytes_read") or 0)),
            max_bytes_written=max(0, int(template.get("max_bytes_written") or 0)),
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
            "allowed_hostnames": list(self.allowed_hostnames),
            "max_steps": int(self.max_steps),
            "max_duration_s": int(self.max_duration_s),
            "max_network_calls": int(self.max_network_calls),
            "max_files_touched": int(self.max_files_touched),
            "max_bytes_read": int(self.max_bytes_read),
            "max_bytes_written": int(self.max_bytes_written),
            "triggered_by": self.triggered_by,
            "delivery_mode": self.delivery_mode,
            "status": self.status,
            "created_at": self.created_at,
            "result_text": self.result_text,
            "metadata": dict(self.metadata),
        }

    def scope_summary(self) -> str:
        tools = ", ".join(self.tools_allowed) if self.tools_allowed else "no tools"
        if self.allowed_hostnames:
            hostnames = ", ".join(self.allowed_hostnames[:4])
            if len(self.allowed_hostnames) > 4:
                hostnames += f", +{len(self.allowed_hostnames) - 4} more"
            return f"Uses {tools}. Can only reach: {hostnames}."
        return f"Uses {tools}. No external websites are allowed."

    def budget_summary(self) -> str:
        return (
            f"Can take up to {int(self.max_steps)} step{'s' if int(self.max_steps) != 1 else ''}, "
            f"make up to {int(self.max_network_calls)} web request{'s' if int(self.max_network_calls) != 1 else ''}, "
            f"read up to {int(self.max_files_touched)} local file{'s' if int(self.max_files_touched) != 1 else ''}, "
            f"and runs for up to {int(self.max_duration_s)} seconds."
        )

    def preview_dict(self) -> dict[str, Any]:
        return {
            "tools_allowed": list(self.tools_allowed),
            "allowed_hostnames": list(self.allowed_hostnames),
            "max_steps": int(self.max_steps),
            "max_duration_s": int(self.max_duration_s),
            "max_network_calls": int(self.max_network_calls),
            "max_files_touched": int(self.max_files_touched),
            "max_bytes_read": int(self.max_bytes_read),
            "max_bytes_written": int(self.max_bytes_written),
            "scope_summary": self.scope_summary(),
            "budget_summary": self.budget_summary(),
            "read_only": int(self.max_bytes_written) == 0,
        }

    def hostname_allowed(self, hostname: str) -> bool:
        target = str(hostname or "").strip().lower()
        if not target:
            return False
        allowed = [
            str(item or "").strip().lower()
            for item in list(self.allowed_hostnames or [])
            if str(item or "").strip()
        ]
        return any(target == item or target.endswith(f".{item}") for item in allowed)

    def url_allowed(self, url: str) -> bool:
        try:
            hostname = str(urlparse(str(url or "").strip()).hostname or "").strip().lower()
        except Exception:
            return False
        return self.hostname_allowed(hostname)
