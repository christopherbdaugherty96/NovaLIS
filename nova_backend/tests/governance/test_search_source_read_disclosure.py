from __future__ import annotations

import socket

import pytest
from src.actions.action_request import ActionRequest
from src.executors.web_search_executor import WebSearchExecutor
from src.governor.disclosure_policy import (
    DataCategory,
    DestinationClass,
    DisclosureGrant,
    DisclosurePolicy,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import disclosure_facts
from src.governor.exceptions import DisclosureDeniedError, NetworkMediatorError
from src.governor.network_mediator import NetworkMediator
from src.services.search_source_disclosure import (
    build_search_source_admission,
    search_source_disclosure_classifier,
)


def _admission(**overrides):
    values = {
        "url": "https://example.com/report?id=7",
        "search_provider": "brave",
        "capability_id": 16,
        "request_id": "request-1",
        "session_id": "session-1",
        "initiation": InitiationClass.USER_INITIATED,
    }
    values.update(overrides)
    return build_search_source_admission(**values)


def _facts(url: str = "https://example.com/report?id=7"):
    return disclosure_facts(
        transport=TransportClass.HTTP,
        method="GET",
        url=url,
        capability_id=16,
    )


def test_source_classifier_binds_exact_current_search_result():
    admission = _admission()
    classifier = search_source_disclosure_classifier(admission)

    context = classifier(_facts())

    assert context is not None
    assert context.provider == "example.com"
    assert context.provider_class is ProviderClass.SEARCH
    assert context.data_categories == frozenset({DataCategory.SOURCE_URL})
    assert context.initiation is InitiationClass.USER_INITIATED


@pytest.mark.parametrize(
    "facts",
    [
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url="https://example.com/other?id=7",
            capability_id=16,
        ),
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="POST",
            url="https://example.com/report?id=7",
            capability_id=16,
        ),
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url="https://example.com/report?id=7",
            headers={"Authorization": "secret"},
            capability_id=16,
        ),
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url="https://example.com/report?id=7",
            capability_id=48,
        ),
    ],
)
def test_source_classifier_rejects_modified_request(facts):
    assert search_source_disclosure_classifier(_admission())(facts) is None


def test_source_classifier_is_single_use_so_redirects_require_new_admission():
    classifier = search_source_disclosure_classifier(_admission())

    assert classifier(_facts()) is not None
    assert classifier(_facts()) is None


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/report",
        "https://user:password@example.com/report",
        "https://example.com:8443/report",
        "https://127.0.0.1/report",
        "https://localhost/report",
        "file:///tmp/report",
        "https://example.com/report#fragment",
    ],
)
def test_source_admission_rejects_unsafe_or_noncanonical_urls(url):
    with pytest.raises(ValueError):
        _admission(url=url)


def test_source_read_rejects_stale_request_binding_without_network_attempt():
    attempts = []

    class _Network:
        def request(self, **kwargs):
            attempts.append(kwargs)
            raise AssertionError("stale admission must not reach the network boundary")

    executor = WebSearchExecutor(_Network(), object())
    outcome = executor._fetch_source_text(
        capability_id=16,
        admission=_admission(),
        request_id="later-request",
        session_id="session-1",
    )

    assert outcome.status == "denied"
    assert outcome.text == ""
    assert attempts == []


def test_source_read_denial_is_truthful_and_does_not_fallback(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "synthetic")
    calls = []

    class _Network:
        def request(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                return {
                    "status_code": 200,
                    "data": {
                        "web": {
                            "results": [
                                {
                                    "title": "Result",
                                    "url": "https://example.com/report",
                                    "description": "Search snippet only",
                                }
                            ]
                        }
                    },
                }
            raise DisclosureDeniedError("sensitive-policy-reason")

    result = WebSearchExecutor(_Network(), object()).execute(
        ActionRequest(capability_id=16, params={"query": "private topic"})
    )

    assert result.success is True
    assert len(calls) == 2
    assert "disclosure_classifier" in calls[1]
    assert result.data["widget"]["data"]["source_pages_read"] == 0
    assert "authorization was unavailable" in result.message
    assert "reviewed 0 pages" not in result.message
    assert "sensitive-policy-reason" not in repr(result.data)


def test_source_read_network_failure_is_not_reported_as_security_denial(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "synthetic")
    calls = []

    class _Network:
        def request(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                return {
                    "status_code": 200,
                    "data": {
                        "web": {
                            "results": [
                                {
                                    "title": "Result",
                                    "url": "https://example.com/report",
                                    "description": "Search snippet only",
                                }
                            ]
                        }
                    },
                }
            raise NetworkMediatorError("site unavailable")

    result = WebSearchExecutor(_Network(), object()).execute(
        ActionRequest(capability_id=16, params={"query": "private topic"})
    )

    assert result.success is True
    assert len(calls) == 2
    assert "page was unavailable" in result.message
    assert "authorization was unavailable" not in result.message


def test_default_source_denial_precedes_dns(monkeypatch):
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("source denial must precede DNS")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden_dns)
    monkeypatch.setattr(
        "src.governor.network_mediator.requests.Session",
        lambda: attempts.__setitem__("session", attempts["session"] + 1),
    )
    admission = _admission()
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="source-read-test-v1"),
        disclosure_evidence_sink=None,
    )
    mediator._registry = type(
        "Registry",
        (),
        {"get": lambda _self, _capability_id: object(), "is_enabled": lambda _self, _capability_id: True},
    )()

    outcome = WebSearchExecutor(mediator, object())._fetch_source_text(
        capability_id=16,
        admission=admission,
        request_id="request-1",
        session_id="session-1",
    )

    assert outcome.status == "denied"
    assert attempts == {"dns": 0, "session": 0}


def test_synthetic_source_allow_records_sanitized_evidence():
    admission = _admission()
    facts = _facts()
    policy = DisclosurePolicy(
        version="source-read-test-v1",
        grants=(
            DisclosureGrant(
                provider="example.com",
                provider_class=ProviderClass.SEARCH,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({admission.destination}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.SOURCE_URL}),
                http_methods=frozenset({"GET"}),
                request_shapes=frozenset({facts.request_shape}),
                credential_categories=frozenset(),
                purposes=frozenset({"read_current_search_result"}),
                callers=frozenset({"search_result_source.capability_16"}),
                capability_ids=frozenset({16}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )

    class _Sink:
        def __init__(self):
            self.records = []

        def append(self, record):
            self.records.append(record)

    sink = _Sink()
    mediator = NetworkMediator(disclosure_policy=policy, disclosure_evidence_sink=sink)
    mediator._registry = type(
        "Registry",
        (),
        {"get": lambda _self, _capability_id: object(), "is_enabled": lambda _self, _capability_id: True},
    )()
    mediator._validate_url = lambda _url: None

    class _Response:
        status_code = 200
        content = b"<html><article>Verified page text.</article></html>"
        text = content.decode()
        is_redirect = False
        is_permanent_redirect = False

        def raise_for_status(self):
            return None

    class _Session:
        def request(self, **_kwargs):
            return _Response()

    mediator._new_session = _Session
    outcome = WebSearchExecutor(mediator, object())._fetch_source_text(
        capability_id=16,
        admission=admission,
        request_id="request-1",
        session_id="session-1",
    )

    assert outcome.status == "read"
    assert "Verified page text" in outcome.text
    assert len(sink.records) == 1
    assert sink.records[0].decision == "allow"
    assert sink.records[0].data_categories == ("source_url",)
    assert "id=7" not in repr(sink.records)
