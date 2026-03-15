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
ALLOWED_AUTHORITY_SCOPES = {"observe", "suggest", "confirm", "automatic"}


def _default_authority_scope_for_risk(risk_level: str) -> str:
    if risk_level in {"confirm", "high"}:
        return "confirm"
    return "suggest"


@dataclass(frozen=True)
class Capability:
    id: int
    name: str
    status: str                # "design", "active", "deprecated", "retired"
    phase_introduced: str
    risk_level: str             # "low", "confirm", "high"
    data_exfiltration: bool
    enabled: bool               # runtime gate, separate from status
    authority_scope: str = "suggest"


class CapabilityRegistry:
    """Singleton loader for the capability registry. Fail-closed if registry unusable."""

    def __init__(self):
        self._selected_profile: str = DEFAULT_RUNTIME_PROFILE
        self._selected_groups: tuple[str, ...] = tuple()
        self._capabilities: Dict[int, Capability] = self._load_registry()
        self._emit_profile_lifecycle_events()

    def _load_registry(self) -> Dict[int, Capability]:
        if not REGISTRY_PATH.exists():
            raise CapabilityRegistryError(
                f"Registry missing at {REGISTRY_PATH}. Execution disabled."
            )

        try:
            raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception as error:
            raise CapabilityRegistryError(
                f"Registry malformed (JSON error): {error}. Execution disabled."
            ) from error

        # Schema validation
        if raw.get("schema_version") != "1.0":
            raise CapabilityRegistryError("Unsupported registry schema version.")
        if raw.get("phase") != EXPECTED_PHASE:
            raise CapabilityRegistryError(f"Registry phase mismatch (expected Phase {EXPECTED_PHASE}).")

        selected_profile = (os.getenv(RUNTIME_PROFILE_ENV) or DEFAULT_RUNTIME_PROFILE).strip() or DEFAULT_RUNTIME_PROFILE
        self._selected_profile = selected_profile

        profiles = raw.get("profiles") or {}
        if not isinstance(profiles, dict):
            raise CapabilityRegistryError("profiles must be an object when provided.")

        profile = profiles.get(selected_profile)
        if profile is None:
            raise CapabilityRegistryError(f"Unknown runtime profile: {selected_profile}")
        if not isinstance(profile, dict):
            raise CapabilityRegistryError(f"Invalid profile definition for: {selected_profile}")

        capabilities: dict[int, dict] = {}
        required_fields = {
            "id",
            "name",
            "status",
            "phase_introduced",
            "risk_level",
            "data_exfiltration",
            "enabled",
        }

        for entry in raw.get("capabilities", []):
            if not required_fields.issubset(entry.keys()):
                missing = required_fields - entry.keys()
                raise CapabilityRegistryError(f"Capability missing fields: {missing}")

            if entry["risk_level"] not in {"low", "confirm", "high"}:
                raise CapabilityRegistryError(f"Invalid risk_level: {entry['risk_level']}")
            if entry["status"] not in {"design", "active", "deprecated", "retired"}:
                raise CapabilityRegistryError(f"Invalid status: {entry['status']}")
            if not isinstance(entry["enabled"], bool):
                raise CapabilityRegistryError("enabled must be a boolean")

            normalized = dict(entry)
            authority_scope = normalized.get("authority_scope")
            if authority_scope is None:
                authority_scope = _default_authority_scope_for_risk(normalized["risk_level"])
            authority_scope = str(authority_scope).strip().lower()
            if authority_scope not in ALLOWED_AUTHORITY_SCOPES:
                raise CapabilityRegistryError(f"Invalid authority_scope: {authority_scope}")
            normalized["authority_scope"] = authority_scope

            cid = normalized["id"]
            if cid in capabilities:
                raise CapabilityRegistryError(f"Duplicate capability ID: {cid}")
            capabilities[cid] = normalized

        known_ids = set(capabilities.keys())
        capability_groups = raw.get("capability_groups") or {}
        if not isinstance(capability_groups, dict):
            raise CapabilityRegistryError("capability_groups must be an object when provided.")

        groups = profile.get("groups") or []
        if not isinstance(groups, list):
            raise CapabilityRegistryError(f"Invalid groups for profile: {selected_profile}")
        self._selected_groups = tuple(str(group) for group in groups)

        for group_name in groups:
            if group_name not in capability_groups:
                raise CapabilityRegistryError(f"Unknown capability group: {group_name}")
            group_ids = capability_groups[group_name]
            if not isinstance(group_ids, list):
                raise CapabilityRegistryError(f"Invalid capability group definition: {group_name}")
            for raw_id in group_ids:
                try:
                    cid = int(raw_id)
                except Exception as error:
                    raise CapabilityRegistryError(
                        f"Invalid capability ID in group {group_name}: {raw_id}"
                    ) from error
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
            except Exception as error:
                raise CapabilityRegistryError(
                    f"Invalid capability ID override in profile {selected_profile}: {cid_raw}"
                ) from error
            if cid not in capabilities:
                raise CapabilityRegistryError(f"Profile {selected_profile} references unknown capability ID: {cid}")
            if not isinstance(enabled_value, bool):
                raise CapabilityRegistryError(
                    f"Profile {selected_profile} enabled override for capability {cid} must be boolean."
                )
            capabilities[cid]["enabled"] = enabled_value

        return {cid: Capability(**entry) for cid, entry in capabilities.items()}

    def _emit_profile_lifecycle_events(self) -> None:
        try:
            from src.ledger.writer import LedgerWriter

            writer = LedgerWriter()
            enabled_caps = [
                cap
                for _, cap in sorted(self._capabilities.items(), key=lambda item: item[0])
                if cap.enabled and cap.status == "active"
            ]
            writer.log_event(
                "CAPABILITY_PROFILE_APPLIED",
                {
                    "runtime_profile": self._selected_profile,
                    "groups": list(self._selected_groups),
                    "enabled_capability_ids": [cap.id for cap in enabled_caps],
                },
            )
            for cap in enabled_caps:
                writer.log_event(
                    "CAPABILITY_INSTALLED",
                    {
                        "capability_id": cap.id,
                        "capability_name": cap.name,
                        "risk_level": cap.risk_level,
                        "authority_scope": cap.authority_scope,
                    },
                )
        except Exception:
            # Lifecycle telemetry must never block capability loading.
            return

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

    def authority_scope(self, capability_id: int) -> str:
        """Return capability authority scope (observe/suggest/confirm/automatic)."""
        return self.get(capability_id).authority_scope

    def all_capabilities(self) -> list[Capability]:
        """Return all registered capabilities in stable ID order."""
        return [cap for _, cap in sorted(self._capabilities.items(), key=lambda item: item[0])]
