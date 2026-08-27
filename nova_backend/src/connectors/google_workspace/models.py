from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from src.semantic import SourceIdentity

FOUNDATION_PROFILE_ID = "identity"
FOUNDATION_SCOPES = ("openid", "email")


def _aware_utc(value: datetime | None, *, field_name: str) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")
    return value.astimezone(timezone.utc)


def _scope_tuple(values: tuple[str, ...] | list[str] | set[str]) -> tuple[str, ...]:
    normalized = {str(value or "").strip() for value in values}
    normalized.discard("")
    return tuple(sorted(normalized))


def mask_google_account(email: str) -> str:
    """Return a stable display hint without exposing the full account address."""
    value = str(email or "").strip()
    if "@" not in value:
        return "***"
    local, domain = value.rsplit("@", 1)
    if not local or not domain:
        return "***"
    prefix = local[:2] if len(local) > 1 else local[:1]
    return f"{prefix}***@{domain}"


class GoogleConnectionState(str, Enum):
    NOT_CONNECTED = "not_connected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    EXPIRED = "expired"
    REFRESH_FAILED = "refresh_failed"
    REVOKED = "revoked"
    SCOPE_INSUFFICIENT = "scope_insufficient"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True)
class GoogleGrantProfile:
    profile_id: str
    display_name: str
    scopes: tuple[str, ...]
    enabled: bool = True

    def __post_init__(self) -> None:
        profile_id = str(self.profile_id or "").strip().lower()
        display_name = str(self.display_name or "").strip()
        scopes = _scope_tuple(self.scopes)
        if not profile_id or not display_name or not scopes:
            raise ValueError("Google grant profiles require an id, name, and scopes.")
        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(self, "display_name", display_name)
        object.__setattr__(self, "scopes", scopes)


class GoogleGrantProfileCatalog:
    """Explicit scope bundles; the foundation activates identity only."""

    def __init__(self, profiles: tuple[GoogleGrantProfile, ...] | None = None) -> None:
        configured = profiles or (
            GoogleGrantProfile(
                profile_id=FOUNDATION_PROFILE_ID,
                display_name="Google account identity",
                scopes=FOUNDATION_SCOPES,
            ),
        )
        self._profiles = {profile.profile_id: profile for profile in configured}
        if len(self._profiles) != len(configured):
            raise ValueError("Duplicate Google grant profile id.")

    def get_enabled(self, profile_id: str) -> GoogleGrantProfile:
        profile = self._profiles.get(str(profile_id or "").strip().lower())
        if profile is None or not profile.enabled:
            raise KeyError("Google grant profile is unavailable.")
        return profile

    def all_profiles(self) -> tuple[GoogleGrantProfile, ...]:
        return tuple(self._profiles[key] for key in sorted(self._profiles))


@dataclass(frozen=True)
class GoogleScopeInventory:
    requested: tuple[str, ...]
    granted: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "requested", _scope_tuple(self.requested))
        object.__setattr__(self, "granted", _scope_tuple(self.granted))

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.requested).difference(self.granted)))

    @property
    def sufficient(self) -> bool:
        return not self.missing

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested": list(self.requested),
            "granted": list(self.granted),
            "missing": list(self.missing),
            "sufficient": self.sufficient,
        }


@dataclass(frozen=True)
class GoogleWorkspaceAccount:
    subject: str = field(repr=False)
    email: str = field(repr=False)

    def __post_init__(self) -> None:
        subject = str(self.subject or "").strip()
        email = str(self.email or "").strip()
        if not subject or "@" not in email:
            raise ValueError("Google account identity requires subject and email.")
        object.__setattr__(self, "subject", subject)
        object.__setattr__(self, "email", email)

    @property
    def source_identity(self) -> SourceIdentity:
        return SourceIdentity(
            provider="google",
            service="workspace",
            account_id=self.subject,
        )

    @property
    def masked_email(self) -> str:
        return mask_google_account(self.email)


