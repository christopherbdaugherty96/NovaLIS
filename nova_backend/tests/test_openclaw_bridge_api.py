from __future__ import annotations

from fastapi.testclient import TestClient

from src import brain_server


def test_openclaw_bridge_status_reports_disabled_when_token_missing(monkeypatch):
    monkeypatch.delenv("NOVA_OPENCLAW_BRIDGE_TOKEN", raising=False)
    monkeypatch.delenv("NOVA_BRIDGE_TOKEN", raising=False)

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/bridge/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["bridge"]["enabled"] is False
    assert payload["bridge"]["status"] == "disabled"


def test_openclaw_bridge_status_reports_enabled_when_token_present(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/bridge/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["bridge"]["enabled"] is True
    assert payload["bridge"]["status"] == "enabled"
    assert payload["connections"]["bridge_enabled"] is True


def test_openclaw_bridge_message_requires_configured_token(monkeypatch):
    monkeypatch.delenv("NOVA_OPENCLAW_BRIDGE_TOKEN", raising=False)
    monkeypatch.delenv("NOVA_BRIDGE_TOKEN", raising=False)

    client = TestClient(brain_server.app)
    response = client.post("/api/openclaw/bridge/message", json={"text": "daily brief"})

    assert response.status_code == 503
    assert "disabled" in response.json()["detail"].lower()


def test_openclaw_bridge_message_rejects_invalid_token(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "daily brief"},
        headers={"X-Nova-Bridge-Token": "wrong-token"},
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_openclaw_bridge_message_blocks_effectful_scope(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "save this"},
        headers={"X-Nova-Bridge-Token": "secret-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["errors"][0]["code"] == "bridge_scope_limited"
    assert "read, review, and reasoning only" in payload["reply"].lower()


def test_openclaw_bridge_message_routes_read_only_request(monkeypatch):
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    async def _fake_run_bridge_messages(_messages):
        return [
            {
                "type": "trust_status",
                "data": {
                    "mode": "Online",
                    "bridge_runtime": {"status_label": "Enabled"},
                },
            },
            {
                "type": "chat",
                "message": "Here is your daily brief.",
                "confidence": "high",
                "suggested_actions": [{"label": "Trust Center", "command": "trust center"}],
            },
            {"type": "chat_done"},
        ]

    monkeypatch.setattr(brain_server, "_run_bridge_messages", _fake_run_bridge_messages)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "daily brief"},
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["reply"] == "Here is your daily brief."
    assert payload["bridge"]["status"] == "enabled"
    assert payload["trust_status"]["bridge_runtime"]["status_label"] == "Enabled"
