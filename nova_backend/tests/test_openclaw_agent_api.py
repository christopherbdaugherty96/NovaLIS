from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from src import brain_server
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
from src.settings.runtime_settings_store import RuntimeSettingsStore
from src.tasks.notification_schedule_store import NotificationScheduleStore
from src.usage.provider_usage_store import ProviderUsageStore


def _install_runtime_settings_store(monkeypatch, tmp_path: Path):
    store = RuntimeSettingsStore(tmp_path / "runtime_settings.json")
    # Fresh usage store with generous budget so tests don't fail due to cross-test token accumulation.
    usage_store = ProviderUsageStore(tmp_path / "provider_usage.json", daily_token_budget=1_000_000)

    settings_module = importlib.import_module("src.settings.runtime_settings_store")
    diagnostics_module = importlib.import_module("src.executors.os_diagnostics_executor")

    monkeypatch.setattr(settings_module, "runtime_settings_store", store)
    monkeypatch.setattr(diagnostics_module, "runtime_settings_store", store)
    monkeypatch.setattr(diagnostics_module, "provider_usage_store", usage_store)
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


def _install_notification_schedule_store(monkeypatch, tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "notification_schedules.json")
    monkeypatch.setattr(brain_server, "NotificationScheduleStore", lambda: store)
    return store


def test_openclaw_agent_status_reports_foundation(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    monkeypatch.delenv("NOVA_OPENCLAW_BRIDGE_TOKEN", raising=False)
    monkeypatch.delenv("NOVA_BRIDGE_TOKEN", raising=False)
    monkeypatch.delenv("NOVA_CALENDAR_ICS_PATH", raising=False)

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/agent/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent"]["status"] == "foundation"
    assert payload["agent"]["status_label"] == "Foundation live"
    assert payload["agent"]["delivery_ready_count"] == 0
    assert payload["agent"]["running_now"] is None
    assert payload["agent"]["scheduler_status_label"] == "Paused"
    assert payload["agent"]["setup"]["status_label"] == "Ready for briefing runs"
    assert payload["agent"]["setup"]["weather_provider_configured"] is False
    assert payload["agent"]["setup"]["calendar_connected"] is False
    assert payload["agent"]["setup"]["remote_bridge_token_configured"] is False
    assert "morning_brief" in payload["agent"]["setup"]["runnable_template_ids"]
    assert "project_snapshot" in payload["agent"]["setup"]["runnable_template_ids"]
    assert "inbox_check" in [item["id"] for item in payload["agent"]["setup"]["blocked_templates"]]
    assert payload["settings"]["permissions"]["home_agent_enabled"] is True
    assert payload["settings"]["permissions"]["home_agent_scheduler_enabled"] is False


def test_openclaw_agent_status_reports_running_now(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    agent_store = _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)
    agent_store.set_active_run(
        {
            "envelope_id": "ENV-ACTIVE",
            "template_id": "morning_brief",
            "title": "Morning Brief",
            "status": "running",
        }
    )

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/agent/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent"]["running_now"]["envelope_id"] == "ENV-ACTIVE"


def test_openclaw_agent_status_reports_connected_setup_inputs(monkeypatch, tmp_path):
    settings_store = _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)
    calendar_path = tmp_path / "calendar.ics"
    calendar_path.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR\n", encoding="utf-8")
    monkeypatch.setenv("WEATHER_API_KEY", "weather-key")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("NOVA_OPENCLAW_BRIDGE_TOKEN", "bridge-token")
    monkeypatch.setenv("NOVA_CALENDAR_ICS_PATH", str(calendar_path))
    settings_store.set_permission("metered_openai_enabled", True, source="test")

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/agent/status")

    assert response.status_code == 200
    payload = response.json()
    setup = payload["agent"]["setup"]
    assert setup["weather_provider_configured"] is True
    assert setup["calendar_connected"] is True
    assert setup["remote_bridge_token_configured"] is True
    assert any(item["label"] == "OpenAI lane" and item["status_label"] == "Available" for item in setup["source_cards"])
    assert any(item["label"] == "Calendar source" and item["status_label"] == "Ready" for item in setup["source_cards"])


def test_openclaw_agent_run_respects_settings_permission(monkeypatch, tmp_path):
    settings_store = _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)
    settings_store.set_permission("home_agent_enabled", False, source="test")

    client = TestClient(brain_server.app)
    response = client.post("/api/openclaw/agent/templates/morning_brief/run")

    assert response.status_code == 403
    assert "paused in settings" in response.json()["detail"].lower()


def test_openclaw_agent_goal_rejects_when_run_is_active(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    agent_store = _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)
    agent_store.set_active_run(
        {
            "envelope_id": "ENV-ACTIVE",
            "template_id": "morning_brief",
            "title": "Morning Brief",
            "status": "running",
        }
    )

    client = TestClient(brain_server.app)
    response = client.post("/api/openclaw/agent/goal", json={"goal": "summarize the workspace"})

    assert response.status_code == 409
    assert "already in progress" in response.json()["detail"].lower()


def test_openclaw_agent_run_returns_manual_brief(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    agent_store = _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)

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


def test_openclaw_agent_schedule_can_be_staged_while_scheduler_is_paused(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/agent/templates/morning_brief/schedule",
        json={"enabled": True},
    )

    assert response.status_code == 200
    payload = response.json()
    morning = next(item for item in payload["agent"]["templates"] if item["id"] == "morning_brief")
    assert morning["schedule_enabled"] is True
    assert morning["next_run_label"].startswith("Next at ")
    assert payload["agent"]["scheduler_permission_enabled"] is False


def test_openclaw_agent_schedule_rejects_template_that_is_not_schedule_ready(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)

    client = TestClient(brain_server.app)
    response = client.post(
        "/api/openclaw/agent/templates/inbox_check/schedule",
        json={"enabled": True},
    )

    assert response.status_code == 409
    assert "not connected yet" in response.json()["detail"].lower()


def test_openclaw_agent_dismisses_delivery_item(monkeypatch, tmp_path):
    _install_runtime_settings_store(monkeypatch, tmp_path)
    agent_store = _install_agent_store(monkeypatch, tmp_path)
    _install_notification_schedule_store(monkeypatch, tmp_path)
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


def test_openclaw_agent_status_includes_scheduler_policy_summary(monkeypatch, tmp_path):
    settings_store = _install_runtime_settings_store(monkeypatch, tmp_path)
    _install_agent_store(monkeypatch, tmp_path)
    notification_store = _install_notification_schedule_store(monkeypatch, tmp_path)
    settings_store.set_permission("home_agent_scheduler_enabled", True, source="test")
    notification_store.update_policy(
        quiet_hours_enabled=True,
        quiet_hours_start="22:00",
        quiet_hours_end="07:00",
        max_deliveries_per_hour=1,
    )

    client = TestClient(brain_server.app)
    response = client.get("/api/openclaw/agent/status")

    assert response.status_code == 200
    payload = response.json()
    assert "Quiet hours:" in payload["agent"]["schedule_summary"]
    scheduler_card = next(item for item in payload["agent"]["setup"]["source_cards"] if item["id"] == "scheduler")
    assert "Rate limit: 1 per hour." in scheduler_card["summary"]
