from __future__ import annotations

import asyncio

import pytest
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
from src.governor.network_mediator import NetworkMediator
from src.openclaw.tool_registry import get_tool_registry
from src.skills.news import NewsSkill, _news_rss_disclosure_classifier
from src.tools.rss_fetch import fetch_rss_headlines

FEED_URL = "https://feeds.npr.org/1001/rss.xml"
RSS_XML = (
    "<rss><channel><item><title>Headline</title>"
    "<link>https://www.npr.org/story</link></item></channel></rss>"
)


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


def _rss_facts(*, url: str = FEED_URL, method: str = "GET", capability_id: int = 56, headers=None):
    return disclosure_facts(
        transport=TransportClass.HTTP,
        method=method,
        url=url,
        headers=(
            headers
            if headers is not None
            else {
                "Accept": "application/rss+xml",
                "User-Agent": "Nova/1.0 (+https://local.nova)",
            }
        ),
        capability_id=capability_id,
    )


def test_news_rss_classifier_binds_exact_feed_shape_and_taxonomy():
    classifier = _news_rss_disclosure_classifier(
        FEED_URL,
        provider="npr_org",
        initiation=InitiationClass.USER_INITIATED,
    )

    context = classifier(_rss_facts())

    assert context is not None
    assert context.caller == "news_skill.capability_56"
    assert context.purpose == "news_rss_retrieval"
    assert context.provider == "npr_org"
    assert context.provider_class is ProviderClass.NEWS_SOURCE
    assert context.data_categories == frozenset({DataCategory.SOURCE_URL})
    assert context.credential_categories == frozenset()
    assert context.initiation is InitiationClass.USER_INITIATED


@pytest.mark.parametrize(
    "facts",
    [
        _rss_facts(method="POST"),
        _rss_facts(url="https://feeds.npr.org/1002/rss.xml"),
        _rss_facts(capability_id=48),
        _rss_facts(headers={"Accept": "application/rss+xml", "Authorization": "Bearer secret"}),
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url=FEED_URL,
            params={"topic": "private"},
            headers={"Accept": "application/rss+xml", "User-Agent": "Nova/1.0 (+https://local.nova)"},
            capability_id=56,
        ),
    ],
)
def test_news_rss_classifier_rejects_changed_request(facts):
    classifier = _news_rss_disclosure_classifier(
        FEED_URL,
        provider="npr_org",
        initiation=InitiationClass.USER_INITIATED,
    )

    assert classifier(facts) is None


def test_news_rss_default_denial_precedes_dns_and_session(monkeypatch):
    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("RSS denial must precede DNS")

    def forbidden_session(*_args, **_kwargs):
        attempts["session"] += 1
        raise AssertionError("RSS denial must precede session construction")

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", forbidden_dns)
    monkeypatch.setattr("src.governor.network_mediator.requests.Session", forbidden_session)
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="news-rss-test-v1"),
        disclosure_evidence_sink=None,
    )
    mediator._registry = _Registry()

    result = asyncio.run(NewsSkill(network=mediator).handle("news"))

    assert result.success is False
    assert attempts == {"dns": 0, "session": 0}


def test_news_rss_synthetic_allow_preserves_injected_boundary(monkeypatch):
    classifier = _news_rss_disclosure_classifier(
        FEED_URL,
        provider="npr_org",
        initiation=InitiationClass.USER_INITIATED,
    )
    facts = _rss_facts()
    policy = DisclosurePolicy(
        version="news-rss-test-v1",
        grants=(
            DisclosureGrant(
                provider="npr_org",
                provider_class=ProviderClass.NEWS_SOURCE,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({FEED_URL}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.SOURCE_URL}),
                http_methods=frozenset({"GET"}),
                request_shapes=frozenset({facts.request_shape}),
                purposes=frozenset({"news_rss_retrieval"}),
                callers=frozenset({"news_skill.capability_56"}),
                capability_ids=frozenset({56}),
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
        content = RSS_XML.encode()
        text = RSS_XML
        is_redirect = False
        is_permanent_redirect = False

        def raise_for_status(self):
            return None

    class _Session:
        def request(self, **_kwargs):
            return _Response()

    mediator._new_session = _Session

    items = asyncio.run(
        fetch_rss_headlines(
            FEED_URL,
            network=mediator,
            disclosure_classifier=classifier,
        )
    )

    assert items[0]["title"] == "Headline"
    assert len(sink.records) == 1
    assert sink.records[0].decision == "allow"
    assert sink.records[0].data_categories == ("source_url",)


def test_news_rss_classifier_rejects_uncatalogued_feed():
    url = "https://example.com/rss"
    classifier = _news_rss_disclosure_classifier(
        url,
        provider="example_com",
        initiation=InitiationClass.USER_INITIATED,
    )

    assert classifier(_rss_facts(url=url)) is None


def test_openclaw_news_uses_approved_initiation():
    marker = object()

    skill = get_tool_registry().create("news", network=marker)

    assert skill.network is marker
    assert skill.initiation is InitiationClass.APPROVED
