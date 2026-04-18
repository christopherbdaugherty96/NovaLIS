# tests/certification/test_lock_regression_guard.py
"""
Capability Lock Regression Guard
=================================
This test file is the enforcer. For every capability that has been locked
(capability_locks.json → "locked": true), it verifies:

  1. The capability still exists in registry.json
  2. The governance fields that were locked have not changed
     (authority_class, risk_level, external_effect, reversible)
  3. All automated certification tests for the capability still pass

If ANY of these checks fail for a locked capability, this file fails —
blocking the commit.

HOW TO UNLOCK A CAPABILITY (e.g. for a breaking change):
  python scripts/certify_capability.py unlock {cap_id} --reason "..."
This resets locked=false and clears p5_live, requiring a new live sign-off.
"""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.certification.conftest import (
    LOCKS_FILE,
    NOVA_BACKEND_ROOT,
    REGISTRY_FILE,
    load_locks,
    load_registry,
    locked_capability_ids,
)

# ---------------------------------------------------------------------------
# Meta-tests: verify the lock infrastructure itself is intact
# ---------------------------------------------------------------------------

def test_locks_file_exists_and_is_valid_json():
    """The lock file must always exist and be valid JSON."""
    assert LOCKS_FILE.exists(), f"Lock file missing: {LOCKS_FILE}"
    data = json.loads(LOCKS_FILE.read_text(encoding="utf-8"))
    assert "capabilities" in data
    assert "schema_version" in data


def test_registry_file_exists_and_is_valid_json():
    """The registry must always exist and be valid JSON."""
    assert REGISTRY_FILE.exists(), f"Registry missing: {REGISTRY_FILE}"
    data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    assert "capabilities" in data


def test_all_lock_entries_reference_real_registry_ids():
    """Every capability_id in the lock file must exist in registry.json."""
    locks = load_locks()
    registry = load_registry()
    registry_ids = {str(cap["id"]) for cap in registry["capabilities"]}
    for cap_id in locks["capabilities"]:
        assert cap_id in registry_ids, (
            f"Cap {cap_id} in lock file is not in registry.json. "
            "Either add it to the registry or remove it from the lock file."
        )


def test_lock_file_covers_all_registry_capabilities():
    """Every capability in registry.json must have an entry in the lock file."""
    locks = load_locks()
    registry = load_registry()
    lock_ids = set(locks["capabilities"].keys())
    for cap in registry["capabilities"]:
        cap_id = str(cap["id"])
        assert cap_id in lock_ids, (
            f"Capability {cap['id']} ({cap['name']}) is in registry.json but "
            "missing from capability_locks.json. Add it to the lock file."
        )


# ---------------------------------------------------------------------------
# Per-locked-capability regression checks
# ---------------------------------------------------------------------------

def _locked_caps() -> list[tuple[int, dict, dict]]:
    """Return (cap_id, lock_entry, registry_entry) for all locked capabilities."""
    locks = load_locks()
    registry = load_registry()
    registry_by_id = {str(cap["id"]): cap for cap in registry["capabilities"]}
    result = []
    for cap_id_str, lock_entry in locks["capabilities"].items():
        if lock_entry.get("locked"):
            registry_entry = registry_by_id.get(cap_id_str, {})
            result.append((int(cap_id_str), lock_entry, registry_entry))
    return result


@pytest.mark.parametrize("cap_id,lock_entry,registry_entry", _locked_caps())
def test_locked_capability_still_in_registry(cap_id, lock_entry, registry_entry):
    """Locked capability must still exist in registry.json."""
    assert registry_entry, (
        f"Cap {cap_id} ({lock_entry['name']}) is LOCKED but no longer in registry.json. "
        "You must unlock it before removing it from the registry."
    )


@pytest.mark.parametrize("cap_id,lock_entry,registry_entry", _locked_caps())
def test_locked_capability_governance_fields_unchanged(cap_id, lock_entry, registry_entry):
    """Locked capability's governance fields must not have changed."""
    fields = ["authority_class", "risk_level", "external_effect", "reversible"]
    for field in fields:
        locked_value = lock_entry.get(field)
        current_value = registry_entry.get(field)
        assert locked_value == current_value, (
            f"REGRESSION: Cap {cap_id} ({lock_entry['name']}) — "
            f"'{field}' changed from {locked_value!r} (locked) to {current_value!r} (current). "
            "Run: python scripts/certify_capability.py unlock {cap_id} --reason '...' "
            "then re-certify."
        )


@pytest.mark.parametrize("cap_id,lock_entry,registry_entry", _locked_caps())
def test_locked_capability_is_still_enabled(cap_id, lock_entry, registry_entry):
    """Locked capability must not have been disabled in the registry."""
    assert registry_entry.get("enabled", False), (
        f"REGRESSION: Cap {cap_id} ({lock_entry['name']}) is LOCKED but "
        "registry.json shows enabled=false. Unlock it before disabling."
    )


@pytest.mark.parametrize("cap_id,lock_entry,registry_entry", _locked_caps())
def test_locked_capability_certification_tests_exist(cap_id, lock_entry, registry_entry):
    """Locked capability must have certification test files on disk."""
    cap_name = lock_entry["name"]
    cert_dir = NOVA_BACKEND_ROOT / "tests" / "certification" / f"cap_{cap_id}_{cap_name}"
    assert cert_dir.exists(), (
        f"Cap {cap_id} ({cap_name}) is LOCKED but certification directory "
        f"'{cert_dir}' does not exist. Create it or unlock the capability."
    )
    for phase in ("p1_unit", "p2_routing", "p3_integration"):
        test_file = cert_dir / f"test_{phase}.py"
        assert test_file.exists(), (
            f"Cap {cap_id} ({cap_name}) is LOCKED but "
            f"'{test_file.name}' is missing from the certification directory."
        )


# ---------------------------------------------------------------------------
# Guard: all phases must show "pass" before locked=true is accepted
# ---------------------------------------------------------------------------

def test_no_capability_is_locked_without_all_phases_passing():
    """A capability cannot be locked if any automated phase is not 'pass'."""
    locks = load_locks()
    automated_phases = ("p1_unit", "p2_routing", "p3_integration", "p4_api")
    problems = []
    for cap_id_str, entry in locks["capabilities"].items():
        if not entry.get("locked"):
            continue
        for phase in automated_phases:
            status = (entry.get(phase) or {}).get("status", "pending")
            if status != "pass":
                problems.append(
                    f"Cap {cap_id_str} ({entry['name']}): locked=true but {phase}={status!r}"
                )
    assert not problems, (
        "Capabilities locked with failing/pending phases:\n" + "\n".join(problems)
    )


def test_no_capability_is_locked_without_live_signoff():
    """A capability cannot be locked if p5_live is not 'pass'."""
    locks = load_locks()
    problems = []
    for cap_id_str, entry in locks["capabilities"].items():
        if not entry.get("locked"):
            continue
        live_status = (entry.get("p5_live") or {}).get("status", "pending")
        if live_status != "pass":
            problems.append(
                f"Cap {cap_id_str} ({entry['name']}): locked=true but p5_live={live_status!r}"
            )
    assert not problems, (
        "Capabilities locked without live sign-off:\n" + "\n".join(problems)
    )
