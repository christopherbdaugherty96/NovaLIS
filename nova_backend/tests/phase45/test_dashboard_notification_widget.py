from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_notification_widget_and_schedule_modal():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'case "notification_schedule":' in source
    assert "renderNotificationOverviewWidget(" in source
    assert 'safeWSSend({ text: "notification status", silent_widget_refresh: true });' in source
    assert "function showScheduleModal()" in source
    assert 'injectUserText("show schedules", "text")' in source


def test_home_page_includes_notification_widget():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="notification-overview-widget"' in source
    assert 'id="notification-overview-summary"' in source
    assert 'id="notification-overview-due"' in source
    assert 'id="notification-overview-upcoming"' in source
    assert 'id="btn-home-schedules"' in source
    assert 'id="btn-home-schedule-brief"' in source
    assert 'id="btn-home-schedule-reminder"' in source
