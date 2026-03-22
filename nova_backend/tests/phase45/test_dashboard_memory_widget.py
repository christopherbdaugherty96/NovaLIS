from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_memory_overview_widget_and_hydration():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'case "memory_overview":' in source
    assert "renderMemoryOverviewWidget(" in source
    assert 'safeWSSend({ text: "memory overview", silent_widget_refresh: true });' in source
    assert 'injectUserText("memory overview", "text")' in source
    assert 'injectUserText("list memories", "text")' in source
    assert "memory list thread ${name}" in source
    assert "memory show ${id}" in source
    assert 'Number(scopes.nova_core || scopes.general || 0)' in source


def test_dashboard_includes_dedicated_memory_page_and_home_summary():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-memory"' in source
    assert 'id="memory-overview-widget"' in source
    assert 'id="memory-page-summary"' in source
    assert 'id="memory-overview-summary"' in source
    assert 'id="memory-overview-tier-row"' in source
    assert 'id="memory-overview-scope-row"' in source
    assert 'id="memory-overview-linked"' in source
    assert 'id="memory-overview-recent"' in source
    assert 'id="btn-memory-overview"' in source
    assert 'id="btn-memory-list"' in source
    assert 'id="personal-layer-widget"' in source
    assert 'id="btn-home-memory-page"' in source
