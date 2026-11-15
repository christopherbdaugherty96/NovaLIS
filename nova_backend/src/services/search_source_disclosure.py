"""Caller-scoped admission for Cap 16 reads of current search-result pages."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from src.governor.disclosure_policy import (
    DataCategory,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import HttpDisclosureContext, disclosure_facts

_SEARCH_PROVIDERS = frozenset({"brave", "duckduckgo"})
_DNS_LABEL_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")


@dataclass(frozen=True)
class SearchSourceAdmission:
    """Exact, request-scoped provenance for one current search result."""

    url: str
    destination: str
    hostname: str
    query_fields: tuple[str, ...]
    search_provider: str
    capability_id: int
    request_id: str
    session_id: str
    initiation: InitiationClass


def _canonical_external_https_url(value: str) -> tuple[str, str]:
    url = str(value or "").strip()
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise ValueError("Search-result URL is invalid.") from error
    hostname = str(parsed.hostname or "").strip().lower().rstrip(".")
    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or parsed.fragment
        or parsed.netloc != hostname
    ):
        raise ValueError("Search-result URL is not a canonical external HTTPS URL.")
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Search-result URL must be external.")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            hostname.encode("ascii")
        except UnicodeEncodeError as error:
            raise ValueError("Search-result hostname must use its ASCII form.") from error
        labels = hostname.split(".")
        if len(labels) < 2 or any(not _DNS_LABEL_RE.fullmatch(label) for label in labels):
            raise ValueError("Search-result hostname is not canonical.")
    else:
        if not address.is_global:
            raise ValueError("Search-result URL must be external.")
    return url, hostname


def build_search_source_admission(
    *,
    url: str,
    search_provider: str,
    capability_id: int,
    request_id: str | None,
    session_id: str | None,
    initiation: InitiationClass,
) -> SearchSourceAdmission:
    """Create provenance only for a Cap 16 result from a supported search call."""

    canonical_url, hostname = _canonical_external_https_url(url)
    normalized_provider = str(search_provider or "").strip().lower()
    normalized_request_id = str(request_id or "").strip()
    normalized_session_id = str(session_id or "").strip()
    if normalized_provider not in _SEARCH_PROVIDERS:
        raise ValueError("Search-result provider is unsupported.")
    if int(capability_id) != 16:
        raise ValueError("Search-result page reads are limited to capability 16.")
    if not normalized_request_id:
        raise ValueError("Search-result provenance requires a request identifier.")
    if not isinstance(initiation, InitiationClass):
        raise ValueError("Search-result provenance requires governed initiation.")
    facts = disclosure_facts(
        transport=TransportClass.HTTP,
        method="GET",
        url=canonical_url,
        capability_id=16,
    )
    return SearchSourceAdmission(
        url=canonical_url,
        destination=facts.destination,
        hostname=hostname,
        query_fields=facts.query_fields,
        search_provider=normalized_provider,
        capability_id=16,
        request_id=normalized_request_id,
        session_id=normalized_session_id,
        initiation=initiation,
    )


def search_source_disclosure_classifier(admission: SearchSourceAdmission):
    """Classify only the exact credential-free GET bound by ``admission``."""

    classified = False

    def classify(facts):
        nonlocal classified
        if (
            classified
            or not isinstance(admission, SearchSourceAdmission)
            or facts.transport is not TransportClass.HTTP
            or facts.method != "GET"
            or facts.destination != admission.destination
            or facts.capability_id != admission.capability_id
            or not facts.shape_supported
            or facts.query_fields != admission.query_fields
            or facts.parameter_fields
            or facts.header_fields
            or facts.cookie_fields
            or facts.json_fields
            or facts.form_fields
            or facts.credential_categories
        ):
            return None
        classified = True
        return HttpDisclosureContext(
            caller="search_result_source.capability_16",
            purpose="read_current_search_result",
            provider=admission.hostname,
            provider_class=ProviderClass.SEARCH,
            data_categories=frozenset({DataCategory.SOURCE_URL}),
            initiation=admission.initiation,
            action_id=admission.request_id,
        )

    return classify
