from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_screen_and_file_insight_widgets():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert 'case "screen_capture":' in source
    assert 'case "screen_analysis":' in source
    assert 'case "file_explanation":' in source
    assert 'case "thread_map":' in source
    assert 'case "thread_detail":' in source
    assert "renderContextInsight(" in source
    assert "renderThreadMapWidget(" in source
    assert "renderThreadDetailWidget(" in source
    assert "Recent decisions:" in source
    assert "Why this next step:" in source
    assert "Blocked context:" in source
    assert "thread-detail-memory-time" in source
    assert "project status ${name}" in source
    assert "thread detail ${name}" in source
    assert "memory save thread ${name}" in source
    assert "memory list thread ${name}" in source
    assert "memory save decision for ${name}:" in source
    assert "thread-decision-row" in source
    assert "thread-memory-badge" in source
    assert "List memory (${memoryCount})" in source
    assert "Latest decision:" in source
    assert "Last memory update:" in source
    assert "change_summary" in source
    assert "thread-map-change" in source
    assert "which project is most blocked right now" in source
    assert "why this recommendation" in source


def test_home_page_keeps_explain_entry_and_project_thread_surface():
    source = INDEX_PATH.read_text(encoding="utf-8")
    assert 'id="home-launch-widget"' in source
    assert 'id="btn-home-explain"' in source
    assert 'id="btn-home-research"' in source
    assert 'id="btn-home-continue-project"' in source
    assert 'id="thread-map-widget"' in source
    assert 'id="btn-home-threads"' in source
    assert 'id="thread-detail-panel"' in source
    assert 'id="thread-detail-title"' in source
    assert 'id="thread-detail-blocked"' in source
    assert 'id="thread-detail-next"' in source
    assert 'id="thread-detail-decisions"' in source
