"""Short-lived, session-bound admission for Cap 49/50 news article reads."""

from __future__ import annotations

import ipaddress
import re
import secrets
import threading
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from src.governor.disclosure_policy import (
    DataCategory,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import HttpDisclosureContext, disclosure_facts
from src.governor.exceptions import DisclosureDeniedError

_DNS_LABEL_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
_PROVIDER_RE = re.compile(r"[a-z0-9](?:[a-z0-9_.-]{0,78}[a-z0-9])?\Z")
_NEWS_CAPABILITIES = frozenset({49, 50})
NEWS_USER_INITIATED = InitiationClass.USER_INITIATED


def is_news_disclosure_denial(error: BaseException) -> bool:
    return isinstance(error, DisclosureDeniedError)


def news_initiation_for_activity(value: object) -> InitiationClass:
    if str(value or "").strip().lower() == "user_action":
        return InitiationClass.USER_INITIATED
    return InitiationClass.AUTOMATIC


def _canonical_external_https_url(value: str) -> tuple[str, str]:
    url = str(value or "").strip()
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise ValueError("News article URL is invalid.") from error
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
        raise ValueError("News article URL is not a canonical external HTTPS URL.")
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("News article URL must be external.")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            hostname.encode("ascii")
        except UnicodeEncodeError as error:
            raise ValueError("News article hostname must use its ASCII form.") from error
        labels = hostname.split(".")
        if len(labels) < 2 or any(not _DNS_LABEL_RE.fullmatch(label) for label in labels):
            raise ValueError("News article hostname is not canonical.")
    else:
        if not address.is_global:
            raise ValueError("News article URL must be external.")
    return url, hostname


def _utc_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as error:
            raise ValueError("News provenance requires a valid fetch time.") from error
    if parsed.tzinfo is None:
        raise ValueError("News provenance fetch time must include a timezone.")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class _NewsSourceReceipt:
    url: str
    hostname: str
    provider: str
    session_id: str
    expires_at: datetime


@dataclass(frozen=True)
class NewsSourceAdmission:
    url: str
    destination: str
    hostname: str
    query_fields: tuple[str, ...]
    provider: str
    capability_id: int
    request_id: str
    session_id: str
    initiation: InitiationClass


class NewsSourceProvenanceRegistry:
    """Bounded process-local store of opaque receipts from governed Cap 56 reads."""

    def __init__(self, *, max_entries: int = 512) -> None:
        self._max_entries = max(1, int(max_entries))
        self._records: OrderedDict[str, _NewsSourceReceipt] = OrderedDict()
        self._lock = threading.Lock()

    def reset(self) -> None:
        with self._lock:
            self._records.clear()

    def issue(
        self,
        *,
        url: str,
        provider: str,
        session_id: str,
        fetched_at: datetime | str,
        ttl_seconds: float,
    ) -> str:
        canonical_url, hostname = _canonical_external_https_url(url)
        normalized_provider = str(provider or "").strip().lower()
        normalized_session = str(session_id or "").strip()
        if not _PROVIDER_RE.fullmatch(normalized_provider):
            raise ValueError("News provenance requires a canonical provider identity.")
        if not normalized_session:
            raise ValueError("News provenance requires a trusted session identifier.")
        try:
            ttl = float(ttl_seconds)
        except (TypeError, ValueError) as error:
            raise ValueError("News provenance requires a valid TTL.") from error
        if ttl <= 0 or ttl > 900:
            raise ValueError("News provenance TTL is outside the supported range.")
        expires_at = _utc_datetime(fetched_at) + timedelta(seconds=ttl)
        token = secrets.token_urlsafe(32)
        record = _NewsSourceReceipt(
            url=canonical_url,
            hostname=hostname,
            provider=normalized_provider,
            session_id=normalized_session,
            expires_at=expires_at,
        )
        with self._lock:
            self._records[token] = record
            self._records.move_to_end(token)
            while len(self._records) > self._max_entries:
                self._records.popitem(last=False)
        return token

    def admit(
        self,
        *,
        token: str,
        url: str,
        capability_id: int,
        request_id: str | None,
        session_id: str | None,
        initiation: InitiationClass,
    ) -> NewsSourceAdmission:
        normalized_token = str(token or "").strip()
        normalized_session = str(session_id or "").strip()
        normalized_request = str(request_id or "").strip()
        canonical_url, _hostname = _canonical_external_https_url(url)
        if int(capability_id) not in _NEWS_CAPABILITIES:
            raise ValueError("News source reads are limited to capabilities 49 and 50.")
        if not normalized_request or not normalized_session:
            raise ValueError("News source admission requires request and session identifiers.")
        if not isinstance(initiation, InitiationClass):
            raise ValueError("News source admission requires governed initiation.")
        with self._lock:
            record = self._records.get(normalized_token)
        if record is None:
            raise ValueError("News source provenance is missing or invalid.")
        if datetime.now(timezone.utc) >= record.expires_at:
            with self._lock:
                self._records.pop(normalized_token, None)
            raise ValueError("News source provenance has expired.")
        if record.url != canonical_url or record.session_id != normalized_session:
            raise ValueError("News source provenance does not match this request.")
        facts = disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url=canonical_url,
            capability_id=int(capability_id),
        )
        return NewsSourceAdmission(
            url=canonical_url,
            destination=facts.destination,
            hostname=record.hostname,
            query_fields=facts.query_fields,
            provider=record.provider,
            capability_id=int(capability_id),
            request_id=normalized_request,
            session_id=normalized_session,
            initiation=initiation,
        )


def news_source_disclosure_classifier(admission: NewsSourceAdmission):
    """Classify one exact, credential-free GET bound by a current receipt."""

    classified = False

    def classify(facts):
        nonlocal classified
        if (
            classified
            or not isinstance(admission, NewsSourceAdmission)
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
            caller=f"news_source.capability_{admission.capability_id}",
            purpose="read_current_news_source",
            provider=admission.provider,
            provider_class=ProviderClass.NEWS_SOURCE,
            data_categories=frozenset({DataCategory.SOURCE_URL}),
            initiation=admission.initiation,
            action_id=admission.request_id,
        )

    return classify


news_source_provenance_registry = NewsSourceProvenanceRegistry()
