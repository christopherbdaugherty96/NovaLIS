"""Pure provider-neutral Data-Out policy and secret-free decision evidence.

Slice 1 defines vocabulary only. It is intentionally not wired into network,
filesystem, process, browser, or model transports; those are later slices.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit

from src.utils.persistent_state import shared_path_lock


class DisclosureDecisionValue(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    UNKNOWN = "unknown"


class TransportClass(str, Enum):
    HTTP = "http"
    OAUTH_SETUP = "oauth_setup"
    BROWSER_HANDOFF = "browser_handoff"
    MAIL_CLIENT_HANDOFF = "mail_client_handoff"
    PROCESS_HANDOFF = "process_handoff"
    APPLICATION_HANDOFF = "application_handoff"
    NETWORK_FILESYSTEM = "network_filesystem"
    LOCAL_PRIVATE_MODEL = "local_private_model"
    LOCAL_OS_HANDOFF = "local_os_handoff"


class DestinationClass(str, Enum):
    EXTERNAL_PROVIDER = "external_provider"
    EXTERNAL_WEB = "external_web"
    EXTERNAL_STORAGE = "external_storage"
    LOCAL_LOOPBACK = "local_loopback"
    LOCAL_PRIVATE = "local_private"
    LOCAL_OS = "local_os"
    DELEGATED_APPLICATION = "delegated_application"
    UNCLASSIFIED = "unclassified"


class ProviderClass(str, Enum):
    HOSTED_MODEL = "hosted_model"
    SEARCH = "search"
    NEWS_SOURCE = "news_source"
    WEATHER = "weather"
    COMMERCE = "commerce"
    OAUTH = "oauth"
    LOCAL_MODEL = "local_model"
    LOCAL_OS = "local_os"
    DELEGATED_APPLICATION = "delegated_application"
    REMOTE_STORAGE = "remote_storage"
    UNCLASSIFIED = "unclassified"


class DataCategory(str, Enum):
    PROMPT = "prompt"
    CONVERSATION_CONTEXT = "conversation_context"
    DOCUMENT_TEXT = "document_text"
    SEARCH_QUERY = "search_query"
    LOCATION = "location"
    SOURCE_URL = "source_url"
    TASK_REPORT = "task_report"
    SHOP_DATA = "shop_data"
    OAUTH_MATERIAL = "oauth_material"
    FILE_CONTENT = "file_content"
    RUNTIME_STATE = "runtime_state"
    NOTIFICATION_CONTENT = "notification_content"
    STRUCTURAL_METADATA = "structural_metadata"
    TLS_SESSION_SECRET = "tls_session_secret"


class CredentialCategory(str, Enum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH_TOKEN = "oauth_token"
    ORIGIN_CREDENTIAL = "origin_credential"
    PROXY_CREDENTIAL = "proxy_credential"
    NETWORK_SHARE_CREDENTIAL = "network_share_credential"
    AMBIENT_NETRC = "ambient_netrc"


class InitiationClass(str, Enum):
    USER_INITIATED = "user_initiated"
    APPROVED = "approved"
    AUTOMATIC = "automatic"


class RequestShapeSource(str, Enum):
    QUERY = "query"
    PARAMETER = "parameter"
    HEADER = "header"
    COOKIE = "cookie"
    JSON = "json"
    FORM = "form"


class RequestShapeStepKind(str, Enum):
    FIELD = "field"
    ARRAY_ELEMENT = "array_element"


class RequestShapeValueKind(str, Enum):
    SCALAR = "scalar"
    OBJECT = "object"
    ARRAY = "array"


@dataclass(frozen=True)
class RequestShapeStep:
    kind: RequestShapeStepKind
    name: str = ""


@dataclass(frozen=True)
class RequestShapeField:
    source: RequestShapeSource
    path: tuple[RequestShapeStep, ...]
    value_kind: RequestShapeValueKind
    repeated: bool = False


@dataclass(frozen=True)
class DisclosureRequest:
    caller: str
    purpose: str
    transport: TransportClass
    destination_class: DestinationClass
    provider_class: ProviderClass
    derived_destination: str
    policy_version: str
    data_categories: frozenset[DataCategory]
    http_method: str = ""
    request_shape: frozenset[RequestShapeField] = frozenset()
    credential_categories: frozenset[CredentialCategory] = frozenset()
    initiating_capability_id: int | None = None
    request_id: str = ""
    session_id: str = ""
    action_id: str = ""
    declared_provider: str = ""
    derived_provider: str = ""
    declared_destination: str = ""
    effective_route: str = ""
    initiation: InitiationClass = InitiationClass.AUTOMATIC


@dataclass(frozen=True)
class DisclosureGrant:
    provider: str
    provider_class: ProviderClass
    destination_class: DestinationClass
    destinations: frozenset[str]
    effective_routes: frozenset[str]
    transports: frozenset[TransportClass]
    data_categories: frozenset[DataCategory]
    http_methods: frozenset[str] = frozenset()
    request_shapes: frozenset[frozenset[RequestShapeField]] = frozenset()
    credential_categories: frozenset[CredentialCategory] = frozenset()
    purposes: frozenset[str] = frozenset()
    callers: frozenset[str] = frozenset()
    capability_ids: frozenset[int] = frozenset()
    initiations: frozenset[InitiationClass] = frozenset()


@dataclass(frozen=True)
class DisclosurePolicy:
    version: str
    grants: tuple[DisclosureGrant, ...] = tuple()


@dataclass(frozen=True)
class DisclosureDecision:
    value: DisclosureDecisionValue
    reason: str
    policy_version: str
    request_id: str = ""
    session_id: str = ""
    action_id: str = ""
    evidence_recorded: bool = False

    @property
    def may_proceed(self) -> bool:
        return self.value is DisclosureDecisionValue.ALLOW and self.evidence_recorded


@dataclass(frozen=True)
class DisclosureEvidenceRecord:
    record_kind: str
    transport_observed: bool
    decision: str
    reason: str
    policy_version: str
    caller: str
    purpose: str
    transport: str
    http_method: str
    request_shape_fingerprint: str
    provider: str
    provider_class: str
    destination: str
    destination_class: str
    data_categories: tuple[str, ...]
    credential_categories: tuple[str, ...]
    initiation: str
    initiating_capability_id: int | None
    request_id: str
    session_id: str
    action_id: str
    recorded_at_utc: str

    @classmethod
    def from_decision(
        cls,
        request: DisclosureRequest,
        decision: DisclosureDecision,
    ) -> "DisclosureEvidenceRecord":
        trusted_taxonomy = decision.value is DisclosureDecisionValue.ALLOW
        return cls(
            record_kind="disclosure_policy_evaluation",
            transport_observed=False,
            decision=decision.value.value,
            reason=_safe_label(decision.reason, fallback="unclassified_reason"),
            policy_version=_fingerprint(decision.policy_version) or "unavailable",
            caller=_evidence_taxonomy(
                request.caller,
                fallback="unclassified_caller",
                trusted=trusted_taxonomy,
            ),
            purpose=_evidence_taxonomy(
                request.purpose,
                fallback="unclassified_purpose",
                trusted=trusted_taxonomy,
            ),
            transport=_enum_value(
                request.transport,
                TransportClass,
                fallback="unclassified_transport",
            ),
            http_method=_safe_http_method(request.http_method),
            request_shape_fingerprint=_request_shape_fingerprint(request.request_shape),
            provider=_evidence_taxonomy(
                request.derived_provider,
                fallback="unclassified_provider",
                trusted=trusted_taxonomy,
            ),
            provider_class=_enum_value(
                request.provider_class,
                ProviderClass,
                fallback="unclassified_provider",
            ),
            destination=_safe_destination(request),
            destination_class=_enum_value(
                request.destination_class,
                DestinationClass,
                fallback="unclassified_destination",
            ),
            data_categories=_safe_enum_values(
                request.data_categories,
                DataCategory,
                fallback="unclassified_data",
            ),
            credential_categories=tuple(
                _safe_enum_values(
                    request.credential_categories,
                    CredentialCategory,
                    fallback="unclassified_credential",
                )
            ),
            initiation=_enum_value(
                request.initiation,
                InitiationClass,
                fallback="unclassified_initiation",
            ),
            initiating_capability_id=_safe_capability_id(request.initiating_capability_id),
            request_id=_fingerprint(request.request_id),
            session_id=_fingerprint(request.session_id),
            action_id=_fingerprint(request.action_id),
            recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": self.record_kind,
            "transport_observed": self.transport_observed,
            "decision": self.decision,
            "reason": self.reason,
            "policy_version": self.policy_version,
            "caller": self.caller,
            "purpose": self.purpose,
            "transport": self.transport,
            "http_method": self.http_method,
            "request_shape_fingerprint": self.request_shape_fingerprint,
            "provider": self.provider,
            "provider_class": self.provider_class,
            "destination": self.destination,
            "destination_class": self.destination_class,
            "data_categories": list(self.data_categories),
            "credential_categories": list(self.credential_categories),
            "initiation": self.initiation,
            "initiating_capability_id": self.initiating_capability_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "action_id": self.action_id,
            "recorded_at_utc": self.recorded_at_utc,
        }


class DisclosureEvidenceSink(Protocol):
    def append(self, record: DisclosureEvidenceRecord) -> None: ...


@dataclass(frozen=True)
class VerifiedLocalEvidenceTarget:
    """A bootstrap-supplied target already proven local outside this slice.

    Slice 1 cannot establish filesystem locality without probing. Construction is
    therefore explicit and rejects an unverified target; Slice 5 owns locality.
    """

    path: Path
    locality_verified: bool = field(repr=False)

    def __post_init__(self) -> None:
        if not self.locality_verified:
            raise ValueError("Disclosure evidence target must be pre-verified local.")


class JsonlDisclosureEvidenceSink:
    """Append secret-free decision evidence to an explicit verified-local target."""

    def __init__(self, target: VerifiedLocalEvidenceTarget) -> None:
        self._target = target
        self._lock = shared_path_lock(target.path)

    def append(self, record: DisclosureEvidenceRecord) -> None:
        payload = json.dumps(record.as_dict(), sort_keys=True, separators=(",", ":"))
        with self._lock:
            self._target.path.parent.mkdir(parents=True, exist_ok=True)
            with self._target.path.open("a", encoding="utf-8") as handle:
                handle.write(payload + "\n")
                handle.flush()
                os.fsync(handle.fileno())


class DisclosurePolicyEvaluator:
    """Deterministic evaluator with no transport, DNS, or path-classification I/O."""

    def evaluate(
        self,
        request: DisclosureRequest,
        policy: DisclosurePolicy | None,
    ) -> DisclosureDecision:
        base = {
            "policy_version": request.policy_version or "unavailable",
            "request_id": request.request_id,
            "session_id": request.session_id,
            "action_id": request.action_id,
        }
        if policy is None:
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "policy_unavailable",
                **base,
            )
        if not _request_vocabulary_valid(request):
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "request_vocabulary_unclassified",
                **base,
            )
        if not _policy_vocabulary_valid(policy):
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "policy_vocabulary_invalid",
                policy_version=policy.version or "unavailable",
                request_id=request.request_id,
                session_id=request.session_id,
                action_id=request.action_id,
            )
        if not request.policy_version or request.policy_version != policy.version:
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "policy_version_mismatch",
                policy_version=policy.version or "unavailable",
                request_id=request.request_id,
                session_id=request.session_id,
                action_id=request.action_id,
            )
        if not all(
            (
                request.caller,
                request.purpose,
                request.derived_destination,
                request.derived_provider,
                request.effective_route,
            )
        ):
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "request_unclassified",
                **base,
            )
        if request.destination_class is DestinationClass.UNCLASSIFIED:
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "destination_unclassified",
                **base,
            )
        if request.provider_class is ProviderClass.UNCLASSIFIED:
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "provider_unclassified",
                **base,
            )
        if not request.data_categories:
            return DisclosureDecision(
                DisclosureDecisionValue.UNKNOWN,
                "data_categories_unclassified",
                **base,
            )
        if request.declared_provider and (
            _normalized_identity(request.declared_provider)
            != _normalized_identity(request.derived_provider)
        ):
            return DisclosureDecision(
                DisclosureDecisionValue.DENY,
                "provider_identity_mismatch",
                **base,
            )
        if request.declared_destination and (
            _normalized_destination(request.declared_destination, request.transport)
            != _normalized_destination(request.derived_destination, request.transport)
        ):
            return DisclosureDecision(
                DisclosureDecisionValue.DENY,
                "destination_identity_mismatch",
                **base,
            )

        for grant in policy.grants:
            if _grant_matches(request, grant):
                return DisclosureDecision(
                    DisclosureDecisionValue.ALLOW,
                    "explicit_policy_grant",
                    **base,
                )
        return DisclosureDecision(
            DisclosureDecisionValue.DENY,
            "no_matching_policy_grant",
            **base,
        )

    def evaluate_and_record(
        self,
        request: DisclosureRequest,
        policy: DisclosurePolicy | None,
        evidence_sink: DisclosureEvidenceSink | None,
    ) -> DisclosureDecision:
        decision = self.evaluate(request, policy)
        if evidence_sink is None:
            return replace(
                decision,
                value=DisclosureDecisionValue.UNKNOWN,
                reason="evidence_unavailable",
            )
        try:
            evidence_sink.append(DisclosureEvidenceRecord.from_decision(request, decision))
        except Exception:
            return replace(
                decision,
                value=DisclosureDecisionValue.UNKNOWN,
                reason="evidence_write_failed",
            )
        return replace(decision, evidence_recorded=True)


def _grant_matches(request: DisclosureRequest, grant: DisclosureGrant) -> bool:
    if _normalized_identity(grant.provider) != _normalized_identity(request.derived_provider):
        return False
    if grant.provider_class is not request.provider_class:
        return False
    if grant.destination_class is not request.destination_class:
        return False
    if _normalized_destination(request.derived_destination, request.transport) not in {
        _normalized_destination(item, request.transport) for item in grant.destinations
    }:
        return False
    if request.effective_route not in grant.effective_routes:
        return False
    if request.transport not in grant.transports:
        return False
    if request.transport in _HTTP_OPERATION_TRANSPORTS:
        if request.http_method not in grant.http_methods:
            return False
        if request.request_shape not in grant.request_shapes:
            return False
    if not request.data_categories.issubset(grant.data_categories):
        return False
    if not request.credential_categories.issubset(grant.credential_categories):
        return False
    if request.purpose not in grant.purposes:
        return False
    if request.caller not in grant.callers:
        return False
    if request.initiating_capability_id not in grant.capability_ids:
        return False
    if request.initiation not in grant.initiations:
        return False
    return True


def _request_vocabulary_valid(request: DisclosureRequest) -> bool:
    base_valid = (
        isinstance(request.caller, str)
        and isinstance(request.purpose, str)
        and isinstance(request.derived_destination, str)
        and isinstance(request.declared_destination, str)
        and isinstance(request.derived_provider, str)
        and isinstance(request.declared_provider, str)
        and isinstance(request.effective_route, str)
        and isinstance(request.policy_version, str)
        and isinstance(request.transport, TransportClass)
        and isinstance(request.destination_class, DestinationClass)
        and isinstance(request.provider_class, ProviderClass)
        and isinstance(request.initiation, InitiationClass)
        and isinstance(request.data_categories, frozenset)
        and all(isinstance(item, DataCategory) for item in request.data_categories)
        and isinstance(request.credential_categories, frozenset)
        and all(isinstance(item, CredentialCategory) for item in request.credential_categories)
        and _safe_capability_id(request.initiating_capability_id)
        == request.initiating_capability_id
        and bool(_normalized_destination(request.derived_destination, request.transport))
        and (
            not request.declared_destination
            or bool(_normalized_destination(request.declared_destination, request.transport))
        )
    )
    if not base_valid:
        return False
    if request.transport in _HTTP_OPERATION_TRANSPORTS:
        return (
            _safe_http_method(request.http_method) == request.http_method
            and _request_shape_valid(request.request_shape)
        )
    return request.http_method == "" and request.request_shape == frozenset()


def _policy_vocabulary_valid(policy: DisclosurePolicy) -> bool:
    if not isinstance(policy.version, str) or not policy.version.strip():
        return False
    if not isinstance(policy.grants, tuple):
        return False
    for grant in policy.grants:
        if not isinstance(grant, DisclosureGrant):
            return False
        if not isinstance(grant.destination_class, DestinationClass):
            return False
        if not isinstance(grant.provider_class, ProviderClass):
            return False
        if not isinstance(grant.provider, str) or not grant.provider.strip():
            return False
        if not grant.destinations or not isinstance(grant.destinations, frozenset):
            return False
        if (
            not grant.transports
            or not isinstance(grant.transports, frozenset)
            or not all(isinstance(item, TransportClass) for item in grant.transports)
        ):
            return False
        if any(item in _HTTP_OPERATION_TRANSPORTS for item in grant.transports):
            if (
                not isinstance(grant.http_methods, frozenset)
                or not grant.http_methods
                or not all(_safe_http_method(item) == item for item in grant.http_methods)
                or not isinstance(grant.request_shapes, frozenset)
                or not grant.request_shapes
                or not all(_request_shape_valid(item) for item in grant.request_shapes)
            ):
                return False
        elif grant.http_methods or grant.request_shapes:
            return False
        if not all(
            isinstance(destination, str)
            and all(
                bool(_normalized_destination(destination, transport))
                for transport in grant.transports
            )
            for destination in grant.destinations
        ):
            return False
        if (
            not grant.effective_routes
            or not isinstance(grant.effective_routes, frozenset)
            or not all(
                isinstance(item, str) and bool(item.strip()) for item in grant.effective_routes
            )
        ):
            return False
        if (
            not grant.data_categories
            or not isinstance(grant.data_categories, frozenset)
            or not all(isinstance(item, DataCategory) for item in grant.data_categories)
        ):
            return False
        if not isinstance(grant.credential_categories, frozenset) or not all(
            isinstance(item, CredentialCategory) for item in grant.credential_categories
        ):
            return False
        if (
            not grant.purposes
            or not isinstance(grant.purposes, frozenset)
            or not all(isinstance(item, str) and bool(item.strip()) for item in grant.purposes)
        ):
            return False
        if (
            not grant.callers
            or not isinstance(grant.callers, frozenset)
            or not all(isinstance(item, str) and bool(item.strip()) for item in grant.callers)
        ):
            return False
        if (
            not grant.capability_ids
            or not isinstance(grant.capability_ids, frozenset)
            or not all(_safe_capability_id(item) == item for item in grant.capability_ids)
        ):
            return False
        if (
            not grant.initiations
            or not isinstance(grant.initiations, frozenset)
            or not all(isinstance(item, InitiationClass) for item in grant.initiations)
        ):
            return False
    return True


def _normalized_identity(value: str) -> str:
    return str(value or "").strip().lower()


_URL_TRANSPORTS = {
    TransportClass.HTTP,
    TransportClass.OAUTH_SETUP,
    TransportClass.LOCAL_PRIVATE_MODEL,
    TransportClass.BROWSER_HANDOFF,
}

_HTTP_OPERATION_TRANSPORTS = {
    TransportClass.HTTP,
    TransportClass.OAUTH_SETUP,
    TransportClass.LOCAL_PRIVATE_MODEL,
}

_HTTP_METHOD_RE = re.compile(r"^[A-Z]{3,16}$")
def _safe_http_method(value: object) -> str:
    if not isinstance(value, str):
        return "unclassified_method"
    method = value.strip().upper()
    return method if _HTTP_METHOD_RE.fullmatch(method) else "unclassified_method"


def _request_shape_valid(value: object) -> bool:
    if not isinstance(value, frozenset):
        return False
    for item in value:
        if not isinstance(item, RequestShapeField):
            return False
        if not isinstance(item.source, RequestShapeSource):
            return False
        if not isinstance(item.value_kind, RequestShapeValueKind):
            return False
        if not isinstance(item.path, tuple) or not all(
            isinstance(step, RequestShapeStep)
            and isinstance(step.kind, RequestShapeStepKind)
            and isinstance(step.name, str)
            and (
                (
                    step.kind is RequestShapeStepKind.FIELD
                    and bool(step.name)
                    and len(step.name) <= 240
                )
                or (
                    step.kind is RequestShapeStepKind.ARRAY_ELEMENT
                    and step.name == ""
                )
            )
            for step in item.path
        ):
            return False
        if item.source is not RequestShapeSource.JSON and (
            len(item.path) != 1
            or item.path[0].kind is not RequestShapeStepKind.FIELD
            or item.value_kind is not RequestShapeValueKind.SCALAR
        ):
            return False
        if item.repeated and item.source not in {
            RequestShapeSource.QUERY,
            RequestShapeSource.PARAMETER,
        }:
            return False
    return True


def _request_shape_fingerprint(value: object) -> str:
    if not _request_shape_valid(value):
        return "unclassified_shape"
    canonical = [
        {
            "source": item.source.value,
            "path": [
                {"kind": step.kind.value, "name": step.name} for step in item.path
            ],
            "value_kind": item.value_kind.value,
            "repeated": item.repeated,
        }
        for item in value
    ]
    canonical.sort(
        key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"))
    )
    serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return _fingerprint(serialized) or "empty_shape"


def _normalized_destination(value: str, transport: TransportClass) -> str:
    raw = str(value or "")
    try:
        if transport in _URL_TRANSPORTS:
            parsed = urlsplit(raw.strip())
            if (
                parsed.scheme.lower() not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
            ):
                return ""
            return (
                f"{parsed.scheme.lower()}://{_url_authority(parsed.hostname, parsed.port)}"
                f"{parsed.path or '/'}"
            )
    except ValueError:
        return ""
    # Non-URL identities may be case- and whitespace-sensitive (for example
    # POSIX paths and process arguments). Preserve every character unless a
    # transport-specific canonicalizer has established a safe normalization.
    return raw if raw and not raw.isspace() and "://" not in raw else ""


def _safe_destination(request: DisclosureRequest) -> str:
    if request.transport in {
        TransportClass.HTTP,
        TransportClass.OAUTH_SETUP,
        TransportClass.LOCAL_PRIVATE_MODEL,
    }:
        try:
            parsed = urlsplit(request.derived_destination)
            if parsed.scheme and parsed.hostname:
                return f"{parsed.scheme.lower()}://{_url_authority(parsed.hostname, parsed.port)}"
        except ValueError:
            pass
    return _enum_value(
        request.destination_class,
        DestinationClass,
        fallback="unclassified_destination",
    )


def _url_authority(hostname: str, port: int | None) -> str:
    host = hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    return f"{host}:{port}" if port is not None else host


def _safe_capability_id(value: object) -> int | None:
    if type(value) is int and value >= 0:
        return value
    return None


def _enum_value(value: object, expected_type: type[Enum], *, fallback: str) -> str:
    if not isinstance(value, expected_type):
        return fallback
    raw = value.value
    return str(raw) if isinstance(raw, str) and raw else fallback


def _safe_enum_values(
    values: object,
    expected_type: type[Enum],
    *,
    fallback: str,
) -> tuple[str, ...]:
    if not isinstance(values, frozenset):
        return (fallback,)
    safe = sorted(
        str(item.value)
        for item in values
        if isinstance(item, expected_type) and isinstance(item.value, str)
    )
    return tuple(safe) if len(safe) == len(values) else (fallback,)


_SAFE_LABEL = re.compile(r"[^a-zA-Z0-9_.:/-]+")


def _safe_label(value: str, *, fallback: str) -> str:
    clean = _SAFE_LABEL.sub("_", str(value or "").strip())[:120].strip("_")
    return clean or fallback


def _evidence_taxonomy(value: str, *, fallback: str, trusted: bool) -> str:
    if not str(value or "").strip():
        return fallback
    if not trusted:
        return _fingerprint(value)
    return _safe_label(value, fallback=fallback)


def _fingerprint(value: str) -> str:
    clean = str(value or "").strip()
    if not clean:
        return ""
    return f"sha256:{hashlib.sha256(clean.encode('utf-8')).hexdigest()[:16]}"
