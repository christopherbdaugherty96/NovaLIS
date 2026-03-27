from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from src.openclaw.agent_personality_bridge import (
    DEFAULT_DELIVERY_MODE_BY_TEMPLATE,
    normalize_delivery_mode,
)
from src.openclaw.strict_preflight import strict_foundation_snapshot


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class OpenClawAgentRuntimeStore:
    """Persistent operator-facing store for OpenClaw home-agent foundations."""

    SCHEMA_VERSION = "1.1"
    DEFAULT_TEMPLATES = (
        {
            "id": "morning_brief",
            "title": "Morning Brief",
            "category": "Named briefing",
            "description": "Collect weather, calendar, news, and schedule context into one calm morning report.",
            "tools_allowed": ["weather", "calendar", "news", "schedules", "summarize"],
            "delivery_mode": DEFAULT_DELIVERY_MODE_BY_TEMPLATE["morning_brief"],
            "schedule_label": "Planned daily trigger at 7:00 AM",
            "schedule_status": "Planned",
            "manual_run_available": True,
            "availability_label": "Ready now",
            "availability_reason": "Manual run is live. Scheduled background execution still arrives later.",
            "max_steps": 6,
            "max_duration_s": 90,
        },
        {
            "id": "evening_digest",
            "title": "Evening Digest",
            "category": "Named briefing",
            "description": "Summarize the rest of the day, outstanding schedules, and headline movement in one compact report.",
            "tools_allowed": ["calendar", "news", "schedules", "summarize"],
            "delivery_mode": DEFAULT_DELIVERY_MODE_BY_TEMPLATE["evening_digest"],
            "schedule_label": "Planned daily trigger at 8:00 PM",
            "schedule_status": "Planned",
            "manual_run_available": True,
            "availability_label": "Ready now",
            "availability_reason": "Manual run is live. Scheduled background execution still arrives later.",
            "max_steps": 5,
            "max_duration_s": 90,
        },
        {
            "id": "inbox_check",
            "title": "Inbox Check",
            "category": "Quiet review",
            "description": "Future quiet review task for inbox triage and email pull-forward work.",
            "tools_allowed": ["email_read", "summarize"],
            "delivery_mode": DEFAULT_DELIVERY_MODE_BY_TEMPLATE["inbox_check"],
            "schedule_label": "Planned every 30 minutes",
            "schedule_status": "Needs connector",
            "manual_run_available": False,
            "availability_label": "Needs connector",
            "availability_reason": "Email review is part of the longer OpenClaw path and is not connected yet.",
            "max_steps": 8,
            "max_duration_s": 120,
        },
    )

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nova_state"
            / "openclaw"
            / "agent_runtime.json"
        )
        self._path = Path(path) if path else default_path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write_state(self._default_state())

    @property
    def path(self) -> Path:
        return self._path

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
        templates = self._normalized_templates(state.get("templates"))
        recent_runs = list(state.get("recent_runs") or [])[:12]
        delivery_inbox = [
            item
            for item in list(state.get("delivery_inbox") or [])
            if str(dict(item).get("status") or "ready").strip() == "ready"
        ][:8]
        runnable = sum(1 for item in templates if item.get("manual_run_available"))
        strict_foundation = strict_foundation_snapshot()
        delivery_ready_count = len(delivery_inbox)
        return {
            "schema_version": self.SCHEMA_VERSION,
            "status": "foundation",
            "status_label": "Foundation live",
            "summary": (
                "Manual home-agent briefing runs are available now. "
                "Scheduled background execution and wider envelope authority still arrive later."
            ),
            "delivery_model_summary": (
                "Named briefings can surface in chat and the operator surface. "
                "Quiet review tasks stay surface-first."
            ),
            "personality_summary": (
                "Nova owns the voice. OpenClaw stays behind the scenes and results come back through Nova's presentation layer."
            ),
            "schedule_summary": "Template schedules are documented and visible, but automatic triggers are not live yet.",
            "strict_foundation_label": str(strict_foundation.get("label") or "").strip(),
            "strict_foundation_summary": str(strict_foundation.get("summary") or "").strip(),
            "template_count": len(templates),
            "manual_run_count": runnable,
            "templates": templates,
            "recent_runs": recent_runs,
            "delivery_ready_count": delivery_ready_count,
            "delivery_summary": (
                f"{delivery_ready_count} agent deliver{'y' if delivery_ready_count == 1 else 'ies'} ready for review."
                if delivery_ready_count
                else "No agent deliveries are waiting right now."
            ),
            "delivery_inbox": delivery_inbox,
            "updated_at": str(state.get("updated_at") or ""),
        }

    def get_template(self, template_id: str) -> dict[str, Any] | None:
        target = str(template_id or "").strip()
        if not target:
            return None
        with self._lock:
            state = self._read_state()
            templates = self._normalized_templates(state.get("templates"))
        for item in templates:
            if str(item.get("id") or "").strip() == target:
                return dict(item)
        return None

    def set_template_delivery_mode(
        self,
        template_id: str,
        delivery_mode: str,
    ) -> dict[str, Any]:
        target = str(template_id or "").strip()
        if not target:
            raise KeyError(template_id)
        with self._lock:
            state = self._read_state()
            templates = self._normalized_templates(state.get("templates"))
            found = False
            for item in templates:
                if str(item.get("id") or "").strip() != target:
                    continue
                item["delivery_mode"] = normalize_delivery_mode(target, delivery_mode)
                found = True
                break
            if not found:
                raise KeyError(template_id)
            state["templates"] = templates
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
            return self.snapshot()

    def record_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        entry = self._normalize_run(dict(payload or {}))
        with self._lock:
            state = self._read_state()
            recent_runs = list(state.get("recent_runs") or [])
            recent_runs.insert(0, entry)
            state["recent_runs"] = recent_runs[:20]
            delivery_inbox = [self._normalize_delivery_item(item) for item in list(state.get("delivery_inbox") or [])]
            if bool(dict(entry.get("delivery_channels") or {}).get("widget")):
                delivery_inbox.insert(0, self._build_delivery_item(entry))
            state["delivery_inbox"] = delivery_inbox[:20]
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
        return dict(entry)

    def dismiss_delivery(self, delivery_id: str) -> dict[str, Any]:
        target = str(delivery_id or "").strip()
        if not target:
            raise KeyError(delivery_id)
        with self._lock:
            state = self._read_state()
            delivery_inbox = [self._normalize_delivery_item(item) for item in list(state.get("delivery_inbox") or [])]
            found = False
            for item in delivery_inbox:
                if str(item.get("id") or "").strip() != target:
                    continue
                item["status"] = "dismissed"
                item["dismissed_at"] = _utc_now_iso()
                found = True
                break
            if not found:
                raise KeyError(delivery_id)
            state["delivery_inbox"] = delivery_inbox
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
            return self.snapshot()

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "templates": [dict(item) for item in self.DEFAULT_TEMPLATES],
            "recent_runs": [],
            "delivery_inbox": [],
            "updated_at": _utc_now_iso(),
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = self._default_state()
        if not isinstance(payload, dict):
            payload = self._default_state()
        payload.setdefault("schema_version", self.SCHEMA_VERSION)
        payload["templates"] = self._normalized_templates(payload.get("templates"))
        payload["recent_runs"] = [self._normalize_run(item) for item in list(payload.get("recent_runs") or [])]
        payload["delivery_inbox"] = [
            self._normalize_delivery_item(item)
            for item in list(payload.get("delivery_inbox") or [])
        ]
        payload.setdefault("updated_at", _utc_now_iso())
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "templates": self._normalized_templates(state.get("templates")),
            "recent_runs": [self._normalize_run(item) for item in list(state.get("recent_runs") or [])],
            "delivery_inbox": [
                self._normalize_delivery_item(item)
                for item in list(state.get("delivery_inbox") or [])
            ],
            "updated_at": str(state.get("updated_at") or _utc_now_iso()),
        }
        self._path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")

    def _normalized_templates(self, value: Any) -> list[dict[str, Any]]:
        raw_items = list(value or []) if isinstance(value, list) else [dict(item) for item in self.DEFAULT_TEMPLATES]
        default_lookup = {
            str(item["id"]): dict(item)
            for item in self.DEFAULT_TEMPLATES
        }
        templates: list[dict[str, Any]] = []
        for default_id, default_item in default_lookup.items():
            current = next(
                (dict(item) for item in raw_items if str((item or {}).get("id") or "").strip() == default_id),
                {},
            )
            merged = dict(default_item)
            merged.update(current)
            merged["id"] = default_id
            merged["delivery_mode"] = normalize_delivery_mode(default_id, merged.get("delivery_mode"))
            merged["tools_allowed"] = [
                str(tool).strip()
                for tool in list(merged.get("tools_allowed") or [])
                if tool is not None and str(tool).strip()
            ]
            merged["manual_run_available"] = bool(merged.get("manual_run_available"))
            templates.append(merged)
        return templates

    def _normalize_run(self, value: Any) -> dict[str, Any]:
        raw = dict(value or {})
        return {
            "envelope_id": str(raw.get("envelope_id") or "").strip(),
            "template_id": str(raw.get("template_id") or "").strip(),
            "title": str(raw.get("title") or "").strip(),
            "status": str(raw.get("status") or "").strip() or "completed",
            "triggered_by": str(raw.get("triggered_by") or "").strip() or "dashboard",
            "delivery_mode": str(raw.get("delivery_mode") or "").strip() or "widget",
            "delivery_channels": {
                "widget": bool(dict(raw.get("delivery_channels") or {}).get("widget")),
                "chat": bool(dict(raw.get("delivery_channels") or {}).get("chat")),
            },
            "presented_message": str(raw.get("presented_message") or "").strip(),
            "summary": str(raw.get("summary") or "").strip(),
            "started_at": str(raw.get("started_at") or _utc_now_iso()),
            "completed_at": str(raw.get("completed_at") or _utc_now_iso()),
            "llm_summary_used": bool(raw.get("llm_summary_used")),
            "estimated_input_tokens": int(raw.get("estimated_input_tokens") or 0),
            "estimated_output_tokens": int(raw.get("estimated_output_tokens") or 0),
            "estimated_total_tokens": int(raw.get("estimated_total_tokens") or 0),
            "source_notes": dict(raw.get("source_notes") or {}),
            "strict_preflight": dict(raw.get("strict_preflight") or {}),
        }

    def _build_delivery_item(self, run_entry: dict[str, Any]) -> dict[str, Any]:
        return self._normalize_delivery_item(
            {
                "id": self._new_delivery_id(),
                "envelope_id": str(run_entry.get("envelope_id") or "").strip(),
                "template_id": str(run_entry.get("template_id") or "").strip(),
                "title": str(run_entry.get("title") or "").strip(),
                "presented_message": str(run_entry.get("presented_message") or "").strip(),
                "summary": str(run_entry.get("summary") or "").strip(),
                "delivery_mode": str(run_entry.get("delivery_mode") or "").strip() or "widget",
                "delivery_channels": dict(run_entry.get("delivery_channels") or {}),
                "created_at": str(run_entry.get("completed_at") or run_entry.get("started_at") or _utc_now_iso()),
                "status": "ready",
                "dismissed_at": "",
            }
        )

    def _normalize_delivery_item(self, value: Any) -> dict[str, Any]:
        raw = dict(value or {})
        return {
            "id": str(raw.get("id") or "").strip(),
            "envelope_id": str(raw.get("envelope_id") or "").strip(),
            "template_id": str(raw.get("template_id") or "").strip(),
            "title": str(raw.get("title") or "").strip(),
            "presented_message": str(raw.get("presented_message") or "").strip(),
            "summary": str(raw.get("summary") or "").strip(),
            "delivery_mode": str(raw.get("delivery_mode") or "").strip() or "widget",
            "delivery_channels": {
                "widget": bool(dict(raw.get("delivery_channels") or {}).get("widget")),
                "chat": bool(dict(raw.get("delivery_channels") or {}).get("chat")),
            },
            "created_at": str(raw.get("created_at") or _utc_now_iso()),
            "status": str(raw.get("status") or "ready").strip() or "ready",
            "dismissed_at": str(raw.get("dismissed_at") or "").strip(),
        }

    def _new_delivery_id(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"DEL-{stamp}-{uuid4().hex[:4].upper()}"


openclaw_agent_runtime_store = OpenClawAgentRuntimeStore()
