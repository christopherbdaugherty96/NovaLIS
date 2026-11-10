from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from src.actions.action_request import ActionRequest
from src.executors.multi_source_reporting_executor import (
    MultiSourceReportingExecutor,
    build_cap48_network_plan,
)
from src.executors.web_search_executor import WebSearchExecutor
from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    DestinationClass,
    DisclosureGrant,
    DisclosurePolicy,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import disclosure_facts
from src.governor.exceptions import DisclosureDeniedError
from src.governor.network_mediator import NetworkMediator
from src.openclaw.tool_registry import get_tool_registry
from src.services.search_disclosure import search_disclosure_classifier

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
DUCK_URL = "https://api.duckduckgo.com/"


class _Registry:
    def get(self, _capability_id: int):
        return object()

    def is_enabled(self, _capability_id: int) -> bool:
        return True


class _Sink:
    def __init__(self) -> None:
        self.records = []

    def append(self, record) -> None:
        self.records.append(record)


def _facts(provider: str, capability_id: int = 16):
    if provider == "brave":
        return disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url=BRAVE_URL,
            params={"q": "private topic", "count": 5},
            headers={"Accept": "application/json", "X-Subscription-Token": "secret"},
            capability_id=capability_id,
        )
    return disclosure_facts(
        transport=TransportClass.HTTP,
        method="GET",
        url=DUCK_URL,
        params={
            "q": "private topic",
            "format": "json",
            "no_html": "1",
            "no_redirect": "1",
            "skip_disambig": "1",
        },
        headers={"Accept": "application/json"},
        capability_id=capability_id,
    )


@pytest.mark.parametrize(
    ("provider", "capability_id", "initiation", "expected_provider", "expected_credentials"),
    [
        ("brave", 16, InitiationClass.USER_INITIATED, "brave_search", {CredentialCategory.ORIGIN_CREDENTIAL}),
        ("duckduckgo", 16, InitiationClass.APPROVED, "duckduckgo", set()),
        ("brave", 48, InitiationClass.APPROVED, "brave_search", {CredentialCategory.ORIGIN_CREDENTIAL}),
        ("duckduckgo", 48, InitiationClass.APPROVED, "duckduckgo", set()),
    ],
)
def test_search_classifier_binds_provider_shape_capability_and_initiation(
    provider,
    capability_id,
    initiation,
    expected_provider,
    expected_credentials,
):
    classifier = search_disclosure_classifier(
        provider=provider,
        capability_id=capability_id,
        initiation=initiation,
    )

    context = classifier(_facts(provider, capability_id))

    assert context is not None
    assert context.provider == expected_provider
    assert context.provider_class is ProviderClass.SEARCH
    assert context.data_categories == frozenset({DataCategory.SEARCH_QUERY})
    assert context.initiation is initiation
    assert _facts(provider, capability_id).credential_categories == frozenset(expected_credentials)


@pytest.mark.parametrize(
    "facts",
    [
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="POST",
            url=BRAVE_URL,
            params={"q": "topic", "count": 5},
            headers={"Accept": "application/json", "X-Subscription-Token": "secret"},
            capability_id=16,
        ),
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url="https://search.example.com/",
            params={"q": "topic", "count": 5},
            headers={"Accept": "application/json", "X-Subscription-Token": "secret"},
            capability_id=16,
        ),
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url=BRAVE_URL,
            params={"q": "topic", "count": 5, "extra": "value"},
            headers={"Accept": "application/json", "X-Subscription-Token": "secret"},
            capability_id=16,
        ),
        _facts("brave", 48),
    ],
)
def test_search_classifier_rejects_changed_brave_request(facts):
    classifier = search_disclosure_classifier(
        provider="brave",
        capability_id=16,
        initiation=InitiationClass.USER_INITIATED,
    )

    assert classifier(facts) is None


@pytest.mark.parametrize("brave_key", ["synthetic-key", ""])
def test_cap16_disclosure_denial_is_terminal_and_sanitized(monkeypatch, brave_key):
    if brave_key:
        monkeypatch.setenv("BRAVE_API_KEY", brave_key)
    else:
        monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    calls = []

    class _Network:
        def request(self, **kwargs):
            calls.append(kwargs)
            raise DisclosureDeniedError("sensitive-policy-reason")

    result = WebSearchExecutor(_Network(), object()).execute(
        ActionRequest(capability_id=16, params={"query": "private topic"})
    )

    assert result.success is False
    assert len(calls) == 1
    assert "sensitive-policy-reason" not in result.message
    assert "sensitive-policy-reason" not in repr(result.data)


def test_cap48_disclosure_denial_does_not_fall_back(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "synthetic-key")
    calls = []

    class _Network:
        def request(self, **kwargs):
            calls.append(kwargs)
            raise DisclosureDeniedError("sensitive-policy-reason")

    query = "private topic"
    request = SimpleNamespace(
        capability_id=48,
        params={"query": query, "network_plan": build_cap48_network_plan(query)},
        request_id="cap48-denied",
    )

    result = MultiSourceReportingExecutor(_Network()).execute(request)

    assert result.success is False
    assert result.structured_data["failure_kind"] == "disclosure_denied"
    assert len(calls) == 1
    assert "sensitive-policy-reason" not in repr(result.data)


