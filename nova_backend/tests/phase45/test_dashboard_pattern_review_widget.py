from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_pattern_review_widget_and_hydration():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'case "pattern_review":' in source
    assert "renderPatternReviewWidget(" in source
    assert 'safeWSSend({ text: "pattern status", silent_widget_refresh: true });' in source
    assert 'injectUserText("review patterns", "text")' in source


def test_home_page_includes_pattern_review_controls_in_personal_layer():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="personal-layer-widget"' in source
    assert 'id="btn-home-pattern-status"' in source
