# src/governor/capability_registry.py

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from src.governor.exceptions import CapabilityRegistryError

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "config" / "registry.json"
EXPECTED_PHASE = "4"
RUNTIME_PROFILE_ENV = "NOVA_RUNTIME_PROFILE"
DEFAULT_RUNTIME_PROFILE = "default"


@dataclass(frozen=True)
class Capability:
    id: int
    name: str
    status: str                # "design", "active", "deprecated", "retired"
    phase_introduced: str
    risk_level: str             # "low", "confirm", "high"
    data_exfiltration: bool
    enabled: bool               # runtime gate, separate from status


class CapabilityRegistry:
    """Singleton loader for the capability registry. Fail‑closed if registry unusable."""

    def __init__(self):
        self._capabilities: Dict[int, Capability] = self._load_registry()

    def _load_registry(self) -> Dict[int, Capability]:
        if not REGISTRY_PATH.exists():
            raise CapabilityRegistryError(
                f"Registry missing at {REGISTRY_PATH}. Execution disabled."
            )

        try:
            raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            raise CapabilityRegistryError(
                f"Registry malformed (JSON error): {e}. Execution disabled."
            ) from e

        # Schema validation
        if raw.get("schema_version") != "1.0":
            raise CapabilityRegistryError("Unsupported registry schema version.")
        if raw.get("phase") != EXPECTED_PHASE:
            raise CapabilityRegistryError(f"Registry phase mismatch (expected Phase {EXPECTED_PHASE}).")

        selected_profile = (os.getenv(RUNTIME_PROFILE_ENV) or DEFAULT_RUNTIME_PROFILE).strip() or DEFAULT_RUNTIME_PROFILE
        profiles = raw.get("profiles") or {}
        if not isinstance(profiles, dict):
            raise CapabilityRegistryError("profiles must be an object when provided.")

        profile = profiles.get(selected_profile)
        if profile is None:
            raise CapabilityRegistryError(f"Unknown runtime profile: {selected_profile}")
        if not isinstance(profile, dict):
            raise CapabilityRegistryError(f"Invalid profile definition for: {selected_profile}")

        capabilities: dict[int, dict] = {}
        required_fields = {"id", "name", "status", "phase_introduced",
                           "risk_level", "data_exfiltration", "enabled"}

        for entry in raw.get("capabilities", []):
            # Check required fields
            if not required_fields.issubset(entry.keys()):
                missing = required_fields - entry.keys()
                raise CapabilityRegistryError(f"Capability missing fields: {missing}")

            # Validate field values
            if entry["risk_level"] not in {"low", "confirm", "high"}:
                raise CapabilityRegistryError(f"Invalid risk_level: {entry['risk_level']}")
            if entry["status"] not in {"design", "active", "deprecated", "retired"}:
                raise CapabilityRegistryError(f"Invalid status: {entry['status']}")
            if not isinstance(entry["enabled"], bool):
                raise CapabilityRegistryError("enabled must be a boolean")

            cid = entry["id"]
            if cid in capabilities:
                raise CapabilityRegistryError(f"Duplicate capability ID: {cid}")

            capabilities[cid] = dict(entry)

        known_ids = set(capabilities.keys())
        capability_groups = raw.get("capability_groups") or {}
        if not isinstance(capability_groups, dict):
            raise CapabilityRegistryError("capability_groups must be an object when provided.")

        groups = profile.get("groups") or []
        if not isinstance(groups, list):
            raise CapabilityRegistryError(f"Invalid groups for profile: {selected_profile}")

        for group_name in groups:
            if group_name not in capability_groups:
                raise CapabilityRegistryError(f"Unknown capability group: {group_name}")
            group_ids = capability_groups[group_name]
            if not isinstance(group_ids, list):
                raise CapabilityRegistryError(f"Invalid capability group definition: {group_name}")
            for raw_id in group_ids:
                try:
                    cid = int(raw_id)
                except Exception as e:
                    raise CapabilityRegistryError(
                        f"Invalid capability ID in group {group_name}: {raw_id}"
                    ) from e
                if cid not in known_ids:
                    raise CapabilityRegistryError(
                        f"Capability group '{group_name}' references unknown ID: {cid}"
                    )
                capabilities[cid]["enabled"] = True

        enabled_overrides = profile.get("enabled_overrides") or {}
        if not isinstance(enabled_overrides, dict):
            raise CapabilityRegistryError(f"enabled_overrides must be an object for profile: {selected_profile}")

        for cid_raw, enabled_value in enabled_overrides.items():
            try:
                cid = int(cid_raw)
            except Exception as e:
                raise CapabilityRegistryError(f"Invalid capability ID override in profile {selected_profile}: {cid_raw}") from e
            if cid not in capabilities:
                raise CapabilityRegistryError(f"Profile {selected_profile} references unknown capability ID: {cid}")
            if not isinstance(enabled_value, bool):
                raise CapabilityRegistryError(
                    f"Profile {selected_profile} enabled override for capability {cid} must be boolean."
                )
            capabilities[cid]["enabled"] = enabled_value
        return {cid: Capability(**entry) for cid, entry in capabilities.items()}

    def get(self, capability_id: int) -> Capability:
        """Return capability; raises if unknown."""
        cap = self._capabilities.get(capability_id)
        if cap is None:
            raise CapabilityRegistryError(f"Unknown capability ID: {capability_id}")
        return cap

    def is_enabled(self, capability_id: int) -> bool:
        """Check if capability is both active and enabled at runtime."""
        cap = self.get(capability_id)
        return cap.status == "active" and cap.enabled
