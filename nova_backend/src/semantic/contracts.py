"""Provider-neutral semantic contracts for evidence, state, and outcomes.

These objects describe what Nova knows, what is intended, and what an outcome
means. They do not collect data, persist records, call providers, grant
authority, invoke capabilities, or execute actions.

Semantic knowledge is not permission. Evidence is not authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Generic, TypeVar

_SOURCE_COMPONENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

StateT = TypeVar("StateT")


def _require_aware(value: datetime, *, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")
    return value.astimezone(timezone.utc)


class Confidence(str, Enum):
    """Epistemic confidence only; never verification, freshness, or authority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceIdentity:
    """Identity of an information source without credentials or provider clients."""

    provider: str
    service: str
    account_id: str = ""
    resource_id: str = ""

    def __post_init__(self) -> None:
        provider = str(self.provider or "").strip().lower()
        service = str(self.service or "").strip().lower()
        for field_name, value in (("provider", provider), ("service", service)):
            if not _SOURCE_COMPONENT_RE.fullmatch(value):
                raise ValueError(
                    f"{field_name} must be a non-empty lowercase identity component."
                )
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "service", service)
        object.__setattr__(self, "account_id", str(self.account_id or "").strip())
        object.__setattr__(self, "resource_id", str(self.resource_id or "").strip())

    @property
    def canonical(self) -> str:
        return f"{self.provider}:{self.service}"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Freshness:
    """Observation time with caller-supplied, domain-specific age evaluation."""

    observed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.observed_at is not None:
            object.__setattr__(
                self,
                "observed_at",
                _require_aware(self.observed_at, field_name="observed_at"),
            )

    @property
    def is_unknown(self) -> bool:
        return self.observed_at is None

    def age_at(self, as_of: datetime) -> timedelta | None:
        """Return deterministic age at ``as_of``; unknown observations have no age."""
        if self.observed_at is None:
            return None
        reference = _require_aware(as_of, field_name="as_of")
        return reference - self.observed_at

    def evaluate(self, *, as_of: datetime, max_age: timedelta) -> FreshnessStatus:
        """Evaluate freshness without embedding a domain-specific threshold."""
        if max_age < timedelta(0):
            raise ValueError("max_age must not be negative.")
        age = self.age_at(as_of)
        if age is None or age < timedelta(0):
            return FreshnessStatus.UNKNOWN
        return FreshnessStatus.FRESH if age <= max_age else FreshnessStatus.STALE


@dataclass(frozen=True)
class EvidenceEnvelope:
    """Evidence claim/reference plus provenance; never a raw provider payload."""

    source: SourceIdentity
    freshness: Freshness
    confidence: Confidence = Confidence.UNKNOWN
    claim: str = ""
    reference: str = ""

    def __post_init__(self) -> None:
        claim = str(self.claim or "").strip()
        reference = str(self.reference or "").strip()
        if not claim and not reference:
            raise ValueError("EvidenceEnvelope requires a claim or opaque reference.")
        object.__setattr__(self, "claim", claim)
        object.__setattr__(self, "reference", reference)

    @property
    def observed_at(self) -> datetime | None:
        return self.freshness.observed_at


@dataclass(frozen=True)
class ObservedState(Generic[StateT]):
    """Evidence-backed current-state description, including explicit unknown state."""

    known: bool
    value: StateT | None = None
    evidence: tuple[EvidenceEnvelope, ...] = field(default_factory=tuple)
    reason: str = ""

    def __post_init__(self) -> None:
        evidence = tuple(self.evidence)
        if self.known and not evidence:
            raise ValueError("Known observed state requires supporting evidence.")
        if not self.known and self.value is not None:
            raise ValueError("Unknown observed state cannot carry a known value.")
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "reason", str(self.reason or "").strip())

    @classmethod
    def known_state(
        cls,
        value: StateT,
        *,
        evidence: Sequence[EvidenceEnvelope],
    ) -> ObservedState[StateT]:
        return cls(known=True, value=value, evidence=tuple(evidence))

    @classmethod
    def unknown_state(
        cls,
        *,
        reason: str = "",
        evidence: Sequence[EvidenceEnvelope] = (),
    ) -> ObservedState[StateT]:
        return cls(known=False, value=None, evidence=tuple(evidence), reason=reason)


@dataclass(frozen=True)
class IntendedState(Generic[StateT]):
    """Desired or expected state; its existence creates no mandate or authority."""

    target: StateT
    reference: str = ""
    target_at: datetime | None = None
    condition: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference", str(self.reference or "").strip())
        object.__setattr__(self, "condition", str(self.condition or "").strip())
        if self.target_at is not None:
            object.__setattr__(
                self,
                "target_at",
                _require_aware(self.target_at, field_name="target_at"),
            )


