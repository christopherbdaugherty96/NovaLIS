from __future__ import annotations

from pathlib import Path

from src.api.settings_api import _runtime_settings_payload

REPO_ROOT = Path(__file__).resolve().parents[2]


class _Store:
    @staticmethod
    def snapshot():
        return {"permission_cards": []}


class _Startup:
    @staticmethod
    def status():
        return {"enabled": False, "entry_exists": False}


class _Diagnostics:
    @staticmethod
    def _runtime_health_projection():
        return {}

    @staticmethod
    def _bridge_status_details():
        return {}

    @staticmethod
    def _connection_status_details():
        return {}

    @staticmethod
    def _external_reasoning_status_details():
        return {}

    @staticmethod
    def _openai_status_details():
        return {}


class _Deps:
    runtime_settings_store = _Store()
    windows_startup_registration = _Startup()
    OSDiagnosticsExecutor = _Diagnostics


def test_runtime_settings_payload_exposes_trial_profile(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")

    payload = _runtime_settings_payload(_Deps())

    assert payload["runtime_profile"] == "trial"
    assert payload["trial_mode"] is True
    assert payload["trial_truth"] == {
        "outside_connections": "disabled_by_profile",
        "cost": "no_provider_usage",
    }


def test_dashboard_labels_disabled_trial_surfaces():
    source = (REPO_ROOT / "nova_backend" / "static" / "dashboard-control-center.js").read_text(
        encoding="utf-8"
    )

    assert 'document.body.classList.toggle("trial-profile"' in source
    assert '"Not in this trial version"' in source
    assert '"Trial mode: outside connections are disabled by profile; provider cost is $0."' in source
    assert '$("weather-widget")' in source
    assert '$("page-news")' in source
    assert '$("deepseek-btn")' in source
