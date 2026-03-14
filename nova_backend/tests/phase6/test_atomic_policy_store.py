from __future__ import annotations

from src.policies.atomic_policy_store import AtomicPolicyStore
from src.policies.policy_validator import PolicyValidationResult


def _valid_result() -> PolicyValidationResult:
    return PolicyValidationResult(
        valid=True,
        reasons=[],
        warnings=[],
        normalized_policy={
            "name": "Weekday calendar snapshot at 8:00 AM",
            "created_by": "user",
            "enabled": False,
            "state": "draft",
            "trigger": {
                "type": "time_weekly",
                "days": ["MO", "TU", "WE", "TH", "FR"],
                "time": "08:00",
            },
            "action": {
                "capability_id": 57,
                "capability_name": "calendar_snapshot",
                "input": {"mode": "today"},
            },
            "envelope": {
                "max_runs_per_hour": 1,
                "max_runs_per_day": 1,
                "timeout_seconds": 30,
                "retry_budget": 0,
                "suspend_after_failures": 3,
                "network_allowed": False,
            },
        },
    )


def test_create_draft_and_overview(tmp_path):
    store = AtomicPolicyStore(path=tmp_path / "atomic_policies.json")

    item = store.create_draft(policy=_valid_result().normalized_policy or {}, validation_result=_valid_result())
    snapshot = store.overview()

    assert item["policy_id"].startswith("POL-")
    assert snapshot["active_count"] == 1
    assert snapshot["draft_count"] == 1
    assert store.get_policy(item["policy_id"]) is not None


def test_delete_policy_marks_it_deleted(tmp_path):
    store = AtomicPolicyStore(path=tmp_path / "atomic_policies.json")

    item = store.create_draft(policy=_valid_result().normalized_policy or {}, validation_result=_valid_result())
    deleted = store.delete_policy(item["policy_id"])
    snapshot = store.overview()

    assert deleted["state"] == "deleted"
    assert snapshot["active_count"] == 0
    assert snapshot["deleted_count"] == 1


def test_invalid_validation_result_cannot_be_stored(tmp_path):
    store = AtomicPolicyStore(path=tmp_path / "atomic_policies.json")
    invalid = PolicyValidationResult(valid=False, reasons=["bad"], warnings=[], normalized_policy=None)

    try:
        store.create_draft(policy={}, validation_result=invalid)
    except ValueError as exc:
        assert "successful validation" in str(exc)
    else:
        raise AssertionError("Expected invalid draft creation to fail.")
