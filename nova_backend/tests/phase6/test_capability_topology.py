from __future__ import annotations

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

    assert weather.authority_class == "read_only_network"
    assert topology.is_within_current_limit(55) is False
    assert memory.persistent_change is True
    assert memory.policy_delegatable is False
