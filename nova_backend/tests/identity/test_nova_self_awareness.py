"""Tests for Nova self-awareness context builder."""

from src.identity.nova_self_awareness import (
    build_self_awareness_block,
    _identity_block,
    _tools_block,
    _status_block,
)


def test_identity_block_contains_nova():
    block = _identity_block()
    assert "Nova" in block
    assert "real" in block.lower()
    assert "not" in block.lower()


def test_tools_block_lists_registered_tools():
    block = _tools_block()
    assert "weather" in block.lower()
    assert "calendar" in block.lower()
    assert "volume" in block.lower()
    assert "web_search" in block.lower() or "web search" in block.lower()


def test_status_block_has_platform_and_model():
    block = _status_block()
    assert "Running on" in block
    assert "Uptime" in block
    assert "model" in block.lower()


def test_full_block_assembles_all_sections():
    block = build_self_awareness_block()
    assert "WHO YOU ARE" in block
    assert "TOOLS" in block or "CAPABILITIES" in block
    assert "STATUS" in block
    # Should be substantial — not just a few lines
    assert len(block) > 200


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
