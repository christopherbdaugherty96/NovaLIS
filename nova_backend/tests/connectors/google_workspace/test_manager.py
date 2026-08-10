from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from src.connectors.google_workspace.manager import (
    GoogleReconnectRequired,
    GoogleWorkspaceConnectionManager,
    GoogleWorkspaceFoundationError,
)
from src.connectors.google_workspace.models import (
    GoogleConnectionState,
    GoogleGrantProfile,
    GoogleGrantProfileCatalog,
)
from src.connectors.google_workspace.oauth import (
    GoogleIdentity,
    GoogleOAuthCallback,
    GoogleOAuthClientConfig,
    GoogleOAuthProtocolError,
    GoogleTokenGrant,
)

NOW = datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc)


class _FakeVault:
    def __init__(self) -> None:
        self.credential = None

    def load(self):
        return self.credential

    def save(self, credential) -> None:
        self.credential = credential


class _FakeReceiver:
    redirect_uri = "http://127.0.0.1:49152/oauth/callback"

    def __init__(self) -> None:
        self.state = ""
        self.code = "fake-authorization-code"
        self.error = ""
        self.closed = False

    def wait_for_callback(self, *, timeout=180):
        return GoogleOAuthCallback(state=self.state, code=self.code, error=self.error)

    def close(self) -> None:
        self.closed = True


class _ReceiverFactory:
    def __init__(self) -> None:
        self.instances: list[_FakeReceiver] = []

    def __call__(self):
        receiver = _FakeReceiver()
        self.instances.append(receiver)
        return receiver


class _FakeTransport:
    def __init__(self) -> None:
        self.exchange_grant = GoogleTokenGrant(
            access_token="fake-access-token",
            refresh_token="fake-refresh-token",
            granted_scopes=("openid", "email"),
            expires_in_seconds=3600,
        )
        self.refresh_grant = GoogleTokenGrant(
            access_token="fake-refreshed-access-token",
            granted_scopes=("openid", "email"),
            expires_in_seconds=3600,
        )
        self.identity = GoogleIdentity(
            subject="fake-google-subject",
            email="fake.user@example.test",
        )
        self.fail_refresh = False
        self.revoked_refresh = False
        self.calls: list[str] = []

    def exchange_code(self, config, session, authorization_code):
        self.calls.append("exchange_code")
        return self.exchange_grant

    def refresh_token(self, config, refresh_token):
        self.calls.append("refresh_token")
        if self.fail_refresh:
            raise RuntimeError("fake refresh failure with fake-refresh-token")
        if self.revoked_refresh:
            raise GoogleOAuthProtocolError("invalid_grant")
        return self.refresh_grant

    def fetch_identity(self, access_token):
        self.calls.append("fetch_identity")
        return self.identity

    def revoke_token(self, token):
        self.calls.append("revoke_token")


def _manager(*, profiles=None):
    current = [NOW]
    vault = _FakeVault()
    transport = _FakeTransport()
    receivers = _ReceiverFactory()
    manager = GoogleWorkspaceConnectionManager(
        config=GoogleOAuthClientConfig("fake-client-id", "fake-client-secret"),
        vault=vault,
        transport=transport,
        profiles=profiles,
        receiver_factory=receivers,
        clock=lambda: current[0],
    )
    return manager, vault, transport, receivers, current


def _complete(manager, receivers, request):
    session, _ = manager._sessions[request.session_id]
    receivers.instances[-1].state = session.state
    return manager.complete_connection(request.session_id)


def test_connection_lifecycle_captures_identity_scopes_and_safe_status():
    manager, vault, transport, receivers, _ = _manager()

    assert manager.status().state is GoogleConnectionState.NOT_CONNECTED
    request = manager.begin_connection()
    assert manager.status().state is GoogleConnectionState.CONNECTING
    status = _complete(manager, receivers, request)
    safe = status.as_dict()

    assert status.state is GoogleConnectionState.CONNECTED
    assert status.credential_valid is True
    assert status.account is not None
    assert status.account.source_identity.canonical == "google:workspace"
    assert safe["account_hint"] == "fa***@example.test"
    assert safe["scope_inventory"]["granted"] == ["email", "openid"]
    assert safe["scope_inventory"]["sufficient"] is True
    assert transport.calls == ["exchange_code", "fetch_identity"]
    assert vault.credential.access_token == "fake-access-token"
    rendered = str(safe)
    for secret in (
        "fake-access-token",
        "fake-refresh-token",
        "fake-client-secret",
        "fake-authorization-code",
    ):
        assert secret not in rendered


def test_expiration_is_detected_without_automatic_network_activity():
    manager, _, transport, receivers, current = _manager()
    request = manager.begin_connection()
    _complete(manager, receivers, request)
    transport.calls.clear()

    current[0] = NOW + timedelta(hours=2)
    status = manager.status()

    assert status.state is GoogleConnectionState.EXPIRED
    assert status.credential_valid is False
    assert transport.calls == []


def test_expired_connection_session_is_closed_and_no_longer_connecting():
    manager, _, _, receivers, current = _manager()
    manager.begin_connection()
    receiver = receivers.instances[-1]

    current[0] = NOW + timedelta(minutes=11)
    status = manager.status()

    assert status.state is GoogleConnectionState.NOT_CONNECTED
    assert receiver.closed is True


