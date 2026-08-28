from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from src.connectors.google_workspace.credential_vault import (
    EncryptedGoogleCredentialVault,
    GoogleCredentialVaultError,
    WindowsDpapiProtector,
)
from src.connectors.google_workspace.models import (
    GoogleConnectionState,
    GoogleStoredCredential,
    GoogleWorkspaceAccount,
)

NOW = datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc)


class _TestOnlyProtector:
    """Reversible test double; never used by the production factory."""

    protection_name = "test_only_not_for_live_credentials"
    _KEY = b"nova-test-only"

    def protect(self, plaintext: bytes) -> bytes:
        return bytes(
            byte ^ self._KEY[index % len(self._KEY)]
            for index, byte in enumerate(plaintext)
        )

    def unprotect(self, ciphertext: bytes) -> bytes:
        return self.protect(ciphertext)


def _credential() -> GoogleStoredCredential:
    return GoogleStoredCredential(
        state=GoogleConnectionState.CONNECTED,
        grant_profile_id="identity",
        requested_scopes=("openid", "email"),
        granted_scopes=("openid", "email"),
        access_token="fake-access-token-for-tests",
        refresh_token="fake-refresh-token-for-tests",
        expires_at=NOW + timedelta(hours=1),
        account=GoogleWorkspaceAccount(
            subject="fake-google-subject",
            email="fake.user@example.test",
        ),
    )


def test_encrypted_vault_round_trip_and_no_plaintext_secrets(tmp_path):
    path = tmp_path / "google_workspace_credentials.json"
    vault = EncryptedGoogleCredentialVault(path, protector=_TestOnlyProtector())

    vault.save(_credential())
    loaded = vault.load()
    raw = path.read_text(encoding="utf-8")

    assert loaded is not None
    assert loaded.access_token == "fake-access-token-for-tests"
    assert loaded.refresh_token == "fake-refresh-token-for-tests"
    assert loaded.account is not None
    assert loaded.account.email == "fake.user@example.test"
    for secret in (
        "fake-access-token-for-tests",
        "fake-refresh-token-for-tests",
        "fake.user@example.test",
        "fake-google-subject",
    ):
        assert secret not in raw
    assert "ciphertext" in raw
    assert "test_only_not_for_live_credentials" in raw
    assert "windows_dpapi_current_user" not in raw


def test_missing_vault_is_not_connected_and_delete_is_idempotent(tmp_path):
    vault = EncryptedGoogleCredentialVault(
        tmp_path / "missing.json",
        protector=_TestOnlyProtector(),
    )

    assert vault.load() is None
    vault.delete()
    assert vault.load() is None


def test_corrupt_vault_fails_closed(tmp_path):
    path = tmp_path / "google_workspace_credentials.json"
    path.write_text(
        '{"schema_version":"1.0",'
        '"protection":"test_only_not_for_live_credentials",'
        '"ciphertext":"not base64!"}'
    )
    vault = EncryptedGoogleCredentialVault(path, protector=_TestOnlyProtector())

    with pytest.raises(GoogleCredentialVaultError, match="could not be read safely"):
        vault.load()


def test_vault_rejects_a_different_protection_scheme(tmp_path):
    path = tmp_path / "google_workspace_credentials.json"
    vault = EncryptedGoogleCredentialVault(path, protector=_TestOnlyProtector())
    vault.save(_credential())
    raw = path.read_text(encoding="utf-8").replace(
        "test_only_not_for_live_credentials",
        "windows_dpapi_current_user",
    )
    path.write_text(raw, encoding="utf-8")

    with pytest.raises(GoogleCredentialVaultError, match="protection does not match"):
        vault.load()


def test_default_protector_is_windows_dpapi():
    vault = EncryptedGoogleCredentialVault()
    assert isinstance(vault._protector, WindowsDpapiProtector)


def test_dpapi_fails_closed_when_unavailable(monkeypatch):
    monkeypatch.setattr("src.connectors.google_workspace.credential_vault.os.name", "posix")

    with pytest.raises(GoogleCredentialVaultError, match="Windows DPAPI"):
        WindowsDpapiProtector().protect(b"fake-test-secret")


@pytest.mark.skipif(os.name != "nt", reason="Windows DPAPI live platform contract")
def test_windows_dpapi_round_trip_uses_current_user_protection(tmp_path):
    path = tmp_path / "google_workspace_credentials.json"
    vault = EncryptedGoogleCredentialVault(path)

    vault.save(_credential())
    loaded = vault.load()

    assert loaded is not None
    assert loaded.access_token == "fake-access-token-for-tests"
    assert "fake-access-token-for-tests" not in path.read_text(encoding="utf-8")
