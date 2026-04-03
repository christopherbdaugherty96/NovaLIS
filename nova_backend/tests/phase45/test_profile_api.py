from __future__ import annotations

"""Tests for /api/profile endpoints via profile_api.py."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.profile_api import build_profile_router
from src.profiles.user_profile_store import UserProfileStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_profile_path(tmp_path):
    return tmp_path / "user_profile.json"


@pytest.fixture()
def app(tmp_profile_path, monkeypatch):
    """Build a FastAPI test app with a fresh profile store."""
    store = UserProfileStore(path=tmp_profile_path)

    # Patch the module-level singleton so the API uses our test store
    monkeypatch.setattr("src.api.profile_api.user_profile_store", store)
    monkeypatch.setattr("src.profiles.user_profile_store.user_profile_store", store)

    # Stub deps so ledger calls don't blow up
    deps = MagicMock()
    deps.RUNTIME_GOVERNOR = "test-governor"
    deps._log_ledger_event = MagicMock()

    # Also stub out the memory write so it's a no-op
    monkeypatch.setattr(
        "src.api.profile_api._write_identity_to_memory",
        lambda: None,
    )

    fast_app = FastAPI()
    fast_app.include_router(build_profile_router(deps))
    return fast_app


@pytest.fixture()
def client(app):
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/profile
# ---------------------------------------------------------------------------

class TestGetProfile:
    def test_returns_200(self, client):
        res = client.get("/api/profile")
        assert res.status_code == 200

    def test_returns_expected_keys(self, client):
        data = client.get("/api/profile").json()
        for key in ("name", "nickname", "email", "rules", "preferences", "is_set_up"):
            assert key in data, f"Missing key: {key}"

    def test_default_is_set_up_false(self, client):
        data = client.get("/api/profile").json()
        assert data["is_set_up"] is False


# ---------------------------------------------------------------------------
# POST /api/profile/identity
# ---------------------------------------------------------------------------

class TestPostIdentity:
    def test_save_name(self, client):
        res = client.post("/api/profile/identity", json={"name": "Chris"})
        assert res.status_code == 200
        assert res.json()["name"] == "Chris"

    def test_save_nickname(self, client):
        res = client.post("/api/profile/identity", json={"name": "Chris", "nickname": "Boss"})
        assert res.status_code == 200
        assert res.json()["nickname"] == "Boss"

    def test_save_email(self, client):
        res = client.post("/api/profile/identity", json={"email": "chris@example.com"})
        assert res.status_code == 200
        assert res.json()["email"] == "chris@example.com"

    def test_is_set_up_true_after_name(self, client):
        res = client.post("/api/profile/identity", json={"name": "Chris"})
        assert res.json()["is_set_up"] is True

    def test_invalid_name_type_returns_400(self, client):
        res = client.post("/api/profile/identity", json={"name": 123})
        assert res.status_code == 400

    def test_invalid_nickname_type_returns_400(self, client):
        res = client.post("/api/profile/identity", json={"nickname": 456})
        assert res.status_code == 400

    def test_invalid_email_type_returns_400(self, client):
        res = client.post("/api/profile/identity", json={"email": True})
        assert res.status_code == 400

    def test_empty_payload_is_accepted(self, client):
        res = client.post("/api/profile/identity", json={})
        assert res.status_code == 200

    def test_get_reflects_saved_identity(self, client):
        client.post("/api/profile/identity", json={"name": "Chris"})
        data = client.get("/api/profile").json()
        assert data["name"] == "Chris"


# ---------------------------------------------------------------------------
# POST /api/profile/preferences
# ---------------------------------------------------------------------------

class TestPostPreferences:
    def test_save_response_style_concise(self, client):
        res = client.post("/api/profile/preferences", json={"response_style": "concise"})
        assert res.status_code == 200
        assert res.json()["preferences"]["response_style"] == "concise"

    def test_save_response_style_detailed(self, client):
        res = client.post("/api/profile/preferences", json={"response_style": "detailed"})
        assert res.status_code == 200
        assert res.json()["preferences"]["response_style"] == "detailed"

    def test_invalid_response_style_returns_400(self, client):
        res = client.post("/api/profile/preferences", json={"response_style": "verbose"})
        assert res.status_code == 400

    def test_toggle_use_name_false(self, client):
        res = client.post("/api/profile/preferences", json={"use_name_in_responses": False})
        assert res.status_code == 200
        assert res.json()["preferences"]["use_name_in_responses"] is False

    def test_toggle_proactive_suggestions(self, client):
        res = client.post("/api/profile/preferences", json={"proactive_suggestions": False})
        assert res.status_code == 200
        assert res.json()["preferences"]["proactive_suggestions"] is False

    def test_morning_brief_enabled(self, client):
        res = client.post(
            "/api/profile/preferences",
            json={"morning_brief_enabled": True, "morning_brief_time": "07:30"},
        )
        assert res.status_code == 200
        prefs = res.json()["preferences"]
        assert prefs["morning_brief_enabled"] is True
        assert prefs["morning_brief_time"] == "07:30"

    def test_empty_payload_is_accepted(self, client):
        res = client.post("/api/profile/preferences", json={})
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/profile/rules
# ---------------------------------------------------------------------------

class TestPostRules:
    def test_save_rules(self, client):
        rules = "- Always be concise\n- No filler phrases"
        res = client.post("/api/profile/rules", json={"rules": rules})
        assert res.status_code == 200
        assert "Always be concise" in res.json()["rules"]

    def test_non_string_rules_returns_400(self, client):
        res = client.post("/api/profile/rules", json={"rules": 42})
        assert res.status_code == 400

    def test_empty_rules_accepted(self, client):
        res = client.post("/api/profile/rules", json={"rules": ""})
        assert res.status_code == 200

    def test_missing_rules_key_defaults_empty(self, client):
        res = client.post("/api/profile/rules", json={})
        assert res.status_code == 200

    def test_get_reflects_saved_rules(self, client):
        client.post("/api/profile/rules", json={"rules": "Be direct"})
        data = client.get("/api/profile").json()
        assert data["rules"] == "Be direct"
