from __future__ import annotations

import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from src.connectors.google_workspace.credential_vault import (
    EncryptedGoogleCredentialVault,
)
from src.connectors.google_workspace.models import (
    FOUNDATION_PROFILE_ID,
    GoogleConnectionState,
    GoogleConnectionStatus,
    GoogleGrantProfileCatalog,
    GoogleScopeInventory,
    GoogleStoredCredential,
    GoogleWorkspaceAccount,
)
from src.connectors.google_workspace.oauth import (
    GoogleAuthorizationRequest,
    GoogleAuthSession,
    GoogleLoopbackCallbackReceiver,
    GoogleOAuthClientConfig,
    GoogleOAuthNetworkTransport,
    GoogleOAuthProtocolError,
    GoogleOAuthTransport,
    GoogleTokenGrant,
    create_authorization_session,
)


class GoogleWorkspaceFoundationError(RuntimeError):
    pass


class GoogleReconnectRequired(GoogleWorkspaceFoundationError):
    pass


class GoogleWorkspaceConnectionManager:
    """Single-account Google connection lifecycle with no domain-data access."""

    def __init__(
        self,
        *,
        config: GoogleOAuthClientConfig,
        vault: EncryptedGoogleCredentialVault,
        transport: GoogleOAuthTransport | None = None,
        profiles: GoogleGrantProfileCatalog | None = None,
        receiver_factory: Callable[[], GoogleLoopbackCallbackReceiver] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config
        self._vault = vault
        self._transport = transport or GoogleOAuthNetworkTransport()
        self._profiles = profiles or GoogleGrantProfileCatalog()
        self._receiver_factory = receiver_factory or GoogleLoopbackCallbackReceiver
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._sessions: dict[
            str,
            tuple[GoogleAuthSession, GoogleLoopbackCallbackReceiver],
        ] = {}

    @classmethod
    def from_environment(cls) -> GoogleWorkspaceConnectionManager:
        return cls(
            config=GoogleOAuthClientConfig.from_environment(),
            vault=EncryptedGoogleCredentialVault(),
        )

    def begin_connection(
        self,
        *,
        profile_id: str = FOUNDATION_PROFILE_ID,
        reconnect: bool = False,
    ) -> GoogleAuthorizationRequest:
        profile = self._profiles.get_enabled(profile_id)
        existing = self._vault.load()
        if existing is not None and existing.state not in {
            GoogleConnectionState.REVOKED,
            GoogleConnectionState.DISCONNECTED,
        }:
            missing = set(profile.scopes).difference(existing.granted_scopes)
            if missing and not reconnect:
                raise GoogleReconnectRequired(
                    "Google scope expansion requires explicit reconnect."
                )

        self._close_sessions()
        receiver = self._receiver_factory()
        try:
            session, request = create_authorization_session(
                self._config,
                profile_id=profile.profile_id,
                scopes=profile.scopes,
                redirect_uri=receiver.redirect_uri,
                now=self._now(),
            )
        except Exception:
            receiver.close()
            raise
        self._sessions[session.session_id] = (session, receiver)
        return request

    def complete_connection(
        self,
        session_id: str,
        *,
        timeout: float = 180,
    ) -> GoogleConnectionStatus:
        key = str(session_id or "")
        entry = self._sessions.get(key)
        if entry is None:
            raise GoogleWorkspaceFoundationError("Google connection session is unavailable.")
        session, receiver = entry
        if self._now() >= session.expires_at:
            self._remove_session(key)
            raise GoogleWorkspaceFoundationError("Google connection session expired.")

        try:
            callback = receiver.wait_for_callback(
                expected_state=session.state,
                timeout=timeout,
            )
        except Exception:
            self._remove_session(key)
            raise GoogleWorkspaceFoundationError(
                "Google authorization callback failed or timed out."
            ) from None

        if not secrets.compare_digest(callback.state, session.state):
            # Defense in depth for alternate receiver implementations: an invalid
            # callback does not consume the still-legitimate authorization session.
            raise GoogleWorkspaceFoundationError(
                "Google authorization state validation failed."
            )
        if not callback.code and not callback.error:
            raise GoogleWorkspaceFoundationError(
                "Google authorization callback was incomplete."
            )

        self._remove_session(key)
        if callback.error:
            raise GoogleWorkspaceFoundationError("Google authorization was not granted.")

        try:
            grant = self._transport.exchange_code(
                self._config,
                session,
                callback.code,
            )
        except Exception:
            raise GoogleWorkspaceFoundationError("Google token exchange failed.") from None

        inventory = GoogleScopeInventory(session.requested_scopes, grant.granted_scopes)
        expiry = self._now() + timedelta(seconds=grant.expires_in_seconds)
        if not inventory.sufficient:
            self._save_scope_insufficient(
                grant=grant,
                profile_id=session.profile_id,
                inventory=inventory,
            )
            return self.status()

        try:
            identity = self._transport.fetch_identity(grant.access_token)
        except Exception:
            revoked = self._best_effort_revoke(grant)
            self._vault.save(
                GoogleStoredCredential(
                    state=(
                        GoogleConnectionState.REVOKED
                        if revoked
                        else GoogleConnectionState.DISCONNECTED
                    ),
                    grant_profile_id=session.profile_id,
                    requested_scopes=inventory.requested,
                    granted_scopes=inventory.granted,
                    safe_reason=(
                        "identity_lookup_failed_credentials_revoked"
                        if revoked
                        else "identity_lookup_failed_credentials_discarded_revocation_unverified"
                    ),
                )
            )
            raise GoogleWorkspaceFoundationError(
                "Google account identity lookup failed."
            ) from None

        credential = GoogleStoredCredential(
            state=GoogleConnectionState.CONNECTED,
            grant_profile_id=session.profile_id,
            requested_scopes=inventory.requested,
            granted_scopes=inventory.granted,
            access_token=grant.access_token,
            refresh_token=grant.refresh_token,
            token_type=grant.token_type,
            expires_at=expiry,
            account=GoogleWorkspaceAccount(subject=identity.subject, email=identity.email),
        )
        self._vault.save(credential)
        return self.status()

    def refresh(self) -> GoogleConnectionStatus:
        credential = self._vault.load()
        if credential is None or not credential.refresh_token:
            raise GoogleReconnectRequired("Google reconnect is required before refresh.")
        try:
            grant = self._transport.refresh_token(
                self._config,
                credential.refresh_token,
            )
        except GoogleOAuthProtocolError as error:
            if error.error_code in {"invalid_grant", "invalid_token"}:
                self._vault.save(
                    GoogleStoredCredential(
                        state=GoogleConnectionState.DISCONNECTED,
                        grant_profile_id=credential.grant_profile_id,
                        requested_scopes=credential.requested_scopes,
                        granted_scopes=(),
                        safe_reason=(
                            "refresh_credential_expired_or_invalidated_"
                            "reconnect_required"
                        ),
                    )
                )
                return self.status()
            self._save_refresh_failed(credential)
            return self.status()
        except Exception:
            self._save_refresh_failed(credential)
            return self.status()

        granted_scopes = grant.granted_scopes or credential.granted_scopes
        inventory = GoogleScopeInventory(credential.requested_scopes, granted_scopes)
        refreshed_at = self._now()
        if not inventory.sufficient:
            refresh_grant = GoogleTokenGrant(
                access_token=grant.access_token,
                refresh_token=grant.refresh_token or credential.refresh_token,
                token_type=grant.token_type,
                granted_scopes=inventory.granted,
                expires_in_seconds=grant.expires_in_seconds,
            )
            self._save_scope_insufficient(
                grant=refresh_grant,
                profile_id=credential.grant_profile_id,
                inventory=inventory,
                account=credential.account,
            )
            return self.status()

        self._vault.save(
            GoogleStoredCredential(
                state=GoogleConnectionState.CONNECTED,
                grant_profile_id=credential.grant_profile_id,
                requested_scopes=inventory.requested,
                granted_scopes=inventory.granted,
                access_token=grant.access_token,
                refresh_token=grant.refresh_token or credential.refresh_token,
                token_type=grant.token_type,
                expires_at=refreshed_at + timedelta(seconds=grant.expires_in_seconds),
                last_successful_refresh_at=refreshed_at,
                account=credential.account,
            )
        )
        return self.status()

    def _save_refresh_failed(self, credential: GoogleStoredCredential) -> None:
        self._vault.save(
            GoogleStoredCredential(
                state=GoogleConnectionState.REFRESH_FAILED,
                grant_profile_id=credential.grant_profile_id,
                requested_scopes=credential.requested_scopes,
                granted_scopes=credential.granted_scopes,
                access_token=credential.access_token,
                refresh_token=credential.refresh_token,
                token_type=credential.token_type,
                expires_at=credential.expires_at,
                last_successful_refresh_at=credential.last_successful_refresh_at,
                account=credential.account,
                safe_reason="refresh_failed",
            )
        )

    def revoke(self) -> GoogleConnectionStatus:
        self._close_sessions()
        credential = self._vault.load()
        if credential is None:
            return self.status()
        token = credential.refresh_token or credential.access_token
        if token:
            try:
                self._transport.revoke_token(token)
            except Exception:
                raise GoogleWorkspaceFoundationError("Google revocation failed.") from None
        elif credential.state is GoogleConnectionState.REVOKED:
            return self.status()
        elif not credential.safe_reason.endswith("credentials_revoked"):
            raise GoogleWorkspaceFoundationError(
                "Google revocation cannot be verified without a retained credential."
            )
        self._vault.save(self._tombstone(GoogleConnectionState.REVOKED))
        return self.status()

    def disconnect(self) -> GoogleConnectionStatus:
        self._close_sessions()
        self._vault.save(self._tombstone(GoogleConnectionState.DISCONNECTED))
        return self.status()

    def status(self) -> GoogleConnectionStatus:
        self._prune_expired_sessions()
        if self._sessions:
            return GoogleConnectionStatus(state=GoogleConnectionState.CONNECTING)
        credential = self._vault.load()
        if credential is None:
            return GoogleConnectionStatus(state=GoogleConnectionState.NOT_CONNECTED)

        state = credential.state
        now = self._now()
        if (
            state is GoogleConnectionState.CONNECTED
            and credential.expires_at is not None
            and now >= credential.expires_at
        ):
            state = GoogleConnectionState.EXPIRED
        inventory = credential.scope_inventory
        if state is GoogleConnectionState.CONNECTED and not inventory.sufficient:
            state = GoogleConnectionState.SCOPE_INSUFFICIENT
        credential_valid = bool(
            state is GoogleConnectionState.CONNECTED
            and credential.access_token
            and credential.expires_at is not None
            and now < credential.expires_at
        )
        return GoogleConnectionStatus(
            state=state,
            grant_profile_id=credential.grant_profile_id,
            scope_inventory=inventory,
            account=credential.account,
            expires_at=credential.expires_at,
            last_successful_refresh_at=credential.last_successful_refresh_at,
            credential_valid=credential_valid,
            safe_reason=credential.safe_reason,
        )

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Google connection clock must be timezone-aware.")
        return value.astimezone(timezone.utc)

    def _close_sessions(self) -> None:
        sessions = tuple(self._sessions.values())
        self._sessions.clear()
        for _, receiver in sessions:
            receiver.close()

    def _remove_session(self, session_id: str) -> None:
        entry = self._sessions.pop(session_id, None)
        if entry is not None:
            _, receiver = entry
            receiver.close()

    def _prune_expired_sessions(self) -> None:
        now = self._now()
        expired = tuple(
            session_id
            for session_id, (session, _) in self._sessions.items()
            if now >= session.expires_at
        )
        for session_id in expired:
            self._remove_session(session_id)

    def _save_scope_insufficient(
        self,
        *,
        grant: GoogleTokenGrant,
        profile_id: str,
        inventory: GoogleScopeInventory,
        account: GoogleWorkspaceAccount | None = None,
    ) -> None:
        revoked = self._best_effort_revoke(grant)
        self._vault.save(
            GoogleStoredCredential(
                state=GoogleConnectionState.SCOPE_INSUFFICIENT,
                grant_profile_id=profile_id,
                requested_scopes=inventory.requested,
                granted_scopes=inventory.granted,
                account=account,
                safe_reason=(
                    "required_scopes_not_granted_credentials_revoked"
                    if revoked
                    else "required_scopes_not_granted_credentials_discarded_revocation_unverified"
                ),
            )
        )

    def _best_effort_revoke(self, grant: GoogleTokenGrant) -> bool:
        token = grant.refresh_token or grant.access_token
        if not token:
            return False
        try:
            self._transport.revoke_token(token)
        except Exception:
            return False
        return True

    @staticmethod
    def _tombstone(state: GoogleConnectionState) -> GoogleStoredCredential:
        return GoogleStoredCredential(
            state=state,
            grant_profile_id=FOUNDATION_PROFILE_ID,
            requested_scopes=(),
            granted_scopes=(),
        )
