from __future__ import annotations

import socket
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from src.governor.disclosure_policy import DataCategory, InitiationClass, ProviderClass


def _registry():
    from src.services.news_source_provenance import NewsSourceProvenanceRegistry

    return NewsSourceProvenanceRegistry(max_entries=8)


def _issued(registry, **overrides):
    values = {
        "url": "https://news.example.com/story?id=7",
        "provider": "example_news",
        "session_id": "session-1",
        "fetched_at": datetime.now(timezone.utc),
        "ttl_seconds": 180,
    }
    values.update(overrides)
    return registry.issue(**values)


def test_current_news_receipt_builds_exact_capability_bound_admission():
    from src.governor.disclosure_policy import TransportClass
    from src.governor.disclosure_transport import disclosure_facts
    from src.services.news_source_provenance import news_source_disclosure_classifier

    registry = _registry()
    token = _issued(registry)
    admission = registry.admit(
        token=token,
        url="https://news.example.com/story?id=7",
        capability_id=49,
        request_id="request-1:source",
        session_id="session-1",
        initiation=InitiationClass.USER_INITIATED,
    )

    facts = disclosure_facts(
        transport=TransportClass.HTTP,
        method="GET",
        url=admission.url,
        capability_id=49,
    )
    context = news_source_disclosure_classifier(admission)(facts)

    assert context is not None
    assert context.provider == "example_news"
    assert context.provider_class is ProviderClass.NEWS_SOURCE
    assert context.data_categories == frozenset({DataCategory.SOURCE_URL})
    assert context.initiation is InitiationClass.USER_INITIATED


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("token", "forged-token"),
        ("url", "https://news.example.com/changed?id=7"),
        ("session_id", "other-session"),
        ("capability_id", 16),
    ],
)
def test_provenance_rejects_forged_modified_cross_session_or_wrong_capability(field, value):
    registry = _registry()
    values = {
        "token": _issued(registry),
        "url": "https://news.example.com/story?id=7",
        "capability_id": 50,
        "request_id": "request-1",
        "session_id": "session-1",
        "initiation": InitiationClass.USER_INITIATED,
    }
    values[field] = value

    with pytest.raises(ValueError):
        registry.admit(**values)


def test_provenance_expires_from_original_fetch_time_not_issue_time():
    registry = _registry()
    token = _issued(
        registry,
        fetched_at=datetime.now(timezone.utc) - timedelta(seconds=181),
    )

    with pytest.raises(ValueError, match="expired"):
        registry.admit(
            token=token,
            url="https://news.example.com/story?id=7",
            capability_id=49,
            request_id="request-1",
            session_id="session-1",
            initiation=InitiationClass.USER_INITIATED,
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://news.example.com/story",
        "https://user:secret@news.example.com/story",
        "https://news.example.com:8443/story",
        "https://127.0.0.1/story",
        "https://localhost/story",
        "https://news.example.com/story#fragment",
    ],
)
def test_provenance_rejects_unsafe_article_urls(url):
    with pytest.raises(ValueError):
        _issued(_registry(), url=url)


def test_snapshot_issues_receipts_only_for_retrieved_items(monkeypatch):
    from src.executors import info_snapshot_executor as mod

    now = datetime.now(timezone.utc).isoformat()
    widget = {
        "type": "news",
        "fetched_at": now,
        "cache_ttl_seconds": 180,
        "items": [
            {
                "title": "Retrieved",
                "url": "https://news.example.com/retrieved",
                "source": "Example",
                "source_provider": "example_news",
                "source_retrieved": True,
            },
            {
                "title": "Fallback",
                "url": "https://news.example.com/",
                "source": "Example",
                "source_retrieved": False,
            },
        ],
        "categories": {},
    }
    result = SimpleNamespace(success=True, message="News", widget_data=widget)
    monkeypatch.setattr(mod, "_run_skill", lambda *_args: result)

    request = SimpleNamespace(params={"session_id": "trusted-session"}, request_id="req-1")
    action = mod.NewsSnapshotExecutor().execute(request)
    items = action.data["widget"]["items"]

    assert items[0]["source_provenance"]
    assert "source_provenance" not in items[1]


