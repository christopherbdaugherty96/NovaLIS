from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_tone_profile_widget_and_hydration():
    source = load_dashboard_runtime_js()

    assert 'case "tone_profile":' in source
    assert "renderToneOverviewWidget(" in source
    assert 'safeWSSend({ text: "tone status", silent_widget_refresh: true });' in source
    assert "function showToneModal()" in source
    assert 'injectUserText("tone reset all", "text")' in source


def test_home_page_includes_tone_controls_in_personal_layer():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-settings"' in source
    assert 'id="settings-voice-summary"' in source
    assert 'id="settings-permission-grid"' in source
    assert 'id="btn-settings-refresh-runtime"' in source
