from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.openclaw.agent_personality_bridge import (
    DEFAULT_DELIVERY_MODE_BY_TEMPLATE,
    normalize_delivery_mode,
)
from src.openclaw.strict_preflight import strict_foundation_snapshot
from src.openclaw.task_envelope import TaskEnvelope
from src.utils.persistent_state import shared_path_lock, write_json_atomic


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _local_now() -> datetime:
    return datetime.now().astimezone()


def _parse_clock(value: str) -> tuple[int, int] | None:
    raw = str(value or "").strip()
    if not raw or ":" not in raw:
        return None
    try:
        hour_text, minute_text = raw.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except Exception:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return hour, minute


def _local_due_slot(clock_value: str, *, now: datetime | None = None) -> datetime | None:
    parsed = _parse_clock(clock_value)
    current = (now or _local_now()).astimezone()
    if parsed is None:
        return None
    hour, minute = parsed
    return current.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _display_clock_label(clock_value: str) -> str:
    parsed = _parse_clock(clock_value)
    if parsed is None:
        return "Planned"
    hour, minute = parsed
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute:02d} {period} local"


MAX_SCHEDULE_LATENESS = timedelta(hours=2)


def _is_stale_scheduled_slot(slot_local: datetime, *, now: datetime | None = None) -> bool:
    current = (now or _local_now()).astimezone()
    return current - slot_local > MAX_SCHEDULE_LATENESS


