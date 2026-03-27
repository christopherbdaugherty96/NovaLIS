from __future__ import annotations

import importlib
from types import SimpleNamespace

from fastapi.testclient import TestClient

from src import brain_server
from src.executors.external_reasoning_executor import ExternalReasoningExecutor
from src.settings.runtime_settings_store import RuntimeSettingsStore


def _install_runtime_settings_store(monkeypatch, tmp_path):
    store = RuntimeSettingsStore(tmp_path / "runtime_settings.json")

    settings_module = importlib.import_module("src.settings.runtime_settings_store")
    diagnostics_module = importlib.import_module("src.executors.os_diagnostics_executor")
    reasoning_module = importlib.import_module("src.executors.external_reasoning_executor")

    monkeypatch.setattr(settings_module, "runtime_settings_store", store)
    monkeypatch.setattr(diagnostics_module, "runtime_settings_store", store)
    monkeypatch.setattr(reasoning_module, "runtime_settings_store", store)
    monkeypatch.setattr(brain_server, "runtime_settings_store", store)
    return store


def test_runtime_settings_api_reports_defaults(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.get("/api/settings/runtime")

    assert response.status_code == 200
    payload = response.json()
    assert payload["settings"]["setup_mode"] == "local"
    assert payload["settings"]["permissions"]["external_reasoning_enabled"] is True
    assert payload["settings"]["permissions"]["remote_bridge_enabled"] is True
    assert payload["settings"]["permissions"]["home_agent_enabled"] is True


def test_runtime_settings_setup_mode_update_changes_snapshot(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/settings/runtime/setup-mode",
        json={"setup_mode": "bring_your_own_key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["settings"]["setup_mode"] == "bring_your_own_key"
    assert payload["connections"]["setup_mode"] == "bring_your_own_key"


def test_runtime_settings_can_pause_remote_bridge(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "secret-token")

    client = TestClient(brain_server.app)
    pause_response = client.post(
        "/api/settings/runtime/permissions",
        json={"permission": "remote_bridge_enabled", "enabled": False},
    )

    assert pause_response.status_code == 200
    payload = pause_response.json()
    assert payload["settings"]["permissions"]["remote_bridge_enabled"] is False
    assert payload["bridge"]["status"] == "paused"

    bridge_response = client.post(
        "/api/openclaw/bridge/message",
        json={"text": "daily brief"},
        headers={"X-Nova-Bridge-Token": "secret-token"},
    )
    assert bridge_response.status_code == 403
    assert "paused in settings" in bridge_response.json()["detail"].lower()


def test_external_reasoning_respects_runtime_permission(monkeypatch, tmp_path):
    store = _install_runtime_settings_store(monkeypatch, tmp_path)
    store.set_permission("external_reasoning_enabled", False, source="test")

    executor = ExternalReasoningExecutor()
    request = SimpleNamespace(capability_id=62, params={"text": "Review this answer."}, request_id="req-1")
    result = executor.execute(request)

    assert result.success is False
    assert "paused in settings" in result.message.lower()
    assert result.structured_data["failure_kind"] == "settings_paused"
