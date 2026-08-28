from __future__ import annotations

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import monotonic
from typing import Any, Mapping, Protocol
from urllib.parse import parse_qs, urlencode, urlsplit
from uuid import uuid4

from src.governor.exceptions import ProviderConnectionNetworkError
from src.governor.network_mediator import NetworkMediator

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
REVOCATION_ENDPOINT = "https://oauth2.googleapis.com/revoke"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuthError(RuntimeError):
    pass


class GoogleOAuthProtocolError(GoogleOAuthError):
    def __init__(self, error_code: str) -> None:
        self.error_code = str(error_code or "oauth_error")
        super().__init__(f"Google OAuth request failed ({self.error_code}).")


@dataclass(frozen=True)
class GoogleOAuthClientConfig:
    client_id: str
    client_secret: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        client_id = str(self.client_id or "").strip()
        if not client_id:
            raise ValueError("Google OAuth client id is required.")
        object.__setattr__(self, "client_id", client_id)
        object.__setattr__(self, "client_secret", str(self.client_secret or "").strip())

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> GoogleOAuthClientConfig:
        source = environ if environ is not None else os.environ
        return cls(
            client_id=str(source.get("NOVA_GOOGLE_OAUTH_CLIENT_ID") or ""),
            client_secret=str(source.get("NOVA_GOOGLE_OAUTH_CLIENT_SECRET") or ""),
        )


@dataclass(frozen=True)
class GoogleTokenGrant:
    access_token: str = field(repr=False)
    refresh_token: str = field(default="", repr=False)
    token_type: str = field(default="Bearer", repr=False)
    granted_scopes: tuple[str, ...] = ()
    expires_in_seconds: int = 0

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> GoogleTokenGrant:
        access_token = str(payload.get("access_token") or "")
        if not access_token:
            raise GoogleOAuthError("Google did not return an access token.")
        raw_scope = payload.get("scope") or ""
        scopes = tuple(sorted({scope for scope in str(raw_scope).split() if scope}))
        try:
            expires_in = max(0, int(payload.get("expires_in") or 0))
        except (TypeError, ValueError):
            expires_in = 0
        return cls(
            access_token=access_token,
            refresh_token=str(payload.get("refresh_token") or ""),
            token_type=str(payload.get("token_type") or "Bearer"),
            granted_scopes=scopes,
            expires_in_seconds=expires_in,
        )


@dataclass(frozen=True)
class GoogleIdentity:
    subject: str = field(repr=False)
    email: str = field(repr=False)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> GoogleIdentity:
        subject = str(payload.get("sub") or "")
        email = str(payload.get("email") or "")
        if not subject or "@" not in email:
            raise GoogleOAuthError("Google account identity was incomplete.")
        if payload.get("email_verified") is not True:
            raise GoogleOAuthError("Google account email was not verified.")
        return cls(subject=subject, email=email)


@dataclass(frozen=True)
class GoogleAuthSession:
    session_id: str
    profile_id: str
    requested_scopes: tuple[str, ...]
    redirect_uri: str
    state: str = field(repr=False)
    code_verifier: str = field(repr=False)
    created_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class GoogleAuthorizationRequest:
    session_id: str
    profile_id: str
    requested_scopes: tuple[str, ...]
    authorization_url: str = field(repr=False)
    expires_at: datetime

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": "google_workspace",
            "session_id": self.session_id,
            "grant_profile": self.profile_id,
            "requested_scopes": list(self.requested_scopes),
            "authorization_url": self.authorization_url,
            "expires_at": self.expires_at.isoformat(),
        }


@dataclass(frozen=True)
class GoogleOAuthCallback:
    state: str = field(repr=False)
    code: str = field(default="", repr=False)
    error: str = field(default="", repr=False)


class GoogleOAuthTransport(Protocol):
    def exchange_code(
        self,
        config: GoogleOAuthClientConfig,
        session: GoogleAuthSession,
        authorization_code: str,
    ) -> GoogleTokenGrant: ...

    def refresh_token(
        self,
        config: GoogleOAuthClientConfig,
        refresh_token: str,
    ) -> GoogleTokenGrant: ...

    def fetch_identity(self, access_token: str) -> GoogleIdentity: ...

    def revoke_token(self, token: str) -> None: ...


