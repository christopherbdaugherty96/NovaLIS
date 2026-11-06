from __future__ import annotations

"""Tests for /api/settings/connections endpoints."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.connections_api import (
    CONNECTION_HEALTH_OPERATIONS,
    build_connections_router,
)
from src.connections.connections_store import ConnectionsStore
from src.governor.exceptions import DisclosureDeniedError, NetworkMediatorError
from src.governor.network_mediator import CONNECTION_OPERATION_ENDPOINTS, NetworkMediator

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


class _RecordingConnectionMediator:
    def __init__(self, *, result=None, error=None):
        self.result = result or {"status_code": 200, "data": {}}
        self.error = error
        self.calls = []

    def connection_request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.error is not None:
            raise self.error
        return self.result


def _client_with_mediator(store, monkeypatch, mediator):
    monkeypatch.setattr("src.api.connections_api.connections_store", store)
    app = FastAPI()
    app.include_router(build_connections_router(network_mediator=mediator))
    return TestClient(app)


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
    def test_trial_rejects_save_before_persistence_or_health_check(
        self, client, store, monkeypatch
    ):
        monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
        calls = []
        monkeypatch.setattr(
            "src.api.connections_api._health_check",
            lambda provider, key, mediator: calls.append((provider, key)) or (True, "unexpected"),
        )

        res = client.post(
            "/api/settings/connections/openai/key",
            json={"key": "synthetic-proof-key"},
        )

        assert res.status_code == 403
        assert "isn't available in this trial version" in res.json()["detail"]
        assert store.get_key("openai") == ""
        assert calls == []

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
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k, m: (True, "OK"))
        res = client.post("/api/settings/connections/brave/key", json={"key": "BSA-key12345678"})
        assert res.status_code == 200
        assert store.get_key("brave") == "BSA-key12345678"

    def test_returns_ok_and_detail_on_success(self, client, monkeypatch):
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k, m: (True, "Connected."))
        res = client.post("/api/settings/connections/news/key", json={"key": "newskey123456789"})
        assert res.status_code == 200
        data = res.json()
        assert data["ok"] is True
        assert "detail" in data
        assert "provider" in data

    def test_returns_ok_false_on_failed_health(self, client, monkeypatch):
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k, m: (False, "401 invalid"))
        res = client.post("/api/settings/connections/openai/key", json={"key": "sk-badkey1234567"})
        assert res.status_code == 200
        data = res.json()
        assert data["ok"] is False
        assert "401" in data["detail"]

    def test_stale_offloaded_result_cannot_mark_replaced_configuration_healthy(
        self, client, store, monkeypatch, tmp_path
    ):
        original = tmp_path / "original.ics"
        original.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR", encoding="utf-8")
        replacement = tmp_path / "missing.ics"

        def replace_before_result(provider, key, mediator):
            assert key == str(original)
            store.save_key("calendar", str(replacement))
            return True, "File found."

        monkeypatch.setattr(
            "src.api.connections_api._health_check", replace_before_result
        )

        res = client.post(
            "/api/settings/connections/calendar/key", json={"key": str(original)}
        )

        assert res.status_code == 200
        assert res.json()["ok"] is None
        assert store.get_key("calendar") == str(replacement)
        provider = res.json()["provider"]
        assert provider["health_ok"] is None
        assert provider["connected"] is False


# ---------------------------------------------------------------------------
# POST /api/settings/connections/{provider}/test
# ---------------------------------------------------------------------------

class TestTestKey:
    def test_trial_rejects_test_before_health_check(self, client, store, monkeypatch):
        store.save_key("openai", "synthetic-proof-key")
        monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
        calls = []
        monkeypatch.setattr(
            "src.api.connections_api._health_check",
            lambda provider, key, mediator: calls.append((provider, key)) or (True, "unexpected"),
        )

        res = client.post("/api/settings/connections/openai/test")

        assert res.status_code == 403
        assert "isn't available in this trial version" in res.json()["detail"]
        assert calls == []

    def test_no_key_returns_400(self, client):
        res = client.post("/api/settings/connections/openai/test")
        assert res.status_code == 400

    def test_unknown_provider_returns_404(self, client):
        res = client.post("/api/settings/connections/unknown/test")
        assert res.status_code == 404

    def test_existing_key_runs_check(self, client, store, monkeypatch):
        store.save_key("weather", "vcweather12345678")
        monkeypatch.setattr("src.api.connections_api._health_check", lambda p, k, m: (True, "Good"))
        res = client.post("/api/settings/connections/weather/test")
        assert res.status_code == 200
        assert res.json()["ok"] is True

    def test_data_out_denial_is_unverified_not_invalid_key(
        self, store, monkeypatch
    ):
        store.save_key("openai", "synthetic-secret-key")
        store.record_health("openai", ok=True, detail="Previously connected")
        mediator = _RecordingConnectionMediator(
            error=DisclosureDeniedError("policy_unavailable")
        )
        client = _client_with_mediator(store, monkeypatch, mediator)

        res = client.post("/api/settings/connections/openai/test")

        assert res.status_code == 200
        assert res.json()["ok"] is None
        provider = res.json()["provider"]
        assert provider["health_ok"] is None
        assert provider["connected"] is False
        assert provider["last_checked"] == ""
        assert "Data-Out policy" in provider["health_detail"]
        assert "synthetic-secret-key" not in str(res.json())

    def test_default_policy_denial_makes_zero_transport_attempts(
        self, store, monkeypatch
    ):
        store.save_key("news", "synthetic-news-secret")
        attempts = []

        def forbidden(*args, **kwargs):
            attempts.append((args, kwargs))
            raise AssertionError("transport must not be reached")

        monkeypatch.setattr(
            "src.governor.network_mediator.NetworkMediator._new_session", forbidden
        )
        monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", forbidden)
        client = _client_with_mediator(
            store, monkeypatch, NetworkMediator()
        )

        res = client.post("/api/settings/connections/news/test")

        assert res.status_code == 200
        assert res.json()["ok"] is None
        assert attempts == []
        assert "synthetic-news-secret" not in str(res.json())

    def test_health_check_is_offloaded_from_async_endpoint(
        self, store, monkeypatch
    ):
        store.save_key("openai", "synthetic-openai-secret")
        calls = []

        async def recording_to_thread(function, *args):
            calls.append((function, args))
            return function(*args)

        monkeypatch.setattr("src.api.connections_api.asyncio.to_thread", recording_to_thread)
        monkeypatch.setattr(
            "src.api.connections_api._health_check",
            lambda provider, key, mediator: (True, "Connected."),
        )

        res = _client_with_mediator(
            store, monkeypatch, _RecordingConnectionMediator()
        ).post("/api/settings/connections/openai/test")

        assert res.status_code == 200
        assert len(calls) == 1
        assert calls[0][1][0:2] == ("openai", "synthetic-openai-secret")

    def test_health_failure_does_not_expose_exception_detail(self):
        class _LeakyMediator:
            def connection_request(self, *args, **kwargs):
                raise NetworkMediatorError("synthetic-secret-in-exception")

        from src.api.connections_api import _health_check

        ok, detail = _health_check("openai", "synthetic-key", _LeakyMediator())

        assert ok is False
        assert detail == "Provider connection request failed."
        assert "synthetic-secret" not in detail

    def test_existing_key_check_rejects_result_after_configuration_change(
        self, client, store, monkeypatch, tmp_path
    ):
        original = tmp_path / "original.ics"
        original.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR", encoding="utf-8")
        replacement = tmp_path / "missing.ics"
        store.save_key("calendar", str(original))

        def replace_before_result(provider, key, mediator):
            assert key == str(original)
            store.save_key("calendar", str(replacement))
            return True, "File found."

        monkeypatch.setattr(
            "src.api.connections_api._health_check", replace_before_result
        )

        res = client.post("/api/settings/connections/calendar/test")

        assert res.status_code == 200
        assert res.json()["ok"] is None
        assert store.get_key("calendar") == str(replacement)
        assert res.json()["provider"]["health_ok"] is None

    def test_repeated_policy_denials_remain_unverified(self):
        mediator = NetworkMediator()

        results = [
            __import__("src.api.connections_api", fromlist=["_health_check"])
            ._health_check("openai", "synthetic-key", mediator)[0]
            for _ in range(51)
        ]

        assert results == [None] * 51


@pytest.mark.parametrize("provider", ["openai", "brave", "news", "weather"])
def test_provider_health_uses_exact_governed_connection_operation(
    provider, store, monkeypatch
):
    secret = f"synthetic-{provider}-secret"
    store.save_key(provider, secret)
    mediator = _RecordingConnectionMediator()
    client = _client_with_mediator(store, monkeypatch, mediator)

    res = client.post(f"/api/settings/connections/{provider}/test")

    assert res.status_code == 200
    assert len(mediator.calls) == 1
    args, kwargs = mediator.calls[0]
    expected = CONNECTION_HEALTH_OPERATIONS[provider]
    assert args == (provider, "health", "GET", expected.url)
    assert kwargs.get("params") == expected.params(secret)
    assert kwargs.get("headers") == expected.headers(secret)
    assert secret not in str(res.json())


def test_health_operation_endpoints_match_transport_allowlist():
    assert {
        provider: ("GET", operation.url)
        for provider, operation in CONNECTION_HEALTH_OPERATIONS.items()
    } == {
        provider: CONNECTION_OPERATION_ENDPOINTS[provider]["health"]
        for provider in CONNECTION_HEALTH_OPERATIONS
    }


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
