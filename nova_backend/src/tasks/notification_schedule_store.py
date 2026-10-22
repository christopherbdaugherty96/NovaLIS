from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from src.durability.corruption import StateCorruptError, read_json_state, require_state
from src.durability.maintenance import authoritative_mutation, mutation_scope
from src.tasks.local_time import as_local, resolve_local_wall_time
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


@dataclass(frozen=True)
class ScheduleReadResult:
    schedules: tuple[dict[str, Any], ...]
    available: bool
    error: str = ""


class NotificationScheduleStore:
    """Persistent explicit schedule store for reminders and brief cues."""

    SCHEMA_VERSION = "1.3"
    ALLOWED_KINDS = {"reminder", "daily_brief"}
    ALLOWED_RECURRENCES = {"once", "daily", "weekly"}
    ALLOWED_HOLD_REASONS = {
        "quiet_hours",
        "display_off",
        "session_locked",
        "state_unknown",
    }
    DEFAULT_POLICY = {
        "quiet_hours_enabled": False,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "max_deliveries_per_hour": 2,
    }

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        local_zone: tzinfo | None = None,
    ) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "notifications", "schedules.json")
        )
        self._path = Path(path) if path else default_path
        self._local_zone = local_zone
        self._lock = shared_path_lock(self._path)
        if not self._path.exists():
            with mutation_scope(), self._lock:
                if not self._path.exists():
                    self._path.parent.mkdir(parents=True, exist_ok=True)
                    self._write_state(self._default_state())

    @property
    def path(self) -> Path:
        return self._path

    @authoritative_mutation
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
            "delivery_occurrence_id": "",
            "delivery_claimed_at": "",
            "delivery_state": "pending",
            "delivery_grant": {},
            "delivery_hold_reason": "",
            "delivery_retry_state": "",
            "delivery_held_at": "",
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

    def read_schedules(
        self,
        *,
        include_inactive: bool = False,
        limit: int = 25,
    ) -> ScheduleReadResult:
        """Read schedules while distinguishing empty state from unreadable state."""

        try:
            with self._lock:
                payload = read_json_state(self._path, "notification_schedules")
        except FileNotFoundError:
            return ScheduleReadResult((), available=True)
        except StateCorruptError as exc:
            return ScheduleReadResult((), available=False, error=type(exc).__name__)
        try:
            if not isinstance(payload, dict) or not isinstance(payload.get("schedules"), list):
                raise ValueError("Invalid notification schedule state")
            if not all(self._is_structurally_valid_item(item) for item in payload["schedules"]):
                raise ValueError("Invalid notification schedule entry")
            schedules = [
                self._normalize_item(dict(item))
                for item in payload["schedules"]
            ]
            if not include_inactive:
                schedules = [item for item in schedules if bool(item.get("active"))]
            schedules.sort(key=lambda row: str(row.get("next_run_at") or ""))
            safe_limit = max(1, min(int(limit or 25), 100))
            return ScheduleReadResult(tuple(schedules[:safe_limit]), available=True)
        except Exception as exc:
            return ScheduleReadResult((), available=False, error=type(exc).__name__)

    def _is_structurally_valid_item(self, item: Any) -> bool:
        if not isinstance(item, dict) or not isinstance(item.get("active"), bool):
            return False
        required_text = ("id", "kind", "title", "body", "recurrence", "next_run_at")
        if any(not str(item.get(field) or "").strip() for field in required_text):
            return False
        if str(item.get("kind")).strip().lower() not in self.ALLOWED_KINDS:
            return False
        if str(item.get("recurrence")).strip().lower() not in self.ALLOWED_RECURRENCES:
            return False
        return _from_iso(item.get("next_run_at")) is not None

    def get_schedule(self, schedule_id: str) -> dict[str, Any] | None:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                return None
            return dict(item)

    @authoritative_mutation
    def grant_delivery_authority(
        self,
        schedule_id: str,
        *,
        channel: str,
        receipt_logger: Callable[[str, dict[str, Any]], None],
    ) -> dict[str, Any]:
        """Persist an exact delivery grant only after its ledger receipt succeeds."""

        normalized_channel = str(channel or "").strip().lower()
        if normalized_channel != "windows_toast":
            raise ValueError("Unsupported reminder delivery channel.")
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            scope = self._delivery_grant_scope(item, state, channel=normalized_channel)
            scope_hash = self._scope_hash(scope)
            grant = {
                "schema_version": "1.0",
                "grant_id": f"RDG-{uuid4().hex.upper()}",
                "scope_hash": scope_hash,
                "schedule_id": str(item.get("id") or ""),
                "text": str(item.get("body") or ""),
                "due_at": str(item.get("next_run_at") or ""),
                "recurrence": str(item.get("recurrence") or "once"),
                "channel": normalized_channel,
                "delivery_policy": scope["delivery_policy"],
                "state": "active",
                "issued_at": _as_iso(_utc_now()),
            }
            # Deliberately not best-effort: authority must not exist without a
            # durable receipt. The caller sees and reports any ledger failure.
            receipt_logger(
                "NOTIFICATION_DELIVERY_AUTHORIZED",
                {
                    "grant_id": grant["grant_id"],
                    "schedule_id": grant["schedule_id"],
                    "scope_hash": scope_hash,
                    "channel": normalized_channel,
                },
            )
            item["delivery_grant"] = grant
            item["delivery_hold_reason"] = ""
            item["delivery_retry_state"] = ""
            item["delivery_held_at"] = ""
            item["updated_at"] = _as_iso(_utc_now())
            self._write_state(state)
            return dict(grant)

    def delivery_authority_decision(
        self, schedule_id: str, *, channel: str
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            grant = dict(item.get("delivery_grant") or {})
            if str(grant.get("state") or "") != "active":
                return {"allowed": False, "reason": "missing_or_revoked_grant"}
            scope = self._delivery_grant_scope(
                item, state, channel=str(channel or "").strip().lower()
            )
            if str(grant.get("scope_hash") or "") != self._scope_hash(scope):
                return {"allowed": False, "reason": "grant_scope_mismatch"}
            return {
                "allowed": True,
                "reason": "authorized",
                "grant_id": str(grant.get("grant_id") or ""),
                "scope_hash": str(grant.get("scope_hash") or ""),
            }

    @authoritative_mutation
    def record_delivery_hold(
        self,
        schedule_id: str,
        *,
        reason: str,
        retry_state: str = "waiting_for_safe_state",
        now: datetime | None = None,
    ) -> dict[str, Any]:
        normalized_reason = str(reason or "").strip().lower()
        if normalized_reason not in self.ALLOWED_HOLD_REASONS:
            raise ValueError("Unsupported reminder hold reason.")
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["delivery_hold_reason"] = normalized_reason
            item["delivery_retry_state"] = str(retry_state or "").strip()[:80]
            item["delivery_held_at"] = _as_iso(current)
            item["last_delivery_outcome"] = "held"
            item["last_delivery_note"] = f"Held: {normalized_reason}."
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    @authoritative_mutation
    def clear_delivery_hold(self, schedule_id: str) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["delivery_hold_reason"] = ""
            item["delivery_retry_state"] = ""
            item["delivery_held_at"] = ""
            self._write_state(state)
            return dict(item)

    @authoritative_mutation
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

    @authoritative_mutation
    def cancel_schedule(self, schedule_id: str) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            item["active"] = False
            self._revoke_delivery_grant(item, reason="cancelled")
            item["updated_at"] = _as_iso(_utc_now())
            self._write_state(state)
            return dict(item)

    @authoritative_mutation
    def dismiss_schedule(self, schedule_id: str, *, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            recurrence = self._normalize_recurrence(item.get("recurrence"))
            if recurrence in {"daily", "weekly"}:
                next_run = _from_iso(item.get("next_run_at")) or current
                local_next_run = as_local(next_run, self._local_zone)
                interval_days = 1 if recurrence == "daily" else 7
                local_date = local_next_run.date()
                while next_run <= current:
                    local_date += timedelta(days=interval_days)
                    try:
                        next_run = resolve_local_wall_time(
                            local_date,
                            time(local_next_run.hour, local_next_run.minute),
                            local_zone=self._local_zone,
                        )
                    except ValueError:
                        # A recurrence cannot run inside a spring-forward gap.
                        # Skip that occurrence and preserve its wall time on the
                        # next valid recurrence date.
                        continue
                    local_next_run = next_run
                item["next_run_at"] = _as_iso(next_run)
                item["last_dismissed_at"] = _as_iso(current)
                item["updated_at"] = _as_iso(current)
            else:
                item["active"] = False
                item["last_dismissed_at"] = _as_iso(current)
                item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    @authoritative_mutation
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
            self._revoke_delivery_grant(item, reason="edited")
            item["last_surface_at"] = ""
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    @authoritative_mutation
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

    @authoritative_mutation
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

    @authoritative_mutation
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

    @authoritative_mutation
    def claim_due_occurrence(
        self,
        schedule_id: str,
        *,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """Atomically claim the current due instant before any display attempt."""

        current = (now or _utc_now()).astimezone(timezone.utc)
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            due_at = _from_iso(item.get("next_run_at"))
            occurrence_id = f"{schedule_id}@{str(item.get('next_run_at') or '')}"
            existing_occurrence = str(item.get("delivery_occurrence_id") or "")
            existing_state = str(item.get("delivery_state") or "pending")
            if (
                not bool(item.get("active"))
                or due_at is None
                or due_at > current
                or (existing_occurrence == occurrence_id and existing_state != "pending")
            ):
                return {"claimed": False, "occurrence_id": occurrence_id, **dict(item)}
            item["delivery_occurrence_id"] = occurrence_id
            item["delivery_claimed_at"] = _as_iso(current)
            item["delivery_state"] = "attempted"
            item["last_delivery_attempt_at"] = _as_iso(current)
            item["last_delivery_outcome"] = "delivery_attempted"
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return {"claimed": True, "occurrence_id": occurrence_id, **dict(item)}

    @authoritative_mutation
    def finish_claimed_occurrence(
        self,
        schedule_id: str,
        *,
        occurrence_id: str,
        outcome: str,
        note: str = "",
        now: datetime | None = None,
    ) -> dict[str, Any]:
        current = (now or _utc_now()).astimezone(timezone.utc)
        normalized_outcome = str(outcome or "").strip()
        if normalized_outcome not in {"delivered", "delivery_uncertain"}:
            raise ValueError("Unsupported terminal delivery outcome.")
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, schedule_id)
            if item is None:
                raise KeyError(schedule_id)
            if str(item.get("delivery_occurrence_id") or "") != str(occurrence_id or ""):
                raise ValueError("Delivery occurrence no longer matches the claimed reminder.")
            if str(item.get("delivery_state") or "") != "attempted":
                return dict(item)
            item["delivery_state"] = normalized_outcome
            item["last_delivery_outcome"] = normalized_outcome
            item["last_delivery_note"] = str(note or "").strip()[:240]
            if normalized_outcome == "delivered":
                item["last_surface_at"] = _as_iso(current)
                item["last_delivered_at"] = _as_iso(current)
            self._advance_after_terminal_delivery(item, current=current)
            item["updated_at"] = _as_iso(current)
            self._write_state(state)
            return dict(item)

    @authoritative_mutation
    def recover_interrupted_claims(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        """Close claims left ambiguous by a prior backend interruption."""

        current = (now or _utc_now()).astimezone(timezone.utc)
        recovered: list[dict[str, Any]] = []
        with self._lock:
            state = self._read_state()
            for item in list(state.get("schedules") or []):
                if str(item.get("delivery_state") or "") != "attempted":
                    continue
                item["delivery_state"] = "delivery_uncertain"
                item["last_delivery_outcome"] = "delivery_uncertain"
                item["last_delivery_note"] = (
                    "The backend stopped after claiming this occurrence; delivery was not retried."
                )
                self._advance_after_terminal_delivery(item, current=current)
                item["updated_at"] = _as_iso(current)
                recovered.append(dict(item))
            if recovered:
                self._write_state(state)
        return recovered

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
            "delivery_hold_reason": str(item.get("delivery_hold_reason") or ""),
            "delivery_retry_state": str(item.get("delivery_retry_state") or ""),
            "delivery_held_at": str(item.get("delivery_held_at") or ""),
            "delivery_authorized": str(
                dict(item.get("delivery_grant") or {}).get("state") or ""
            )
            == "active",
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
            payload = read_json_state(self._path, "notification_schedules")
        except FileNotFoundError:
            return self._default_state()
        require_state(isinstance(payload, dict), "notification_schedules", self._path, "expected object")
        require_state(isinstance(payload.get("schedules", []), list), "notification_schedules", self._path, "schedules must be a list")
        require_state(
            all(self._is_structurally_valid_item(item) for item in payload["schedules"]),
            "notification_schedules",
            self._path,
            "schedule entries must be structurally valid",
        )
        require_state(isinstance(payload.get("policy", {}), dict), "notification_schedules", self._path, "policy must be an object")
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {
                "schema_version": self.SCHEMA_VERSION,
                "schedules": list(payload.get("schedules") or []),
                "policy": dict(payload.get("policy") or self.DEFAULT_POLICY),
            }
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
            "delivery_occurrence_id",
            "delivery_claimed_at",
            "delivery_hold_reason",
            "delivery_retry_state",
            "delivery_held_at",
        ):
            normalized[field_name] = str(normalized.get(field_name) or "").strip()
        normalized["delivery_state"] = str(normalized.get("delivery_state") or "pending").strip()
        normalized["delivery_grant"] = dict(normalized.get("delivery_grant") or {})
        return normalized

    def _delivery_grant_scope(
        self,
        item: dict[str, Any],
        state: dict[str, Any],
        *,
        channel: str,
    ) -> dict[str, Any]:
        policy = self._normalize_policy(state.get("policy"))
        grant = dict(item.get("delivery_grant") or {})
        # A recurrence authorizes the series rooted at the approved due time;
        # advancing a delivered occurrence does not silently widen its scope.
        approved_due = str(
            grant.get("due_at")
            if str(grant.get("state") or "") == "active"
            else item.get("next_run_at") or ""
        )
        return {
            "schedule_id": str(item.get("id") or ""),
            "text": str(item.get("body") or ""),
            "due_at": approved_due,
            "recurrence": str(item.get("recurrence") or "once"),
            "channel": str(channel or ""),
            "delivery_policy": {
                "quiet_hours_enabled": bool(policy["quiet_hours_enabled"]),
                "quiet_hours_start": str(policy["quiet_hours_start"]),
                "quiet_hours_end": str(policy["quiet_hours_end"]),
                "max_deliveries_per_hour": int(policy["max_deliveries_per_hour"]),
            },
        }

    @staticmethod
    def _scope_hash(scope: dict[str, Any]) -> str:
        encoded = json.dumps(scope, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _revoke_delivery_grant(item: dict[str, Any], *, reason: str) -> None:
        grant = dict(item.get("delivery_grant") or {})
        if grant:
            grant["state"] = "revoked"
            grant["revoked_reason"] = str(reason or "")
            grant["revoked_at"] = _as_iso(_utc_now())
            item["delivery_grant"] = grant

    def _advance_after_terminal_delivery(self, item: dict[str, Any], *, current: datetime) -> None:
        recurrence = self._normalize_recurrence(item.get("recurrence"))
        if recurrence == "once":
            item["active"] = False
            return
        next_run = _from_iso(item.get("next_run_at")) or current
        local_next_run = as_local(next_run, self._local_zone)
        interval_days = 1 if recurrence == "daily" else 7
        local_date = local_next_run.date()
        while next_run <= current:
            local_date += timedelta(days=interval_days)
            try:
                next_run = resolve_local_wall_time(
                    local_date,
                    time(local_next_run.hour, local_next_run.minute),
                    local_zone=self._local_zone,
                )
            except ValueError:
                continue
        item["next_run_at"] = _as_iso(next_run)


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
        local_now = as_local(now, self._local_zone)
        current_minutes = local_now.hour * 60 + local_now.minute
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
