from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
CHAT_NEWS_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"
CONTROL_CENTER_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-control-center.js"


def test_dashboard_defines_canonical_runtime_health_reducer():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'const RUNTIME_HEALTH_STATES = ["Healthy", "Connecting", "Degraded", "Unavailable", "Recovering"];' in source
    assert "function resolveCanonicalRuntimeHealth(overrides = {})" in source
    assert "HTTP timeout" not in source  # copy belongs in docs, reducer uses concrete signals
    assert "runtimeHealthState.httpTimedOut || overrides.httpTimedOut" in source
    assert 'manualTurnTerminalState === "Timed Out"' in source
    assert 'return { tone: "degraded", label: "Unavailable" };' in source
    assert 'return { tone: "connected", label: "Healthy" };' in source


def test_dashboard_health_probe_uses_existing_read_only_runtime_settings_endpoint():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "function probeRuntimeHealthOnce()" in source
    assert 'fetch(`${API_BASE}/api/settings/runtime`' in source
    assert "RUNTIME_HEALTH_PROBE_TIMEOUT_MS" in source
    assert "markRuntimeHealthProbeFailure" in source
    assert "markRuntimeHealthProbeSuccess" in source


def test_chat_turn_timeout_is_terminal_and_checks_runtime_health():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert "function scheduleManualTurnTimeout(turnId)" in source
    assert "MANUAL_TURN_TIMEOUT_MS" in source
    assert 'clearActiveManualTurn("Timed Out"' in source
    assert "Nothing new was confirmed." in source
    assert "Retry after checking status" in source
    assert "probeRuntimeHealthOnce" in source


def test_trust_surfaces_consume_canonical_runtime_health():
    source = CONTROL_CENTER_PATH.read_text(encoding="utf-8")

    assert "runtimeHealthState.state !== \"Healthy\"" in source
    assert "runtimeHealthState.whatNext" in source
    assert '["Health", runtimeHealthState.state]' in source
    assert '["Next", runtimeHealthState.whatNext]' in source
