from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_iso(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat()


def _from_iso(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw)
    except Exception:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class NotificationScheduleStore:
    """Persistent explicit schedule store for reminders and brief cues."""

    SCHEMA_VERSION = "1.0"
    ALLOWED_KINDS = {"reminder", "daily_brief"}
    ALLOWED_RECURRENCES = {"once", "daily"}

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nova_state"
            / "notifications"
            / "schedules.json"
        )
        self._path = Path(path) if path else default_path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write_state(self._default_state())

    @property
    def path(self) -> Path:
        return self._path

    def create_schedule(
        self,
        *,
        kind: str,
        title: str,
        body: str,
        recurrence: str,
        next_run_at: datetime,
        command: str = "",
    ) -> dict[str, Any]:
        normalized_kind = self._normalize_kind(kind)
        normalized_recurrence = self._normalize_recurrence(recurrence)
        title_text = str(title or "").strip()
        body_text = str(body or "").strip()
        if not title_text:
            raise ValueError("Schedule title cannot be empty.")
        if not body_text:
            raise ValueError("Schedule body cannot be empty.")

        now = _utc_now()
        item = {
            "id": self._new_id(),
            "kind": normalized_kind,
            "title": title_text[:140],
            "body": body_text[:400],
            "recurrence": normalized_recurrence,
            "command": str(command or "").strip(),
            "active": True,
            "created_at": _as_iso(now),
            "updated_at": _as_iso(now),
            "next_run_at": _as_iso(next_run_at),
            "last_surface_at": "",
            "last_dismissed_at": "",
        }
        with self._lock:
            state = self._read_state()
            schedules = list(state.get("schedules") or [])
            schedules.append(item)
            state["schedules"] = schedules
            self._write_state(state)
        return dict(item)

    def list_schedules(self, *, include_inactive: bool = False, limit: int = 25) -> list[dict[str, Any]]:
        with self._lock:
            state = self._read_state()
            schedules = list(state.get("schedules") or [])
        if not include_inactive:
            schedules = [item for item in schedules if bool(item.get("active"))]
        schedules = sorted(
            schedules,
            key=lambda row: str(row.get("next_run_at") or ""),
        )
        safe_limit = max(1, min(int(limit or 25), 100))
        return [dict(item) for item in schedules[:safe_limit]]

    def get_schedule(self, schedule_id: str) -> dict[str, Any] | None:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                return None
            return dict(item)

    def cancel_schedule(self, schedule_id: str) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["active"] = False
            item["updated_at"] = _as_iso(_utc_now())
            self._write_state(state)
            return dict(item)

    def dismiss_schedule(self, schedule_id: str, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            recurrence = self._normalize_recurrence(item.get("recurrence"))
            if recurrence == "daily":
                next_run = _from_iso(item.get("next_run_at")) or current
                while next_run <= current:
                    next_run = next_run + timedelta(days=1)
                item["next_run_at"] = _as_iso(next_run)
                item["last_dismissed_at"] = _as_iso(current)
                item["updated_at"] = _as_iso(current)
            else:
                item["active"] = False
                item["last_dismissed_at"] = _as_iso(current)
                item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    def mark_due_surface(self, schedule_id: str, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["last_surface_at"] = _as_iso(current)
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    def summarize(self, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        schedules = self.list_schedules(include_inactive=False, limit=100)
        due_items: list[dict[str, Any]] = []
        upcoming_items: list[dict[str, Any]] = []

        for item in schedules:
            next_run = _from_iso(item.get("next_run_at"))
            if next_run is None:
                continue
            row = self._serialize_schedule(item, now=current)
            if next_run <= current:
                due_items.append(row)
            else:
                upcoming_items.append(row)

        summary = (
            f"{len(due_items)} due | {len(upcoming_items)} upcoming"
            if schedules
            else "No schedules yet. Create one explicitly when you want Nova to remind you."
        )

        return {
            "summary": summary,
            "active_count": len(schedules),
            "due_count": len(due_items),
            "upcoming_count": len(upcoming_items),
            "due_items": due_items[:5],
            "upcoming_items": upcoming_items[:5],
        }

    def _serialize_schedule(self, item: dict[str, Any], *, now: datetime) -> dict[str, Any]:
        next_run = _from_iso(item.get("next_run_at"))
        due = bool(next_run and next_run <= now)
        return {
            "id": str(item.get("id") or ""),
            "kind": str(item.get("kind") or ""),
            "title": str(item.get("title") or ""),
            "body": str(item.get("body") or ""),
            "command": str(item.get("command") or ""),
            "recurrence": str(item.get("recurrence") or ""),
            "active": bool(item.get("active")),
            "next_run_at": str(item.get("next_run_at") or ""),
            "last_surface_at": str(item.get("last_surface_at") or ""),
            "due": due,
        }

    def _new_id(self) -> str:
        stamp = _utc_now().strftime("%Y%m%d-%H%M%S")
        return f"SCH-{stamp}-{uuid4().hex[:4].upper()}"

    def _find_item(self, state: dict[str, Any], schedule_id: str) -> dict[str, Any] | None:
        target = str(schedule_id or "").strip()
        for item in list(state.get("schedules") or []):
            if str(item.get("id") or "").strip() == target:
                return item
        return None

    def _normalize_kind(self, value: Any) -> str:
        lowered = str(value or "reminder").strip().lower()
        if lowered not in self.ALLOWED_KINDS:
            return "reminder"
        return lowered

    def _normalize_recurrence(self, value: Any) -> str:
        lowered = str(value or "once").strip().lower()
        if lowered not in self.ALLOWED_RECURRENCES:
            return "once"
        return lowered

    def _default_state(self) -> dict[str, Any]:
        return {"schema_version": self.SCHEMA_VERSION, "schedules": []}

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = self._default_state()
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {
                "schema_version": self.SCHEMA_VERSION,
                "schedules": list(payload.get("schedules") or []),
            }
        if not isinstance(payload.get("schedules"), list):
            payload["schedules"] = []
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "schedules": list(state.get("schedules") or []),
        }
        self._path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
