from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_trust_center_page_from_runtime_state():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "function renderTrustCenterPage()" in source
    assert "function requestSettingsRuntimeRefresh(force = false)" in source
    assert "function setRuntimePermission(permission, enabled)" in source
    assert 'safeWSSend({ text: "trust center", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "system status", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "operational context", silent_widget_refresh: true });' in source
    assert "renderTrustCenterPage();" in source
    assert "trust-center-voice-grid" in source
    assert "trust-center-operational-grid" in source
    assert "trust-center-assistive-list" in source
    assert "trust-center-assistive-handled" in source
    assert "renderHandledList" in source
    assert "No handled assistive notices are recorded in the current continuity window." in source
    assert "Use this page to confirm what Nova did, what it refused, and whether anything left the device." in source
    assert "OpenClaw is Nova's worker layer for manual, reviewable runs." in source
    assert "Most provider keys and connector logins are still configured manually today." in source
    assert "trust-center-reasoning-grid" in source
    assert "trust-center-bridge-grid" in source
    assert "Estimated tokens today" in source
    assert "Budget state" in source
    assert "Bottom line" in source
    assert "Main gap" in source
    assert "Best correction" in source
    assert "settings-reasoning-grid" in source
    assert "settings-assistive-grid" in source
    assert "settings-connection-grid" in source
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
    assert 'id="trust-center-activity-detail"' in source
    assert 'id="trust-center-blocked"' in source
    assert 'id="trust-center-blocked-detail"' in source
    assert 'id="trust-center-health-summary"' in source
    assert 'id="trust-center-health-grid"' in source
    assert 'id="trust-center-operational-summary"' in source
    assert 'id="trust-center-operational-grid"' in source
    assert 'id="trust-center-assistive-summary"' in source
    assert 'id="trust-center-assistive-list"' in source
    assert 'id="trust-center-assistive-handled"' in source
    assert 'id="trust-center-voice-summary"' in source
    assert 'id="trust-center-voice-grid"' in source
    assert 'id="trust-center-reasoning-summary"' in source
    assert 'id="trust-center-reasoning-grid"' in source
    assert 'id="trust-center-bridge-summary"' in source
    assert 'id="trust-center-bridge-grid"' in source
    assert 'id="trust-center-capability-summary"' in source
    assert 'id="trust-center-capability-groups"' in source
    assert 'id="settings-reasoning-summary"' in source
    assert 'id="settings-reasoning-grid"' in source
    assert 'id="settings-assistive-summary"' in source
    assert 'id="settings-assistive-grid"' in source
    assert 'id="settings-connection-summary"' in source
    assert 'id="settings-connection-grid"' in source
    assert "Trust Center shows what Nova did, what it refused, what left the device, and what may need your attention." in source
    assert "A quick answer to whether Nova stayed local, called anything external, or hit a problem." in source
    assert "See where Nova stopped instead of guessing or pushing past a boundary." in source
    assert "OpenClaw is Nova's worker layer for manual, reviewable runs. It stays visible, bounded, and permission-first." in source
    assert "What is connected now is visible here. Most provider keys and connector logins are still configured manually today, and that setup should remain explicit and governed." in source
    assert 'id="btn-trust-center-refresh"' in source
    assert 'id="btn-trust-center-system"' in source
    assert 'id="btn-trust-center-workspace"' in source
    assert 'id="btn-trust-center-memory"' in source
    assert 'id="btn-trust-center-bridge-status"' in source
    assert 'id="btn-trust-center-voice-check"' in source
    assert 'id="btn-trust-center-settings"' in source
    assert 'id="btn-operational-context-refresh"' in source
    assert 'id="btn-operational-context-reset"' in source
    assert 'id="btn-assistive-notices-refresh"' in source
    assert 'id="btn-assistive-open-settings"' in source
