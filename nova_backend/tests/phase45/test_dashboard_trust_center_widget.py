from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_trust_center_page_from_runtime_state():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "function renderTrustCenterPage()" in source
    assert 'safeWSSend({ text: "trust center", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "system status", silent_widget_refresh: true });' in source
    assert "renderTrustCenterPage();" in source
    assert '"trust"' in source


def test_trust_page_includes_recent_actions_and_runtime_health_surfaces():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-trust"' in source
    assert 'id="trust-center-summary"' in source
    assert 'id="trust-center-mode"' in source
    assert 'id="trust-center-last-call"' in source
    assert 'id="trust-center-egress"' in source
    assert 'id="trust-center-failure"' in source
    assert 'id="trust-center-activity"' in source
    assert 'id="trust-center-blocked"' in source
    assert 'id="trust-center-health-summary"' in source
    assert 'id="trust-center-health-grid"' in source
    assert 'id="trust-center-capability-summary"' in source
    assert 'id="trust-center-capability-groups"' in source
    assert 'id="btn-trust-center-refresh"' in source
    assert 'id="btn-trust-center-system"' in source
    assert 'id="btn-trust-center-workspace"' in source
    assert 'id="btn-trust-center-memory"' in source
