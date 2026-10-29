"""Typed Data-Out admission at final HTTP/model transport boundaries.

This module performs no DNS, filesystem probing, client construction, or
network I/O.  Callers must supply the policy and a pre-verified local evidence
sink.  Missing inputs are deliberately fail-closed.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol
from urllib.parse import parse_qsl, urlsplit

from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    DestinationClass,
    DisclosureDecision,
    DisclosureEvidenceSink,
    DisclosurePolicy,
    DisclosurePolicyEvaluator,
    DisclosureRequest,
    InitiationClass,
    ProviderClass,
    TransportClass,
)


@dataclass(frozen=True)
class HttpDisclosureContext:
    """Boundary-owned taxonomy for one prepared HTTP disclosure."""

    caller: str
    purpose: str
    provider: str
    provider_class: ProviderClass
    data_categories: frozenset[DataCategory]
    initiation: InitiationClass = InitiationClass.AUTOMATIC
    action_id: str = ""


@dataclass(frozen=True)
class HttpDisclosureFacts:
    """Value-free facts derived by the final transport boundary."""

    transport: TransportClass
    method: str
    destination: str
    field_names: tuple[str, ...]
    capability_id: int | None


class HttpDisclosureClassifier(Protocol):
    """Trusted composition-owned mapping from transport facts to taxonomy."""

    def __call__(self, facts: HttpDisclosureFacts) -> HttpDisclosureContext | None: ...


def authorize_http_disclosure(
    *,
    evaluator: DisclosurePolicyEvaluator,
    policy: DisclosurePolicy | None,
    evidence_sink: DisclosureEvidenceSink | None,
    context: HttpDisclosureContext | None,
    transport: TransportClass,
    url: str,
    headers: Mapping[str, str] | None,
    field_names: Iterable[str],
    ambient_tls_keylog: bool = False,
    has_body: bool,
    capability_id: int | None,
    request_id: str,
    session_id: str,
) -> DisclosureDecision:
    """Evaluate the exact next-hop request without touching the destination."""

    destination, destination_class = _classify_url_without_io(url)
    credentials = set(_credential_categories(url, headers, field_names))
    if context is None:
        caller = ""
        purpose = ""
        provider = ""
        provider_class = ProviderClass.UNCLASSIFIED
        categories = frozenset()
        initiation = InitiationClass.AUTOMATIC
        action_id = ""
    else:
        caller = context.caller
        purpose = context.purpose
        provider = context.provider
        provider_class = context.provider_class
        categories = context.data_categories
        initiation = context.initiation
        action_id = context.action_id

    if ambient_tls_keylog:
        categories = frozenset({*categories, DataCategory.TLS_SESSION_SECRET})

    # A body with no declared taxonomy is deliberately unclassified.  The
    # evaluator will return UNKNOWN, never an accidental empty-data grant.
    if has_body and not categories:
        categories = frozenset()

    request = DisclosureRequest(
        caller=caller,
        purpose=purpose,
        transport=transport,
        destination_class=destination_class,
        provider_class=provider_class,
        derived_destination=destination,
        policy_version=policy.version if policy is not None else "unavailable",
        data_categories=categories,
        credential_categories=frozenset(credentials),
        initiating_capability_id=capability_id,
        request_id=request_id,
        session_id=session_id,
        action_id=action_id,
        derived_provider=provider,
        effective_route="direct",
        initiation=initiation,
    )
    return evaluator.evaluate_and_record(request, policy, evidence_sink)


def disclosure_facts(
    *,
    transport: TransportClass,
    method: str,
    url: str,
    field_names: Iterable[str],
    capability_id: int | None,
) -> HttpDisclosureFacts:
    """Build classifier input without query values, credentials, or payloads."""

    destination, _destination_class = _classify_url_without_io(url)
    return HttpDisclosureFacts(
        transport=transport,
        method=method.upper(),
        destination=destination,
        field_names=tuple(str(name) for name in field_names),
        capability_id=capability_id,
    )


def _classify_url_without_io(url: str) -> tuple[str, DestinationClass]:
    try:
        parsed = urlsplit(str(url or ""))
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return "", DestinationClass.UNCLASSIFIED
        host = parsed.hostname.lower()
        port = parsed.port
        authority = f"[{host}]" if ":" in host else host
        if port is not None:
            authority = f"{authority}:{port}"
        destination = f"{parsed.scheme.lower()}://{authority}{parsed.path or '/'}"
        if host == "localhost":
            return destination, DestinationClass.LOCAL_LOOPBACK
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return destination, DestinationClass.EXTERNAL_WEB
        if address.is_loopback:
            return destination, DestinationClass.LOCAL_LOOPBACK
        if address.is_private or address.is_link_local:
            return destination, DestinationClass.LOCAL_PRIVATE
        return destination, DestinationClass.EXTERNAL_WEB
    except (TypeError, ValueError):
        return "", DestinationClass.UNCLASSIFIED


def _credential_categories(
    url: str,
    headers: Mapping[str, str] | None,
    field_names: Iterable[str],
) -> frozenset[CredentialCategory]:
    categories: set[CredentialCategory] = set()
    try:
        parsed = urlsplit(str(url or ""))
        if parsed.username is not None or parsed.password is not None:
            categories.add(CredentialCategory.ORIGIN_CREDENTIAL)
        names = [name for name, _value in parse_qsl(parsed.query, keep_blank_values=True)]
    except ValueError:
        names = []
    names.extend(str(name) for name in field_names)
    names.extend(str(name) for name in (headers or {}))
    for name in names:
        lowered = str(name).strip().lower()
        if lowered in {"authorization", "proxy-authorization"}:
            categories.add(
                CredentialCategory.PROXY_CREDENTIAL
                if lowered == "proxy-authorization"
                else CredentialCategory.BEARER_TOKEN
            )
        elif lowered in {"x-api-key", "api-key", "api_key", "apikey"}:
            categories.add(CredentialCategory.API_KEY)
        elif "oauth" in lowered or lowered in {
            "access_token",
            "refresh_token",
            "authorization_code",
            "client_secret",
        }:
            categories.add(CredentialCategory.OAUTH_TOKEN)
    return frozenset(categories)
