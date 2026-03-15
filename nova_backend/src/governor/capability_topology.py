from __future__ import annotations

from dataclasses import dataclass
from typing import Any


AUTHORITY_CLASS_ORDER = {
    "read_only_local": 1,
    "read_only_network": 2,
    "reversible_local": 3,
    "persistent_change": 4,
    "external_effect": 5,
}
CURRENT_DELEGATED_AUTHORITY_LIMIT = "read_only_local"


@dataclass(frozen=True)
class CapabilityTopologyEntry:
    capability_id: int
    name: str
    authority_class: str
    risk_level: str
    policy_delegatable: bool
    requires_confirmation: bool
    reversible: bool
    persistent_change: bool
    external_effect: bool
    requires_network_mediator: bool
    delegation_class: str
    envelope_notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "capability_id": int(self.capability_id),
            "name": str(self.name),
            "authority_class": str(self.authority_class),
            "risk_level": str(self.risk_level),
            "policy_delegatable": bool(self.policy_delegatable),
            "requires_confirmation": bool(self.requires_confirmation),
            "reversible": bool(self.reversible),
            "persistent_change": bool(self.persistent_change),
            "external_effect": bool(self.external_effect),
            "requires_network_mediator": bool(self.requires_network_mediator),
            "delegation_class": str(self.delegation_class),
            "envelope_notes": str(self.envelope_notes),
        }


_TOPOLOGY_OVERRIDES: dict[int, dict[str, Any]] = {
    16: {
        "authority_class": "read_only_network",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": True,
        "delegation_class": "informational",
        "envelope_notes": "Network-mediated search remains explicit-only in the current delegated phase.",
    },
    17: {
        "authority_class": "reversible_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
    },
    18: {
        "authority_class": "reversible_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
    },
    19: {
        "authority_class": "reversible_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
    },
    20: {
        "authority_class": "reversible_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
    },
    21: {
        "authority_class": "reversible_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
    },
    22: {
        "authority_class": "reversible_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
    },
    32: {
        "authority_class": "read_only_local",
        "policy_delegatable": True,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
        "envelope_notes": "Safe first-slice delegated snapshot candidate.",
    },
    48: {
        "authority_class": "read_only_network",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": True,
        "delegation_class": "informational",
    },
    49: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
    },
    50: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
    },
    51: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
    },
    52: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
    },
    53: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
    },
    54: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "informational",
    },
    55: {
        "authority_class": "read_only_network",
        "policy_delegatable": True,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": True,
        "delegation_class": "observational",
        "envelope_notes": "Network snapshot remains simulatably lawful but blocked from current manual delegated execution.",
    },
    56: {
        "authority_class": "read_only_network",
        "policy_delegatable": True,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": True,
        "delegation_class": "informational",
        "envelope_notes": "News snapshot remains above the current delegated authority class.",
    },
    57: {
        "authority_class": "read_only_local",
        "policy_delegatable": True,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
        "envelope_notes": "Safe first-slice delegated snapshot candidate.",
    },
    58: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
    },
    59: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "informational",
    },
    60: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "informational",
    },
    61: {
        "authority_class": "persistent_change",
        "policy_delegatable": False,
        "reversible": False,
        "persistent_change": True,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
        "envelope_notes": "Governed memory remains explicitly user-directed and non-delegatable.",
    },
}


class CapabilityTopology:
    """Capability classification model for delegated-policy decisions."""

    def __init__(self, registry: Any) -> None:
        self._registry = registry
        self._entries = self._build_entries()

    def _build_entries(self) -> dict[int, CapabilityTopologyEntry]:
        entries: dict[int, CapabilityTopologyEntry] = {}
        for capability in self._registry.all_capabilities():
            override = dict(_TOPOLOGY_OVERRIDES.get(int(capability.id)) or {})
            if not override:
                continue
            authority_class = str(override.get("authority_class") or "read_only_local").strip()
            entries[int(capability.id)] = CapabilityTopologyEntry(
                capability_id=int(capability.id),
                name=str(capability.name),
                authority_class=authority_class,
                risk_level=str(capability.risk_level),
                policy_delegatable=bool(override.get("policy_delegatable")),
                requires_confirmation=bool(
                    override.get("requires_confirmation", capability.risk_level == "confirm")
                ),
                reversible=bool(override.get("reversible", True)),
                persistent_change=bool(override.get("persistent_change", False)),
                external_effect=bool(override.get("external_effect", False)),
                requires_network_mediator=bool(override.get("requires_network_mediator", False)),
                delegation_class=str(override.get("delegation_class") or "observational").strip(),
                envelope_notes=str(override.get("envelope_notes") or "").strip(),
            )
        return entries

    def get(self, capability_id: int) -> CapabilityTopologyEntry:
        try:
            return self._entries[int(capability_id)]
        except Exception as error:
            raise KeyError(int(capability_id)) from error

    def all_entries(self) -> list[CapabilityTopologyEntry]:
        return [entry for _, entry in sorted(self._entries.items(), key=lambda item: item[0])]

    def current_delegated_authority_limit(self) -> str:
        return CURRENT_DELEGATED_AUTHORITY_LIMIT

    def authority_rank(self, authority_class: str) -> int:
        return int(AUTHORITY_CLASS_ORDER.get(str(authority_class or "").strip(), 999))

    def is_within_current_limit(self, capability_id: int) -> bool:
        entry = self.get(capability_id)
        return self.authority_rank(entry.authority_class) <= self.authority_rank(
            self.current_delegated_authority_limit()
        )
