"""Tests for Nova self-awareness context builder."""

from src.identity.nova_self_awareness import (
    _identity_block,
    _status_block,
    _tools_block,
    build_self_awareness_block,
)


def test_identity_block_contains_nova():
    block = _identity_block()
    assert "Nova" in block
    assert "real" in block.lower()
    assert "not" in block.lower()


def test_tools_block_lists_registered_tools():
    block = _tools_block()
    assert "weather" in block.lower()
    assert "news" in block.lower()
    assert "web_search" in block.lower() or "web search" in block.lower()
    assert "volume" not in block.lower()
    assert "brightness" not in block.lower()
    assert "open_webpage" not in block.lower()
    assert "calendar" not in block.lower()
    assert "not authorization" in block.lower()


def test_status_block_has_platform_and_model():
    block = _status_block()
    assert "Running on" in block
    assert "Uptime" in block
    assert "model" in block.lower()


def test_status_block_does_not_turn_permission_settings_into_availability(monkeypatch):
    from src.settings.runtime_settings_store import runtime_settings_store

    monkeypatch.setattr(runtime_settings_store, "is_permission_enabled", lambda _name: True)

    block = _status_block()
    assert "External reasoning permission setting: enabled" in block
    assert "External reasoning: available" not in block
    assert "Home agent: active" not in block


def test_full_block_assembles_all_sections():
    block = build_self_awareness_block()
    assert "WHO YOU ARE" in block
    assert "TOOLS" in block or "CAPABILITIES" in block
    assert "STATUS" in block
    # Should be substantial — not just a few lines
    assert len(block) > 200


def test_capability_block_uses_shared_truth_dimensions():
    block = build_self_awareness_block()
    assert "configured=" in block
    assert "verification=" in block
    assert "available_here=" in block
    assert "approval_required=" in block
    assert "authority=" in block
    assert "authorized=" not in block


def test_full_block_does_not_crash_on_missing_dependencies():
    """Even if some subsystems fail, the block should still return something."""
    block = build_self_awareness_block()
    assert isinstance(block, str)
    assert len(block) > 0


def test_full_block_refreshes_volatile_sections_each_call(monkeypatch):
    state = {"connected": True}

    monkeypatch.setattr(
        "src.identity.nova_self_awareness._stable_sections",
        lambda: ["WHO YOU ARE RIGHT NOW:\nYou are Nova."],
    )
    monkeypatch.setattr(
        "src.identity.nova_self_awareness._status_block",
        lambda: "YOUR CURRENT STATUS:\n  - Model status: ready",
    )

    def fake_connections():
        status = "connected" if state["connected"] else "disconnected"
        return f"YOUR CONNECTIONS:\n  - Brave Search: {status}"

    monkeypatch.setattr("src.identity.nova_self_awareness._connections_block", fake_connections)

    block_one = build_self_awareness_block()
    assert "Brave Search: connected" in block_one

    state["connected"] = False
    block_two = build_self_awareness_block()
    assert "Brave Search: disconnected" in block_two
    assert block_one != block_two


def test_connection_block_does_not_promote_configuration_to_connection(monkeypatch):
    from src.connections.connections_store import connections_store
    from src.identity.nova_self_awareness import _connections_block

    monkeypatch.setattr(
        connections_store,
        "snapshot",
        lambda: [
            {
                "id": "brave",
                "label": "Brave Search",
                "has_key": True,
                "health_ok": None,
            }
        ],
    )

    block = _connections_block()
    assert "configured; provider health unverified" in block
    assert "connected" not in block.lower()
