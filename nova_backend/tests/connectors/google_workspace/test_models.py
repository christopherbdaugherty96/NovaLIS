from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from src.connectors.google_workspace.models import (
    FOUNDATION_PROFILE_ID,
    FOUNDATION_SCOPES,
    GoogleConnectionState,
    GoogleConnectionStatus,
    GoogleGrantProfile,
    GoogleGrantProfileCatalog,
    GoogleScopeInventory,
    GoogleStoredCredential,
    GoogleWorkspaceAccount,
    mask_google_account,
)

NOW = datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc)


def test_foundation_profile_requests_identity_only():
    profile = GoogleGrantProfileCatalog().get_enabled(FOUNDATION_PROFILE_ID)

    assert profile.scopes == tuple(sorted(FOUNDATION_SCOPES))
    assert profile.scopes == ("email", "openid")
    assert not any(
        name in " ".join(profile.scopes).lower()
        for name in ("tasks", "gmail", "calendar", "drive", "docs", "sheets")
    )


def test_disabled_future_profile_cannot_be_selected():
    catalog = GoogleGrantProfileCatalog(
        (
            GoogleGrantProfile("identity", "Identity", ("openid", "email")),
            GoogleGrantProfile("future", "Future", ("example.scope",), enabled=False),
        )
    )

    with pytest.raises(KeyError, match="unavailable"):
        catalog.get_enabled("future")


def test_scope_inventory_reports_actual_grants_and_missing_scopes():
    inventory = GoogleScopeInventory(
        requested=("openid", "email", "future.scope"),
        granted=("openid", "email"),
    )

    assert inventory.granted == ("email", "openid")
    assert inventory.missing == ("future.scope",)
    assert inventory.sufficient is False
    assert "future.scope" not in inventory.granted


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        ("christopher@gmail.com", "ch***@gmail.com"),
        ("a@gmail.com", "a***@gmail.com"),
        ("invalid", "***"),
    ],
)
def test_account_masking_is_safe(email, expected):
    assert mask_google_account(email) == expected


def test_google_account_reuses_source_identity_without_credentials():
    account = GoogleWorkspaceAccount(
        subject="google-subject-123",
        email="christopher@gmail.com",
    )
    source = account.source_identity

    assert source.provider == "google"
    assert source.service == "workspace"
    assert source.account_id == "google-subject-123"
    assert not hasattr(source, "token")
    assert not hasattr(source, "credential")


def test_safe_status_never_serializes_tokens_or_raw_account_identity():
    account = GoogleWorkspaceAccount(
        subject="google-subject-123",
        email="christopher@gmail.com",
    )
    credential = GoogleStoredCredential(
        state=GoogleConnectionState.CONNECTED,
        grant_profile_id="identity",
        requested_scopes=("openid", "email"),
        granted_scopes=("openid", "email"),
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=NOW + timedelta(hours=1),
        account=account,
    )
    status = GoogleConnectionStatus(
        state=GoogleConnectionState.CONNECTED,
        grant_profile_id=credential.grant_profile_id,
        scope_inventory=credential.scope_inventory,
        account=account,
        expires_at=credential.expires_at,
        credential_valid=True,
    ).as_dict()
    rendered = str(status)

    assert status["account_hint"] == "ch***@gmail.com"
    assert status["source"] == "google:workspace"
    assert "christopher@gmail.com" not in rendered
    assert "google-subject-123" not in rendered
    assert "test-access-token" not in rendered
    assert "test-refresh-token" not in rendered
    assert "access_token" not in status
    assert "refresh_token" not in status


def test_token_fields_are_redacted_from_repr():
    credential = GoogleStoredCredential(
        state=GoogleConnectionState.CONNECTED,
        grant_profile_id="identity",
        requested_scopes=("openid", "email"),
        granted_scopes=("openid", "email"),
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=NOW + timedelta(hours=1),
    )

    rendered = repr(credential)
    assert "test-access-token" not in rendered
    assert "test-refresh-token" not in rendered


def test_scope_insufficient_state_is_metadata_only():
    credential = GoogleStoredCredential(
        state=GoogleConnectionState.SCOPE_INSUFFICIENT,
        grant_profile_id="identity",
        requested_scopes=("openid", "email"),
        granted_scopes=("openid",),
        safe_reason="required_scopes_not_granted_credentials_revoked",
    )

    assert credential.access_token == ""
    assert credential.refresh_token == ""
    assert credential.scope_inventory.missing == ("email",)


@pytest.mark.parametrize(
    "state",
    [
        GoogleConnectionState.SCOPE_INSUFFICIENT,
        GoogleConnectionState.REVOKED,
        GoogleConnectionState.DISCONNECTED,
    ],
)
def test_token_free_states_reject_reusable_credentials(state):
    with pytest.raises(ValueError, match="cannot retain credentials"):
        GoogleStoredCredential(
            state=state,
            grant_profile_id="identity",
            requested_scopes=("openid", "email"),
            granted_scopes=("openid",),
            refresh_token="must-not-be-retained",
        )