class OpenClawAgentRuntimeStore:
    """Persistent operator-facing store for OpenClaw home-agent foundations."""

    SCHEMA_VERSION = "1.4"
    DEFAULT_TEMPLATES = (
        {
            "id": "morning_brief",
            "title": "Morning Brief",
            "category": "Named briefing",
            "description": "Collect weather, calendar, news, and schedule context into one calm morning report.",
            "tools_allowed": ["weather", "calendar", "news", "schedules", "summarize"],
            "allowed_hostnames": [
                "weather.visualcrossing.com",
                "www.reuters.com",
                "apnews.com",
                "feeds.apnews.com",
                "feeds.npr.org",
                "feeds.bbci.co.uk",
                "www.pbs.org",
                "abcnews.go.com",
                "feeds.foxnews.com",
                "rss.cnn.com",
                "www.aljazeera.com",
                "www.politico.com",
                "moxie.foxnews.com",
                "www.theverge.com",
                "feeds.arstechnica.com",
                "techcrunch.com",
                "feeds.content.dowjones.io",
                "www.coindesk.com",
                "www.cnbc.com",
            ],
            "delivery_mode": DEFAULT_DELIVERY_MODE_BY_TEMPLATE["morning_brief"],
            "schedule_label": "Planned daily trigger at 7:00 AM",
            "schedule_clock_local": "07:00",
            "schedule_enabled": False,
            "schedule_status": "Paused",
            "next_run_at": "",
            "next_run_label": "Paused",
            "last_scheduled_window": "",
            "last_scheduled_run_at": "",
            "last_scheduled_outcome": "",
            "last_scheduled_note": "",
            "last_suppression_window": "",
            "last_suppressed_at": "",
            "last_suppression_reason": "",
            "last_suppression_note": "",
            "manual_run_available": True,
            "availability_label": "Ready now",
            "availability_reason": "Manual run is live. Scheduled background execution stays opt-in.",
            "max_steps": 6,
            "max_duration_s": 90,
            "max_network_calls": 11,
            "max_files_touched": 1,
            "max_bytes_read": 1_200_000,
            "max_bytes_written": 0,
        },
        {
            "id": "evening_digest",
            "title": "Evening Digest",
            "category": "Named briefing",
            "description": "Summarize the rest of the day, outstanding schedules, and headline movement in one compact report.",
            "tools_allowed": ["calendar", "news", "schedules", "summarize"],
            "allowed_hostnames": [
                "www.reuters.com",
                "apnews.com",
                "feeds.apnews.com",
                "feeds.npr.org",
                "feeds.bbci.co.uk",
                "www.pbs.org",
                "abcnews.go.com",
                "feeds.foxnews.com",
                "rss.cnn.com",
                "www.aljazeera.com",
                "www.politico.com",
                "moxie.foxnews.com",
                "www.theverge.com",
                "feeds.arstechnica.com",
                "techcrunch.com",
                "feeds.content.dowjones.io",
                "www.coindesk.com",
                "www.cnbc.com",
            ],
            "delivery_mode": DEFAULT_DELIVERY_MODE_BY_TEMPLATE["evening_digest"],
            "schedule_label": "Planned daily trigger at 8:00 PM",
            "schedule_clock_local": "20:00",
            "schedule_enabled": False,
            "schedule_status": "Paused",
            "next_run_at": "",
            "next_run_label": "Paused",
            "last_scheduled_window": "",
            "last_scheduled_run_at": "",
            "last_scheduled_outcome": "",
            "last_scheduled_note": "",
            "last_suppression_window": "",
            "last_suppressed_at": "",
            "last_suppression_reason": "",
            "last_suppression_note": "",
            "manual_run_available": True,
            "availability_label": "Ready now",
            "availability_reason": "Manual run is live. Scheduled background execution stays opt-in.",
            "max_steps": 5,
            "max_duration_s": 90,
            "max_network_calls": 10,
            "max_files_touched": 1,
            "max_bytes_read": 1_000_000,
            "max_bytes_written": 0,
        },
        {
            "id": "inbox_check",
            "title": "Inbox Check",
            "category": "Quiet review",
            "description": "Future quiet review task for inbox triage and email pull-forward work.",
            "tools_allowed": ["email_read", "summarize"],
            "allowed_hostnames": [],
            "delivery_mode": DEFAULT_DELIVERY_MODE_BY_TEMPLATE["inbox_check"],
            "schedule_label": "Planned every 30 minutes",
            "schedule_clock_local": "",
            "schedule_enabled": False,
            "schedule_status": "Needs connector",
            "next_run_at": "",
            "next_run_label": "Needs connector",
            "last_scheduled_window": "",
            "last_scheduled_run_at": "",
            "last_scheduled_outcome": "",
            "last_scheduled_note": "",
            "last_suppression_window": "",
            "last_suppressed_at": "",
            "last_suppression_reason": "",
            "last_suppression_note": "",
            "manual_run_available": False,
            "availability_label": "Needs connector",
            "availability_reason": "Email review is part of the longer OpenClaw path and is not connected yet.",
            "max_steps": 8,
            "max_duration_s": 120,
            "max_network_calls": 0,
            "max_files_touched": 0,
            "max_bytes_read": 0,
            "max_bytes_written": 0,
        },
        {
            "id": "market_watch",
            "title": "Market Watch",
            "category": "Research-only",
            "description": "Read-only market and crypto news watch. Research only; no buy, sell, or broker actions.",
            "tools_allowed": ["news", "summarize"],
            "allowed_hostnames": [
                "www.coindesk.com",
                "www.cnbc.com",
                "feeds.content.dowjones.io",
            ],
            "delivery_mode": "widget",
            "schedule_label": "Manual research only",
            "schedule_clock_local": "",
            "schedule_enabled": False,
            "schedule_status": "Manual only",
            "next_run_at": "",
            "next_run_label": "Manual only",
            "last_scheduled_window": "",
            "last_scheduled_run_at": "",
            "last_scheduled_outcome": "",
            "last_scheduled_note": "",
            "last_suppression_window": "",
            "last_suppressed_at": "",
            "last_suppression_reason": "",
            "last_suppression_note": "",
            "manual_run_available": True,
            "availability_label": "Read-only",
            "availability_reason": "Read-only market research is allowed. Paper trading and live order execution still stay disabled.",
            "max_steps": 4,
            "max_duration_s": 90,
            "max_network_calls": 4,
            "max_files_touched": 0,
            "max_bytes_read": 700000,
            "max_bytes_written": 0,
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
        self._lock = shared_path_lock(self._path)
        with self._lock:
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
        active_run = self._normalize_active_run(state.get("active_run"))
        recent_runs = list(state.get("recent_runs") or [])[:12]
        delivery_inbox = [
            item
            for item in list(state.get("delivery_inbox") or [])
            if str(dict(item).get("status") or "ready").strip() == "ready"
        ][:8]
        runnable = sum(1 for item in templates if item.get("manual_run_available"))
        scheduled_enabled = sum(1 for item in templates if item.get("schedule_enabled"))
        strict_foundation = strict_foundation_snapshot()
        delivery_ready_count = len(delivery_inbox)
        return {
            "schema_version": self.SCHEMA_VERSION,
            "status": "foundation",
            "status_label": "Foundation live",
            "summary": (
                "Manual home-agent briefing runs and the narrow scheduled briefing lane are available now. "
                "Wider envelope-governed execution still arrives later."
            ),
            "delivery_model_summary": (
                "Named briefings can surface in chat and the operator surface. "
                "Quiet review tasks stay surface-first."
            ),
            "personality_summary": (
                "Nova owns the voice. OpenClaw stays behind the scenes and results come back through Nova's presentation layer."
            ),
            "schedule_summary": (
                f"{scheduled_enabled} scheduled template{'s' if scheduled_enabled != 1 else ''} enabled."
                if scheduled_enabled
                else "Template schedules are visible and paused until you explicitly enable them."
            ),
            "strict_foundation_label": str(strict_foundation.get("label") or "").strip(),
            "strict_foundation_summary": str(strict_foundation.get("summary") or "").strip(),
            "template_count": len(templates),
            "manual_run_count": runnable,
            "scheduled_enabled_count": scheduled_enabled,
            "active_run": active_run,
            "active_run_summary": self._active_run_summary(active_run),
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

    def set_template_delivery_mode(self, template_id: str, delivery_mode: str) -> dict[str, Any]:
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

    def set_template_schedule_enabled(self, template_id: str, enabled: bool) -> dict[str, Any]:
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
                if not item.get("manual_run_available") or not str(item.get("schedule_clock_local") or "").strip():
                    raise RuntimeError(str(item.get("availability_reason") or "This template cannot be scheduled yet.").strip())
                item["schedule_enabled"] = bool(enabled)
                item["schedule_status"] = "Scheduled" if enabled else "Paused"
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
            if bool(dict(entry.get("delivery_channels") or {}).get("widget")) or str(entry.get("triggered_by") or "").strip() == "scheduler":
                delivery_inbox.insert(0, self._build_delivery_item(entry))
            state["delivery_inbox"] = delivery_inbox[:20]
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
        return dict(entry)

    def set_active_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        entry = self._normalize_active_run(payload)
        with self._lock:
            state = self._read_state()
            state["active_run"] = entry
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
        return dict(entry)

    def update_active_run(self, envelope_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        target = str(envelope_id or "").strip()
        if not target:
            return None
        with self._lock:
            state = self._read_state()
            active_run = self._normalize_active_run(state.get("active_run"))
            if not active_run or str(active_run.get("envelope_id") or "").strip() != target:
                return None
            merged = dict(active_run)
            for key, value in dict(payload or {}).items():
                merged[key] = value
            state["active_run"] = self._normalize_active_run(merged)
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
            return dict(state["active_run"] or {})

    def request_cancel_active_run(self, envelope_id: str | None = None) -> bool:
        """Mark the active run as cancel-requested. Returns True if the flag was set."""
        target = str(envelope_id or "").strip()
        with self._lock:
            state = self._read_state()
            active_run = self._normalize_active_run(state.get("active_run"))
            if not active_run:
                return False
            if target and str(active_run.get("envelope_id") or "").strip() != target:
                return False
            active_run["cancel_requested"] = True
            active_run["status_label"] = "Cancelling\u2026"
            state["active_run"] = active_run
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
        return True

    def is_cancel_requested(self, envelope_id: str) -> bool:
        target = str(envelope_id or "").strip()
        with self._lock:
            state = self._read_state()
            active_run = self._normalize_active_run(state.get("active_run"))
        if not active_run:
            return False
        if target and str(active_run.get("envelope_id") or "").strip() != target:
            return False
        return bool(active_run.get("cancel_requested"))

    def clear_active_run(self, envelope_id: str | None = None) -> None:
        target = str(envelope_id or "").strip()
        with self._lock:
            state = self._read_state()
            active_run = self._normalize_active_run(state.get("active_run"))
            if not active_run:
                return
            if target and str(active_run.get("envelope_id") or "").strip() != target:
                return
            state["active_run"] = None
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)

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

    def due_scheduled_templates(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        current = (now or _local_now()).astimezone()
        due: list[dict[str, Any]] = []
        with self._lock:
            state = self._read_state()
            templates = self._normalized_templates(state.get("templates"))
            for item in templates:
                if not bool(item.get("schedule_enabled")):
                    continue
                if not bool(item.get("manual_run_available")):
                    continue
                slot_local = _local_due_slot(str(item.get("schedule_clock_local") or "").strip(), now=current)
                if slot_local is None or current < slot_local:
                    continue
                if _is_stale_scheduled_slot(slot_local, now=current):
                    continue
                slot_key = slot_local.astimezone(timezone.utc).isoformat()
                if str(item.get("last_scheduled_window") or "").strip() == slot_key:
                    continue
                due.append(
                    {
                        "template_id": str(item.get("id") or "").strip(),
                        "slot_key": slot_key,
                        "last_suppression_window": str(item.get("last_suppression_window") or "").strip(),
                        "last_suppression_reason": str(item.get("last_suppression_reason") or "").strip(),
                        "last_suppression_note": str(item.get("last_suppression_note") or "").strip(),
                    }
                )
        return due

    def claim_due_scheduled_templates(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        claims: list[dict[str, Any]] = []
        for item in self.due_scheduled_templates(now=now):
            template_id = str(item.get("template_id") or "").strip()
            slot_key = str(item.get("slot_key") or "").strip()
            if not template_id or not slot_key:
                continue
            if self.claim_scheduled_template(template_id, slot_key):
                claims.append({"template_id": template_id, "slot_key": slot_key})
        return claims

    def claim_scheduled_template(self, template_id: str, slot_key: str) -> bool:
        target = str(template_id or "").strip()
        safe_slot_key = str(slot_key or "").strip()
        if not target or not safe_slot_key:
            raise KeyError(template_id)
        with self._lock:
            state = self._read_state()
            templates = self._normalized_templates(state.get("templates"))
            found = False
            claimed = False
            for item in templates:
                if str(item.get("id") or "").strip() != target:
                    continue
                found = True
                if str(item.get("last_scheduled_window") or "").strip() == safe_slot_key:
                    claimed = False
                    break
                item["last_scheduled_window"] = safe_slot_key
                item["last_suppression_window"] = ""
                item["last_suppressed_at"] = ""
                item["last_suppression_reason"] = ""
                item["last_suppression_note"] = ""
                item["schedule_status"] = "Running"
                claimed = True
                break
            if not found:
                raise KeyError(template_id)
            if claimed:
                state["templates"] = templates
                state["updated_at"] = _utc_now_iso()
                self._write_state(state)
            return claimed

    def record_schedule_suppression(
        self,
        template_id: str,
        *,
        slot_key: str,
        reason: str,
        note: str = "",
        now: datetime | None = None,
    ) -> dict[str, Any]:
        current = (now or _local_now()).astimezone()
        target = str(template_id or "").strip()
        safe_slot_key = str(slot_key or "").strip()
        if not target or not safe_slot_key:
            raise KeyError(template_id)
        with self._lock:
            state = self._read_state()
            templates = self._normalized_templates(state.get("templates"))
            found = False
            for item in templates:
                if str(item.get("id") or "").strip() != target:
                    continue
                item["last_suppression_window"] = safe_slot_key
                item["last_suppressed_at"] = current.astimezone(timezone.utc).isoformat()
                item["last_suppression_reason"] = str(reason or "").strip()
                item["last_suppression_note"] = str(note or "").strip()
                item["last_scheduled_outcome"] = "suppressed"
                item["last_scheduled_note"] = str(note or "").strip()
                found = True
                break
            if not found:
                raise KeyError(template_id)
            state["templates"] = templates
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
            return self.snapshot()

    def scheduled_delivery_count_last_hour(self, *, now: datetime | None = None) -> int:
        current = (now or _local_now()).astimezone(timezone.utc)
        window_start = current - timedelta(hours=1)
        with self._lock:
            state = self._read_state()
        count = 0
        for item in list(state.get("recent_runs") or []):
            row = self._normalize_run(item)
            if str(row.get("triggered_by") or "").strip() != "scheduler":
                continue
            if str(row.get("status") or "").strip().lower() != "completed":
                continue
            completed_at = str(row.get("completed_at") or "").strip()
            try:
                completed = datetime.fromisoformat(completed_at)
            except Exception:
                continue
            if completed.tzinfo is None:
                completed = completed.replace(tzinfo=timezone.utc)
            else:
                completed = completed.astimezone(timezone.utc)
            if completed >= window_start:
                count += 1
        return count

    def record_scheduled_run_outcome(
        self,
        template_id: str,
        *,
        outcome: str,
        note: str = "",
        now: datetime | None = None,
    ) -> dict[str, Any]:
        current = (now or _local_now()).astimezone()
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
                item["last_scheduled_run_at"] = current.astimezone(timezone.utc).isoformat()
                item["last_scheduled_outcome"] = str(outcome or "").strip() or "completed"
                item["last_scheduled_note"] = str(note or "").strip()
                item["last_suppression_window"] = ""
                item["last_suppressed_at"] = ""
                item["last_suppression_reason"] = ""
                item["last_suppression_note"] = ""
                item["schedule_status"] = "Scheduled" if bool(item.get("schedule_enabled")) else "Paused"
                found = True
                break
            if not found:
                raise KeyError(template_id)
            state["templates"] = templates
            state["updated_at"] = _utc_now_iso()
            self._write_state(state)
            return self.snapshot()

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "templates": [dict(item) for item in self.DEFAULT_TEMPLATES],
            "active_run": None,
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
        payload["active_run"] = self._normalize_active_run(payload.get("active_run"))
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
            "active_run": self._normalize_active_run(state.get("active_run")),
            "recent_runs": [self._normalize_run(item) for item in list(state.get("recent_runs") or [])],
            "delivery_inbox": [
                self._normalize_delivery_item(item)
                for item in list(state.get("delivery_inbox") or [])
            ],
            "updated_at": str(state.get("updated_at") or _utc_now_iso()),
        }
        write_json_atomic(self._path, normalized)

    def _normalized_templates(self, value: Any) -> list[dict[str, Any]]:
        raw_items = list(value or []) if isinstance(value, list) else [dict(item) for item in self.DEFAULT_TEMPLATES]
        default_lookup = {str(item["id"]): dict(item) for item in self.DEFAULT_TEMPLATES}
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
            merged["allowed_hostnames"] = [
                str(host).strip()
                for host in list(merged.get("allowed_hostnames") or [])
                if host is not None and str(host).strip()
            ]
            merged["manual_run_available"] = bool(merged.get("manual_run_available"))
            merged["schedule_enabled"] = bool(merged.get("schedule_enabled"))
            merged["max_network_calls"] = max(0, int(merged.get("max_network_calls") or 0))
            merged["max_files_touched"] = max(0, int(merged.get("max_files_touched") or 0))
            merged["max_bytes_read"] = max(0, int(merged.get("max_bytes_read") or 0))
            merged["max_bytes_written"] = max(0, int(merged.get("max_bytes_written") or 0))
            merged["schedule_clock_local"] = str(merged.get("schedule_clock_local") or "").strip()
            merged["last_scheduled_window"] = str(merged.get("last_scheduled_window") or "").strip()
            merged["last_scheduled_run_at"] = str(merged.get("last_scheduled_run_at") or "").strip()
            merged["last_scheduled_outcome"] = str(merged.get("last_scheduled_outcome") or "").strip()
            merged["last_scheduled_note"] = str(merged.get("last_scheduled_note") or "").strip()
            merged["last_suppression_window"] = str(merged.get("last_suppression_window") or "").strip()
            merged["last_suppressed_at"] = str(merged.get("last_suppressed_at") or "").strip()
            merged["last_suppression_reason"] = str(merged.get("last_suppression_reason") or "").strip()
            merged["last_suppression_note"] = str(merged.get("last_suppression_note") or "").strip()
            next_run_at, next_run_label, schedule_status = self._schedule_runtime_fields(merged)
            merged["next_run_at"] = next_run_at
            merged["next_run_label"] = next_run_label
            merged["schedule_status"] = schedule_status
            merged["envelope_preview"] = self._template_envelope_preview(merged)
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
            "summary_route": str(raw.get("summary_route") or "").strip(),
            "summary_model": str(raw.get("summary_model") or "").strip(),
            "scope_summary": str(raw.get("scope_summary") or "").strip(),
            "budget_summary": str(raw.get("budget_summary") or "").strip(),
            "budget_usage": dict(raw.get("budget_usage") or {}),
            "source_notes": dict(raw.get("source_notes") or {}),
            "strict_preflight": dict(raw.get("strict_preflight") or {}),
            "usage_meta": dict(raw.get("usage_meta") or {}),
        }

    def _normalize_active_run(self, value: Any) -> dict[str, Any] | None:
        if not value:
            return None
        raw = dict(value or {})
        envelope_id = str(raw.get("envelope_id") or "").strip()
        if not envelope_id:
            return None
        return {
            "envelope_id": envelope_id,
            "template_id": str(raw.get("template_id") or "").strip(),
            "title": str(raw.get("title") or "").strip() or "Run",
            "status": str(raw.get("status") or "").strip() or "running",
            "status_label": str(raw.get("status_label") or "").strip() or "Running now",
            "triggered_by": str(raw.get("triggered_by") or "").strip() or "dashboard",
            "delivery_mode": str(raw.get("delivery_mode") or "").strip() or "widget",
            "delivery_channels": {
                "widget": bool(dict(raw.get("delivery_channels") or {}).get("widget")),
                "chat": bool(dict(raw.get("delivery_channels") or {}).get("chat")),
            },
            "started_at": str(raw.get("started_at") or _utc_now_iso()),
            "summary": str(raw.get("summary") or "").strip(),
            "scope_summary": str(raw.get("scope_summary") or "").strip(),
            "budget_summary": str(raw.get("budget_summary") or "").strip(),
            "budget_usage": dict(raw.get("budget_usage") or {}),
            "cancel_requested": bool(raw.get("cancel_requested")),
        }

    def _active_run_summary(self, active_run: dict[str, Any] | None) -> str:
        if not active_run:
            return "No home-agent runs are active right now."
        title = str(active_run.get("title") or "Task").strip() or "Task"
        triggered_by = str(active_run.get("triggered_by") or "").strip()
        source = "scheduled" if triggered_by == "scheduler" else "manual"
        status = str(active_run.get("status_label") or "Running now").strip() or "Running now"
        return f"{title} is {status.lower()} through the {source} OpenClaw lane."

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
                "triggered_by": str(run_entry.get("triggered_by") or "").strip() or "dashboard",
                "created_at": str(run_entry.get("completed_at") or run_entry.get("started_at") or _utc_now_iso()),
                "status": "ready",
                "dismissed_at": "",
                "usage_meta": dict(run_entry.get("usage_meta") or {}),
            }
        )

    def _template_envelope_preview(self, template: dict[str, Any]) -> dict[str, Any]:
        envelope = TaskEnvelope(
            id="ENV-PREVIEW",
            title=str(template.get("title") or "OpenClaw Task").strip(),
            template_id=str(template.get("id") or "").strip(),
            tools_allowed=[
                str(tool).strip()
                for tool in list(template.get("tools_allowed") or [])
                if str(tool).strip()
            ],
            allowed_hostnames=[
                str(host).strip()
                for host in list(template.get("allowed_hostnames") or [])
                if str(host).strip()
            ],
            max_steps=max(0, int(template.get("max_steps") or 0)),
            max_duration_s=max(0, int(template.get("max_duration_s") or 0)),
            max_network_calls=max(0, int(template.get("max_network_calls") or 0)),
            max_files_touched=max(0, int(template.get("max_files_touched") or 0)),
            max_bytes_read=max(0, int(template.get("max_bytes_read") or 0)),
            max_bytes_written=max(0, int(template.get("max_bytes_written") or 0)),
            triggered_by="preview",
            delivery_mode=str(template.get("delivery_mode") or "widget").strip() or "widget",
        )
        return envelope.preview_dict()

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
            "triggered_by": str(raw.get("triggered_by") or "").strip() or "dashboard",
            "created_at": str(raw.get("created_at") or _utc_now_iso()),
            "status": str(raw.get("status") or "ready").strip() or "ready",
            "dismissed_at": str(raw.get("dismissed_at") or "").strip(),
            "usage_meta": dict(raw.get("usage_meta") or {}),
        }

    def _new_delivery_id(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"DEL-{stamp}-{uuid4().hex[:4].upper()}"

    def _schedule_runtime_fields(self, template: dict[str, Any]) -> tuple[str, str, str]:
        if not bool(template.get("manual_run_available")):
            label = str(template.get("availability_label") or "Needs connector").strip() or "Needs connector"
            return "", label, label

        clock_value = str(template.get("schedule_clock_local") or "").strip()
        if not clock_value:
            return "", "Schedule unavailable", "Unavailable"
        if not bool(template.get("schedule_enabled")):
            return "", "Paused", "Paused"

        now_local = _local_now()
        slot_local = _local_due_slot(clock_value, now=now_local)
        if slot_local is None:
            return "", "Schedule unavailable", "Unavailable"

        slot_key = slot_local.astimezone(timezone.utc).isoformat()
        last_window = str(template.get("last_scheduled_window") or "").strip()
        last_suppression_window = str(template.get("last_suppression_window") or "").strip()
        last_suppression_reason = str(template.get("last_suppression_reason") or "").strip()
        last_suppression_note = str(template.get("last_suppression_note") or "").strip()
        if now_local < slot_local:
            next_run_local = slot_local
        elif last_window == slot_key:
            next_run_local = slot_local + timedelta(days=1)
        elif last_suppression_window == slot_key and last_suppression_reason:
            return "", last_suppression_note or "Held until policy allows", self._suppression_status_label(last_suppression_reason)
        elif _is_stale_scheduled_slot(slot_local, now=now_local):
            next_run_local = slot_local + timedelta(days=1)
        else:
            next_run_local = slot_local

        next_run_at = next_run_local.astimezone(timezone.utc).isoformat()
        last_outcome = str(template.get("last_scheduled_outcome") or "").strip().lower()
        status = "Scheduled (last run failed)" if last_outcome == "failed" else "Scheduled"
        return next_run_at, f"Next at {_display_clock_label(clock_value)}", status

    def _suppression_status_label(self, reason: str) -> str:
        normalized = str(reason or "").strip().lower()
        if normalized == "quiet_hours":
            return "Held by quiet hours"
        if normalized == "rate_limit":
            return "Held by rate limit"
        return "Held by policy"


openclaw_agent_runtime_store = OpenClawAgentRuntimeStore()
