from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
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


def _function_source(source: str, name: str, next_name: str) -> str:
    start = source.index(f"function {name}(")
    end = source.index(f"function {next_name}(", start)
    return source[start:end]


def test_trial_dashboard_behavior_preserves_default_navigation_and_trial_labels():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for dashboard behavior verification")
    source = (REPO_ROOT / "nova_backend" / "static" / "dashboard-control-center.js").read_text(
        encoding="utf-8"
    )
    functions = "\n".join(
        (
            _function_source(source, "applyTrialProfileTruth", "applyRuntimeSettingsPayload"),
            _function_source(source, "renderMorningPanel", "renderContextInsight"),
        )
    )
    script = f"""
const elements = {{
  'weather-widget': {{hidden: false, setAttribute() {{}}}},
  'page-news': {{hidden: true, setAttribute() {{}}}},
  'deepseek-btn': {{hidden: true, setAttribute() {{}}}},
  'morning-weather': {{textContent: ''}},
  'morning-news': {{textContent: ''}},
  'morning-system': {{textContent: ''}},
  'morning-calendar': {{textContent: ''}},
  'btn-morning-calendar-connect': {{hidden: false}},
}};
const bodyClasses = new Set();
const document = {{
  body: {{
    classList: {{
      toggle(name, enabled) {{ if (enabled) bodyClasses.add(name); else bodyClasses.delete(name); }},
      contains(name) {{ return bodyClasses.has(name); }},
    }},
  }},
  querySelector(selector) {{
    if (selector === '.header-right') return {{prepend() {{}}}};
    return {{hidden: true, setAttribute() {{}}}};
  }},
  createElement() {{ return {{hidden: false, className: '', textContent: ''}}; }},
}};
function $(id) {{ return elements[id] || null; }}
const settingsRuntimeState = {{}};
const morningState = {{weather: 'Live weather', news: 'Live news', system: 'Ready', calendar: 'Not connected'}};
{functions}
applyTrialProfileTruth({{trial_mode: false, runtime_profile: 'default'}});
const defaultNewsHidden = elements['page-news'].hidden;
applyTrialProfileTruth({{trial_mode: true, runtime_profile: 'trial'}});
renderMorningPanel();
console.log(JSON.stringify({{
  defaultNewsHidden,
  weather: elements['morning-weather'].textContent,
  news: elements['morning-news'].textContent,
  calendar: elements['morning-calendar'].textContent,
}}));
"""
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    assert payload == {
        "defaultNewsHidden": True,
        "weather": "Not in this trial version",
        "news": "Not in this trial version",
        "calendar": "Not in this trial version",
    }


def test_trial_dashboard_hides_connection_controls():
    source = (REPO_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js").read_text(
        encoding="utf-8"
    )

    assert "settingsRuntimeState.trialMode" in source
    assert "Connections are disabled by the trial profile." in source
