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
PARITY_FIELDS = (
    "authority_class",
    "requires_confirmation",
    "reversible",
    "external_effect",
)


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
    31: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "informational",
    },
    62: {
        "authority_class": "read_only_local",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "informational",
        "envelope_notes": "External reasoning remains advisory-only and cannot widen Nova's execution authority.",
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
        "authority_class": "read_only_network",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": True,
        "delegation_class": "observational",
    },
    50: {
        "authority_class": "read_only_network",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": False,
        "requires_network_mediator": True,
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
        "authority_class": "persistent_change",
        "policy_delegatable": False,
        "reversible": False,
        "persistent_change": True,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
        "envelope_notes": "Story tracking writes durable local snapshots and relationship state.",
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
        "authority_class": "persistent_change",
        "policy_delegatable": False,
        "reversible": False,
        "persistent_change": True,
        "external_effect": False,
        "requires_network_mediator": False,
        "delegation_class": "observational",
        "envelope_notes": "Screen capture persists an explicit request-time PNG for later analysis.",
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
    63: {
        "authority_class": "read_only_network",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": True,
        "requires_network_mediator": True,
        "delegation_class": "observational",
        "envelope_notes": "Home-agent templates are read-only network runs. External effect is True because results are delivered to the agent inbox. Not policy-delegatable in the current phase.",
    },
    64: {
        "authority_class": "persistent_change",
        "policy_delegatable": False,
        "reversible": False,
        "persistent_change": True,
        "external_effect": True,
        "requires_network_mediator": False,
        "delegation_class": "local_action",
        "envelope_notes": "Opens system mail client via mailto: URI with a pre-composed draft. External effect is True because the system mail client is invoked. Not delegatable — requires explicit user confirmation and involves data exfiltration risk.",
    },
    65: {
        "authority_class": "read_only_network",
        "policy_delegatable": False,
        "reversible": True,
        "persistent_change": False,
        "external_effect": True,
        "requires_network_mediator": True,
        "delegation_class": "observational",
        "envelope_notes": "Tier 1 read-only Shopify store intelligence. External effect is True because it calls the Shopify GraphQL Admin API. Not delegatable in the current phase — requires explicit connector configuration.",
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
            if str(getattr(capability, "status", "")).strip().lower() == "active" and not override:
                raise ValueError(f"Active capability {capability.id} missing topology override.")
            if not override:
                continue
            authority_class = str(getattr(capability, "authority_class", "read_only_local")).strip()
            requires_confirmation = bool(getattr(capability, "requires_confirmation", False))
            reversible = bool(getattr(capability, "reversible", True))
            external_effect = bool(getattr(capability, "external_effect", False))
            persistent_change = authority_class == "persistent_change"

            mismatches: list[str] = []
            for field_name in PARITY_FIELDS:
                if field_name not in override:
                    continue
                if override[field_name] != getattr(capability, field_name):
                    mismatches.append(
                        f"{field_name}: registry={getattr(capability, field_name)!r}, topology={override[field_name]!r}"
                    )
            if "persistent_change" in override and bool(override["persistent_change"]) != persistent_change:
                mismatches.append(
                    f"persistent_change: derived={persistent_change!r}, topology={bool(override['persistent_change'])!r}"
                )
            if mismatches:
                raise ValueError(
                    f"Capability {capability.id} governance metadata parity mismatch: {', '.join(mismatches)}"
                )

            requires_network_mediator = bool(
                override.get("requires_network_mediator", authority_class == "read_only_network")
            )
            if authority_class == "read_only_network" and not requires_network_mediator:
                raise ValueError(
                    f"Capability {capability.id} has read_only_network authority without network mediator enforcement."
                )
            entries[int(capability.id)] = CapabilityTopologyEntry(
                capability_id=int(capability.id),
                name=str(capability.name),
                authority_class=authority_class,
                risk_level=str(capability.risk_level),
                policy_delegatable=bool(override.get("policy_delegatable")),
                requires_confirmation=requires_confirmation,
                reversible=reversible,
                persistent_change=persistent_change,
                external_effect=external_effect,
                requires_network_mediator=requires_network_mediator,
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
