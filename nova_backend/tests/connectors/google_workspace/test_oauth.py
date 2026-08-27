from __future__ import annotations

import http.client
from datetime import datetime, timezone
from threading import Thread
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from src.connectors.google_workspace.oauth import (
    AUTHORIZATION_ENDPOINT,
    REVOCATION_ENDPOINT,
    TOKEN_ENDPOINT,
    USERINFO_ENDPOINT,
    GoogleIdentity,
    GoogleLoopbackCallbackReceiver,
    GoogleOAuthClientConfig,
    GoogleOAuthError,
    GoogleOAuthNetworkTransport,
    create_authorization_session,
)

NOW = datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc)


class _FakeMediator:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def connection_request(self, provider_id, operation, method, url, **kwargs):
        self.calls.append(
            {
                "provider_id": provider_id,
                "operation": operation,
                "method": method,
                "url": url,
                **kwargs,
            }
        )
        if operation == "fetch_identity":
            return {
                "status_code": 200,
                "data": {
                    "sub": "fake-subject",
                    "email": "fake.user@example.test",
                    "email_verified": True,
                },
            }
        if operation == "revoke":
            return {"status_code": 200, "text": ""}
        return {
            "status_code": 200,
            "data": {
                "access_token": "fake-access-token",
                "refresh_token": "fake-refresh-token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "openid email",
            },
        }


def test_authorization_request_uses_pkce_state_and_loopback_without_exposing_secrets():
    config = GoogleOAuthClientConfig(
        client_id="fake-client-id.apps.googleusercontent.com",
        client_secret="fake-client-secret",
    )
    session, request = create_authorization_session(
        config,
        profile_id="identity",
        scopes=("openid", "email"),
        redirect_uri="http://127.0.0.1:49152/oauth/callback",
        now=NOW,
    )
    parsed = urlsplit(request.authorization_url)
    query = parse_qs(parsed.query)
    safe = str(request.as_dict())

    assert request.authorization_url.startswith(AUTHORIZATION_ENDPOINT)
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"][0]
    assert query["state"][0] == session.state
    assert query["scope"] == ["email openid"]
    assert query["include_granted_scopes"] == ["false"]
    assert query["access_type"] == ["offline"]
    assert session.code_verifier not in request.authorization_url
    assert "fake-client-secret" not in request.authorization_url
    assert "fake-client-secret" not in repr(config)
    assert session.code_verifier not in safe
    assert session.state not in repr(request)
    assert "code_verifier" not in safe
    assert "client_secret" not in safe


@pytest.mark.parametrize(
    "redirect_uri",
    [
        "http://localhost:49152/oauth/callback",
        "http://user@127.0.0.1:49152/oauth/callback",
        "http://127.0.0.1:49152/oauth/callback?unexpected=1",
        "https://127.0.0.1:49152/oauth/callback",
    ],
)
def test_authorization_request_rejects_non_exact_loopback_redirects(redirect_uri):
    with pytest.raises(ValueError, match="127.0.0.1 loopback"):
        create_authorization_session(
            GoogleOAuthClientConfig("fake-client-id"),
            profile_id="identity",
            scopes=("openid", "email"),
            redirect_uri=redirect_uri,
            now=NOW,
        )


def test_oauth_transport_uses_only_auth_endpoints_and_preserves_actual_scopes():
    mediator = _FakeMediator()
    transport = GoogleOAuthNetworkTransport(mediator=mediator)
    config = GoogleOAuthClientConfig("fake-client-id", "fake-client-secret")
    session, _ = create_authorization_session(
        config,
        profile_id="identity",
        scopes=("openid", "email"),
        redirect_uri="http://127.0.0.1:49152/oauth/callback",
        now=NOW,
    )

    grant = transport.exchange_code(config, session, "fake-auth-code")
    refreshed = transport.refresh_token(config, "fake-refresh-token")
    identity = transport.fetch_identity("fake-access-token")
    transport.revoke_token("fake-refresh-token")

    assert grant.granted_scopes == ("email", "openid")
    assert refreshed.granted_scopes == ("email", "openid")
    assert identity.subject == "fake-subject"
    assert [call["url"] for call in mediator.calls] == [
        TOKEN_ENDPOINT,
        TOKEN_ENDPOINT,
        USERINFO_ENDPOINT,
        REVOCATION_ENDPOINT,
    ]


def test_code_exchange_uses_requested_scopes_when_google_omits_identical_scope():
    mediator = _FakeMediator()
    original_request = mediator.connection_request

    def request_without_scope(*args, **kwargs):
        response = original_request(*args, **kwargs)
        if args[1] == "exchange_code":
            response["data"].pop("scope")
        return response

    mediator.connection_request = request_without_scope
    transport = GoogleOAuthNetworkTransport(mediator=mediator)
    config = GoogleOAuthClientConfig("fake-client-id")
    session, _ = create_authorization_session(
        config,
        profile_id="identity",
        scopes=("openid", "email"),
        redirect_uri="http://127.0.0.1:49152/oauth/callback",
        now=NOW,
    )

    grant = transport.exchange_code(config, session, "fake-auth-code")

    assert grant.granted_scopes == ("email", "openid")


@pytest.mark.parametrize("email_verified", [False, None])
def test_identity_requires_explicit_positive_email_verification(email_verified):
    payload = {
        "sub": "fake-subject",
        "email": "fake.user@example.test",
    }
    if email_verified is not None:
        payload["email_verified"] = email_verified

    with pytest.raises(GoogleOAuthError, match="not verified"):
        GoogleIdentity.from_payload(payload)


def test_loopback_callback_ignores_invalid_state_then_accepts_legitimate_callback(capsys):
    receiver = GoogleLoopbackCallbackReceiver()
    parsed = urlsplit(receiver.redirect_uri)
    result: dict[str, object] = {}

    def wait() -> None:
        result["callback"] = receiver.wait_for_callback(
            expected_state="expected-state",
            timeout=3,
        )

    thread = Thread(target=wait)
    thread.start()

    invalid = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=3)
    invalid_query = urlencode({"state": "wrong-state", "code": "attacker-code"})
    invalid.request("GET", f"{parsed.path}?{invalid_query}")
    invalid_response = invalid.getresponse()
    invalid_body = invalid_response.read().decode("utf-8")
    invalid.close()

    valid = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=3)
    valid_query = urlencode(
        {"state": "expected-state", "code": "fake-auth-code"}
    )
    valid.request("GET", f"{parsed.path}?{valid_query}")
    valid_response = valid.getresponse()
    valid_body = valid_response.read().decode("utf-8")
    valid.close()
    thread.join(timeout=3)

    callback = result["callback"]
    assert invalid_response.status == 400
    assert valid_response.status == 200
    assert callback.state == "expected-state"
    assert callback.code == "fake-auth-code"
    for secret in ("attacker-code", "fake-auth-code", "expected-state"):
        assert secret not in invalid_body
        assert secret not in valid_body
        assert secret not in capsys.readouterr().out
