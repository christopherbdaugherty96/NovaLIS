from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_WEEKDAY_CODES = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}
_ALLOWED_STATES = {"draft", "disabled", "suspended", "deleted"}
_ALLOWED_TRIGGER_TYPES = {"time_once", "time_daily", "time_weekly", "calendar_event", "device_event"}
_FORBIDDEN_ACTION_KEYS = {"actions", "steps", "fallback_action", "fallback_actions", "plan"}

POLICY_CAPABILITY_RULES: dict[int, dict[str, Any]] = {
    32: {
        "name": "system_status",
        "label": "System status",
        "network_required": False,
        "allowed_input_keys": set(),
    },
    55: {
        "name": "weather_snapshot",
        "label": "Weather snapshot",
        "network_required": True,
        "allowed_input_keys": set(),
    },
    56: {
        "name": "news_snapshot",
        "label": "News snapshot",
        "network_required": True,
        "allowed_input_keys": set(),
    },
    57: {
        "name": "calendar_snapshot",
        "label": "Calendar snapshot",
        "network_required": False,
        "allowed_input_keys": {"mode"},
        "allowed_mode_values": {"today"},
    },
}


@dataclass(frozen=True)
class PolicyValidationResult:
    valid: bool
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    normalized_policy: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": bool(self.valid),
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "normalized_policy": dict(self.normalized_policy or {}),
        }


