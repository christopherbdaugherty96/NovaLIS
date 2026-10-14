from __future__ import annotations

from types import SimpleNamespace

import pytest
import requests
from src.governor.exceptions import NetworkMediatorError
from src.governor.network_mediator import NetworkMediator


class _FakeRegistry:
    def get(self, capability_id: int):
        return SimpleNamespace(name=f"cap-{capability_id}")

    def is_enabled(self, capability_id: int) -> bool:
        return True


class _Ledger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


class _Response:
    def __init__(
        self,
        status_code: int,
        *,
        location: str | None = None,
        text: str = "ok",
    ) -> None:
        self.status_code = status_code
        self.is_redirect = status_code in {301, 302, 303, 307, 308}
        self.is_permanent_redirect = status_code in {301, 308}
        self.headers = {"Location": location} if location is not None else {}
        self.content = text.encode()
        self.text = text

    def raise_for_status(self) -> None:
        return None


def _mediator() -> NetworkMediator:
    mediator = NetworkMediator()
    mediator._registry = _FakeRegistry()
    mediator.ledger = _Ledger()
    mediator._validate_url = lambda _url: None
    return mediator


@pytest.mark.parametrize("status_code", [301, 302, 303, 307, 308])
@pytest.mark.parametrize(
    ("method", "params", "headers", "json_payload"),
    [
        ("GET", {"key": "query-secret"}, None, None),
        ("GET", None, {"X-Subscription-Token": "header-secret"}, None),
        (
            "POST",
            None,
            {"Authorization": "Bearer bearer-secret"},
            {"prompt": "distinctive prompt body"},
        ),
    ],
)
def test_network_mediator_rejects_cross_origin_redirect_before_second_request(
    monkeypatch,
    status_code,
    method,
    params,
    headers,
    json_payload,
):
    mediator = _mediator()
    attempts: list[dict] = []

    def _fake_request(**kwargs):
        attempts.append(kwargs)
        return _Response(status_code, location="https://blocked.example/collect")

    monkeypatch.setattr("src.governor.network_mediator.requests.request", _fake_request)

    with pytest.raises(NetworkMediatorError, match="cross-origin redirect"):
        mediator.request(
            16,
            method,
            "https://allowed.example/start",
            params=params,
            headers=headers,
            json_payload=json_payload,
            as_json=False,
        )

    assert len(attempts) == 1
    assert attempts[0]["url"] == "https://allowed.example/start"


@pytest.mark.parametrize(
    ("start_url", "location"),
    [
        ("https://example.com/start", "https://other.example/next"),
        ("https://example.com/start", "http://example.com/next"),
        ("https://example.com/start", "https://example.com:444/next"),
    ],
)
def test_network_mediator_rejects_redirect_origin_changes(
    monkeypatch, start_url, location
):
    mediator = _mediator()
    attempts = 0

    def _fake_request(**_kwargs):
        nonlocal attempts
        attempts += 1
        return _Response(302, location=location)

    monkeypatch.setattr("src.governor.network_mediator.requests.request", _fake_request)

    with pytest.raises(NetworkMediatorError, match="cross-origin redirect"):
        mediator.request(16, "GET", start_url, as_json=False)

    assert attempts == 1


@pytest.mark.parametrize(
    ("start_url", "location"),
    [
        ("https://example.com/start", "/next"),
        ("https://example.com/start", "https://EXAMPLE.com:443/next"),
        ("http://example.com:80/start", "http://example.com/next"),
    ],
)
def test_network_mediator_allows_same_origin_redirects(
    monkeypatch, start_url, location
):
    mediator = _mediator()
    attempts: list[str] = []

    def _fake_request(**kwargs):
        attempts.append(kwargs["url"])
        if len(attempts) == 1:
            return _Response(302, location=location)
        return _Response(200)

    monkeypatch.setattr("src.governor.network_mediator.requests.request", _fake_request)

    result = mediator.request(16, "GET", start_url, as_json=False)

    assert result == {"status_code": 200, "text": "ok"}
    assert len(attempts) == 2


def test_network_mediator_failure_never_persists_or_propagates_query_secret(
    monkeypatch,
):
    mediator = _mediator()
    secret = "fake-query-key-do-not-persist"
    url = f"https://weather.example/forecast?key={secret}"

    def _fail(**_kwargs):
        raise requests.RequestException(f"request failed for {url}")

    monkeypatch.setattr("src.governor.network_mediator.requests.request", _fail)

    with pytest.raises(NetworkMediatorError) as exc_info:
        mediator.request(16, "GET", url, as_json=False)

    assert secret not in str(exc_info.value)
    assert mediator.ledger.events
    assert all(secret not in repr(event) for event in mediator.ledger.events)
