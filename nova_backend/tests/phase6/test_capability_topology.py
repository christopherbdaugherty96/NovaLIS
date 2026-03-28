from __future__ import annotations

import json

import pytest

import src.governor.capability_registry as cr
from src.governor.capability_registry import CapabilityRegistry
from src.governor.capability_topology import CapabilityTopology


def test_topology_marks_first_slice_snapshot_capabilities_as_delegatable():
    topology = CapabilityTopology(CapabilityRegistry())

    calendar = topology.get(57)
    system_status = topology.get(32)

    assert calendar.policy_delegatable is True
    assert calendar.authority_class == "read_only_local"
    assert system_status.policy_delegatable is True
    assert topology.is_within_current_limit(57) is True


def test_topology_blocks_network_and_persistent_classes_from_current_limit():
    topology = CapabilityTopology(CapabilityRegistry())

    weather = topology.get(55)
    memory = topology.get(61)
    headline_summary = topology.get(49)
    intelligence_brief = topology.get(50)
    story_update = topology.get(52)
    screen_capture = topology.get(58)

    assert weather.authority_class == "read_only_network"
    assert topology.is_within_current_limit(55) is False
    assert headline_summary.authority_class == "read_only_network"
    assert headline_summary.requires_network_mediator is True
    assert intelligence_brief.authority_class == "read_only_network"
    assert intelligence_brief.requires_network_mediator is True
    assert story_update.authority_class == "persistent_change"
    assert story_update.persistent_change is True
    assert story_update.reversible is False
    assert screen_capture.authority_class == "persistent_change"
    assert screen_capture.persistent_change is True
    assert screen_capture.reversible is False
    assert memory.persistent_change is True
    assert memory.policy_delegatable is False


def test_topology_fails_closed_when_registry_authority_metadata_drifts(monkeypatch, tmp_path):
    registry_data = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {},
        "profiles": {"default": {"groups": [], "enabled_overrides": {}}},
        "capabilities": [
            {
                "id": 57,
                "name": "calendar_snapshot",
                "status": "active",
                "phase_introduced": "4",
                "risk_level": "low",
                "data_exfiltration": False,
                "enabled": True,
                "authority_class": "read_only_network",
                "requires_confirmation": False,
                "reversible": True,
                "external_effect": False,
            }
        ],
    }

    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry_data), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)

    with pytest.raises(ValueError, match="parity mismatch"):
        CapabilityTopology(CapabilityRegistry())
