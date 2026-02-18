# src/governor/capability_registry.py

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from src.governor.exceptions import CapabilityRegistryError

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "config" / "registry.json"
EXPECTED_PHASE = "4"


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

        capabilities = {}
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

            capabilities[cid] = Capability(**entry)

        return capabilities

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