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


class _FakeScheduler:
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self._ledger_logger = None

    async def start(self) -> None:
        self.start_calls += 1

    async def stop(self) -> None:
        self.stop_calls += 1


def _install_fake_scheduler(monkeypatch) -> _FakeScheduler:
    scheduler = _FakeScheduler()
    monkeypatch.setattr(brain_server, "openclaw_agent_scheduler", scheduler)
    return scheduler


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
    assert payload["settings"]["permissions"]["home_agent_scheduler_enabled"] is False
    assert payload["settings"]["permissions"]["metered_openai_enabled"] is False
    assert payload["settings"]["provider_policy"]["routing_mode"] == "local_first"
    assert payload["settings"]["usage_budget"]["daily_metered_token_budget"] == 4000
    assert payload["settings"]["assistive_policy"]["assistive_notice_mode"] == "suggestive"


def test_runtime_settings_api_rejects_non_local_host(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/settings/runtime/permissions",
        json={"permission": "remote_bridge_enabled", "enabled": False},
        headers={"Host": "evil.example"},
    )

    assert response.status_code == 403
    assert "loopback host" in response.json()["detail"].lower()


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


def test_runtime_settings_permission_updates_sync_openclaw_scheduler(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    scheduler = _install_fake_scheduler(monkeypatch)
    monkeypatch.setattr(
        brain_server,
        "write_current_runtime_state_snapshot",
        lambda: tmp_path / "CURRENT_RUNTIME_STATE.md",
    )

    with TestClient(brain_server.app) as client:
        enable_response = client.post(
            "/api/settings/runtime/permissions",
            json={"permission": "home_agent_scheduler_enabled", "enabled": True},
        )

        assert enable_response.status_code == 200
        assert enable_response.json()["settings"]["permissions"]["home_agent_scheduler_enabled"] is True
        assert scheduler.start_calls == 1
        assert scheduler.stop_calls == 0

        disable_response = client.post(
            "/api/settings/runtime/permissions",
            json={"permission": "home_agent_scheduler_enabled", "enabled": False},
        )

        assert disable_response.status_code == 200
        assert disable_response.json()["settings"]["permissions"]["home_agent_scheduler_enabled"] is False
        assert scheduler.start_calls == 1
        assert scheduler.stop_calls == 1


def test_runtime_settings_lifespan_keeps_scheduler_dormant_until_enabled(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    scheduler = _install_fake_scheduler(monkeypatch)
    monkeypatch.setattr(
        brain_server,
        "write_current_runtime_state_snapshot",
        lambda: tmp_path / "CURRENT_RUNTIME_STATE.md",
    )

    with TestClient(brain_server.app):
        assert scheduler.start_calls == 0
        assert scheduler.stop_calls == 0

    assert scheduler.start_calls == 0
    assert scheduler.stop_calls == 1


def test_runtime_settings_lifespan_starts_scheduler_after_explicit_enable(monkeypatch, tmp_path):
    store = _install_runtime_settings_store(monkeypatch, tmp_path)
    store.set_permission("home_agent_scheduler_enabled", True, source="test")
    scheduler = _install_fake_scheduler(monkeypatch)
    monkeypatch.setattr(
        brain_server,
        "write_current_runtime_state_snapshot",
        lambda: tmp_path / "CURRENT_RUNTIME_STATE.md",
    )

    with TestClient(brain_server.app):
        assert scheduler.start_calls == 1
        assert scheduler.stop_calls == 0

    assert scheduler.start_calls == 1
    assert scheduler.stop_calls == 1


def test_runtime_settings_provider_policy_update_changes_snapshot(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/settings/runtime/provider-policy",
        json={"routing_mode": "explicit_openai", "preferred_openai_model": "gpt-5.4"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["settings"]["provider_policy"]["routing_mode"] == "explicit_openai"
    assert payload["settings"]["provider_policy"]["preferred_openai_model"] == "gpt-5.4"
    assert payload["openai"]["routing_mode"] == "explicit_openai"


def test_runtime_settings_usage_budget_update_changes_snapshot(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/settings/runtime/usage-budget",
        json={"daily_metered_token_budget": 12000, "warning_ratio": 0.9},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["settings"]["usage_budget"]["daily_metered_token_budget"] == 12000
    assert payload["settings"]["usage_budget"]["warning_ratio"] == 0.9
    assert payload["openai"]["daily_budget_tokens"] == 12000


def test_runtime_settings_assistive_mode_update_changes_snapshot(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/settings/runtime/assistive-mode",
        json={"assistive_notice_mode": "workflow_assist"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["settings"]["assistive_policy"]["assistive_notice_mode"] == "workflow_assist"


def test_external_reasoning_respects_runtime_permission(monkeypatch, tmp_path):
    store = _install_runtime_settings_store(monkeypatch, tmp_path)
    store.set_permission("external_reasoning_enabled", False, source="test")

    executor = ExternalReasoningExecutor()
    request = SimpleNamespace(capability_id=62, params={"text": "Review this answer."}, request_id="req-1")
    result = executor.execute(request)

    assert result.success is False
    assert "paused in settings" in result.message.lower()
    assert result.structured_data["failure_kind"] == "settings_paused"
