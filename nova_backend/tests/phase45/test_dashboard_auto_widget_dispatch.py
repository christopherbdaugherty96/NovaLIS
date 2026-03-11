from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


def test_websocket_open_hydrates_dashboard_widgets():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onopen\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "hydrateDashboardWidgets()" in body


def test_dashboard_starts_widget_auto_refresh_scheduler():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert "function startWidgetAutoRefresh()" in source
    assert "setInterval(() => {" in source
    assert "WIDGET_AUTO_REFRESH_INTERVAL_MS" in source
    assert "if (!document.hidden) hydrateDashboardWidgets();" in source


def test_dashboard_stops_auto_refresh_on_socket_close():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onclose\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "stopWidgetAutoRefresh()" in body
