from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_notification_widget_and_schedule_modal():
    source = load_dashboard_runtime_js()

    assert 'case "notification_schedule":' in source
    assert "renderNotificationOverviewWidget(" in source
    assert 'safeWSSend({ text: "notification status", silent_widget_refresh: true });' in source
    assert "function showScheduleModal()" in source
    assert 'injectUserText("show schedules", "text")' in source


def test_home_page_includes_schedule_controls_in_personal_layer():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="home-launch-widget"' in source
    assert 'id="home-launch-actions"' in source
