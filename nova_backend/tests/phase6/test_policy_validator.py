from __future__ import annotations

from src.governor.capability_registry import CapabilityRegistry
from src.policies.policy_validator import PolicyValidator


def _make_policy(*, capability_id: int = 57, network_allowed: bool = False) -> dict:
    return {
        "name": "Weekday calendar snapshot at 08:00",
        "created_by": "user",
        "enabled": False,
        "state": "draft",
        "trigger": {
            "type": "time_weekly",
            "days": ["MO", "TU", "WE", "TH", "FR"],
            "time": "08:00",
        },
        "action": {
            "capability_id": capability_id,
            "input": {"mode": "today"} if capability_id == 57 else {},
        },
        "envelope": {
            "max_runs_per_hour": 1,
            "max_runs_per_day": 1,
            "timeout_seconds": 30,
            "retry_budget": 0,
            "suspend_after_failures": 3,
            "network_allowed": network_allowed,
        },
    }


def test_valid_calendar_snapshot_policy_passes():
    validator = PolicyValidator(CapabilityRegistry())

    result = validator.validate(_make_policy())

    assert result.valid is True
    assert result.normalized_policy is not None
    assert result.normalized_policy["action"]["capability_id"] == 57
    assert result.normalized_policy["trigger"]["type"] == "time_weekly"


def test_foundation_rejects_memory_write_capability():
    validator = PolicyValidator(CapabilityRegistry())

    result = validator.validate(_make_policy(capability_id=61))

    assert result.valid is False
    assert any("allowlist" in reason.lower() for reason in result.reasons)


def test_foundation_rejects_network_mismatch():
    validator = PolicyValidator(CapabilityRegistry())

    result = validator.validate(_make_policy(capability_id=55, network_allowed=False))

    assert result.valid is False
    assert any("network_allowed" in reason for reason in result.reasons)


def test_foundation_rejects_enabled_policy_state():
    validator = PolicyValidator(CapabilityRegistry())
    policy = _make_policy()
    policy["enabled"] = True

    result = validator.validate(policy)

    assert result.valid is False
    assert any("disabled" in reason.lower() for reason in result.reasons)