def test_new_connection_replaces_prior_pending_session():
    manager, _, _, receivers, _ = _manager()
    first = manager.begin_connection()
    first_receiver = receivers.instances[-1]

    second = manager.begin_connection()

    assert first.session_id not in manager._sessions
    assert second.session_id in manager._sessions
    assert first_receiver.closed is True


def test_refresh_success_preserves_refresh_token_and_records_timestamp():
    manager, vault, transport, receivers, current = _manager()
    request = manager.begin_connection()
    _complete(manager, receivers, request)
    current[0] = NOW + timedelta(minutes=30)

    status = manager.refresh()

    assert status.state is GoogleConnectionState.CONNECTED
    assert status.last_successful_refresh_at == current[0]
    assert vault.credential.access_token == "fake-refreshed-access-token"
    assert vault.credential.refresh_token == "fake-refresh-token"


def test_refresh_failure_is_safe_and_does_not_log_tokens(caplog):
    manager, vault, transport, receivers, _ = _manager()
    request = manager.begin_connection()
    _complete(manager, receivers, request)
    transport.fail_refresh = True

    status = manager.refresh()

    assert status.state is GoogleConnectionState.REFRESH_FAILED
    assert status.safe_reason == "refresh_failed"
    assert vault.credential.refresh_token == "fake-refresh-token"
    assert "fake-refresh-token" not in caplog.text


def test_refresh_invalid_grant_marks_revoked_and_clears_tokens():
    manager, vault, transport, receivers, _ = _manager()
    request = manager.begin_connection()
    _complete(manager, receivers, request)
    transport.revoked_refresh = True

    status = manager.refresh()

    assert status.state is GoogleConnectionState.REVOKED
    assert vault.credential.access_token == ""
    assert vault.credential.refresh_token == ""


def test_revoke_clears_tokens_and_disconnect_is_local_only():
    manager, vault, transport, receivers, _ = _manager()
    request = manager.begin_connection()
    _complete(manager, receivers, request)

    revoked = manager.revoke()
    assert revoked.state is GoogleConnectionState.REVOKED
    assert vault.credential.access_token == ""
    assert vault.credential.refresh_token == ""
    assert transport.calls[-1] == "revoke_token"

    calls_before_disconnect = list(transport.calls)
    disconnected = manager.disconnect()
    assert disconnected.state is GoogleConnectionState.DISCONNECTED
    assert transport.calls == calls_before_disconnect


def test_revoke_closes_pending_connection_session():
    manager, _, _, receivers, _ = _manager()
    manager.begin_connection()
    receiver = receivers.instances[-1]

    status = manager.revoke()

    assert status.state is GoogleConnectionState.NOT_CONNECTED
    assert receiver.closed is True


@pytest.mark.parametrize(
    "terminal_state",
    [GoogleConnectionState.REVOKED, GoogleConnectionState.DISCONNECTED],
)
def test_terminal_token_free_state_allows_a_new_connection(terminal_state):
    manager, _, _, receivers, _ = _manager()
    _complete(manager, receivers, manager.begin_connection())
    if terminal_state is GoogleConnectionState.REVOKED:
        manager.revoke()
    else:
        manager.disconnect()

    request = manager.begin_connection()

    assert request.profile_id == "identity"
    assert manager.status().state is GoogleConnectionState.CONNECTING


def test_insufficient_grant_is_recorded_exactly_and_skips_identity_lookup():
    manager, vault, transport, receivers, _ = _manager()
    transport.exchange_grant = GoogleTokenGrant(
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
        granted_scopes=("openid",),
        expires_in_seconds=3600,
    )

    status = _complete(manager, receivers, manager.begin_connection())

    assert status.state is GoogleConnectionState.SCOPE_INSUFFICIENT
    assert status.scope_inventory.granted == ("openid",)
    assert status.scope_inventory.missing == ("email",)
    assert "fetch_identity" not in transport.calls
    assert vault.credential.granted_scopes == ("openid",)


def test_scope_expansion_requires_explicit_reconnect():
    profiles = GoogleGrantProfileCatalog(
        (
            GoogleGrantProfile("identity", "Identity", ("openid", "email")),
            GoogleGrantProfile(
                "expanded_test_profile",
                "Expanded test profile",
                ("openid", "email", "example.test.scope"),
            ),
        )
    )
    manager, _, transport, receivers, _ = _manager(profiles=profiles)
    _complete(manager, receivers, manager.begin_connection())

    with pytest.raises(GoogleReconnectRequired, match="explicit reconnect"):
        manager.begin_connection(profile_id="expanded_test_profile")

    request = manager.begin_connection(
        profile_id="expanded_test_profile",
        reconnect=True,
    )
    assert request.profile_id == "expanded_test_profile"
    assert "example.test.scope" in request.requested_scopes
    assert transport.calls == ["exchange_code", "fetch_identity"]


def test_callback_state_mismatch_fails_before_token_exchange():
    manager, _, transport, receivers, _ = _manager()
    request = manager.begin_connection()
    receivers.instances[-1].state = "wrong-state"

    with pytest.raises(GoogleWorkspaceFoundationError, match="state validation failed"):
        manager.complete_connection(request.session_id)

    assert transport.calls == []
