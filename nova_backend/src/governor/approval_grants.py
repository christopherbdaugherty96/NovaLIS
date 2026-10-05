from __future__ import annotations

import hashlib
import json
import math
import threading
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from uuid import uuid4

DEFAULT_APPROVAL_TTL_SECONDS = 120.0
MAX_APPROVAL_TTL_SECONDS = 600.0
DEFAULT_MAX_APPROVAL_RECORDS = 4096
_AUTHORITY_METADATA_KEYS = frozenset({"approval_id", "confirmed"})


class ApprovalGrantError(ValueError):
    """Raised when an approval grant cannot be issued safely."""


class ApprovalAuthorityMetadataError(ApprovalGrantError):
    """Raised when action parameters contain reserved authority metadata."""

    def __init__(self, key: str) -> None:
        self.key = str(key)
        super().__init__(f"Reserved authority metadata is not an action parameter: {self.key}.")


def _normalize_action_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ApprovalGrantError("Action parameters must contain finite numbers.")
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ApprovalGrantError("Action parameter keys must be strings.")
            if key in _AUTHORITY_METADATA_KEYS:
                raise ApprovalAuthorityMetadataError(key)
            normalized[key] = _normalize_action_value(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize_action_value(item) for item in value]
    raise ApprovalGrantError(
        f"Unsupported action parameter type: {type(value).__name__}."
    )


def canonical_action_snapshot(params: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and deeply isolate JSON-like action parameters exactly once."""
    normalized = _normalize_action_value(dict(params or {}))
    if not isinstance(normalized, dict):  # Defensive; the public contract is a mapping.
        raise ApprovalGrantError("Action parameters must be a mapping.")
    return normalized


def _canonical_action_hash(snapshot: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        snapshot,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalized_action_hash(params: Mapping[str, Any]) -> str:
    return _canonical_action_hash(canonical_action_snapshot(params))


@dataclass
class ApprovalGrant:
    approval_id: str
    session_id: str
    capability_id: int
    action_hash: str
    issued_at: str
    expires_at: str
    issued_at_epoch: float
    expires_at_epoch: float
    expires_at_monotonic: float
    consumed_at: str | None = None
    invalidated_at: str | None = None
    invalidation_reason: str | None = None

    @property
    def consumed(self) -> bool:
        return self.consumed_at is not None


@dataclass(frozen=True)
class ApprovalDecision:
    allowed: bool
    reason: str
    grant: ApprovalGrant | None = None


def _utc_iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()


class ApprovalGrantStore:
    """Governor-owned, in-memory authority records for exact approved actions."""

    def __init__(
        self,
        *,
        wall_clock: Callable[[], float] = time.time,
        monotonic_clock: Callable[[], float] = time.monotonic,
        max_records: int = DEFAULT_MAX_APPROVAL_RECORDS,
    ) -> None:
        self._wall_clock = wall_clock
        self._monotonic_clock = monotonic_clock
        self._max_records = max(1, int(max_records))
        self._grants: dict[str, ApprovalGrant] = {}
        self._lock = threading.RLock()

    def issue(
        self,
        *,
        session_id: str,
        capability_id: int,
        params: Mapping[str, Any],
        ttl_seconds: float = DEFAULT_APPROVAL_TTL_SECONDS,
    ) -> ApprovalGrant:
        normalized_session = str(session_id or "").strip()
        if not normalized_session:
            raise ApprovalGrantError("Approval grants require a session ID.")
        normalized_capability = int(capability_id)
        if normalized_capability <= 0:
            raise ApprovalGrantError("Approval grants require a capability ID.")
        ttl = float(ttl_seconds)
        if not math.isfinite(ttl) or ttl <= 0 or ttl > MAX_APPROVAL_TTL_SECONDS:
            raise ApprovalGrantError(
                f"Approval grant TTL must be between 0 and {MAX_APPROVAL_TTL_SECONDS:g} seconds."
            )

        snapshot = canonical_action_snapshot(params)
        wall_now = float(self._wall_clock())
        monotonic_now = float(self._monotonic_clock())
        grant = ApprovalGrant(
            approval_id=str(uuid4()),
            session_id=normalized_session,
            capability_id=normalized_capability,
            action_hash=_canonical_action_hash(snapshot),
            issued_at=_utc_iso(wall_now),
            expires_at=_utc_iso(wall_now + ttl),
            issued_at_epoch=wall_now,
            expires_at_epoch=wall_now + ttl,
            expires_at_monotonic=monotonic_now + ttl,
        )
        with self._lock:
            while len(self._grants) >= self._max_records:
                self._grants.pop(next(iter(self._grants)))
            self._grants[grant.approval_id] = grant
        return replace(grant)

    def consume(
        self,
        *,
        approval_id: str,
        session_id: str,
        capability_id: int,
        params_snapshot: Mapping[str, Any],
    ) -> ApprovalDecision:
        normalized_id = str(approval_id or "").strip()
        if not normalized_id:
            return ApprovalDecision(False, "missing")

        with self._lock:
            grant = self._grants.get(normalized_id)
            if grant is None:
                return ApprovalDecision(False, "unknown")
            if grant.consumed:
                return ApprovalDecision(False, "replayed", replace(grant))
            if grant.invalidated_at is not None:
                return ApprovalDecision(False, "invalidated", replace(grant))

            monotonic_now = float(self._monotonic_clock())
            wall_now = float(self._wall_clock())
            if monotonic_now >= grant.expires_at_monotonic:
                grant.invalidated_at = _utc_iso(wall_now)
                grant.invalidation_reason = "expired"
                return ApprovalDecision(False, "expired", replace(grant))
            if grant.session_id != str(session_id or "").strip():
                return ApprovalDecision(False, "session_mismatch", replace(grant))
            if grant.capability_id != int(capability_id):
                return ApprovalDecision(False, "capability_mismatch", replace(grant))

            try:
                action_hash = _canonical_action_hash(params_snapshot)
            except ApprovalGrantError:
                grant.invalidated_at = _utc_iso(wall_now)
                grant.invalidation_reason = "invalid_action_parameters"
                return ApprovalDecision(False, "action_mismatch", replace(grant))
            if grant.action_hash != action_hash:
                grant.invalidated_at = _utc_iso(wall_now)
                grant.invalidation_reason = "action_mismatch"
                return ApprovalDecision(False, "action_mismatch", replace(grant))

            grant.consumed_at = _utc_iso(wall_now)
            return ApprovalDecision(True, "consumed", replace(grant))

    def revoke_unissued(self, approval_id: str) -> None:
        """Remove authority that could not be durably recorded before issuance."""
        normalized_id = str(approval_id or "").strip()
        if not normalized_id:
            return
        with self._lock:
            self._grants.pop(normalized_id, None)