def test_cap16_default_denial_precedes_dns_and_session(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "synthetic-key")
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("search denial must precede DNS")

    def forbidden_session(*_args, **_kwargs):
        attempts["session"] += 1
        raise AssertionError("search denial must precede session construction")

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", forbidden_dns)
    monkeypatch.setattr("src.governor.network_mediator.requests.Session", forbidden_session)
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="search-test-v1"),
        disclosure_evidence_sink=None,
    )
    mediator._registry = _Registry()

    result = WebSearchExecutor(mediator, object()).execute(
        ActionRequest(capability_id=16, params={"query": "private topic"})
    )

    assert result.success is False
    assert attempts == {"dns": 0, "session": 0}


def test_cap48_default_denial_precedes_dns_and_session(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "synthetic-key")
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("search denial must precede DNS")

    def forbidden_session(*_args, **_kwargs):
        attempts["session"] += 1
        raise AssertionError("search denial must precede session construction")

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", forbidden_dns)
    monkeypatch.setattr("src.governor.network_mediator.requests.Session", forbidden_session)
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="search-test-v1"),
        disclosure_evidence_sink=None,
    )
    mediator._registry = _Registry()
    query = "private topic"
    request = SimpleNamespace(
        capability_id=48,
        params={"query": query, "network_plan": build_cap48_network_plan(query)},
        request_id="cap48-zero-attempt",
    )

    result = MultiSourceReportingExecutor(mediator).execute(request)

    assert result.success is False
    assert result.structured_data["failure_kind"] == "disclosure_denied"
    assert attempts == {"dns": 0, "session": 0}


def test_cap16_synthetic_allow_records_sanitized_evidence(monkeypatch):
    secret = "synthetic-brave-secret-must-not-persist"
    monkeypatch.setenv("BRAVE_API_KEY", secret)
    facts = _facts("brave", 16)
    policy = DisclosurePolicy(
        version="search-test-v1",
        grants=(
            DisclosureGrant(
                provider="brave_search",
                provider_class=ProviderClass.SEARCH,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({BRAVE_URL}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.SEARCH_QUERY}),
                http_methods=frozenset({"GET"}),
                request_shapes=frozenset({facts.request_shape}),
                credential_categories=frozenset({CredentialCategory.ORIGIN_CREDENTIAL}),
                purposes=frozenset({"web_search_query"}),
                callers=frozenset({"fixed_search.capability_16"}),
                capability_ids=frozenset({16}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )
    sink = _Sink()
    mediator = NetworkMediator(
        disclosure_policy=policy,
        disclosure_evidence_sink=sink,
        disclosure_classifier=lambda _facts: None,
    )
    mediator._registry = _Registry()
    mediator._validate_url = lambda _url: None

    class _Response:
        status_code = 200
        content = b'{"web":{"results":[]}}'
        text = content.decode()
        is_redirect = False
        is_permanent_redirect = False

        def raise_for_status(self):
            return None

        def json(self):
            return {"web": {"results": []}}

    class _Session:
        def request(self, **_kwargs):
            return _Response()

    mediator._new_session = _Session

    result = WebSearchExecutor(mediator, object()).execute(
        ActionRequest(capability_id=16, params={"query": "private topic"})
    )

    assert result.success is True
    assert len(sink.records) == 1
    assert sink.records[0].decision == "allow"
    assert sink.records[0].data_categories == ("search_query",)
    assert sink.records[0].credential_categories == ("origin_credential",)
    assert secret not in repr(sink.records)


def test_openclaw_search_uses_approved_initiation_and_sanitizes_denial():
    class _Network:
        def request(self, **_kwargs):
            raise DisclosureDeniedError("sensitive-policy-reason")

    skill = get_tool_registry().create("web_search", network=_Network())
    result = asyncio.run(skill.handle("search private topic"))

    assert skill.initiation is InitiationClass.APPROVED
    assert result.success is False
    assert "sensitive-policy-reason" not in result.message
    assert "sensitive-policy-reason" not in repr(result.data)


def test_normal_brave_provider_failure_may_fall_back_to_duck(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "synthetic-key")
    calls = []

    class _Network:
        def request(self, **kwargs):
            calls.append(kwargs)
            if kwargs["url"] == BRAVE_URL:
                return {"status_code": 500, "data": {}}
            return {"status_code": 200, "data": {"Abstract": "Result", "AbstractURL": "https://example.test"}}

    result = WebSearchExecutor(_Network(), object()).execute(
        ActionRequest(capability_id=16, params={"query": "public topic"})
    )

    assert result.success is True
    assert calls[0]["url"] == BRAVE_URL
    assert calls[1]["url"] == DUCK_URL
    # Any later result-page read remains a separate dynamic destination path.
    assert all("disclosure_classifier" not in call for call in calls[2:])
