from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


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

    SCHEMA_VERSION = "1.1"
    ALLOWED_KINDS = {"reminder", "daily_brief"}
    ALLOWED_RECURRENCES = {"once", "daily"}
    DEFAULT_POLICY = {
        "quiet_hours_enabled": False,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "max_deliveries_per_hour": 2,
    }

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "notifications", "schedules.json")
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
            "last_delivery_attempt_at": "",
            "last_delivery_outcome": "",
            "last_delivery_note": "",
            "last_delivered_at": "",
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

    def update_policy(
        self,
        *,
        quiet_hours_enabled: bool | None = None,
        quiet_hours_start: str | None = None,
        quiet_hours_end: str | None = None,
        max_deliveries_per_hour: int | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            policy = self._normalize_policy(state.get("policy"))
            if quiet_hours_enabled is not None:
                policy["quiet_hours_enabled"] = bool(quiet_hours_enabled)
            if quiet_hours_start is not None:
                policy["quiet_hours_start"] = self._normalize_clock_value(
                    quiet_hours_start,
                    fallback=str(self.DEFAULT_POLICY["quiet_hours_start"]),
                )
            if quiet_hours_end is not None:
                policy["quiet_hours_end"] = self._normalize_clock_value(
                    quiet_hours_end,
                    fallback=str(self.DEFAULT_POLICY["quiet_hours_end"]),
                )
            if max_deliveries_per_hour is not None:
                safe_limit = max(1, min(int(max_deliveries_per_hour), 12))
                policy["max_deliveries_per_hour"] = safe_limit
            state["policy"] = policy
            self._write_state(state)
            return self._build_policy_snapshot(state, now=_utc_now())

    def policy_snapshot(self, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            return self._build_policy_snapshot(state, now=current)

    def delivery_policy_decision(
        self,
        *,
        now: datetime | None = None,
        deliveries_last_hour_override: int | None = None,
    ) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            policy = self._build_policy_snapshot(state, now=current)

        deliveries_last_hour = (
            max(0, int(deliveries_last_hour_override))
            if deliveries_last_hour_override is not None
            else int(policy.get("deliveries_last_hour") or 0)
        )
        max_per_hour = int(policy.get("max_deliveries_per_hour") or 1)
        if bool(policy.get("quiet_hours_enabled")) and self._in_quiet_hours(current, policy):
            return {
                "allowed": False,
                "reason": "quiet_hours",
                "note": f"Held until quiet hours end ({policy.get('quiet_hours_label')}).",
                "policy": dict(policy),
            }
        if deliveries_last_hour >= max_per_hour:
            return {
                "allowed": False,
                "reason": "rate_limit",
                "note": f"Held by rate limit ({max_per_hour} per hour).",
                "policy": dict(policy),
            }
        return {
            "allowed": True,
            "reason": "allowed",
            "note": "Delivery permitted by current notification policy.",
            "policy": dict(policy),
        }

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

    def reschedule_schedule(
        self,
        schedule_id: str,
        *,
        next_run_at: datetime,
    ) -> dict[str, Any]:
        current = _utc_now()
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["next_run_at"] = _as_iso(next_run_at)
            item["last_surface_at"] = ""
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

    def record_delivery_attempt(self, schedule_id: str, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["last_delivery_attempt_at"] = _as_iso(current)
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    def record_delivery_outcome(
        self,
        schedule_id: str,
        *,
        outcome: str,
        note: str = "",
        now: datetime | None = None,
        surfaced: bool = False,
    ) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["last_delivery_outcome"] = str(outcome or "").strip()[:80]
            item["last_delivery_note"] = str(note or "").strip()[:240]
            if surfaced:
                item["last_surface_at"] = _as_iso(current)
                item["last_delivered_at"] = _as_iso(current)
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    def evaluate_delivery_policy(
        self,
        schedule_id: str,
        *,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)

            policy = self._build_policy_snapshot(state, now=current)
            next_run = _from_iso(item.get("next_run_at"))
            last_surface = str(item.get("last_surface_at") or "").strip()
            next_run_raw = str(item.get("next_run_at") or "").strip()

            if not bool(item.get("active")):
                return self._delivery_policy_result(item, policy, False, "inactive", "Schedule is inactive.")
            if next_run is None or next_run > current:
                return self._delivery_policy_result(item, policy, False, "not_due", "Schedule is not due yet.")
            if last_surface and next_run_raw and last_surface >= next_run_raw:
                return self._delivery_policy_result(
                    item,
                    policy,
                    False,
                    "already_surfaced",
                    "Notification already surfaced for the current run window.",
                )
            if bool(policy.get("quiet_hours_enabled")) and self._in_quiet_hours(current, policy):
                return self._delivery_policy_result(
                    item,
                    policy,
                    False,
                    "quiet_hours",
                    f"Held until quiet hours end ({policy.get('quiet_hours_label')}).",
                )

            deliveries_last_hour = int(policy.get("deliveries_last_hour") or 0)
            max_per_hour = int(policy.get("max_deliveries_per_hour") or 1)
            if deliveries_last_hour >= max_per_hour:
                return self._delivery_policy_result(
                    item,
                    policy,
                    False,
                    "rate_limit",
                    f"Held by rate limit ({max_per_hour} per hour).",
                )

            return self._delivery_policy_result(
                item,
                policy,
                True,
                "allowed",
                "Delivery permitted by current notification policy.",
            )

    def summarize(self, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
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
            "policy": self._build_policy_snapshot(state, now=current),
            "policy_summary": self._build_policy_snapshot(state, now=current).get("summary", ""),
            "inspectability_note": "Schedules are explicit, inspectable, cancellable, and policy-bound.",
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
            "last_delivery_attempt_at": str(item.get("last_delivery_attempt_at") or ""),
            "last_delivery_outcome": str(item.get("last_delivery_outcome") or ""),
            "last_delivery_note": str(item.get("last_delivery_note") or ""),
            "last_delivered_at": str(item.get("last_delivered_at") or ""),
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
        return {
            "schema_version": self.SCHEMA_VERSION,
            "schedules": [],
            "policy": dict(self.DEFAULT_POLICY),
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = self._default_state()
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {
                "schema_version": self.SCHEMA_VERSION,
                "schedules": list(payload.get("schedules") or []),
                "policy": dict(payload.get("policy") or self.DEFAULT_POLICY),
            }
        if not isinstance(payload.get("schedules"), list):
            payload["schedules"] = []
        payload["policy"] = self._normalize_policy(payload.get("policy"))
        payload["schedules"] = [self._normalize_item(dict(item or {})) for item in payload["schedules"]]
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "schedules": [self._normalize_item(dict(item or {})) for item in list(state.get("schedules") or [])],
            "policy": self._normalize_policy(state.get("policy")),
        }
        write_json_atomic(self._path, normalized)

    def _normalize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(item)
        for field_name in (
            "last_surface_at",
            "last_dismissed_at",
            "last_delivery_attempt_at",
            "last_delivery_outcome",
            "last_delivery_note",
            "last_delivered_at",
        ):
            normalized[field_name] = str(normalized.get(field_name) or "").strip()
        return normalized

    def _normalize_policy(self, payload: Any) -> dict[str, Any]:
        raw = dict(payload or {})
        safe_limit = raw.get("max_deliveries_per_hour", self.DEFAULT_POLICY["max_deliveries_per_hour"])
        try:
            limit_value = max(1, min(int(safe_limit), 12))
        except Exception:
            limit_value = int(self.DEFAULT_POLICY["max_deliveries_per_hour"])
        return {
            "quiet_hours_enabled": bool(raw.get("quiet_hours_enabled", self.DEFAULT_POLICY["quiet_hours_enabled"])),
            "quiet_hours_start": self._normalize_clock_value(
                raw.get("quiet_hours_start", self.DEFAULT_POLICY["quiet_hours_start"]),
                fallback=str(self.DEFAULT_POLICY["quiet_hours_start"]),
            ),
            "quiet_hours_end": self._normalize_clock_value(
                raw.get("quiet_hours_end", self.DEFAULT_POLICY["quiet_hours_end"]),
                fallback=str(self.DEFAULT_POLICY["quiet_hours_end"]),
            ),
            "max_deliveries_per_hour": limit_value,
        }

    def _normalize_clock_value(self, raw: Any, *, fallback: str) -> str:
        text = str(raw or "").strip().lower().replace(".", "")
        text = text.replace("  ", " ")
        if not text:
            text = str(fallback)
        if text.endswith("am") or text.endswith("pm"):
            text = text[:-2].strip() + f" {text[-2:]}"
        for fmt in ("%H:%M", "%H", "%I:%M %p", "%I %p"):
            try:
                parsed = datetime.strptime(text, fmt)
                return parsed.strftime("%H:%M")
            except ValueError:
                continue
        return str(fallback)

    def _build_policy_snapshot(self, state: dict[str, Any], *, now: datetime) -> dict[str, Any]:
        policy = self._normalize_policy(state.get("policy"))
        deliveries_last_hour = self._deliveries_in_last_hour(state, now)
        quiet_enabled = bool(policy.get("quiet_hours_enabled"))
        quiet_label = (
            f"{self._render_clock_value(policy['quiet_hours_start'])} to {self._render_clock_value(policy['quiet_hours_end'])}"
            if quiet_enabled
            else "Off"
        )
        max_per_hour = int(policy.get("max_deliveries_per_hour") or 1)
        return {
            "quiet_hours_enabled": quiet_enabled,
            "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
            "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
            "quiet_hours_label": quiet_label,
            "max_deliveries_per_hour": max_per_hour,
            "deliveries_last_hour": deliveries_last_hour,
            "summary": f"Quiet hours: {quiet_label}. Rate limit: {max_per_hour} per hour. Delivered last hour: {deliveries_last_hour}.",
        }

    def _render_clock_value(self, raw: str) -> str:
        text = str(raw or "").strip()
        try:
            parsed = datetime.strptime(text, "%H:%M")
        except ValueError:
            return text
        rendered = parsed.strftime("%I:%M %p")
        return rendered.lstrip("0")

    def _deliveries_in_last_hour(self, state: dict[str, Any], now: datetime) -> int:
        window_start = now - timedelta(hours=1)
        count = 0
        for item in list(state.get("schedules") or []):
            delivered_at = _from_iso(item.get("last_delivered_at"))
            if delivered_at is not None and delivered_at >= window_start:
                count += 1
        return count

    def _in_quiet_hours(self, now: datetime, policy: dict[str, Any]) -> bool:
        if not bool(policy.get("quiet_hours_enabled")):
            return False
        try:
            start_value = datetime.strptime(str(policy.get("quiet_hours_start") or ""), "%H:%M")
            end_value = datetime.strptime(str(policy.get("quiet_hours_end") or ""), "%H:%M")
        except ValueError:
            return False
        current_minutes = now.astimezone().hour * 60 + now.astimezone().minute
        start_minutes = start_value.hour * 60 + start_value.minute
        end_minutes = end_value.hour * 60 + end_value.minute
        if start_minutes == end_minutes:
            return False
        if start_minutes < end_minutes:
            return start_minutes <= current_minutes < end_minutes
        return current_minutes >= start_minutes or current_minutes < end_minutes

    def _delivery_policy_result(
        self,
        item: dict[str, Any],
        policy: dict[str, Any],
        allowed: bool,
        reason: str,
        note: str,
    ) -> dict[str, Any]:
        return {
            "allowed": bool(allowed),
            "reason": str(reason or "").strip(),
            "note": str(note or "").strip(),
            "item": dict(item),
            "policy": dict(policy),
        }
