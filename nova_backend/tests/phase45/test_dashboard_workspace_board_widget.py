from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_workspace_board_and_structure_map():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "function requestProjectStructureMapRefresh(force = false)" in source
    assert 'safeWSSend({ text: "show structure map", silent_widget_refresh: true });' in source
    assert "function renderProjectStructureMapWidget(data = {})" in source
    assert "function renderWorkspaceBoardPage()" in source
    assert 'setActivePage("workspace")' in source
    assert '"workspace board"' in source


def test_workspace_page_includes_board_and_structure_map_surfaces():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-workspace"' in source
    assert 'id="workspace-board-summary"' in source
    assert 'id="workspace-board-focus"' in source
    assert 'id="workspace-board-stats"' in source
    assert 'id="workspace-board-threads"' in source
    assert 'id="workspace-board-feed"' in source
    assert 'id="workspace-board-actions"' in source
    assert 'id="btn-workspace-board-refresh"' in source
    assert 'id="btn-workspace-board-threads"' in source
    assert 'id="btn-workspace-board-visual"' in source
    assert 'id="btn-workspace-board-architecture"' in source
    assert 'id="project-structure-summary"' in source
    assert 'id="project-structure-tree"' in source
    assert 'id="project-structure-highlights"' in source
    assert 'id="project-structure-note"' in source
    assert 'id="project-structure-actions"' in source
