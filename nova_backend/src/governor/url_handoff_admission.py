"""Exact, evidence-backed admission for browser and mail-client URL handoffs.

This boundary governs only Nova's delegation of an exact URI to the operating
system.  It does not claim that a website loaded, an email was sent, or the
receiving application remained local after accepting the handoff.
"""
from __future__ import annotations

import hashlib
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable
from urllib.parse import urlsplit

from src.governor.disclosure_policy import (
    DataCategory,
    DestinationClass,
    DisclosureGrant,
    DisclosurePolicy,
    DisclosurePolicyEvaluator,
    DisclosureRequest,
    InitiationClass,
    JsonlDisclosureEvidenceSink,
    ProviderClass,
    TransportClass,
)
from src.llm.local_ollama_bootstrap import _verified_evidence_target

_POLICY_VERSION = "runtime-url-handoff-admission-v1"
_MAX_URI_LENGTH = 16_384
_MAX_CORRELATION_LENGTH = 160


class URLHandoffAdmissionError(RuntimeError):
    """The exact URL handoff did not satisfy its admission contract."""

    def __init__(self, message: str, *, handoff_attempted: bool = False) -> None:
        super().__init__(message)
        self.handoff_attempted = handoff_attempted


class URLHandoffKind(str, Enum):
    WEBPAGE = "webpage"
    MAIL_CLIENT = "mail_client"


@dataclass(frozen=True)
class URLHandoffAdmission:
    uri: str
    uri_fingerprint: str
    kind: URLHandoffKind
    request_id: str
    session_id: str
    capability_id: int
    transport: TransportClass
    purpose: str
    caller: str
    provider: str
    route: str
    data_categories: frozenset[DataCategory]


@dataclass(frozen=True)
class HandoffEvidenceReadyRecord:
    request_id: str
    kind: URLHandoffKind

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "url_handoff_evidence_ready",
            "transport_observed": False,
            "request_id": _fingerprint(self.request_id),
            "handoff_kind": self.kind.value,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }


@dataclass(frozen=True)
class DelegatedURLHandoffOutcomeRecord:
    uri_fingerprint: str
    request_id: str
    kind: URLHandoffKind
    outcome: str
    transport_observed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "delegated_url_handoff_outcome",
            "transport_observed": self.transport_observed,
            "handoff_kind": self.kind.value,
            "uri_fingerprint": self.uri_fingerprint,
            "request_id": _fingerprint(self.request_id),
            "outcome": self.outcome,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _handoff_evidence_sink() -> JsonlDisclosureEvidenceSink:
    return JsonlDisclosureEvidenceSink(_verified_evidence_target())


def _validate_uri(uri: str, kind: URLHandoffKind) -> str:
    if not isinstance(uri, str) or not uri or len(uri) > _MAX_URI_LENGTH:
        raise URLHandoffAdmissionError("A bounded handoff URI is required.")
    if any(ord(character) < 32 or ord(character) == 127 for character in uri):
        raise URLHandoffAdmissionError("The handoff URI contains control characters.")
    try:
        parsed = urlsplit(uri)
    except ValueError as error:
        raise URLHandoffAdmissionError("The handoff URI is malformed.") from error

    if kind is URLHandoffKind.WEBPAGE:
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise URLHandoffAdmissionError("The webpage handoff destination is invalid.")
    elif kind is URLHandoffKind.MAIL_CLIENT:
        # RFC 6068 permits a draft with no prefilled recipient. Nova uses that
        # form when the user supplies subject/body and plans to fill in the
        # recipient in the mail client. A completely empty mailto remains invalid.
        if parsed.scheme.lower() != "mailto" or not (parsed.path or parsed.query):
            raise URLHandoffAdmissionError("The mail-client handoff destination is invalid.")
    else:
        raise URLHandoffAdmissionError("The URL handoff kind is unsupported.")
    return uri


def _build_admission(
    *, uri: str, kind: URLHandoffKind, request_id: str, session_id: str
) -> URLHandoffAdmission:
    if not isinstance(kind, URLHandoffKind):
        raise URLHandoffAdmissionError("The URL handoff kind is unsupported.")
    if not request_id or len(request_id) > _MAX_CORRELATION_LENGTH:
        raise URLHandoffAdmissionError("A bounded request identity is required.")
    if len(session_id) > _MAX_CORRELATION_LENGTH:
        raise URLHandoffAdmissionError("The session identity is unbounded.")
    exact_uri = _validate_uri(uri, kind)

    if kind is URLHandoffKind.WEBPAGE:
        return URLHandoffAdmission(
            uri=exact_uri,
            uri_fingerprint=_fingerprint(exact_uri),
            kind=kind,
            request_id=request_id,
            session_id=session_id,
            capability_id=17,
            transport=TransportClass.BROWSER_HANDOFF,
            purpose="user_approved_webpage_handoff",
            caller="webpage_launch_executor",
            provider="os_default_browser",
            route="exact_uri_browser_handoff",
            data_categories=frozenset(
                {DataCategory.SOURCE_URL, DataCategory.STRUCTURAL_METADATA}
            ),
        )
    return URLHandoffAdmission(
        uri=exact_uri,
        uri_fingerprint=_fingerprint(exact_uri),
        kind=kind,
        request_id=request_id,
        session_id=session_id,
        capability_id=64,
        transport=TransportClass.MAIL_CLIENT_HANDOFF,
        purpose="user_approved_email_draft_handoff",
        caller="send_email_draft_executor",
        provider="os_default_mail_client",
        route="exact_uri_mail_client_handoff",
        data_categories=frozenset(
            {DataCategory.NOTIFICATION_CONTENT, DataCategory.STRUCTURAL_METADATA}
        ),
    )