class GoogleOAuthNetworkTransport:
    """Google auth-only HTTP over NetworkMediator's connection allowlist."""

    def __init__(self, mediator: NetworkMediator | None = None) -> None:
        self._mediator = mediator or NetworkMediator()

    def exchange_code(
        self,
        config: GoogleOAuthClientConfig,
        session: GoogleAuthSession,
        authorization_code: str,
    ) -> GoogleTokenGrant:
        payload = {
            "client_id": config.client_id,
            "code": authorization_code,
            "code_verifier": session.code_verifier,
            "grant_type": "authorization_code",
            "redirect_uri": session.redirect_uri,
        }
        if config.client_secret:
            payload["client_secret"] = config.client_secret
        try:
            response = self._mediator.connection_request(
                "google_workspace",
                "exchange_code",
                "POST",
                TOKEN_ENDPOINT,
                form_payload=payload,
                timeout=10,
            )
        except ProviderConnectionNetworkError as error:
            raise GoogleOAuthProtocolError(error.error_code) from None
        data = response.get("data")
        if not isinstance(data, Mapping):
            raise GoogleOAuthError("Google token exchange returned no usable result.")
        grant = GoogleTokenGrant.from_payload(data)
        if "scope" not in data:
            grant = replace(grant, granted_scopes=session.requested_scopes)
        return grant

    def refresh_token(
        self,
        config: GoogleOAuthClientConfig,
        refresh_token: str,
    ) -> GoogleTokenGrant:
        payload = {
            "client_id": config.client_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        if config.client_secret:
            payload["client_secret"] = config.client_secret
        try:
            response = self._mediator.connection_request(
                "google_workspace",
                "refresh_token",
                "POST",
                TOKEN_ENDPOINT,
                form_payload=payload,
                timeout=10,
            )
        except ProviderConnectionNetworkError as error:
            raise GoogleOAuthProtocolError(error.error_code) from None
        data = response.get("data")
        if not isinstance(data, Mapping):
            raise GoogleOAuthError("Google token refresh returned no usable result.")
        return GoogleTokenGrant.from_payload(data)

    def fetch_identity(self, access_token: str) -> GoogleIdentity:
        response = self._mediator.connection_request(
            "google_workspace",
            "fetch_identity",
            "GET",
            USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        data = response.get("data")
        if not isinstance(data, Mapping):
            raise GoogleOAuthError("Google account identity was unavailable.")
        return GoogleIdentity.from_payload(data)

    def revoke_token(self, token: str) -> None:
        try:
            response = self._mediator.connection_request(
                "google_workspace",
                "revoke",
                "POST",
                REVOCATION_ENDPOINT,
                form_payload={"token": token},
                as_json=False,
                timeout=10,
            )
        except ProviderConnectionNetworkError as error:
            raise GoogleOAuthProtocolError(error.error_code) from None
        if response.get("status_code") != 200:
            raise GoogleOAuthProtocolError("unexpected_revocation_status")


def create_authorization_session(
    config: GoogleOAuthClientConfig,
    *,
    profile_id: str,
    scopes: tuple[str, ...],
    redirect_uri: str,
    now: datetime | None = None,
    lifetime: timedelta = timedelta(minutes=10),
) -> tuple[GoogleAuthSession, GoogleAuthorizationRequest]:
    parsed = urlsplit(redirect_uri)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Google desktop OAuth requires a 127.0.0.1 loopback redirect.")
    requested = tuple(sorted({str(scope).strip() for scope in scopes if str(scope).strip()}))
    if not requested:
        raise ValueError("Google authorization requires explicit scopes.")

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    state = secrets.token_urlsafe(32)
    session = GoogleAuthSession(
        session_id=uuid4().hex,
        profile_id=profile_id,
        requested_scopes=requested,
        redirect_uri=redirect_uri,
        state=state,
        code_verifier=verifier,
        created_at=current,
        expires_at=current + lifetime,
    )
    query = urlencode(
        {
            "access_type": "offline",
            "client_id": config.client_id,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "include_granted_scopes": "false",
            "prompt": "consent",
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(requested),
            "state": state,
        }
    )
    request = GoogleAuthorizationRequest(
        session_id=session.session_id,
        profile_id=profile_id,
        requested_scopes=requested,
        authorization_url=f"{AUTHORIZATION_ENDPOINT}?{query}",
        expires_at=session.expires_at,
    )
    return session, request


class GoogleLoopbackCallbackReceiver:
    """127.0.0.1 callback that ignores invalid requests until expiry."""

    def __init__(self, *, callback_path: str = "/oauth/callback") -> None:
        path = "/" + str(callback_path or "").strip().lstrip("/")
        receiver = self

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
                parsed = urlsplit(self.path)
                if parsed.path != path:
                    self.send_error(404)
                    return
                values = parse_qs(parsed.query, keep_blank_values=True)
                callback = GoogleOAuthCallback(
                    state=str((values.get("state") or [""])[0]),
                    code=str((values.get("code") or [""])[0]),
                    error=str((values.get("error") or [""])[0]),
                )
                if (
                    not receiver._expected_state
                    or not secrets.compare_digest(
                        callback.state,
                        receiver._expected_state,
                    )
                    or not (callback.code or callback.error)
                ):
                    self._send_plain(400, b"Google connection callback was not accepted.")
                    return
                if receiver._callback is not None:
                    self._send_plain(409, b"Google connection callback was already received.")
                    return
                receiver._callback = callback
                self._send_plain(
                    200,
                    b"Google connection received. You may close this window.",
                )

            def _send_plain(self, status: int, body: bytes) -> None:
                self.send_response(status)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        self._callback: GoogleOAuthCallback | None = None
        self._expected_state = ""
        self._server = HTTPServer(("127.0.0.1", 0), CallbackHandler)
        self._path = path

    @property
    def redirect_uri(self) -> str:
        return f"http://127.0.0.1:{self._server.server_port}{self._path}"

    def wait_for_callback(
        self,
        *,
        expected_state: str,
        timeout: float = 180,
    ) -> GoogleOAuthCallback:
        state = str(expected_state or "")
        if not state:
            raise ValueError("Google callback validation requires expected state.")
        self._expected_state = state
        deadline = monotonic() + max(0.1, float(timeout))
        try:
            while self._callback is None:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    break
                self._server.timeout = max(0.05, remaining)
                self._server.handle_request()
        finally:
            self._server.server_close()
        if self._callback is None:
            raise GoogleOAuthError("Google authorization callback timed out.")
        return self._callback

    def close(self) -> None:
        self._server.server_close()
