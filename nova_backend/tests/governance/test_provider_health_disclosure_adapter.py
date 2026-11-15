from __future__ import annotations

import pytest
from src.api.connections_api import CONNECTION_HEALTH_OPERATIONS, _health_check
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
from src.governor.network_mediator import NetworkMediator
from src.services.provider_health_disclosure import (
    PROVIDER_HEALTH_SPECS,
    provider_health_disclosure_classifier,
)


class _Sink:
    def __init__(self) -> None:
        self.records = []

    def append(self, record) -> None:
        self.records.append(record)


class _Response:
    status_code = 200
    content = b"{}"
    text = "{}"
    is_redirect = False
    is_permanent_redirect = False

    def json(self):
        return {}


def _request_parts(provider: str, secret: str = "synthetic-provider-secret"):
    operation = CONNECTION_HEALTH_OPERATIONS[provider]
    return operation.url, operation.params(secret), operation.headers(secret)


def _facts(provider: str, *, method: str = "GET", url: str | None = None, params=None, headers=None):
    expected_url, expected_params, expected_headers = _request_parts(provider)
    return disclosure_facts(
        transport=TransportClass.HTTP,
        method=method,
        url=url or expected_url,
        params=expected_params if params is None else params,
        headers=expected_headers if headers is None else headers,
        capability_id=None,
    )


def _allow_policy(provider: str, secret: str) -> DisclosurePolicy:
    _url, params, headers = _request_parts(provider, secret)
    facts = _facts(provider, params=params, headers=headers)
    spec = PROVIDER_HEALTH_SPECS[provider]
    return DisclosurePolicy(
        version="provider-health-test-v1",
        grants=(
            DisclosureGrant(
                provider=spec.provider,
                provider_class=spec.provider_class,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({spec.url}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
                http_methods=frozenset({"GET"}),
                request_shapes=frozenset({facts.request_shape}),
                credential_categories=spec.credentials,
                purposes=frozenset({"provider_health_verification"}),
                callers=frozenset({f"settings_provider_health.{provider}"}),
                capability_ids=frozenset({None}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )


@pytest.mark.parametrize(
    ("provider", "provider_class", "credentials"),
    [
        ("openai", ProviderClass.HOSTED_MODEL, {CredentialCategory.BEARER_TOKEN}),
        ("brave", ProviderClass.SEARCH, {CredentialCategory.ORIGIN_CREDENTIAL}),
        ("news", ProviderClass.NEWS_SOURCE, {CredentialCategory.API_KEY}),
        ("weather", ProviderClass.WEATHER, {CredentialCategory.API_KEY}),
    ],
)
def test_provider_health_classifier_binds_exact_taxonomy(provider, provider_class, credentials):
    context = provider_health_disclosure_classifier(provider)(_facts(provider))

    assert context is not None
    assert context.caller == f"settings_provider_health.{provider}"
    assert context.purpose == "provider_health_verification"
    assert context.provider_class is provider_class
    assert context.data_categories == frozenset({DataCategory.STRUCTURAL_METADATA})
    assert context.credential_categories == frozenset(credentials)
    assert context.initiation is InitiationClass.USER_INITIATED


def test_visual_crossing_key_is_explicitly_classified_as_api_key():
    facts = _facts("weather")
    context = provider_health_disclosure_classifier("weather")(facts)

    assert facts.credential_categories == frozenset()
    assert context is not None
    assert context.credential_categories == frozenset({CredentialCategory.API_KEY})


@pytest.mark.parametrize("provider", ["openai", "brave", "news", "weather"])
def test_provider_health_classifier_rejects_changed_request_shape(provider):
    classifier = provider_health_disclosure_classifier(provider)
    _url, params, _headers = _request_parts(provider)

    assert classifier(_facts(provider, method="POST")) is None
    assert classifier(_facts(provider, url="https://example.test/health")) is None
    assert classifier(
        _facts(provider, params={**(params or {}), "extra": "value"})
    ) is None


@pytest.mark.parametrize("provider", ["openai", "brave", "news", "weather"])
def test_provider_health_denial_precedes_dns_and_session(provider, monkeypatch):
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("health denial must precede DNS")

    def forbidden_session(*_args, **_kwargs):
        attempts["session"] += 1
        raise AssertionError("health denial must precede session creation")

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", forbidden_dns)
    monkeypatch.setattr("src.governor.network_mediator.requests.Session", forbidden_session)
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="provider-health-test-v1"),
        disclosure_evidence_sink=_Sink(),
    )

    ok, detail = _health_check(provider, "synthetic-provider-secret", mediator)

    assert ok is None
    assert "Data-Out policy" in detail
    assert attempts == {"dns": 0, "session": 0}


@pytest.mark.parametrize("provider", ["openai", "brave", "news", "weather"])
def test_provider_health_synthetic_allow_records_sanitized_evidence(provider):
    secret = "synthetic-provider-secret-must-not-persist"
    spec = PROVIDER_HEALTH_SPECS[provider]
    sink = _Sink()
    mediator = NetworkMediator(
        disclosure_policy=_allow_policy(provider, secret),
        disclosure_evidence_sink=sink,
    )
    mediator._validate_url = lambda _url: None
    mediator._new_session = lambda: type(
        "_Session", (), {"request": lambda self, **_kwargs: _Response()}
    )()

    ok, detail = _health_check(provider, secret, mediator)

    assert ok is True, (detail, sink.records)
    assert len(sink.records) == 1
    assert sink.records[0].decision == "allow"
    assert sink.records[0].credential_categories == tuple(
        sorted(category.value for category in spec.credentials)
    )
    assert secret not in repr(sink.records)


@pytest.mark.parametrize("provider", ["openai", "brave", "news", "weather"])
def test_provider_health_missing_evidence_fails_before_transport(provider, monkeypatch):
    secret = "synthetic-provider-secret"
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("missing evidence must precede DNS")

    def forbidden_session(*_args, **_kwargs):
        attempts["session"] += 1
        raise AssertionError("missing evidence must precede session creation")

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", forbidden_dns)
    monkeypatch.setattr("src.governor.network_mediator.requests.Session", forbidden_session)
    mediator = NetworkMediator(
        disclosure_policy=_allow_policy(provider, secret),
        disclosure_evidence_sink=None,
    )

    ok, detail = _health_check(provider, secret, mediator)

    assert ok is None
    assert "Data-Out policy" in detail
    assert attempts == {"dns": 0, "session": 0}


def test_health_specs_match_the_static_connection_allowlist():
    assert {
        provider: operation.url
        for provider, operation in CONNECTION_HEALTH_OPERATIONS.items()
    } == {
        provider: spec.url
        for provider, spec in PROVIDER_HEALTH_SPECS.items()
    }
