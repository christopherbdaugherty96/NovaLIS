from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from src import brain_server
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
from src.settings.runtime_settings_store import RuntimeSettingsStore


def _install_runtime_settings_store(monkeypatch, tmp_path: Path):
    store = RuntimeSettingsStore(tmp_path / "runtime_settings.json")

    settings_module = importlib.import_module("src.settings.runtime_settings_store")
    diagnostics_module = importlib.import_module("src.executors.os_diagnostics_executor")

    monkeypatch.setattr(settings_module, "runtime_settings_store", store)
    monkeypatch.setattr(diagnostics_module, "runtime_settings_store", store)
    monkeypatch.setattr(brain_server, "runtime_settings_store", store)
    return store


def _install_agent_store(monkeypatch, tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runtime_module = importlib.import_module("src.openclaw.agent_runtime_store")
    diagnostics_module = importlib.import_module("src.executors.os_diagnostics_executor")
    monkeypatch.setattr(runtime_module, "openclaw_agent_runtime_store", store)
    monkeypatch.setattr(diagnostics_module, "openclaw_agent_runtime_store", store)
    monkeypatch.setattr(brain_server, "openclaw_agent_runtime_store", store)
    return store


def test_openclaw_agent_status_reports_foundation(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/agent/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent"]["status"] == "foundation"
    assert payload["agent"]["status_label"] == "Foundation live"
    assert payload["agent"]["delivery_ready_count"] == 0
    assert payload["settings"]["permissions"]["home_agent_enabled"] is True


def test_openclaw_agent_run_respects_settings_permission(monkeypatch, tmp_path):
    settings_store = _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    settings_store.set_permission("home_agent_enabled", False, source="test")

    client = TestClient(brain_server.app)
    response = client.post("/api/openclaw/agent/templates/morning_brief/run")

    assert response.status_code == 403
    assert "paused in settings" in response.json()["detail"].lower()


def test_openclaw_agent_run_returns_manual_brief(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    agent_store = _install_agent_store(monkeypatch, tmp_path)

    class _FakeRunner:
        async def run_template(self, template_id: str, *, triggered_by: str = "dashboard"):
            record = agent_store.record_run(
                {
                    "envelope_id": "ENV-123",
                    "template_id": template_id,
                    "title": "Morning Brief",
                    "status": "completed",
                    "triggered_by": triggered_by,
                    "delivery_mode": "hybrid",
                    "delivery_channels": {"widget": True, "chat": True},
                    "presented_message": "Here's your morning. Clear skies and one meeting at 10.",
                    "summary": "Clear skies and one meeting at 10.",
                    "started_at": "2026-03-26T12:00:00+00:00",
                    "completed_at": "2026-03-26T12:00:05+00:00",
                    "llm_summary_used": True,
                    "estimated_input_tokens": 120,
                    "estimated_output_tokens": 40,
                    "estimated_total_tokens": 160,
                }
            )
            return {
                "envelope": {"id": "ENV-123"},
                "delivery_channels": {"widget": True, "chat": True},
                "presented_message": "Here's your morning. Clear skies and one meeting at 10.",
                "llm_summary_used": True,
                "estimated_total_tokens": 160,
                "run_record": record,
            }

    monkeypatch.setattr(brain_server, "openclaw_agent_runner", _FakeRunner())

    client = TestClient(brain_server.app)
    response = client.post("/api/openclaw/agent/templates/morning_brief/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["run"]["delivery_channels"]["chat"] is True
    assert payload["run"]["presented_message"].startswith("Here's your morning.")
    assert payload["agent"]["recent_runs"][0]["template_id"] == "morning_brief"
    assert payload["agent"]["delivery_ready_count"] == 1


def test_openclaw_agent_dismisses_delivery_item(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    agent_store = _install_agent_store(monkeypatch, tmp_path)
    run = agent_store.record_run(
        {
            "envelope_id": "ENV-123",
            "template_id": "morning_brief",
            "title": "Morning Brief",
            "delivery_mode": "hybrid",
            "delivery_channels": {"widget": True, "chat": True},
            "presented_message": "Here's your morning. Clear skies and one meeting at 10.",
            "summary": "Clear skies and one meeting at 10.",
        }
    )
    delivery_id = agent_store.snapshot()["delivery_inbox"][0]["id"]

    client = TestClient(brain_server.app)
    response = client.post(f"/api/openclaw/agent/delivery/{delivery_id}/dismiss")

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent"]["delivery_ready_count"] == 0
    assert run["template_id"] == "morning_brief"
