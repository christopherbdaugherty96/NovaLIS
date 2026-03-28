from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_workspace_home_widget_and_hydration():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "let workspaceHomeState" in source
    assert "let operationalContextState" in source
    assert "let assistiveNoticeState" in source
    assert "function requestWorkspaceHomeRefresh(force = false)" in source
    assert "function requestOperationalContextRefresh(force = false)" in source
    assert "function requestAssistiveNoticesRefresh(force = false)" in source
    assert 'safeWSSend({ text: "workspace home", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "operational context", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "assistive notices", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "show threads", silent_widget_refresh: true });' in source
    assert 'case "workspace_home":' in source
    assert 'case "operational_context":' in source
    assert 'case "assistive_notices":' in source
    assert "function renderWorkspaceHomeWidget(data = {})" in source
    assert "function renderOperationalContextWidget(data = {})" in source
    assert "function renderAssistiveNoticesWidget(data = {})" in source
    assert 'requestWorkspaceHomeRefresh(true);' in source
    assert 'renderWorkspaceHomeWidget({});' in source


def test_home_page_includes_workspace_home_surface():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="workspace-home-widget"' in source
    assert 'id="workspace-home-summary"' in source
    assert 'id="workspace-home-focus"' in source
    assert 'id="workspace-home-grid"' in source
    assert 'id="workspace-home-docs"' in source
    assert 'id="workspace-home-operational"' in source
    assert 'id="workspace-home-assistive"' in source
    assert 'id="workspace-home-actions"' in source
    assert 'id="btn-workspace-home-refresh"' in source