@dataclass(frozen=True)
class GoogleStoredCredential:
    state: GoogleConnectionState
    grant_profile_id: str
    requested_scopes: tuple[str, ...]
    granted_scopes: tuple[str, ...]
    access_token: str = field(default="", repr=False)
    refresh_token: str = field(default="", repr=False)
    token_type: str = field(default="Bearer", repr=False)
    expires_at: datetime | None = None
    last_successful_refresh_at: datetime | None = None
    account: GoogleWorkspaceAccount | None = None
    safe_reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "grant_profile_id",
            str(self.grant_profile_id or FOUNDATION_PROFILE_ID).strip().lower(),
        )
        object.__setattr__(self, "requested_scopes", _scope_tuple(self.requested_scopes))
        object.__setattr__(self, "granted_scopes", _scope_tuple(self.granted_scopes))
        object.__setattr__(
            self,
            "expires_at",
            _aware_utc(self.expires_at, field_name="expires_at"),
        )
        object.__setattr__(
            self,
            "last_successful_refresh_at",
            _aware_utc(
                self.last_successful_refresh_at,
                field_name="last_successful_refresh_at",
            ),
        )
        object.__setattr__(self, "safe_reason", str(self.safe_reason or "").strip()[:120])
        if self.state in {
            GoogleConnectionState.CONNECTED,
            GoogleConnectionState.EXPIRED,
            GoogleConnectionState.REFRESH_FAILED,
        } and not (self.access_token or self.refresh_token):
            raise ValueError("Credential-bearing connection state requires stored authorization.")
        if self.state in {
            GoogleConnectionState.REVOKED,
            GoogleConnectionState.DISCONNECTED,
            GoogleConnectionState.SCOPE_INSUFFICIENT,
        } and (self.access_token or self.refresh_token):
            raise ValueError("Token-free connection state cannot retain credentials.")

    @property
    def scope_inventory(self) -> GoogleScopeInventory:
        return GoogleScopeInventory(self.requested_scopes, self.granted_scopes)

    def to_secret_payload(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "grant_profile_id": self.grant_profile_id,
            "requested_scopes": list(self.requested_scopes),
            "granted_scopes": list(self.granted_scopes),
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat() if self.expires_at else "",
            "last_successful_refresh_at": (
                self.last_successful_refresh_at.isoformat()
                if self.last_successful_refresh_at
                else ""
            ),
            "account": (
                {"subject": self.account.subject, "email": self.account.email}
                if self.account
                else None
            ),
            "safe_reason": self.safe_reason,
        }

    @classmethod
    def from_secret_payload(cls, payload: Mapping[str, Any]) -> GoogleStoredCredential:
        account_payload = payload.get("account")
        account = None
        if isinstance(account_payload, Mapping):
            account = GoogleWorkspaceAccount(
                subject=str(account_payload.get("subject") or ""),
                email=str(account_payload.get("email") or ""),
            )

        def parse_time(key: str) -> datetime | None:
            raw = str(payload.get(key) or "").strip()
            return datetime.fromisoformat(raw) if raw else None

        return cls(
            state=GoogleConnectionState(str(payload.get("state") or "")),
            grant_profile_id=str(payload.get("grant_profile_id") or FOUNDATION_PROFILE_ID),
            requested_scopes=tuple(payload.get("requested_scopes") or ()),
            granted_scopes=tuple(payload.get("granted_scopes") or ()),
            access_token=str(payload.get("access_token") or ""),
            refresh_token=str(payload.get("refresh_token") or ""),
            token_type=str(payload.get("token_type") or "Bearer"),
            expires_at=parse_time("expires_at"),
            last_successful_refresh_at=parse_time("last_successful_refresh_at"),
            account=account,
            safe_reason=str(payload.get("safe_reason") or ""),
        )


@dataclass(frozen=True)
class GoogleConnectionStatus:
    state: GoogleConnectionState
    grant_profile_id: str = ""
    scope_inventory: GoogleScopeInventory = field(
        default_factory=lambda: GoogleScopeInventory((), ())
    )
    account: GoogleWorkspaceAccount | None = None
    expires_at: datetime | None = None
    last_successful_refresh_at: datetime | None = None
    credential_valid: bool = False
    safe_reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        source = self.account.source_identity if self.account else None
        return {
            "provider": "google_workspace",
            "connection_state": self.state.value,
            "account_hint": self.account.masked_email if self.account else "",
            "source": source.canonical if source else "google:workspace",
            "grant_profile": self.grant_profile_id,
            "scope_inventory": self.scope_inventory.as_dict(),
            "credential_valid": self.credential_valid,
            "token_expiration_state": (
                "valid"
                if self.credential_valid
                else "expired"
                if self.state is GoogleConnectionState.EXPIRED
                else "unavailable"
            ),
            "expires_at": self.expires_at.isoformat() if self.expires_at else "",
            "last_successful_refresh_at": (
                self.last_successful_refresh_at.isoformat()
                if self.last_successful_refresh_at
                else ""
            ),
            "reason": self.safe_reason,
        }
