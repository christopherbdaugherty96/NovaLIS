from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_tone_profile_widget_and_hydration():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'case "tone_profile":' in source
    assert "renderToneOverviewWidget(" in source
    assert 'safeWSSend({ text: "tone status", silent_widget_refresh: true });' in source
    assert "function showToneModal()" in source
    assert 'injectUserText("tone reset all", "text")' in source


def test_home_page_includes_tone_overview_widget():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="tone-overview-widget"' in source
    assert 'id="tone-overview-summary"' in source
    assert 'id="tone-overview-global"' in source
    assert 'id="tone-overview-overrides"' in source
    assert 'id="tone-overview-history"' in source
    assert 'id="btn-home-tone-status"' in source
    assert 'id="btn-home-tone-reset"' in source
