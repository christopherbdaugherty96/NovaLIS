from __future__ import annotations

import json
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "src" / "config" / "registry.json"


def test_registry_phase_matches_expected_phase():
    """Registry phase field must match EXPECTED_PHASE in capability_registry.py."""
    from src.governor.capability_registry import EXPECTED_PHASE

    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert raw["phase"] == EXPECTED_PHASE, (
        f"registry.json phase '{raw['phase']}' does not match "
        f"capability_registry.EXPECTED_PHASE '{EXPECTED_PHASE}'"
    )


def test_registry_phase_is_current_build_phase():
    """Registry and expected phase must both reflect build phase 8."""
    from src.governor.capability_registry import EXPECTED_PHASE
    from src.build_phase import BUILD_PHASE

    assert EXPECTED_PHASE == str(BUILD_PHASE), (
        f"EXPECTED_PHASE '{EXPECTED_PHASE}' does not match BUILD_PHASE '{BUILD_PHASE}'"
    )


def test_registry_loads_without_phase_error():
    """CapabilityRegistry and CapabilityTopology must both initialise cleanly.

    Topology init is fail-closed: it raises ValueError if any active capability
    lacks a _TOPOLOGY_OVERRIDES entry, so a successful round-trip proves every
    active capability has been classified.  The count assertion is intentionally
    absent — it would break every time a new capability is added.
    """
    from src.governor.capability_registry import CapabilityRegistry
    from src.governor.capability_topology import CapabilityTopology

    registry = CapabilityRegistry()
    caps = registry.all_capabilities()
    assert len(caps) > 0, "Registry returned no capabilities"

    # Topology init is the real guard: crashes if any active cap is unclassified
    topology = CapabilityTopology(registry)
    entries = topology.all_entries()
    assert len(entries) > 0, "Topology produced no entries"
