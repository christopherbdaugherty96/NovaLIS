from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHAT_NEWS_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"


def test_websocket_open_hydrates_dashboard_widgets():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onopen\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "startWidgetAutoRefresh()" in body
    assert "scheduleStartupHydration()" in body


def test_dashboard_starts_widget_auto_refresh_scheduler():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    assert "function startWidgetAutoRefresh()" in source
    assert "setInterval(() => {" in source
    assert "WIDGET_AUTO_REFRESH_INTERVAL_MS" in source
    assert "if (!document.hidden) hydrateDashboardWidgets();" in source


def test_dashboard_stops_auto_refresh_on_socket_close():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onclose\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "stopWidgetAutoRefresh()" in body


def test_dashboard_hydration_dispatch_includes_ui_invocation_source():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    assert 'function requestInlineAssistantAction(text, statusText = "", invocationSource = "ui_surface")' in source
    assert 'safeWSSend({ text: clean, invocation_source: invocationSource }, { queueIfUnavailable: true })' in source
