"""Typed Data-Out admission at final HTTP/model transport boundaries.

This module performs no DNS, filesystem probing, client construction, or
network I/O.  Callers must supply the policy and a pre-verified local evidence
sink.  Missing inputs are deliberately fail-closed.
"""

from __future__ import annotations

import ipaddress
from collections import Counter
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from http.cookies import CookieError, SimpleCookie
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
    query_fields: tuple[str, ...]
    parameter_fields: tuple[str, ...]
    header_fields: tuple[str, ...]
    cookie_fields: tuple[str, ...]
    json_fields: tuple[str, ...]
    form_fields: tuple[str, ...]
    credential_categories: frozenset[CredentialCategory]
    shape_supported: bool
    capability_id: int | None

    @property
    def request_shape(self) -> frozenset[str]:
        groups = (
            ("query", self.query_fields),
            ("parameter", self.parameter_fields),
            ("header", self.header_fields),
            ("cookie", self.cookie_fields),
            ("json", self.json_fields),
            ("form", self.form_fields),
        )
        return frozenset(
            f"{source}:{name}" for source, names in groups for name in names
        )


class HttpDisclosureClassifier(Protocol):
    """Trusted composition-owned mapping from transport facts to taxonomy."""

    def __call__(self, facts: HttpDisclosureFacts) -> HttpDisclosureContext | None: ...


def authorize_http_disclosure(
    *,
    evaluator: DisclosurePolicyEvaluator,
    policy: DisclosurePolicy | None,
    evidence_sink: DisclosureEvidenceSink | None,
    context: HttpDisclosureContext | None,
    facts: HttpDisclosureFacts,
    ambient_tls_keylog: bool = False,
    has_body: bool,
    capability_id: int | None,
    request_id: str,
    session_id: str,
) -> DisclosureDecision:
    """Evaluate the exact next-hop request without touching the destination."""

    destination, destination_class = _classify_url_without_io(facts.destination)
    credentials = set(facts.credential_categories)
    if context is None or not facts.shape_supported:
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
        transport=facts.transport,
        destination_class=destination_class,
        provider_class=provider_class,
        derived_destination=destination,
        policy_version=policy.version if policy is not None else "unavailable",
        data_categories=categories,
        http_method=facts.method,
        request_shape=facts.request_shape,
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
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, object] | None = None,
    json_payload: object = None,
    form_payload: Mapping[str, object] | None = None,
    capability_id: int | None,
) -> HttpDisclosureFacts:
    """Build complete, source-separated facts without retaining field values."""

    destination, _destination_class = _classify_url_without_io(url)
    supported = bool(destination)
    try:
        parsed = urlsplit(str(url or ""))
        raw_query_fields = [
            name for name, _ in parse_qsl(parsed.query, keep_blank_values=True)
        ]
        query_fields = _names_with_repetition(raw_query_fields)
        query_supported = all(_name_supported(name) for name in raw_query_fields)
    except (TypeError, ValueError):
        query_fields = tuple()
        query_supported = False
        supported = False

    parameter_fields, params_supported = _parameter_names(params)
    header_fields, headers_supported = _header_names(headers)
    cookie_fields, cookies_supported = _cookie_names(headers)
    json_fields, json_supported = _structured_paths(json_payload, source="json")
    form_fields, form_supported = _form_names(form_payload)
    supported = supported and all(
        (
            params_supported,
            query_supported,
            headers_supported,
            cookies_supported,
            json_supported,
            form_supported,
        )
    )
    credentials = _credential_categories(
        url,
        headers,
        (*query_fields, *parameter_fields, *json_fields, *form_fields),
    )
    return HttpDisclosureFacts(
        transport=transport,
        method=method.upper() if isinstance(method, str) else "",
        destination=destination,
        query_fields=query_fields,
        parameter_fields=parameter_fields,
        header_fields=header_fields,
        cookie_fields=cookie_fields,
        json_fields=json_fields,
        form_fields=form_fields,
        credential_categories=credentials,
        shape_supported=supported,
        capability_id=capability_id,
    )


def _safe_names(names: Iterable[object]) -> tuple[str, ...]:
    safe: set[str] = set()
    for name in names:
        if not _name_supported(name):
            continue
        safe.add(name)
    return tuple(sorted(safe))


