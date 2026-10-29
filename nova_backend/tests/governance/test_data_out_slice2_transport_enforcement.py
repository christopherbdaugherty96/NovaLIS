from __future__ import annotations

from dataclasses import dataclass

import pytest
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
from src.governor.disclosure_transport import HttpDisclosureContext
from src.governor.exceptions import NetworkMediatorError
from src.governor.network_mediator import NetworkMediator
from src.llm.model_network_mediator import ModelNetworkMediator, ModelNetworkMediatorError


class _Sink:
    def __init__(self) -> None:
        self.records = []

    def append(self, record) -> None:
        self.records.append(record)


class _Registry:
    def get(self, _capability_id: int):
        return object()

    def is_enabled(self, _capability_id: int) -> bool:
        return True


def _context(*, provider: str = "search", category=ProviderClass.SEARCH):
    return HttpDisclosureContext(
        caller="slice2_test",
        purpose="bounded_test",
        provider=provider,
        provider_class=category,
        data_categories=frozenset({DataCategory.SEARCH_QUERY}),
        initiation=InitiationClass.USER_INITIATED,
    )


def _policy(
    *destinations: str,
    transport: TransportClass = TransportClass.HTTP,
    provider: str = "search",
    provider_class: ProviderClass = ProviderClass.SEARCH,
    capability_id: int | None = 16,
):
    return DisclosurePolicy(
        version="slice2-test-v1",
        grants=(
            DisclosureGrant(
                provider=provider,
                provider_class=provider_class,
                destination_class=(
                    DestinationClass.LOCAL_LOOPBACK
                    if destinations and "localhost" in destinations[0]
                    else DestinationClass.EXTERNAL_WEB
                ),
                destinations=frozenset(destinations),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({transport}),
                data_categories=frozenset({DataCategory.SEARCH_QUERY}),
                purposes=frozenset({"bounded_test"}),
                callers=frozenset({"slice2_test"}),
                capability_ids=frozenset({capability_id}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )


@pytest.mark.parametrize("with_policy", [False, True])
def test_network_deny_or_missing_evidence_precedes_dns_and_client(
    monkeypatch, with_policy
):
    attempts = {"dns": 0, "client": 0}
    monkeypatch.setattr(
        "src.governor.network_mediator.socket.getaddrinfo",
        lambda *_args, **_kwargs: attempts.__setitem__("dns", attempts["dns"] + 1),
    )
    monkeypatch.setattr(
        "src.governor.network_mediator.requests.Session",
        lambda: attempts.__setitem__("client", attempts["client"] + 1),
    )
    mediator = NetworkMediator(
        disclosure_policy=(
            _policy("https://allowed.example/search") if with_policy else None
        ),
        # Missing evidence is independently fail-closed even with an ALLOW grant.
        disclosure_evidence_sink=None,
        disclosure_classifier=lambda _facts: _context(),
    )
    mediator._registry = _Registry()

    with pytest.raises(NetworkMediatorError, match="Data-Out denied"):
        mediator.request(
            16,
            "GET",
            "https://allowed.example/search?q=secret",
            params={"q": "secret"},
        )

    assert attempts == {"dns": 0, "client": 0}


def test_model_unknown_precedes_dns_and_session_construction(monkeypatch):
    attempts = {"dns": 0, "client": 0}
    monkeypatch.setattr(
        "src.llm.model_network_mediator.socket.getaddrinfo",
        lambda *_args, **_kwargs: attempts.__setitem__("dns", attempts["dns"] + 1),
    )
    monkeypatch.setattr(
        "src.llm.model_network_mediator.requests.Session",
        lambda: attempts.__setitem__("client", attempts["client"] + 1),
    )

    with pytest.raises(ModelNetworkMediatorError, match="Data-Out denied"):
        ModelNetworkMediator().request_json(
            method="POST",
            url="http://localhost:11434/api/chat",
            json_payload={"prompt": "secret"},
        )

    assert attempts == {"dns": 0, "client": 0}


def test_allow_requires_exact_destination_and_secret_free_evidence():
    sink = _Sink()
    mediator = NetworkMediator(
        disclosure_policy=_policy("https://allowed.example/search"),
        disclosure_evidence_sink=sink,
        disclosure_classifier=lambda _facts: _context(),
    )
    mediator._registry = _Registry()
    mediator._validate_url = lambda _url: None

    @dataclass
    class _Response:
        status_code: int = 200
        content: bytes = b""
        text: str = "ok"
        is_redirect: bool = False
        is_permanent_redirect: bool = False

        def raise_for_status(self):
            return None

    class _Session:
        trust_env = True

        def request(self, **_kwargs):
            return _Response()

    mediator._new_session = _Session
    secret = "synthetic-secret-must-not-persist"
    result = mediator.request(
        16,
        "GET",
        f"https://allowed.example/search?q={secret}",
        params={"q": secret},
        as_json=False,
    )

    assert result["status_code"] == 200
    assert sink.records and sink.records[-1].decision == "allow"
    assert secret not in repr(sink.records)


def test_environment_proxy_is_not_discovered(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy-user:proxy-secret@proxy.example")
    session = NetworkMediator._new_session()
    assert session.trust_env is False


def test_oauth_fields_are_derived_from_actual_payload_names():
    from src.governor.disclosure_policy import DisclosurePolicyEvaluator
    from src.governor.disclosure_transport import authorize_http_disclosure

    sink = _Sink()
    policy = DisclosurePolicy(
        version="oauth-v1",
        grants=(
            DisclosureGrant(
                provider="google_workspace",
                provider_class=ProviderClass.OAUTH,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({"https://oauth2.googleapis.com/token"}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.OAUTH_SETUP}),
                data_categories=frozenset({DataCategory.OAUTH_MATERIAL}),
                credential_categories=frozenset({CredentialCategory.OAUTH_TOKEN}),
                purposes=frozenset({"exchange_code"}),
                callers=frozenset({"google_oauth"}),
                capability_ids=frozenset({None}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )
    decision = authorize_http_disclosure(
        evaluator=DisclosurePolicyEvaluator(),
        policy=policy,
        evidence_sink=sink,
        context=HttpDisclosureContext(
            caller="google_oauth",
            purpose="exchange_code",
            provider="google_workspace",
            provider_class=ProviderClass.OAUTH,
            data_categories=frozenset({DataCategory.OAUTH_MATERIAL}),
            initiation=InitiationClass.USER_INITIATED,
        ),
        transport=TransportClass.OAUTH_SETUP,
        url="https://oauth2.googleapis.com/token",
        headers=None,
        field_names=("authorization_code", "client_secret"),
        ambient_tls_keylog=False,
        has_body=True,
        capability_id=None,
        request_id="",
        session_id="",
    )
    assert decision.may_proceed
    assert sink.records[-1].credential_categories == ("oauth_token",)


def test_tls_keylog_requires_explicit_credential_authorization(monkeypatch):
    monkeypatch.setenv("SSLKEYLOGFILE", "C:/external/synthetic-secret.keys")
    sink = _Sink()
    mediator = NetworkMediator(
        disclosure_policy=_policy("https://allowed.example/search"),
        disclosure_evidence_sink=sink,
        disclosure_classifier=lambda _facts: _context(),
    )
    mediator._registry = _Registry()

    with pytest.raises(NetworkMediatorError, match="Data-Out denied"):
        mediator.request(
            16,
            "GET",
            "https://allowed.example/search",
        )

    assert "tls_session_secret" in sink.records[-1].data_categories
    assert "synthetic-secret" not in repr(sink.records)


def test_classifier_receives_value_free_boundary_facts():
    captured = []
    sink = _Sink()

    def classify(facts):
        captured.append(facts)
        return _context()

    mediator = NetworkMediator(
        disclosure_policy=_policy("https://allowed.example/search"),
        disclosure_evidence_sink=sink,
        disclosure_classifier=classify,
    )
    mediator._registry = _Registry()
    mediator._validate_url = lambda _url: None

    class _Response:
        status_code = 200
        content = b""
        text = "ok"
        is_redirect = False
        is_permanent_redirect = False

        def raise_for_status(self):
            return None

    class _Session:
        def request(self, **_kwargs):
            return _Response()

    mediator._new_session = _Session
    secret = "classifier-must-not-see-this"
    mediator.request(
        16,
        "GET",
        f"https://allowed.example/search?opaque={secret}",
        params={"query": secret},
        as_json=False,
    )

    assert captured[0].destination == "https://allowed.example/search"
    assert captured[0].field_names == ("query",)
    assert secret not in repr(captured)


def test_classifier_failure_is_unknown_before_dns(monkeypatch):
    attempts = 0

    def dns(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", dns)
    sink = _Sink()

    def broken_classifier(_facts):
        raise RuntimeError("synthetic-classifier-secret")

    mediator = NetworkMediator(
        disclosure_policy=_policy("https://allowed.example/search"),
        disclosure_evidence_sink=sink,
        disclosure_classifier=broken_classifier,
    )
    mediator._registry = _Registry()
    with pytest.raises(NetworkMediatorError, match="Data-Out denied") as captured:
        mediator.request(16, "GET", "https://allowed.example/search")

    assert attempts == 0
    assert "synthetic-classifier-secret" not in str(captured.value)
