from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_index_no_longer_shows_calendar_coming_soon_placeholder():
    source = INDEX_PATH.read_text(encoding="utf-8").lower()
    assert "morning-calendar" in source
    assert "coming soon" not in source


def test_dashboard_handles_calendar_widget_messages():
    source = load_dashboard_runtime_js()
    assert 'case "calendar"' in source
    assert "morningState.calendar" in source
