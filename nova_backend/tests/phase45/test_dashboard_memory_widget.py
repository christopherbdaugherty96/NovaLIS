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
    assert 'injectUserText("memory list", "text")' in source
    assert "memory list thread ${name}" in source
    assert "memory show ${id}" in source


def test_home_page_includes_memory_overview_widget():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="memory-overview-widget"' in source
    assert 'id="memory-overview-summary"' in source
    assert 'id="memory-overview-tier-row"' in source
    assert 'id="memory-overview-linked"' in source
    assert 'id="memory-overview-recent"' in source
    assert 'id="btn-home-memory-overview"' in source
    assert 'id="btn-home-memory-list"' in source
