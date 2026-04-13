from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_memory_overview_widget_and_hydration():
    source = load_dashboard_runtime_js()

    assert 'case "memory_overview":' in source
    assert 'case "memory_list":' in source
    assert 'case "memory_item":' in source
    assert "renderMemoryOverviewWidget(" in source
    assert "renderMemoryListWidget(" in source
    assert "renderMemoryItemWidget(" in source
    assert 'safeWSSend({ text: "memory overview", silent_widget_refresh: true });' in source
    assert 'sendSilentMemoryCommand("memory overview")' in source
    assert 'sendSilentMemoryCommand("list memories")' in source
    assert 'sendSilentMemoryCommand("recent memories")' in source
    assert 'sendSilentMemoryCommand(`memory show ${item.id}`)' in source
    assert "memory list thread ${name}" in source
    assert 'injectUserText(`edit memory ${selected.id}: ${nextValue}`, "text")' in source
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
    assert 'id="memory-center-status"' in source
    assert 'id="memory-list-host"' in source
    assert 'id="memory-detail-host"' in source
    assert 'id="memory-edit-input"' in source
    assert 'id="btn-memory-list-all"' in source
    assert 'id="btn-memory-detail-edit"' in source
    assert 'id="btn-memory-overview"' in source
    assert 'id="btn-memory-list"' in source
    assert 'id="btn-memory-recent"' in source
    assert 'id="home-launch-widget"' in source
    assert 'id="home-launch-actions"' in source
