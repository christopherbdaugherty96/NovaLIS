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
    assert "renderContextInsight(" in source
    assert "renderThreadMapWidget(" in source
    assert "project status ${name}" in source
    assert "which project is most blocked right now" in source
    assert "why this recommendation" in source


def test_home_page_includes_context_insight_widget():
    source = INDEX_PATH.read_text(encoding="utf-8")
    assert 'id="context-insight-widget"' in source
    assert 'id="btn-home-explain"' in source
    assert 'id="btn-home-help"' in source
    assert 'id="thread-map-widget"' in source
    assert 'id="btn-home-threads"' in source