class PolicyValidator:
    """Validate the smallest lawful Phase-6 delegated policy shape."""

    def __init__(self, registry: Any) -> None:
        self._registry = registry

    def validate(self, policy: dict[str, Any] | None) -> PolicyValidationResult:
        reasons: list[str] = []
        warnings: list[str] = []

        if not isinstance(policy, dict):
            return PolicyValidationResult(valid=False, reasons=["Policy payload must be an object."])

        normalized: dict[str, Any] = {}

        name = str(policy.get("name") or "").strip()
        if not name:
            reasons.append("Policy name cannot be empty.")
        else:
            normalized["name"] = name[:120]

        created_by = str(policy.get("created_by") or "user").strip().lower() or "user"
        normalized["created_by"] = created_by[:80]

        enabled = bool(policy.get("enabled", False))
        state = str(policy.get("state") or "draft").strip().lower() or "draft"
        if state not in _ALLOWED_STATES:
            reasons.append(f"Unsupported policy state: {state}.")
        if enabled:
            reasons.append("Phase-6 foundation policies must remain disabled until trigger runtime is unlocked.")
        if state not in {"draft", "disabled"}:
            reasons.append("Phase-6 foundation policies may only be stored as draft or disabled.")
        normalized["enabled"] = False
        normalized["state"] = "draft" if state not in _ALLOWED_STATES else state

        trigger, trigger_errors = self._validate_trigger(policy.get("trigger"))
        reasons.extend(trigger_errors)
        if trigger is not None:
            normalized["trigger"] = trigger

        action, action_errors = self._validate_action(policy.get("action"))
        reasons.extend(action_errors)
        if action is not None:
            normalized["action"] = action

        envelope, envelope_errors = self._validate_envelope(policy.get("envelope"), action)
        reasons.extend(envelope_errors)
        if envelope is not None:
            normalized["envelope"] = envelope

        if reasons:
            return PolicyValidationResult(valid=False, reasons=reasons, warnings=warnings)

        return PolicyValidationResult(valid=True, reasons=[], warnings=warnings, normalized_policy=normalized)

    def _validate_trigger(self, raw_trigger: Any) -> tuple[dict[str, Any] | None, list[str]]:
        errors: list[str] = []
        if not isinstance(raw_trigger, dict):
            return None, ["Trigger must be an object."]

        trigger_type = str(raw_trigger.get("type") or "").strip().lower()
        if trigger_type not in _ALLOWED_TRIGGER_TYPES:
            return None, [f"Unsupported trigger type: {trigger_type or 'missing'}."]

        normalized: dict[str, Any] = {"type": trigger_type}
        if trigger_type == "time_once":
            at_value = str(raw_trigger.get("at") or "").strip()
            if not at_value:
                errors.append("time_once trigger requires an 'at' value.")
            else:
                normalized["at"] = at_value
            return (normalized if not errors else None), errors

        if trigger_type == "time_daily":
            time_value = str(raw_trigger.get("time") or "").strip()
            if not time_value:
                errors.append("time_daily trigger requires a 'time' value.")
            else:
                normalized["time"] = time_value
            return (normalized if not errors else None), errors

        if trigger_type == "time_weekly":
            time_value = str(raw_trigger.get("time") or "").strip()
            raw_days = list(raw_trigger.get("days") or [])
            days = [str(day or "").strip().upper() for day in raw_days if str(day or "").strip()]
            unique_days: list[str] = []
            for day in days:
                if day not in _WEEKDAY_CODES:
                    errors.append(f"Unsupported weekday code: {day}.")
                    continue
                if day not in unique_days:
                    unique_days.append(day)
            if not time_value:
                errors.append("time_weekly trigger requires a 'time' value.")
            if not unique_days:
                errors.append("time_weekly trigger requires at least one weekday code.")
            if not errors:
                normalized["time"] = time_value
                normalized["days"] = unique_days
            return (normalized if not errors else None), errors

        if trigger_type == "calendar_event":
            offset_minutes = raw_trigger.get("offset_minutes")
            if offset_minutes is None:
                errors.append("calendar_event trigger requires 'offset_minutes'.")
            else:
                try:
                    normalized["offset_minutes"] = max(0, min(int(offset_minutes), 240))
                except Exception:
                    errors.append("calendar_event trigger offset must be an integer.")
            return (normalized if not errors else None), errors

        event_key = str(raw_trigger.get("event_key") or "").strip().upper()
        if not event_key:
            errors.append("device_event trigger requires an 'event_key'.")
        else:
            normalized["event_key"] = event_key[:80]
        return (normalized if not errors else None), errors

    def _validate_action(self, raw_action: Any) -> tuple[dict[str, Any] | None, list[str]]:
        errors: list[str] = []
        if not isinstance(raw_action, dict):
            return None, ["Action must be an object."]

        forbidden_keys = sorted(key for key in raw_action.keys() if key in _FORBIDDEN_ACTION_KEYS)
        if forbidden_keys:
            return None, [f"Action may not include multi-step keys: {', '.join(forbidden_keys)}."]

        capability_id_raw = raw_action.get("capability_id")
        try:
            capability_id = int(capability_id_raw)
        except Exception:
            return None, ["Action must reference one integer capability_id."]

        try:
            capability = self._registry.get(capability_id)
        except Exception:
            return None, [f"Unknown capability id: {capability_id}."]

        if not self._registry.is_enabled(capability_id):
            errors.append(f"Capability {capability_id} is not enabled in the current runtime profile.")

        rule = POLICY_CAPABILITY_RULES.get(capability_id)
        if rule is None:
            errors.append(
                f"Capability {capability_id} is not in the Phase-6 atomic-policy allowlist."
            )

        if getattr(capability, "authority_scope", "suggest") not in {"observe", "suggest"}:
            errors.append(f"Capability {capability_id} is too strong for the Phase-6 foundation allowlist.")
        if getattr(capability, "risk_level", "low") != "low":
            errors.append(f"Capability {capability_id} is not low-risk enough for the Phase-6 foundation.")

        payload = raw_action.get("input", {})
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            errors.append("Action input must be an object.")
            payload = {}

        normalized_payload: dict[str, Any] = {}
        if rule is not None:
            allowed_keys = set(rule.get("allowed_input_keys") or set())
            unexpected = sorted(key for key in payload.keys() if key not in allowed_keys)
            if unexpected:
                errors.append(
                    f"Capability {capability_id} does not allow input keys: {', '.join(unexpected)}."
                )
            if capability_id == 57 and "mode" in payload:
                mode_value = str(payload.get("mode") or "").strip().lower()
                if mode_value not in set(rule.get("allowed_mode_values") or set()):
                    errors.append("Calendar snapshot mode must be 'today' when provided.")
                else:
                    normalized_payload["mode"] = mode_value

        normalized = {
            "capability_id": capability_id,
            "capability_name": str((rule or {}).get("name") or getattr(capability, "name", "") or "").strip(),
            "input": normalized_payload,
        }
        return (normalized if not errors else None), errors

    def _validate_envelope(
        self,
        raw_envelope: Any,
        action: dict[str, Any] | None,
    ) -> tuple[dict[str, Any] | None, list[str]]:
        errors: list[str] = []
        if not isinstance(raw_envelope, dict):
            return None, ["Envelope must be an object."]
        if action is None:
            return None, ["Envelope cannot be validated until the action is valid."]

        normalized: dict[str, Any] = {}
        integer_fields = {
            "max_runs_per_hour": (1, 24),
            "max_runs_per_day": (1, 48),
            "timeout_seconds": (1, 60),
            "retry_budget": (0, 3),
            "suspend_after_failures": (1, 20),
        }
        for field_name, (min_value, max_value) in integer_fields.items():
            raw_value = raw_envelope.get(field_name)
            try:
                value = int(raw_value)
            except Exception:
                errors.append(f"Envelope field '{field_name}' must be an integer.")
                continue
            if value < min_value or value > max_value:
                errors.append(
                    f"Envelope field '{field_name}' must be between {min_value} and {max_value}."
                )
                continue
            normalized[field_name] = value

        if "network_allowed" not in raw_envelope:
            errors.append("Envelope field 'network_allowed' is required.")
        else:
            network_allowed = bool(raw_envelope.get("network_allowed"))
            capability_id = int(action.get("capability_id") or 0)
            rule = POLICY_CAPABILITY_RULES.get(capability_id) or {}
            network_required = bool(rule.get("network_required"))
            if network_required and not network_allowed:
                errors.append(f"Capability {capability_id} requires network_allowed to be true.")
            if not network_required and network_allowed:
                errors.append(f"Capability {capability_id} may not request network access.")
            normalized["network_allowed"] = network_allowed

        if "scope" in raw_envelope and not isinstance(raw_envelope.get("scope"), dict):
            errors.append("Envelope 'scope' must be an object when provided.")
        elif isinstance(raw_envelope.get("scope"), dict):
            normalized["scope"] = dict(raw_envelope.get("scope") or {})

        return (normalized if not errors else None), errors