def test_governor_replaces_caller_claimed_news_session_with_trusted_session(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    governor = Governor()
    captured = {}

    class _Ledger:
        def log_event(self, *_args, **_kwargs):
            return "ledger-ref"

    governor._ledger = _Ledger()
    monkeypatch.setattr(governor._execute_boundary, "allow_execution", lambda: True)
    monkeypatch.setattr(governor._execute_boundary, "enter_execution", lambda: None)
    monkeypatch.setattr(governor._execute_boundary, "exit_execution", lambda: None)
    monkeypatch.setattr(governor._execute_boundary, "enforce_memory_limits", lambda: None)
    monkeypatch.setattr(governor._execute_boundary, "enforce_cpu_limits", lambda: None)
    monkeypatch.setattr(
        governor._execute_boundary,
        "run_with_timeout",
        lambda operation, timeout_seconds: operation(),
    )

    def dispatch(request):
        captured["params"] = request.params
        return ActionResult.ok("captured", request_id=request.request_id)

    monkeypatch.setattr(governor, "_dispatch_capability", dispatch)
    result = governor.handle_governed_invocation(
        49,
        {"headlines": [], "session_id": "caller-controlled"},
        session_id="trusted-session",
    )

    assert result.success is True
    assert captured["params"]["session_id"] == "trusted-session"


def test_missing_provenance_denies_before_network_attempt():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    attempts = []

    class _Network:
        def request(self, **kwargs):
            attempts.append(kwargs)
            raise AssertionError("missing provenance must not reach network")

    executor = NewsIntelligenceExecutor(_Network())
    result = executor.execute_summary(
        SimpleNamespace(
            capability_id=49,
            request_id="req-1",
            params={
                "action": "story_page_summary",
                "story_index": 1,
                "session_id": "session-1",
                "_nova_trusted_activity_origin": "user_action",
                "headlines": [
                    {
                        "title": "Headline",
                        "source": "Example",
                        "url": "https://news.example.com/story",
                    }
                ],
            },
        )
    )

    assert result.success is False
    assert result.data["failure_kind"] == "story_page_authorization_unavailable"
    assert attempts == []


def test_headline_summary_discloses_that_unadmitted_page_was_not_read(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(mod, "generate_chat", lambda *_args, **_kwargs: "Headline-level summary.")
    result = mod.NewsIntelligenceExecutor(network=object()).execute_summary(
        SimpleNamespace(
            capability_id=49,
            request_id="req-1",
            params={
                "indices": [1],
                "session_id": "session-1",
                "_nova_trusted_activity_origin": "user_action",
                "headlines": [
                    {
                        "title": "Headline",
                        "source": "Example",
                        "url": "https://news.example.com/story",
                    }
                ],
            },
        )
    )

    assert result.success is True
    assert "not read" in result.message
    assert "headline-level" in result.message
    assert result.data["widget"]["data"]["source_pages_read"] == 0
    assert result.data["widget"]["data"]["source_pages_denied"] == 1


def test_brief_distinguishes_authorization_denial_from_website_failure(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(mod, "generate_chat", lambda *_args, **_kwargs: "Top Headlines\n- Headline")
    params = {
        "headlines": [
            {
                "title": "Headline",
                "source": "Example",
                "url": "https://news.example.com/story",
            }
        ],
        "read_sources": True,
        "session_id": "session-1",
    }
    result = mod.NewsIntelligenceExecutor(network=object()).execute_brief(
        SimpleNamespace(capability_id=50, request_id="req-1", params=params)
    )

    assert result.success is True
    assert "authorization was unavailable" in result.message
    assert "source pages were unavailable" not in result.message


def test_trusted_story_read_disables_redirects_and_uses_classifier():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
    from src.services.news_source_provenance import news_source_provenance_registry

    news_source_provenance_registry.reset()
    token = news_source_provenance_registry.issue(
        url="https://news.example.com/story",
        provider="example_news",
        session_id="session-1",
        fetched_at=datetime.now(timezone.utc),
        ttl_seconds=180,
    )
    calls = []

    class _Network:
        def request(self, **kwargs):
            calls.append(kwargs)
            return {"text": "<article>Verified article text with enough detail.</article>"}

    executor = NewsIntelligenceExecutor(_Network())
    result = executor.execute_summary(
        SimpleNamespace(
            capability_id=49,
            request_id="req-1",
            params={
                "action": "story_page_summary",
                "story_index": 1,
                "session_id": "session-1",
                "_nova_trusted_activity_origin": "user_action",
                "headlines": [
                    {
                        "title": "Headline",
                        "source": "Example",
                        "url": "https://news.example.com/story",
                        "source_provenance": token,
                    }
                ],
            },
        )
    )

    assert result.success is True
    assert result.data["widget"]["data"]["source_read"] is True
    assert len(calls) == 1
    assert calls[0]["follow_redirects"] is False
    assert callable(calls[0]["disclosure_classifier"])


def test_default_news_source_denial_precedes_dns(monkeypatch):
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
    from src.governor.disclosure_policy import DisclosurePolicy
    from src.governor.network_mediator import NetworkMediator
    from src.services.news_source_provenance import news_source_provenance_registry

    attempts = {"dns": 0, "session": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("news source denial must precede DNS")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden_dns)
    monkeypatch.setattr(
        "src.governor.network_mediator.requests.Session",
        lambda: attempts.__setitem__("session", attempts["session"] + 1),
    )
    news_source_provenance_registry.reset()
    token = news_source_provenance_registry.issue(
        url="https://news.example.com/story",
        provider="example_news",
        session_id="session-1",
        fetched_at=datetime.now(timezone.utc),
        ttl_seconds=180,
    )
    mediator = NetworkMediator(
        disclosure_policy=DisclosurePolicy(version="news-source-test-v1"),
        disclosure_evidence_sink=None,
    )
    mediator._registry = type(
        "Registry",
        (),
        {"get": lambda _self, _capability_id: object(), "is_enabled": lambda _self, _capability_id: True},
    )()
    result = NewsIntelligenceExecutor(mediator).execute_summary(
        SimpleNamespace(
            capability_id=49,
            request_id="req-1",
            params={
                "action": "story_page_summary",
                "story_index": 1,
                "session_id": "session-1",
                "_nova_trusted_activity_origin": "user_action",
                "headlines": [
                    {
                        "title": "Headline",
                        "source": "Example",
                        "url": "https://news.example.com/story",
                        "source_provenance": token,
                    }
                ],
            },
        )
    )

    assert result.success is False
    assert result.data["failure_kind"] == "story_page_authorization_unavailable"
    assert attempts == {"dns": 0, "session": 0}


def test_news_source_redirect_stops_after_one_http_attempt():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor
    from src.governor.disclosure_policy import (
        DestinationClass,
        DisclosureGrant,
        DisclosurePolicy,
        TransportClass,
    )
    from src.governor.disclosure_transport import disclosure_facts
    from src.governor.network_mediator import NetworkMediator
    from src.services.news_source_provenance import news_source_provenance_registry

    url = "https://news.example.com/story"
    facts = disclosure_facts(
        transport=TransportClass.HTTP,
        method="GET",
        url=url,
        capability_id=49,
    )
    policy = DisclosurePolicy(
        version="news-source-test-v1",
        grants=(
            DisclosureGrant(
                provider="example_news",
                provider_class=ProviderClass.NEWS_SOURCE,
                destination_class=DestinationClass.EXTERNAL_WEB,
                destinations=frozenset({facts.destination}),
                effective_routes=frozenset({"direct"}),
                transports=frozenset({TransportClass.HTTP}),
                data_categories=frozenset({DataCategory.SOURCE_URL}),
                http_methods=frozenset({"GET"}),
                request_shapes=frozenset({facts.request_shape}),
                credential_categories=frozenset(),
                purposes=frozenset({"read_current_news_source"}),
                callers=frozenset({"news_source.capability_49"}),
                capability_ids=frozenset({49}),
                initiations=frozenset({InitiationClass.USER_INITIATED}),
            ),
        ),
    )

    class _Sink:
        def append(self, _record):
            return None

    mediator = NetworkMediator(disclosure_policy=policy, disclosure_evidence_sink=_Sink())
    mediator._registry = type(
        "Registry",
        (),
        {"get": lambda _self, _capability_id: object(), "is_enabled": lambda _self, _capability_id: True},
    )()
    mediator._validate_url = lambda _url: None
    attempts = []

    class _Redirect:
        status_code = 302
        content = b""
        text = ""
        is_redirect = True
        is_permanent_redirect = False
        headers = {"Location": url}

    class _Session:
        def request(self, **kwargs):
            attempts.append(kwargs)
            return _Redirect()

    mediator._new_session = _Session
    news_source_provenance_registry.reset()
    token = news_source_provenance_registry.issue(
        url=url,
        provider="example_news",
        session_id="session-1",
        fetched_at=datetime.now(timezone.utc),
        ttl_seconds=180,
    )
    result = NewsIntelligenceExecutor(mediator).execute_summary(
        SimpleNamespace(
            capability_id=49,
            request_id="req-1",
            params={
                "action": "story_page_summary",
                "story_index": 1,
                "session_id": "session-1",
                "_nova_trusted_activity_origin": "user_action",
                "headlines": [
                    {
                        "title": "Headline",
                        "source": "Example",
                        "url": url,
                        "source_provenance": token,
                    }
                ],
            },
        )
    )

    assert result.success is False
    assert result.data["failure_kind"] == "story_page_unavailable"
    assert len(attempts) == 1
