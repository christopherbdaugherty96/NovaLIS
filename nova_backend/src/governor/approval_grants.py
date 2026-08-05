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
_AUTHORITY_METADATA_KEYS = frozenset({"approval_id", "confirmed"})


class ApprovalGrantError(ValueError):
    """Raised when an approval grant cannot be issued safely."""


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
                continue
            normalized[key] = _normalize_action_value(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize_action_value(item) for item in value]
    raise ApprovalGrantError(
        f"Unsupported action parameter type: {type(value).__name__}."
    )


def normalized_action_hash(params: Mapping[str, Any]) -> str:
    normalized = _normalize_action_value(dict(params or {}))
    encoded = json.dumps(
        normalized,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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

    def __init__(self, *, clock: Callable[[], float] = time.time) -> None:
        self._clock = clock
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
        if ttl <= 0 or ttl > MAX_APPROVAL_TTL_SECONDS:
            raise ApprovalGrantError(
                f"Approval grant TTL must be between 0 and {MAX_APPROVAL_TTL_SECONDS:g} seconds."
            )

        now = float(self._clock())
        grant = ApprovalGrant(
            approval_id=str(uuid4()),
            session_id=normalized_session,
            capability_id=normalized_capability,
            action_hash=normalized_action_hash(params),
            issued_at=_utc_iso(now),
            expires_at=_utc_iso(now + ttl),
            issued_at_epoch=now,
            expires_at_epoch=now + ttl,
        )
        with self._lock:
            self._grants[grant.approval_id] = grant
        return replace(grant)

    def consume(
        self,
        *,
        approval_id: str,
        session_id: str,
        capability_id: int,
        params: Mapping[str, Any],
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

            now = float(self._clock())
            if now >= grant.expires_at_epoch:
                grant.invalidated_at = _utc_iso(now)
                grant.invalidation_reason = "expired"
                return ApprovalDecision(False, "expired", replace(grant))
            if grant.session_id != str(session_id or "").strip():
                return ApprovalDecision(False, "session_mismatch", replace(grant))
            if grant.capability_id != int(capability_id):
                return ApprovalDecision(False, "capability_mismatch", replace(grant))

            try:
                action_hash = normalized_action_hash(params)
            except ApprovalGrantError:
                grant.invalidated_at = _utc_iso(now)
                grant.invalidation_reason = "invalid_action_parameters"
                return ApprovalDecision(False, "action_mismatch", replace(grant))
            if grant.action_hash != action_hash:
                grant.invalidated_at = _utc_iso(now)
                grant.invalidation_reason = "action_mismatch"
                return ApprovalDecision(False, "action_mismatch", replace(grant))

            grant.consumed_at = _utc_iso(now)
            return ApprovalDecision(True, "consumed", replace(grant))
