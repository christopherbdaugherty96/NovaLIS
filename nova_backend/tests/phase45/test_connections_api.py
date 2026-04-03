from __future__ import annotations

"""Tests for /api/settings/connections endpoints."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.connections_api import build_connections_router
from src.connections.connections_store import ConnectionsStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path):
    return ConnectionsStore(path=tmp_path / "provider_keys.json")


@pytest.fixture()
def app(store, monkeypatch):
    monkeypatch.setattr("src.api.connections_api.connections_store", store)
    fast_app = FastAPI()
    fast_app.include_router(build_connections_router())
    return fast_app


@pytest.fixture()
def client(app):
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/settings/connections
# ---------------------------------------------------------------------------

class TestGetConnections:
    def test_returns_200(self, client):
        res = client.get("/api/settings/connections")
        assert res.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/settings/connections").json()
        assert isinstance(data, list)

    def test_returns_all_providers(self, client):
        data = client.get("/api/settings/connections").json()
        ids = {p["id"] for p in data}
        for pid in ("openai", "brave", "news", "weather", "calendar", "bridge"):
            assert pid in ids

    def test_no_key_values_returned(self, client, store):
        store.save_key("openai", "sk-secretvalue1")
        data = client.get("/api/settings/connections").json()
        for p in data:
            assert "sk-secretvalue1" not in str(p)

    def test_has_key_true_after_save(self, client, store):
        store.save_key("brave", "BSA-key12345678")
        data = {p["id"]: p for p in client.get("/api/settings/connections").json()}
        assert data["brave"]["has_key"] is True


# ---------------------------------------------------------------------------
# POST /api/settings/connections/{provider}/key
# ---------------------------------------------------------------------------

class TestSaveKey:
    def test_unknown_provider_returns_404(self, client):
        res = client.post("/api/settings/connections/unknown/key", json={"key": "abc"})
        assert res.status_code == 404

    def test_empty_key_returns_400(self, client):
        res = client.post("/api/settings/connections/openai/key", json={"key": ""})
        assert res.status_code == 400

    def test_missing_key_returns_400(self, client):
        res = client.post("/api/settings/connections/openai/key", json={})
        assert res.status_code == 400

    def test_valid_key_persisted(self, client, store, monkeypatch):
        # Stub health check so we don't hit the real API
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k: (True, "OK"))
        res = client.post("/api/settings/connections/brave/key", json={"key": "BSA-key12345678"})
        assert res.status_code == 200
        assert store.get_key("brave") == "BSA-key12345678"

    def test_returns_ok_and_detail_on_success(self, client, monkeypatch):
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k: (True, "Connected."))
        res = client.post("/api/settings/connections/news/key", json={"key": "newskey123456789"})
        assert res.status_code == 200
        data = res.json()
        assert data["ok"] is True
        assert "detail" in data
        assert "provider" in data

    def test_returns_ok_false_on_failed_health(self, client, monkeypatch):
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k: (False, "401 invalid"))
        res = client.post("/api/settings/connections/openai/key", json={"key": "sk-badkey1234567"})
        assert res.status_code == 200
        data = res.json()
        assert data["ok"] is False
        assert "401" in data["detail"]


# ---------------------------------------------------------------------------
# POST /api/settings/connections/{provider}/test
# ---------------------------------------------------------------------------

class TestTestKey:
    def test_no_key_returns_400(self, client):
        res = client.post("/api/settings/connections/openai/test")
        assert res.status_code == 400

    def test_unknown_provider_returns_404(self, client):
        res = client.post("/api/settings/connections/unknown/test")
        assert res.status_code == 404

    def test_existing_key_runs_check(self, client, store, monkeypatch):
        store.save_key("weather", "vcweather12345678")
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k: (True, "Good"))
        res = client.post("/api/settings/connections/weather/test")
        assert res.status_code == 200
        assert res.json()["ok"] is True


# ---------------------------------------------------------------------------
# DELETE /api/settings/connections/{provider}
# ---------------------------------------------------------------------------

class TestDeleteProvider:
    def test_unknown_provider_returns_404(self, client):
        res = client.delete("/api/settings/connections/unknown")
        assert res.status_code == 404

    def test_clears_stored_key(self, client, store):
        store.save_key("bridge", "token12345678901")
        res = client.delete("/api/settings/connections/bridge")
        assert res.status_code == 200
        assert store.get_key("bridge") == ""

    def test_returns_ok_true(self, client, store):
        store.save_key("bridge", "token12345678901")
        data = client.delete("/api/settings/connections/bridge").json()
        assert data["ok"] is True

    def test_provider_snapshot_in_response(self, client, store):
        store.save_key("bridge", "token12345678901")
        data = client.delete("/api/settings/connections/bridge").json()
        assert "provider" in data


# ---------------------------------------------------------------------------
# DELETE /api/settings/connections/all
# ---------------------------------------------------------------------------

class TestDeleteAll:
    def test_requires_confirmed_flag(self, client):
        res = client.request("DELETE", "/api/settings/connections/all", json={})
        assert res.status_code == 400

    def test_confirmed_true_clears_all(self, client, store):
        store.save_key("openai", "sk-key12345678901")
        store.save_key("news", "newskey123456789")
        res = client.request(
            "DELETE", "/api/settings/connections/all", json={"confirmed": True}
        )
        assert res.status_code == 200
        for p in store.snapshot():
            assert p["has_key"] is False

    def test_returns_ok_and_providers_list(self, client):
        res = client.request(
            "DELETE", "/api/settings/connections/all", json={"confirmed": True}
        )
        data = res.json()
        assert data["ok"] is True
        assert isinstance(data["providers"], list)


# ---------------------------------------------------------------------------
# Health check stubs (local checks only — no real network calls)
# ---------------------------------------------------------------------------

class TestHealthCheckLocal:
    def test_calendar_missing_file_fails(self):
        from src.api.connections_api import _check_calendar
        ok, detail = _check_calendar("/nonexistent/path/calendar.ics")
        assert ok is False
        assert "not found" in detail.lower() or "no file" in detail.lower()

    def test_calendar_wrong_extension_fails(self, tmp_path):
        from src.api.connections_api import _check_calendar
        f = tmp_path / "cal.txt"
        f.write_text("not a calendar")
        ok, detail = _check_calendar(str(f))
        assert ok is False

    def test_calendar_valid_ics_passes(self, tmp_path):
        from src.api.connections_api import _check_calendar
        f = tmp_path / "cal.ics"
        f.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR")
        ok, detail = _check_calendar(str(f))
        assert ok is True

    def test_token_too_short_fails(self):
        from src.api.connections_api import _check_token
        ok, _ = _check_token("short")
        assert ok is False

    def test_token_long_enough_passes(self):
        from src.api.connections_api import _check_token
        ok, _ = _check_token("longenoughtoken")
        assert ok is True