def _record_admission(admission: URLHandoffAdmission, sink) -> None:
    # Policy matching sees the exact URI while DisclosureEvidenceRecord projects
    # delegated handoffs to their fixed destination class. Raw webpage queries
    # and mail recipient/subject/body values therefore never enter evidence.
    destination = admission.uri
    request = DisclosureRequest(
        caller=admission.caller,
        purpose=admission.purpose,
        transport=admission.transport,
        destination_class=DestinationClass.DELEGATED_APPLICATION,
        provider_class=ProviderClass.DELEGATED_APPLICATION,
        derived_destination=destination,
        declared_destination=destination,
        policy_version=_POLICY_VERSION,
        data_categories=admission.data_categories,
        initiating_capability_id=admission.capability_id,
        request_id=admission.request_id,
        session_id=admission.session_id,
        action_id=admission.uri_fingerprint,
        declared_provider=admission.provider,
        derived_provider=admission.provider,
        effective_route=admission.route,
        initiation=InitiationClass.APPROVED,
    )
    grant = DisclosureGrant(
        provider=admission.provider,
        provider_class=ProviderClass.DELEGATED_APPLICATION,
        destination_class=DestinationClass.DELEGATED_APPLICATION,
        destinations=frozenset({destination}),
        effective_routes=frozenset({admission.route}),
        transports=frozenset({admission.transport}),
        data_categories=admission.data_categories,
        purposes=frozenset({admission.purpose}),
        callers=frozenset({admission.caller}),
        capability_ids=frozenset({admission.capability_id}),
        initiations=frozenset({InitiationClass.APPROVED}),
    )
    decision = DisclosurePolicyEvaluator().evaluate_and_record(
        request,
        DisclosurePolicy(version=_POLICY_VERSION, grants=(grant,)),
        sink,
    )
    if not decision.may_proceed:
        raise URLHandoffAdmissionError(
            f"URL handoff evidence failed ({decision.reason})."
        )


def _delegate_admitted_handoff(
    admission: URLHandoffAdmission,
    *,
    uri: str,
    sink,
    opener: Callable[[str], bool],
) -> bool:
    if uri != admission.uri or _fingerprint(uri) != admission.uri_fingerprint:
        raise URLHandoffAdmissionError("The URL handoff identity changed before delegation.")

    outcome = "handoff_exception"
    observed = False
    try:
        observed = True
        accepted = bool(opener(uri))
        outcome = "handoff_accepted" if accepted else "handoff_rejected"
        return accepted
    except Exception as error:
        raise URLHandoffAdmissionError(
            "The operating-system handoff raised an error.",
            handoff_attempted=True,
        ) from error
    finally:
        try:
            sink.append(
                DelegatedURLHandoffOutcomeRecord(
                    uri_fingerprint=admission.uri_fingerprint,
                    request_id=admission.request_id,
                    kind=admission.kind,
                    outcome=outcome,
                    transport_observed=observed,
                )
            )
        except Exception as error:
            raise URLHandoffAdmissionError(
                "The URL handoff outcome evidence could not be recorded.",
                handoff_attempted=observed,
            ) from error


def open_governed_url_handoff(
    *,
    uri: str,
    kind: URLHandoffKind,
    request_id: str,
    session_id: str = "",
    opener: Callable[[str], bool] | None = None,
) -> bool:
    """Admit and delegate one exact URL without claiming the child outcome."""
    try:
        sink = _handoff_evidence_sink()
        sink.append(HandoffEvidenceReadyRecord(request_id=request_id, kind=kind))
        handoff = _build_admission(
            uri=uri,
            kind=kind,
            request_id=request_id,
            session_id=session_id,
        )
        _record_admission(handoff, sink)
    except URLHandoffAdmissionError:
        raise
    except Exception as error:
        raise URLHandoffAdmissionError("URL handoff evidence is unavailable.") from error

    return _delegate_admitted_handoff(
        handoff,
        uri=uri,
        sink=sink,
        opener=opener or webbrowser.open,
    )
