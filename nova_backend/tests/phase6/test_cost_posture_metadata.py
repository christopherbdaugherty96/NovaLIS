"""Tests for cost posture metadata on Capability dataclass and registry.json.

Cost posture is metadata + visibility only. No runtime enforcement exists yet.
Values: free | free_tier | paid | unknown_cost

Invariants under test:
  1. ALLOWED_COST_POSTURES contains exactly the four expected values
  2. DEFAULT_COST_POSTURE is "unknown_cost"
  3. Every capability loaded from the live registry has a valid cost_posture
  4. Known specific cost postures are correct (spot-checks)
  5. Invalid cost_posture in a synthetic registry entry raises CapabilityRegistryError
  6. Missing cost_posture defaults to "unknown_cost" (not a hard error)
  7. cost_posture field is accessible on Capability dataclass instances
  8. cost_posture is normalised to lowercase by the loader
"""

from __future__ import annotations

import copy
import json

import pytest

from src.governor.capability_registry import (
    ALLOWED_COST_POSTURES,
    DEFAULT_COST_POSTURE,
    Capability,
    CapabilityRegistry,
)
from src.governor.exceptions import CapabilityRegistryError


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

def test_allowed_cost_postures_contains_four_values():
    assert len(ALLOWED_COST_POSTURES) == 4


def test_allowed_cost_postures_contains_expected_values():
    assert ALLOWED_COST_POSTURES == {"free", "free_tier", "paid", "unknown_cost"}


def test_default_cost_posture_is_unknown_cost():
    assert DEFAULT_COST_POSTURE == "unknown_cost"


# ---------------------------------------------------------------------------
# Capability dataclass — field presence and default
# ---------------------------------------------------------------------------

def test_capability_has_cost_posture_field():
    cap = Capability(
        id=9999,
        name="test_cap",
        status="active",
        phase_introduced="1",
        risk_level="low",
        data_exfiltration=False,
        enabled=True,
    )
    assert hasattr(cap, "cost_posture")


def test_capability_default_cost_posture_is_unknown_cost():
    cap = Capability(
        id=9999,
        name="test_cap",
        status="active",
        phase_introduced="1",
        risk_level="low",
        data_exfiltration=False,
        enabled=True,
    )
    assert cap.cost_posture == "unknown_cost"


def test_capability_accepts_all_valid_cost_postures():
    for posture in ALLOWED_COST_POSTURES:
        cap = Capability(
            id=9999,
            name="test_cap",
            status="active",
            phase_introduced="1",
            risk_level="low",
            data_exfiltration=False,
            enabled=True,
            cost_posture=posture,
        )
        assert cap.cost_posture == posture


# ---------------------------------------------------------------------------
# Live registry — all capabilities must have valid cost_posture
# ---------------------------------------------------------------------------

def test_all_capabilities_have_valid_cost_posture():
    registry = CapabilityRegistry()
    for cap in registry.all_capabilities():
        assert cap.cost_posture in ALLOWED_COST_POSTURES, (
            f"Cap {cap.id} ({cap.name}) has invalid cost_posture: {cap.cost_posture!r}"
        )


def test_all_27_capabilities_loaded():
    registry = CapabilityRegistry()
    assert len(registry.all_capabilities()) == 27


# ---------------------------------------------------------------------------
# Spot-checks — known cost postures
# ---------------------------------------------------------------------------

def test_openclaw_execute_is_unknown_cost():
    registry = CapabilityRegistry()
    cap = registry.get(63)
    assert cap.cost_posture == "unknown_cost"


def test_governed_web_search_is_free_tier():
    registry = CapabilityRegistry()
    cap = registry.get(16)
    assert cap.cost_posture == "free_tier"


def test_weather_snapshot_is_free_tier():
    registry = CapabilityRegistry()
    cap = registry.get(55)
    assert cap.cost_posture == "free_tier"


def test_news_snapshot_is_free_tier():
    registry = CapabilityRegistry()
    cap = registry.get(56)
    assert cap.cost_posture == "free_tier"


def test_shopify_intelligence_report_is_free_tier():
    registry = CapabilityRegistry()
    cap = registry.get(65)
    assert cap.cost_posture == "free_tier"


def test_external_reasoning_review_is_free_tier():
    registry = CapabilityRegistry()
    cap = registry.get(62)
    assert cap.cost_posture == "free_tier"


def test_send_email_draft_is_free():
    registry = CapabilityRegistry()
    cap = registry.get(64)
    assert cap.cost_posture == "free"


