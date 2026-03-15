from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.build_phase import BUILD_PHASE


def _bool_label(value: bool) -> str:
    return "true" if bool(value) else "false"


@dataclass(frozen=True)
class PolicyExecutorGateDecision:
    allowed: bool
    policy_id: str
    policy_name: str
    trigger: str
    action: str
    capability_id: int
    capability_name: str
    delegation_class: str
    capability_class: str
    policy_delegatable: bool
    network_required: bool
    persistent_changes: str
    external_effects: str
    estimated_runtime: str
    governor_verdict: str
    readiness_label: str
    reasoning: list[str] = field(default_factory=list)
    envelope_summary: str = ""
    current_authority_limit: str = ""
    local_system_impact: str = "none"
    network_activity: str = "none"
    blocked_reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed": bool(self.allowed),
            "policy_id": str(self.policy_id),
            "policy_name": str(self.policy_name),
            "trigger": str(self.trigger),
            "action": str(self.action),
            "capability_id": int(self.capability_id),
            "capability_name": str(self.capability_name),
            "delegation_class": str(self.delegation_class),
            "capability_class": str(self.capability_class),
            "policy_delegatable": bool(self.policy_delegatable),
            "network_required": bool(self.network_required),
            "persistent_changes": str(self.persistent_changes),
            "external_effects": str(self.external_effects),
            "estimated_runtime": str(self.estimated_runtime),
            "governor_verdict": str(self.governor_verdict),
            "readiness_label": str(self.readiness_label),
            "reasoning": list(self.reasoning),
            "envelope_summary": str(self.envelope_summary),
            "current_authority_limit": str(self.current_authority_limit),
            "risk_summary": {
                "local_system_impact": str(self.local_system_impact),
                "network_activity": str(self.network_activity),
                "persistent_change": str(self.persistent_changes),
                "external_effect": str(self.external_effects),
            },
            "blocked_reason": str(self.blocked_reason),
        }


