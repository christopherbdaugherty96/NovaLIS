from __future__ import annotations

from typing import Any

import pytest
from src.governor.exceptions import NetworkMediatorError, ProviderConnectionNetworkError
from src.governor.network_mediator import (
    CONNECTION_OPERATION_ENDPOINTS,
    NetworkMediator,
)


class _FailIfUsedRegistry:
    def get(self, capability_id: int):
        raise AssertionError("Google connection must not consult capability registry.")

    def is_enabled(self, capability_id: int) -> bool:
        raise AssertionError("Google connection must not consult capability registry.")


class _RecordingLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append((event_type, payload))


class _Response:
    status_code = 200
    is_redirect = False
    is_permanent_redirect = False
    content = b'{"access_token":"not-returned-to-ledger"}'
    text = ""

    def json(self) -> dict[str, str]:
        return {"access_token": "not-returned-to-ledger"}


def test_allowlisted_connection_request_uses_no_capability_or_governor(monkeypatch):
    mediator = NetworkMediator()
    mediator._registry = _FailIfUsedRegistry()
    ledger = _RecordingLedger()
    mediator.ledger = ledger
    captured: dict[str, Any] = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return _Response()

    monkeypatch.setattr("src.governor.network_mediator.requests.request", fake_request)
    result = mediator.connection_request(
        "google_workspace",
        "exchange_code",
        "POST",
        "https://oauth2.googleapis.com/token",
        form_payload={
            "authorization_code": "test-authorization-code",
            "refresh_token": "test-refresh-token",
            "client_secret": "test-client-secret",
        },
    )

    assert result["status_code"] == 200
    assert captured["allow_redirects"] is False
    assert ledger.events[-1][0] == "CONNECTION_NETWORK_CALL"
    rendered_ledger = str(ledger.events)
    for secret in (
        "test-authorization-code",
        "test-refresh-token",
        "test-client-secret",
        "not-returned-to-ledger",
    ):
        assert secret not in rendered_ledger


@pytest.mark.parametrize(
    ("operation", "method", "url"),
    [
        ("exchange_code", "GET", "https://oauth2.googleapis.com/token"),
        ("tasks", "GET", "https://tasks.googleapis.com/tasks/v1/users/@me/lists"),
        ("gmail", "GET", "https://gmail.googleapis.com/gmail/v1/users/me/messages"),
        ("calendar", "GET", "https://www.googleapis.com/calendar/v3/calendars"),
        ("drive", "GET", "https://www.googleapis.com/drive/v3/files"),
    ],
)
def test_connection_network_allowlist_rejects_methods_and_domain_endpoints(
    operation,
    method,
    url,
):
    mediator = NetworkMediator()
    with pytest.raises(NetworkMediatorError, match="not allowlisted"):
        mediator.connection_request(
            "google_workspace",
            operation,
            method,
            url,
        )


def test_google_connection_endpoint_policy_contains_auth_metadata_only():
    endpoints = CONNECTION_OPERATION_ENDPOINTS["google_workspace"]
    rendered = str(endpoints).lower()

    assert set(endpoints) == {
        "exchange_code",
        "refresh_token",
        "fetch_identity",
        "revoke",
    }
    for forbidden in ("tasks", "gmail", "calendar", "drive", "docs", "sheets"):
        assert forbidden not in rendered


def test_connection_error_exposes_only_safe_oauth_code(monkeypatch):
    mediator = NetworkMediator()
    ledger = _RecordingLedger()
    mediator.ledger = ledger

    class ErrorResponse(_Response):
        status_code = 400
        content = b'{"error":"invalid_grant","error_description":"fake-refresh-token"}'

        def json(self):
            return {
                "error": "invalid_grant",
                "error_description": "fake-refresh-token",
            }

    monkeypatch.setattr(
        "src.governor.network_mediator.requests.request",
        lambda **kwargs: ErrorResponse(),
    )

    with pytest.raises(ProviderConnectionNetworkError) as captured:
        mediator.connection_request(
            "google_workspace",
            "refresh_token",
            "POST",
            "https://oauth2.googleapis.com/token",
            form_payload={"refresh_token": "fake-refresh-token"},
        )

    assert captured.value.error_code == "invalid_grant"
    assert captured.value.status_code == 400
    assert "fake-refresh-token" not in str(captured.value)
    assert "fake-refresh-token" not in str(ledger.events)


def test_connection_request_rejects_redirect_without_following_it(monkeypatch):
    mediator = NetworkMediator()
    ledger = _RecordingLedger()
    mediator.ledger = ledger

    class RedirectResponse(_Response):
        status_code = 302
        is_redirect = True

    monkeypatch.setattr(
        "src.governor.network_mediator.requests.request",
        lambda **kwargs: RedirectResponse(),
    )

    with pytest.raises(NetworkMediatorError, match="redirects are not allowed"):
        mediator.connection_request(
            "google_workspace",
            "fetch_identity",
            "GET",
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": "Bearer fake-access-token"},
        )

    assert "fake-access-token" not in str(ledger.events)