def test_open_website_is_free():
    registry = CapabilityRegistry()
    cap = registry.get(17)
    assert cap.cost_posture == "free"


def test_speak_text_is_free():
    registry = CapabilityRegistry()
    cap = registry.get(18)
    assert cap.cost_posture == "free"


def test_local_control_caps_are_free():
    """Volume, media, brightness, open_file_folder — all local, all free."""
    registry = CapabilityRegistry()
    for cap_id in (19, 20, 21, 22):
        cap = registry.get(cap_id)
        assert cap.cost_posture == "free", (
            f"Cap {cap_id} ({cap.name}) expected free, got {cap.cost_posture!r}"
        )


def test_count_of_free_tier_capabilities():
    """Exactly 5 caps should be free_tier: 16, 55, 56, 62, 65."""
    registry = CapabilityRegistry()
    free_tier = [c for c in registry.all_capabilities() if c.cost_posture == "free_tier"]
    assert len(free_tier) == 5
    assert {c.id for c in free_tier} == {16, 55, 56, 62, 65}


def test_count_of_unknown_cost_capabilities():
    """Exactly 1 cap should be unknown_cost: 63 (openclaw_execute)."""
    registry = CapabilityRegistry()
    unknown = [c for c in registry.all_capabilities() if c.cost_posture == "unknown_cost"]
    assert len(unknown) == 1
    assert unknown[0].id == 63


def test_no_paid_capabilities_in_current_registry():
    """No cap should be 'paid' — paid tier is reserved for future use."""
    registry = CapabilityRegistry()
    paid = [c for c in registry.all_capabilities() if c.cost_posture == "paid"]
    assert paid == [], f"Unexpected paid caps: {[c.id for c in paid]}"


# ---------------------------------------------------------------------------
# Validation — invalid cost_posture raises CapabilityRegistryError
# ---------------------------------------------------------------------------

def test_invalid_cost_posture_raises(tmp_path):
    """Registry loader must reject unknown cost_posture values."""
    import src.governor.capability_registry as cr_module

    raw = json.loads((cr_module.REGISTRY_PATH).read_text(encoding="utf-8"))
    raw_copy = copy.deepcopy(raw)

    # Inject an invalid cost_posture into the first capability entry
    raw_copy["capabilities"][0]["cost_posture"] = "super_cheap"

    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(raw_copy), encoding="utf-8")

    original = cr_module.REGISTRY_PATH
    cr_module.REGISTRY_PATH = registry_path
    try:
        with pytest.raises(CapabilityRegistryError, match="invalid cost_posture"):
            CapabilityRegistry()
    finally:
        cr_module.REGISTRY_PATH = original


def test_missing_cost_posture_defaults_to_unknown_cost(tmp_path):
    """Capabilities without cost_posture in the JSON default to 'unknown_cost'."""
    import src.governor.capability_registry as cr_module

    raw = json.loads((cr_module.REGISTRY_PATH).read_text(encoding="utf-8"))
    raw_copy = copy.deepcopy(raw)

    # Remove cost_posture from all entries
    for entry in raw_copy["capabilities"]:
        entry.pop("cost_posture", None)

    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(raw_copy), encoding="utf-8")

    original = cr_module.REGISTRY_PATH
    cr_module.REGISTRY_PATH = registry_path
    try:
        registry = CapabilityRegistry()
        for cap in registry.all_capabilities():
            assert cap.cost_posture == "unknown_cost", (
                f"Cap {cap.id} expected unknown_cost when field missing, got {cap.cost_posture!r}"
            )
    finally:
        cr_module.REGISTRY_PATH = original


def test_cost_posture_normalised_to_lowercase(tmp_path):
    """cost_posture value in JSON is case-insensitively normalised."""
    import src.governor.capability_registry as cr_module

    raw = json.loads((cr_module.REGISTRY_PATH).read_text(encoding="utf-8"))
    raw_copy = copy.deepcopy(raw)

    # Set first entry to uppercase variant
    raw_copy["capabilities"][0]["cost_posture"] = "FREE"

    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(raw_copy), encoding="utf-8")

    original = cr_module.REGISTRY_PATH
    cr_module.REGISTRY_PATH = registry_path
    try:
        registry = CapabilityRegistry()
        first_cap = registry.get(raw_copy["capabilities"][0]["id"])
        assert first_cap.cost_posture == "free"
    finally:
        cr_module.REGISTRY_PATH = original