class DeltaKind(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class StateDelta(Generic[StateT]):
    """Explicitly classified difference; it performs no detection or prioritization."""

    kind: DeltaKind
    observed: ObservedState[StateT]
    intended: IntendedState[StateT]
    note: str = ""

    def __post_init__(self) -> None:
        if self.kind is DeltaKind.INSUFFICIENT_EVIDENCE and self.observed.known:
            raise ValueError("Insufficient-evidence delta requires an unknown observed state.")
        if self.kind is not DeltaKind.INSUFFICIENT_EVIDENCE and not self.observed.known:
            raise ValueError("Match or mismatch requires a known observed state.")
        object.__setattr__(self, "note", str(self.note or "").strip())


class OutcomeState(str, Enum):
    REJECTED = "rejected"
    FAILED = "failed"
    UNKNOWN_UNVERIFIED = "unknown_unverified"
    ACCEPTED_UNVERIFIED = "accepted_unverified"
    EFFECT_VERIFIED = "effect_verified"
    PARTIAL_FAILURE = "partial_failure"


_OUTCOME_ALIASES = {
    "visible_verified": OutcomeState.EFFECT_VERIFIED,
    "effect_verified": OutcomeState.EFFECT_VERIFIED,
}


@dataclass(frozen=True)
class OutcomeSemantics:
    """Future-facing interpretation of action/receipt outcome metadata.

    This adapter does not replace ``ActionResult`` or Governor lifecycle state.
    It preserves the PR #331 distinction between lifecycle completion, request
    acceptance, and independently verified external effect.
    """

    state: OutcomeState
    request_accepted: bool | None = None
    effect_verified: bool = False
    lifecycle_completed: bool = False
    reason: str = ""
    partial_failure: bool = False

    def __post_init__(self) -> None:
        if self.state is OutcomeState.EFFECT_VERIFIED:
            if not self.effect_verified:
                raise ValueError("effect_verified outcome requires verified effect evidence.")
            if self.request_accepted is False:
                raise ValueError("A rejected request cannot have a verified effect.")
        elif self.state is OutcomeState.ACCEPTED_UNVERIFIED:
            if self.request_accepted is not True or self.effect_verified:
                raise ValueError(
                    "accepted_unverified requires an accepted request and unverified effect."
                )
        elif self.state is OutcomeState.REJECTED:
            if self.request_accepted is not False or self.effect_verified:
                raise ValueError("rejected requires a rejected request and unverified effect.")
        elif self.state in {OutcomeState.FAILED, OutcomeState.UNKNOWN_UNVERIFIED}:
            if self.effect_verified:
                raise ValueError(f"{self.state.value} cannot claim a verified effect.")
        if self.state is OutcomeState.PARTIAL_FAILURE and not self.partial_failure:
            raise ValueError("partial_failure outcome requires partial_failure=True.")
        object.__setattr__(self, "reason", str(self.reason or "").strip())

    @classmethod
    def from_action_metadata(cls, metadata: Mapping[str, Any]) -> OutcomeSemantics:
        """Adapt PR #331-style action or receipt metadata without runtime imports."""
        nested = metadata.get("structured_data")
        structured_data = nested if isinstance(nested, Mapping) else {}

        def metadata_value(*keys: str) -> Any:
            for source in (metadata, structured_data):
                for key in keys:
                    if key in source:
                        return source.get(key)
            return None

        raw_state = str(metadata_value("outcome_state") or "").strip().lower()
        state = _OUTCOME_ALIASES.get(raw_state)
        if state is None:
            try:
                state = OutcomeState(raw_state)
            except ValueError:
                state = OutcomeState.UNKNOWN_UNVERIFIED

        request_accepted = _optional_bool(
            metadata_value("request_accepted", "launch_request_accepted")
        )
        success = _optional_bool(metadata_value("success"))
        effect_verification = _optional_bool(
            metadata_value("effect_verified", "visible_effect_verified")
        )
        effect_verified = effect_verification is True
        partial_failure = bool(metadata_value("partial_failure")) or (
            state is OutcomeState.PARTIAL_FAILURE
        )
        status = str(metadata_value("status") or "").strip().lower()

        positive_state = state in {
            OutcomeState.EFFECT_VERIFIED,
            OutcomeState.ACCEPTED_UNVERIFIED,
        }
        if status in {"rejected", "refused"}:
            state = OutcomeState.REJECTED
            request_accepted = False
            effect_verified = False
        elif positive_state and request_accepted is False:
            state = OutcomeState.REJECTED
            request_accepted = False
            effect_verified = False
        elif positive_state and (status == "failed" or success is False):
            state = OutcomeState.FAILED
            effect_verified = False
        elif state is OutcomeState.EFFECT_VERIFIED:
            verification_is_contradicted = effect_verification is not True
            if verification_is_contradicted:
                effect_verified = False
                if request_accepted is True:
                    state = OutcomeState.ACCEPTED_UNVERIFIED
                else:
                    state = OutcomeState.UNKNOWN_UNVERIFIED
        elif state is OutcomeState.ACCEPTED_UNVERIFIED:
            effect_verified = False
            if request_accepted is not True:
                state = OutcomeState.UNKNOWN_UNVERIFIED
        elif state is OutcomeState.REJECTED:
            request_accepted = False
            effect_verified = False

        lifecycle_completed = status in {"completed", "completed_degraded"}
        reason = str(
            metadata_value("outcome_reason", "failure_reason")
            or ""
        ).strip()
        return cls(
            state=state,
            request_accepted=request_accepted,
            effect_verified=effect_verified,
            lifecycle_completed=lifecycle_completed,
            reason=reason,
            partial_failure=partial_failure,
        )


def _optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None
