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
    assert '"capability_truth_surface"' in source or "data.capability_truth_surface" in source
    assert "group.items" in source or 'items' in source
    assert 'setActivePage("chat");' in source
    assert '"What Nova Can Do Right Now"' in source or "capability-surface-summary" in source
    assert "capability groups are available right now" not in source
    assert "No live capability groups are available right now" not in source
    assert "available_on_this_path" in source
    assert "item.exists" in source
    assert "item.enabled" in source
    assert "verification_status" in source
    assert "requires_approval" in source
    assert "authority_class" in source
    assert "availability === true" in source
    assert "button.disabled = true" in source


def test_home_page_includes_capability_surface_widget():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="capability-surface-widget"' in source
    assert 'id="capability-surface-summary"' in source
    assert 'id="capability-surface-groups"' in source
    assert 'id="capability-surface-note"' in source