class PolicyExecutorGate:
    """Governor-side execution and simulation gate for delegated policies."""

    def __init__(self, registry: Any, validator: Any, topology: Any) -> None:
        self._registry = registry
        self._validator = validator
        self._topology = topology

    def simulate(self, policy_item: dict[str, Any] | None) -> PolicyExecutorGateDecision:
        payload = dict(policy_item or {})
        policy_id = str(payload.get("policy_id") or "").strip()
        policy_name = str(payload.get("name") or "").strip() or "Unnamed policy"
        state = str(payload.get("state") or "draft").strip().lower() or "draft"

        validation = self._validator.validate(
            {
                "name": policy_name,
                "created_by": str(payload.get("created_by") or "user").strip() or "user",
                "enabled": bool(payload.get("enabled", False)),
                "state": state,
                "trigger": dict(payload.get("trigger") or {}),
                "action": dict(payload.get("action") or {}),
                "envelope": dict(payload.get("envelope") or {}),
            }
        )

        action = dict(payload.get("action") or {})
        capability_id = int(action.get("capability_id") or 0)
        capability_name = ""
        policy_delegatable = False
        capability_class = "unknown"
        delegation_class = "observational"
        network_required = bool(dict(payload.get("envelope") or {}).get("network_allowed"))
        persistent_changes = "none"
        external_effects = "none"
        estimated_runtime = "unknown"
        local_system_impact = "none"
        network_activity = "required" if network_required else "none"
        reasoning: list[str] = []
        blocked_reason = ""

        try:
            topology_entry = self._topology.get(capability_id)
            capability_name = str(topology_entry.name)
            policy_delegatable = bool(topology_entry.policy_delegatable)
            capability_class = str(topology_entry.authority_class)
            delegation_class = str(topology_entry.delegation_class)
            network_required = bool(topology_entry.requires_network_mediator)
            persistent_changes = "yes" if bool(topology_entry.persistent_change) else "none"
            external_effects = "yes" if bool(topology_entry.external_effect) else "none"
            local_system_impact = "bounded" if capability_class == "reversible_local" else "none"
            network_activity = "required" if network_required else "none"
            estimated_runtime = "0.3s" if capability_class == "read_only_local" else "1.2s"
        except Exception:
            topology_entry = None
            blocked_reason = "missing_capability_topology"
            reasoning.append("No capability topology entry exists for this target capability.")

        if state == "deleted":
            blocked_reason = blocked_reason or "policy_deleted"
            reasoning.append("Policy is deleted and cannot be simulated for execution.")

        if not validation.valid:
            blocked_reason = blocked_reason or "policy_invalid"
            reasoning.extend(str(reason).strip() for reason in list(validation.reasons or []) if str(reason).strip())

        if topology_entry is not None:
            if not policy_delegatable:
                blocked_reason = blocked_reason or "capability_not_delegatable"
                reasoning.append("Capability is not policy-delegatable under the current topology rules.")
            else:
                reasoning.append("Capability is explicitly marked policy-delegatable.")

            current_limit = self._topology.current_delegated_authority_limit()
            if not self._topology.is_within_current_limit(capability_id):
                blocked_reason = blocked_reason or "authority_class_exceeds_current_limit"
                reasoning.append(
                    f"Capability class {capability_class} exceeds the current delegated limit {current_limit}."
                )
            else:
                reasoning.append(
                    f"Capability class {capability_class} is within the current delegated limit {current_limit}."
                )

            if topology_entry.requires_confirmation:
                blocked_reason = blocked_reason or "confirmation_required"
                reasoning.append("Capability requires confirmation and is excluded from delegated execution.")

            if topology_entry.external_effect:
                blocked_reason = blocked_reason or "external_effect_blocked"
                reasoning.append("Capabilities with external effects are blocked from the current delegated slice.")

            if topology_entry.persistent_change:
                blocked_reason = blocked_reason or "persistent_change_blocked"
                reasoning.append("Capabilities with persistent change are blocked from the current delegated slice.")

        allowed = not blocked_reason and BUILD_PHASE >= 5
        if BUILD_PHASE < 5:
            blocked_reason = blocked_reason or "runtime_phase_locked"
            reasoning.append("Current runtime phase does not expose delegated policy review surfaces.")

        if allowed:
            readiness_label = "Ready for manual review run"
            governor_verdict = "Allowed under current Phase-6 delegation rules."
        else:
            if blocked_reason in {"policy_invalid"}:
                readiness_label = "Needs policy correction"
            elif blocked_reason in {"authority_class_exceeds_current_limit"}:
                readiness_label = "Blocked by current runtime stage"
            else:
                readiness_label = "Blocked by delegated authority rules"
            governor_verdict = "Blocked under current Phase-6 delegation rules."

        envelope = dict(payload.get("envelope") or {})
        envelope_summary = (
            f"{int(envelope.get('max_runs_per_hour') or 0)} per hour, "
            f"{int(envelope.get('max_runs_per_day') or 0)} per day, "
            f"timeout {int(envelope.get('timeout_seconds') or 0)}s"
        )
        if not reasoning:
            reasoning.append("No executor-gate reasoning available.")

        return PolicyExecutorGateDecision(
            allowed=allowed,
            policy_id=policy_id,
            policy_name=policy_name,
            trigger=self._describe_trigger(payload.get("trigger")),
            action=self._describe_action(payload.get("action")),
            capability_id=capability_id,
            capability_name=capability_name or f"capability_{capability_id}",
            delegation_class=delegation_class,
            capability_class=capability_class,
            policy_delegatable=policy_delegatable,
            network_required=network_required,
            persistent_changes=persistent_changes,
            external_effects=external_effects,
            estimated_runtime=estimated_runtime,
            governor_verdict=governor_verdict,
            readiness_label=readiness_label,
            reasoning=reasoning,
            envelope_summary=envelope_summary,
            current_authority_limit=self._topology.current_delegated_authority_limit(),
            local_system_impact=local_system_impact,
            network_activity=network_activity,
            blocked_reason=blocked_reason,
        )

    def authorize_manual_run(self, policy_item: dict[str, Any] | None) -> PolicyExecutorGateDecision:
        return self.simulate(policy_item)

    def _describe_trigger(self, trigger: Any) -> str:
        payload = dict(trigger or {})
        trigger_type = str(payload.get("type") or "").strip().lower()
        if trigger_type == "time_weekly":
            days = ", ".join(list(payload.get("days") or [])[:5]) or "weekdays"
            return f"{days} at {str(payload.get('time') or '').strip()}"
        if trigger_type == "time_daily":
            return f"Daily at {str(payload.get('time') or '').strip()}"
        if trigger_type == "time_once":
            return str(payload.get("at") or "").strip() or "time_once"
        if trigger_type == "calendar_event":
            return f"Calendar offset {int(payload.get('offset_minutes') or 0)} minute(s)"
        if trigger_type == "device_event":
            return f"Device event {str(payload.get('event_key') or '').strip()}"
        return "Unknown trigger"

    def _describe_action(self, action: Any) -> str:
        payload = dict(action or {})
        capability_id = int(payload.get("capability_id") or 0)
        try:
            capability = self._registry.get(capability_id)
            return str(capability.name or "").strip() or f"Capability {capability_id}"
        except Exception:
            return f"Capability {capability_id}"
