from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_pattern_review_widget_and_hydration():
    source = load_dashboard_runtime_js()

    assert 'case "pattern_review":' in source
    assert "renderPatternReviewWidget(" in source
    assert 'safeWSSend({ text: "pattern status", silent_widget_refresh: true });' in source
    assert 'injectUserText("review patterns", "text")' in source


def test_home_page_includes_pattern_review_controls_in_personal_layer():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-trust"' in source
    assert 'id="trust-center-assistive-summary"' in source
    assert 'id="btn-assistive-notices-refresh"' in source
