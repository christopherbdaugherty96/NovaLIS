"""
Authority Rank: 1 (co-equal with GovernorMediator) — Envelope Lifecycle Store
Role: Persistent store for all Nova-issued TaskEnvelopes. Enforces single-use,
      TTL expiration, and atomic status transitions. The authoritative record of
      what was allowed, when, and in what state.
Superseded by: Nothing. Authoritative alongside GovernorMediator.

File-backed under the same governed memory root used by other runtime stores
(src/data/nova_state/openclaw_envelopes.json). Not Redis — Redis is not in
Nova's stack.

Feature flag: NOVA_FEATURE_ENVELOPE_FACTORY=true required for behavioral use.
This module can be imported freely even when the flag is off.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


_STORE_FILENAME = "openclaw_envelopes.json"
_MAX_COMPLETED_RECORDS = 200  # keep rolling window; prevent unbounded growth


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


class EnvelopeStatus:
    ISSUED = "issued"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    _TERMINAL = frozenset({COMPLETED, CANCELLED, EXPIRED})
    _VALID_TRANSITIONS: dict[str, frozenset[str]] = {
        ISSUED: frozenset({RUNNING, CANCELLED, EXPIRED}),
        RUNNING: frozenset({AWAITING_APPROVAL, COMPLETED, CANCELLED, EXPIRED}),
        AWAITING_APPROVAL: frozenset({RUNNING, COMPLETED, CANCELLED}),
        COMPLETED: frozenset(),
        CANCELLED: frozenset(),
        EXPIRED: frozenset(),
    }

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        return status in cls._TERMINAL

    @classmethod
    def transition_allowed(cls, from_status: str, to_status: str) -> bool:
        return to_status in cls._VALID_TRANSITIONS.get(from_status, frozenset())


@dataclass
class EnvelopeRecord:
    """
    Persisted lifecycle record for a single Nova-issued envelope.

    The authority snapshot fields (issuing_channel, settings_hash,
    feature_flags_snapshot) are immutable after issuance. They enable
    post-hoc audit even if settings change after the run completes.
    """
    envelope_id: str
    status: str
    created_at: str
    updated_at: str
    expires_at: str

    # Authority snapshot — written at issuance, never changed
    issuing_channel: str
    settings_hash: str
    feature_flags_snapshot: dict[str, Any] = field(default_factory=dict)
    envelope_data: dict[str, Any] = field(default_factory=dict)   # serialized TaskEnvelope

    # Populated during / after execution
    used_at: Optional[str] = None
    invalidated_reason: Optional[str] = None
    run_metadata: dict[str, Any] = field(default_factory=dict)    # suspended state, etc.

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_expired(self) -> bool:
        if self.status == EnvelopeStatus.AWAITING_APPROVAL:
            return False  # never expire while waiting for user
        if EnvelopeStatus.is_terminal(self.status):
            return False
        expires = _parse_dt(self.expires_at)
        if expires is None:
            return False
        return _utc_now() > expires


class EnvelopeStoreError(RuntimeError):
    pass


class EnvelopeStore:
    """
    File-backed lifecycle store for Nova-issued envelopes.

    Usage:
        store = EnvelopeStore()
        store.register(issued_envelope)         # after EnvelopeFactory.issue()
        store.transition(id, "running")         # before agent_runner starts
        store.mark_used(id)                     # single-use enforcement
        record = store.get(id)                  # None if expired or not found
        store.transition(id, "completed")       # after run finishes
    """

    def __init__(self, store_path: Optional[Path] = None) -> None:
        if store_path is not None:
            self._path = Path(store_path)
        else:
            self._path = runtime_path(__file__, "data", "nova_state", _STORE_FILENAME)
        self._lock = shared_path_lock(self._path)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def register(
        self,
        *,
        envelope_id: UUID,
        envelope_data: dict[str, Any],
        issuing_channel: str,
        settings_hash: str,
        feature_flags_snapshot: dict[str, Any],
        issued_at: datetime,
        expires_at: datetime,
    ) -> EnvelopeRecord:
        """Persist a new envelope record immediately after issuance."""
        now_iso = _utc_now().isoformat()
        record = EnvelopeRecord(
            envelope_id=str(envelope_id),
            status=EnvelopeStatus.ISSUED,
            created_at=issued_at.isoformat(),
            updated_at=now_iso,
            expires_at=expires_at.isoformat(),
            issuing_channel=issuing_channel,
            settings_hash=settings_hash,
            feature_flags_snapshot=dict(feature_flags_snapshot),
            envelope_data=dict(envelope_data),
        )
        with self._lock:
            state = self._load()
            state[str(envelope_id)] = record.to_dict()
            self._save(state)
        return record

    def transition(self, envelope_id: str, to_status: str) -> EnvelopeRecord:
        """Atomically move an envelope to a new status."""
        eid = str(envelope_id or "").strip()
        with self._lock:
            state = self._load()
            raw = state.get(eid)
            if raw is None:
                raise EnvelopeStoreError(f"Envelope not found: {eid}")
            record = self._hydrate(raw)
            if record.is_expired() and not EnvelopeStatus.is_terminal(record.status):
                record = self._expire_in_place(state, eid, record)
                raise EnvelopeStoreError(
                    f"Envelope {eid} has expired (was {record.status}). Cannot transition to {to_status}."
                )
            if not EnvelopeStatus.transition_allowed(record.status, to_status):
                raise EnvelopeStoreError(
                    f"Invalid transition for envelope {eid}: {record.status!r} → {to_status!r}."
                )
            raw["status"] = to_status
            raw["updated_at"] = _utc_now().isoformat()
            state[eid] = raw
            self._save(state)
            return self._hydrate(raw)

    def mark_used(self, envelope_id: str) -> None:
        """Record that the envelope has been consumed. Prevents double-run."""
        eid = str(envelope_id or "").strip()
        with self._lock:
            state = self._load()
            raw = state.get(eid)
            if raw is None:
                raise EnvelopeStoreError(f"Envelope not found: {eid}")
            if raw.get("used_at"):
                raise EnvelopeStoreError(
                    f"Envelope {eid} has already been used at {raw['used_at']}. Single-use only."
                )
            raw["used_at"] = _utc_now().isoformat()
            raw["updated_at"] = raw["used_at"]
            state[eid] = raw
            self._save(state)

    def update_run_metadata(self, envelope_id: str, metadata: dict[str, Any]) -> None:
        """Merge run-time metadata (e.g. suspended state) into the record."""
        eid = str(envelope_id or "").strip()
        with self._lock:
            state = self._load()
            raw = state.get(eid)
            if raw is None:
                raise EnvelopeStoreError(f"Envelope not found: {eid}")
            existing = dict(raw.get("run_metadata") or {})
            existing.update(metadata)
            raw["run_metadata"] = existing
            raw["updated_at"] = _utc_now().isoformat()
            state[eid] = raw
            self._save(state)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, envelope_id: str) -> Optional[EnvelopeRecord]:
        """
        Return the record for an envelope, or None if not found.

        Automatically expires the record in the store if its TTL has passed
        and it is not in AWAITING_APPROVAL state. Returns None for expired
        envelopes so callers never operate on stale data.
        """
        eid = str(envelope_id or "").strip()
        with self._lock:
            state = self._load()
            raw = state.get(eid)
            if raw is None:
                return None
            record = self._hydrate(raw)
            if record.is_expired():
                self._expire_in_place(state, eid, record)
                self._save(state)
                return None
            return record

    def list_active(self) -> list[EnvelopeRecord]:
        """Return all non-terminal, non-expired envelope records."""
        with self._lock:
            state = self._load()
            results: list[EnvelopeRecord] = []
            for eid, raw in list(state.items()):
                record = self._hydrate(raw)
                if EnvelopeStatus.is_terminal(record.status):
                    continue
                if record.is_expired():
                    self._expire_in_place(state, eid, record)
                    continue
                results.append(record)
            self._save(state)
            return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, Any]:
        try:
            return dict(
                __import__("json").loads(self._path.read_text(encoding="utf-8"))
            )
        except FileNotFoundError:
            return {}
        except Exception:
            return {}

    def _save(self, state: dict[str, Any]) -> None:
        # Prune oldest terminal records if we exceed the cap
        terminal = [
            (eid, raw)
            for eid, raw in state.items()
            if EnvelopeStatus.is_terminal(raw.get("status", ""))
        ]
        if len(terminal) > _MAX_COMPLETED_RECORDS:
            terminal.sort(key=lambda item: str(item[1].get("updated_at") or ""))
            for eid, _ in terminal[: len(terminal) - _MAX_COMPLETED_RECORDS]:
                state.pop(eid, None)
        write_json_atomic(self._path, state)

    def _expire_in_place(
        self, state: dict[str, Any], eid: str, record: EnvelopeRecord
    ) -> EnvelopeRecord:
        raw = state.get(eid, {})
        raw["status"] = EnvelopeStatus.EXPIRED
        raw["updated_at"] = _utc_now().isoformat()
        raw["invalidated_reason"] = "ttl_expired"
        state[eid] = raw
        # _save is not called here — caller holds the lock and will call _save itself
        return self._hydrate(raw)

    @staticmethod
    def _hydrate(raw: dict[str, Any]) -> EnvelopeRecord:
        return EnvelopeRecord(
            envelope_id=str(raw.get("envelope_id") or ""),
            status=str(raw.get("status") or EnvelopeStatus.ISSUED),
            created_at=str(raw.get("created_at") or ""),
            updated_at=str(raw.get("updated_at") or ""),
            expires_at=str(raw.get("expires_at") or ""),
            issuing_channel=str(raw.get("issuing_channel") or ""),
            settings_hash=str(raw.get("settings_hash") or ""),
            feature_flags_snapshot=dict(raw.get("feature_flags_snapshot") or {}),
            envelope_data=dict(raw.get("envelope_data") or {}),
            used_at=raw.get("used_at"),
            invalidated_reason=raw.get("invalidated_reason"),
            run_metadata=dict(raw.get("run_metadata") or {}),
        )
