from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


def test_brief_labeled_shortcuts_use_daily_brief_command():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert '{ id: "chat_brief", label: "Today\'s brief", command: "daily brief" }' in source
    assert '{ id: "news_brief", label: "Daily brief", command: "daily brief", stayOnPage: true }' in source
    assert '{ label: "Today\'s brief", command: "daily brief" }' in source


def test_source_grounded_brief_entry_still_uses_todays_news():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert '{ id: "news_sum", label: "Source brief", command: "today\'s news", switchToPage: "chat" }' in source
    assert 'injectUserText("today\'s news", "text")' in source
