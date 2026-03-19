from __future__ import annotations

from src.actions.action_result import ActionResult
from src.governor.capability_registry import CapabilityRegistry
from src.governor.capability_topology import CapabilityTopology
from src.governor.governor import Governor
from src.governor.policy_executor_gate import PolicyExecutorGate
from src.policies.policy_validator import PolicyValidator


def _make_policy(*, capability_id: int = 57, network_allowed: bool = False) -> dict:
    name_map = {
        32: "System status",
        55: "Weather snapshot",
        56: "News snapshot",
        57: "Calendar snapshot",
    }
    inputs = {"mode": "today"} if capability_id == 57 else {}
    return {
        "policy_id": "POL-TEST-0001",
        "name": f"Weekday {name_map.get(capability_id, 'Unknown')} at 08:00",
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
            "input": inputs,
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


def _gate() -> PolicyExecutorGate:
    registry = CapabilityRegistry()
    validator = PolicyValidator(registry)
    topology = CapabilityTopology(registry)
    return PolicyExecutorGate(registry, validator, topology)


def test_executor_gate_allows_local_snapshot_simulation():
    decision = _gate().simulate(_make_policy(capability_id=57))

    assert decision.allowed is True
    assert decision.capability_class == "read_only_local"
    assert decision.readiness_label == "Ready for manual review run"


def test_executor_gate_blocks_network_snapshot_for_current_stage():
    decision = _gate().simulate(_make_policy(capability_id=55, network_allowed=True))

    assert decision.allowed is False
    assert decision.blocked_reason == "authority_class_exceeds_current_limit"
    assert decision.readiness_label == "Blocked by current runtime stage"


def test_governor_manual_run_once_executes_safe_policy(monkeypatch):
    monkeypatch.setattr("src.ledger.writer.LedgerWriter.log_event", lambda self, event_type, metadata: None)
    governor = Governor()
    monkeypatch.setattr(
        governor,
        "handle_governed_invocation",
        lambda capability_id, params: ActionResult.ok(
            "Diagnostics ready.",
            structured_data={"health_state": "healthy"},
        ),
    )

    decision, result = governor.run_atomic_policy_once(_make_policy(capability_id=32))

    assert decision.allowed is True
    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data.get("structured_data", {}).get("health_state") == "healthy"
    assert result.data.get("policy_id") == "POL-TEST-0001"


def test_governor_manual_run_once_blocks_nonlocal_policy(monkeypatch):
    monkeypatch.setattr("src.ledger.writer.LedgerWriter.log_event", lambda self, event_type, metadata: None)
    governor = Governor()

    decision, result = governor.run_atomic_policy_once(_make_policy(capability_id=55, network_allowed=True))

    assert decision.allowed is False
    assert result.success is False
    assert "Blocked under current Phase-6 delegation rules." in result.message
