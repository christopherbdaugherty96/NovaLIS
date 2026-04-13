from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_capability_surface_widget_from_system_status():
    source = load_dashboard_runtime_js()

    assert "let capabilityDiscoveryState" in source
    assert "function renderCapabilitySurfaceWidget(data = {})" in source
    assert "function runCapabilityPrompt(prompt)" in source
    assert 'case "system":' in source
    assert "renderCapabilitySurfaceWidget(msg.data || {});" in source
    assert '"available_capability_surface"' in source or "data.available_capability_surface" in source
    assert "group.items" in source or 'items' in source
    assert 'setActivePage("chat");' in source
    assert '"What Nova Can Do Right Now"' in source or "capability-surface-summary" in source


def test_home_page_includes_capability_surface_widget():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="capability-surface-widget"' in source
    assert 'id="capability-surface-summary"' in source
    assert 'id="capability-surface-groups"' in source
    assert 'id="capability-surface-note"' in source
