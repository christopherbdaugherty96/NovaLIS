from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import brain_server


def test_openclaw_bridge_status_reports_alpha0_unavailable_when_token_missing(monkeypatch):
    monkeypatch.delenv("NOVA_OPENCLAW_BRIDGE_TOKEN", raising=False)
    monkeypatch.delenv("NOVA_BRIDGE_TOKEN", raising=False)

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/bridge/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["bridge"]["enabled"] is False
    assert payload["bridge"]["status"] == "unavailable"
    assert payload["bridge"]["alpha0_disabled"] is True


def test_openclaw_bridge_status_remains_alpha0_unavailable_when_token_present(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/bridge/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["bridge"]["enabled"] is False
    assert payload["bridge"]["status"] == "unavailable"
    assert payload["bridge"]["alpha0_disabled"] is True


def test_openclaw_bridge_message_refuses_without_token(monkeypatch):
    monkeypatch.delenv("NOVA_OPENCLAW_BRIDGE_TOKEN", raising=False)
    monkeypatch.delenv("NOVA_BRIDGE_TOKEN", raising=False)

    client = TestClient(brain_server.app)
    response = client.post("/api/openclaw/bridge/message", json={"text": "daily brief"})

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_openclaw_bridge_message_refuses_invalid_token_configuration(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "daily brief"},
        headers={"X-Nova-Bridge-Token": "wrong-token"},
    )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_openclaw_bridge_message_blocks_effectful_scope(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "save this"},
        headers={"X-Nova-Bridge-Token": "secret-token"},
    )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_openclaw_bridge_message_blocks_paraphrased_memory_write(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "please save this to memory for me"},
        headers={"X-Nova-Bridge-Token": "secret-token"},
    )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_openclaw_bridge_message_blocks_local_context_capability(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "explain this"},
        headers={"X-Nova-Bridge-Token": "secret-token"},
    )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_openclaw_bridge_message_refuses_valid_bearer_token(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "daily brief"},
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


@pytest.mark.parametrize("permission_enabled", [False, True])
@pytest.mark.parametrize("token_header", ["X-Nova-Bridge-Token", "Authorization"])
def test_openclaw_bridge_refuses_every_setting_and_token_combination(
    monkeypatch, permission_enabled, token_header
):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")
    monkeypatch.setattr(
        brain_server.runtime_settings_store,
        "is_permission_enabled",
        lambda name: permission_enabled if name == "remote_bridge_enabled" else False,
    )
    value = "Bearer secret-token" if token_header == "Authorization" else "secret-token"
    response = TestClient(brain_server.app).post(
        "/api/openclaw/bridge/message",
        json={"text": "daily brief"},
        headers={token_header: value},
    )
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()