def _name_supported(name: object) -> bool:
    return isinstance(name, str) and bool(name) and len(name) <= 240


def _names_with_repetition(names: Iterable[object]) -> tuple[str, ...]:
    raw = list(names)
    safe = set(_safe_names(raw))
    counts = Counter(name for name in raw if _name_supported(name))
    safe.update(f"{name}[]" for name, count in counts.items() if count > 1)
    return tuple(sorted(safe))


def _mapping_names(value: object) -> tuple[tuple[str, ...], bool]:
    if value is None:
        return tuple(), True
    if not isinstance(value, MappingABC):
        return tuple(), False
    names = _safe_names(value.keys())
    return names, len(names) == len(value)


def _parameter_names(value: object) -> tuple[tuple[str, ...], bool]:
    names, supported = _mapping_names(value)
    if not supported or value is None:
        return names, supported

    def parameter_value_supported(item: object) -> bool:
        if isinstance(item, (str, int, float, bool)) or item is None:
            return True
        if isinstance(item, (list, tuple)):
            return all(parameter_value_supported(child) for child in item)
        return False

    expanded = set(names)
    for name, item in value.items():
        if isinstance(item, (list, tuple)):
            expanded.add(f"{name}[]")
    return tuple(sorted(expanded)), all(
        parameter_value_supported(item) for item in value.values()
    )


def _form_names(value: object) -> tuple[tuple[str, ...], bool]:
    names, supported = _mapping_names(value)
    if not supported or value is None:
        return names, supported
    return names, all(isinstance(item, str) for item in value.values())


def _header_names(headers: Mapping[str, str] | None) -> tuple[tuple[str, ...], bool]:
    if headers is None:
        return tuple(), True
    if not isinstance(headers, MappingABC):
        return tuple(), False
    if not all(isinstance(name, str) for name in headers):
        return tuple(), False
    names = _safe_names(name.strip().lower() for name in headers)
    return names, len(names) == len(headers) and all(
        isinstance(value, str) for value in headers.values()
    )


def _cookie_names(headers: Mapping[str, str] | None) -> tuple[tuple[str, ...], bool]:
    if not headers:
        return tuple(), True
    if not isinstance(headers, MappingABC) or not all(
        isinstance(name, str) for name in headers
    ):
        return tuple(), False
    cookie_values = [
        value for name, value in headers.items() if name.lower() == "cookie"
    ]
    if not cookie_values:
        return tuple(), True
    names: set[str] = set()
    try:
        for raw in cookie_values:
            if not isinstance(raw, str):
                return tuple(), False
            parsed = SimpleCookie()
            parsed.load(raw)
            if raw and not parsed:
                return tuple(), False
            names.update(parsed.keys())
    except (CookieError, TypeError, ValueError):
        return tuple(), False
    safe = _safe_names(names)
    return safe, len(safe) == len(names)


def _structured_paths(value: object, *, source: str) -> tuple[tuple[str, ...], bool]:
    if value is None:
        return tuple(), True
    paths: set[str] = set()

    def walk(item: object, prefix: str, depth: int) -> bool:
        if depth > 16 or len(paths) > 256:
            return False
        if isinstance(item, MappingABC):
            for key, child in item.items():
                if not isinstance(key, str) or not key or len(key) > 240:
                    return False
                path = f"{prefix}.{key}" if prefix else key
                paths.add(path)
                if not walk(child, path, depth + 1):
                    return False
            return True
        if isinstance(item, (list, tuple)):
            array_path = f"{prefix}[]" if prefix else "$[]"
            paths.add(array_path)
            return all(walk(child, array_path, depth + 1) for child in item)
        if isinstance(item, (str, int, float, bool)) or item is None:
            if not prefix:
                paths.add("$")
            return True
        return False

    supported = walk(value, "", 0)
    safe = _safe_names(paths)
    return safe, supported and len(safe) == len(paths) and source == "json"


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
    except (TypeError, ValueError):
        names = []
    names.extend(name for name in field_names if isinstance(name, str))
    names.extend(name for name in (headers or {}) if isinstance(name, str))
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
        elif lowered == "cookie" or any(
            marker in lowered
            for marker in ("auth", "token", "secret", "credential", "session")
        ):
            categories.add(CredentialCategory.ORIGIN_CREDENTIAL)
    return frozenset(categories)
