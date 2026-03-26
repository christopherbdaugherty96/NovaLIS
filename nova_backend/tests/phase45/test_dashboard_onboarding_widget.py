from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_boots_first_run_guide_with_product_surfaces():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "function showFirstRunGuide(force = false)" in source
    assert "function showFirstRunGuideIfNeeded()" in source
    assert "showFirstRunGuideIfNeeded();" in source
    assert "Open Workspace" in source
    assert "Open Trust" in source
    assert "invocation-bound" in source
    assert 'showFirstRunGuide(true)' in source


def test_home_page_includes_workspace_and_trust_launch_buttons():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="btn-home-workspace-page"' in source
    assert 'id="btn-home-trust-page"' in source
