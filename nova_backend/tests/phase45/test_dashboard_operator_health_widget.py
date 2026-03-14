from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_operator_health_widget_from_system_status():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "let operatorHealthState" in source
    assert "function renderOperatorHealthWidget(data = {})" in source
    assert 'case "system":' in source
    assert "renderOperatorHealthWidget(msg.data || {});" in source
    assert '"operator_health_summary"' in source or "operatorHealthState.summary" in source
    assert '"System Reason"' in source or "System Reason" in source


def test_home_page_includes_operator_health_surface():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="operator-health-widget"' in source
    assert 'id="operator-health-summary"' in source
    assert 'id="operator-health-grid"' in source
    assert 'id="operator-health-locks"' in source
    assert 'id="operator-health-reasons"' in source
    assert 'id="btn-home-system-status"' in source
