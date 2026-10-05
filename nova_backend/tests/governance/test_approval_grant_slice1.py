from __future__ import annotations

from unittest.mock import Mock

import pytest
from src.actions.action_result import ActionResult
from src.governor.approval_grants import (
    ApprovalAuthorityMetadataError,
    ApprovalGrantError,
    ApprovalGrantStore,
    normalized_action_hash,
)
from src.governor.governor import Governor
from src.ledger.reader import LedgerAnalyzer
from src.ledger.writer import LedgerWriter


class _Ledger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, dict(payload or {})))


def _governor(*, wall_clock=None, monotonic_clock=None) -> tuple[Governor, Mock]:
    governor = Governor()
    governor._ledger = _Ledger()
    if wall_clock is not None or monotonic_clock is not None:
        governor._approval_grants = ApprovalGrantStore(
            wall_clock=wall_clock or (lambda: 1000.0),
            monotonic_clock=monotonic_clock or (lambda: 500.0),
        )
    dispatch = Mock(return_value=ActionResult.ok("executed"))
    governor._dispatch_capability = dispatch
    return governor, dispatch


def _grant(governor: Governor, params: dict, *, session_id: str = "session-a", ttl: float = 120.0):
    return governor.issue_approval_grant(
        session_id=session_id,
        capability_id=22,
        params=params,
        ttl_seconds=ttl,
    )


def test_normalized_action_hash_is_mapping_order_independent_and_value_exact():
    left = normalized_action_hash({"path": "C:/Nova", "options": {"a": 1, "b": [2, 3]}})
    reordered = normalized_action_hash({"options": {"b": [2, 3], "a": 1}, "path": "C:/Nova"})
    changed = normalized_action_hash({"path": "C:/Nova2", "options": {"a": 1, "b": [2, 3]}})

    assert left == reordered
    assert left != changed


def test_valid_exact_grant_permits_execution_once_then_refuses_replay():
    governor, dispatch = _governor()
    params = {"target": "documents"}
    grant = _grant(governor, params)

    first = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
        approval_id=grant.approval_id,
    )
    replay = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
        approval_id=grant.approval_id,
    )

    assert first.success is True
    assert replay.success is False
    assert replay.data["approval_reason"] == "replayed"
    assert dispatch.call_count == 1


def test_returned_grant_record_cannot_mutate_governor_authority():
    governor, dispatch = _governor()
    params = {"target": "documents"}
    grant = _grant(governor, params)
    grant.session_id = "attacker-session"
    grant.action_hash = "attacker-hash"

    result = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
        approval_id=grant.approval_id,
    )

    assert result.success is True
    dispatch.assert_called_once()


def test_nested_caller_mutation_after_consumption_cannot_change_dispatched_snapshot():
    governor, dispatch = _governor()
    params = {"operation": {"target": "approved-target", "steps": ["one"]}}
    grant = _grant(governor, params)

    def _inspect_dispatched_request(request):
        params["operation"]["target"] = "different-target"
        params["operation"]["steps"].append("two")
        assert request.params["operation"]["target"] == "approved-target"
        assert request.params["operation"]["steps"] == ["one"]
        return ActionResult.ok("executed")

    dispatch.side_effect = _inspect_dispatched_request
    result = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
        approval_id=grant.approval_id,
    )

    assert result.success is True
    dispatch.assert_called_once()


@pytest.mark.parametrize(
    ("params", "reason"),
    [
        ({"options": {"confirmed": True}}, "caller_confirmation_metadata"),
        ({"options": [{"approval_id": "forged"}]}, "untrusted_approval_metadata"),
    ],
)
def test_reserved_authority_metadata_is_rejected_recursively(params, reason):
    governor, dispatch = _governor()

    with pytest.raises(ApprovalAuthorityMetadataError):
        _grant(governor, params)
    result = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
    )

    assert result.data["approval_reason"] == reason
    dispatch.assert_not_called()


@pytest.mark.parametrize(
    ("invoke_capability", "invoke_session", "invoke_params", "approval_id", "reason"),
    [
        (22, "session-a", {"target": "downloads"}, "grant", "action_mismatch"),
        (22, "session-b", {"target": "documents"}, "grant", "session_mismatch"),
        (64, "session-a", {"target": "documents"}, "grant", "capability_mismatch"),
        (22, "session-a", {"target": "documents"}, "unknown", "unknown"),
    ],
)
def test_invalid_grant_conditions_refuse_before_executor(
    invoke_capability: int,
    invoke_session: str,
    invoke_params: dict,
    approval_id: str,
    reason: str,
):
    governor, dispatch = _governor()
    grant = _grant(governor, {"target": "documents"})
    selected_id = grant.approval_id if approval_id == "grant" else "not-a-real-grant"

    result = governor.handle_governed_invocation(
        invoke_capability,
        invoke_params,
        session_id=invoke_session,
        approval_id=selected_id,
    )

    assert result.success is False
    assert result.data["approval_reason"] == reason
    dispatch.assert_not_called()


def test_parameter_mutation_invalidates_grant_even_if_original_params_are_restored():
    governor, dispatch = _governor()
    original = {"target": "documents"}
    grant = _grant(governor, original)

    changed = governor.handle_governed_invocation(
        22,
        {"target": "downloads"},
        session_id="session-a",
        approval_id=grant.approval_id,
    )
    restored = governor.handle_governed_invocation(
        22,
        original,
        session_id="session-a",
        approval_id=grant.approval_id,
    )

    assert changed.data["approval_reason"] == "action_mismatch"
    assert restored.data["approval_reason"] == "invalidated"
    dispatch.assert_not_called()


def test_expired_grant_refuses_before_executor():
    wall = [1000.0]
    monotonic = [500.0]
    governor, dispatch = _governor(
        wall_clock=lambda: wall[0], monotonic_clock=lambda: monotonic[0]
    )
    params = {"target": "documents"}
    grant = _grant(governor, params, ttl=1.0)
    monotonic[0] = 501.0

    result = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
        approval_id=grant.approval_id,
    )

    assert result.success is False
    assert result.data["approval_reason"] == "expired"
    dispatch.assert_not_called()


@pytest.mark.parametrize("ttl", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_ttl_is_rejected_before_storage_or_ledger_issuance(ttl):
    governor, dispatch = _governor()

    with pytest.raises(ValueError, match="TTL must be between"):
        _grant(governor, {"target": "documents"}, ttl=ttl)

    assert governor._approval_grants._grants == {}
    assert governor.ledger.events == []
    dispatch.assert_not_called()


def test_wall_clock_rollback_cannot_extend_monotonic_expiration():
    wall = [1000.0]
    monotonic = [500.0]
    governor, dispatch = _governor(
        wall_clock=lambda: wall[0], monotonic_clock=lambda: monotonic[0]
    )
    params = {"target": "documents"}
    grant = _grant(governor, params, ttl=2.0)
    wall[0] = 100.0
    monotonic[0] = 502.0

    result = governor.handle_governed_invocation(
        22, params, session_id="session-a", approval_id=grant.approval_id
    )

    assert result.data["approval_reason"] == "expired"
    dispatch.assert_not_called()


def test_wall_clock_jump_forward_does_not_prematurely_expire_grant():
    wall = [1000.0]
    monotonic = [500.0]
    governor, dispatch = _governor(
        wall_clock=lambda: wall[0], monotonic_clock=lambda: monotonic[0]
    )
    params = {"target": "documents"}
    grant = _grant(governor, params, ttl=2.0)
    wall[0] = 100000.0
    monotonic[0] = 501.0

    result = governor.handle_governed_invocation(
        22, params, session_id="session-a", approval_id=grant.approval_id
    )

    assert result.success is True
    dispatch.assert_called_once()


def test_store_size_is_bounded_and_evicted_grants_fail_closed():
    store = ApprovalGrantStore(max_records=2)
    first = store.issue(session_id="s", capability_id=22, params={"target": "one"})
    store.issue(session_id="s", capability_id=22, params={"target": "two"})
    store.issue(session_id="s", capability_id=22, params={"target": "three"})

    decision = store.consume(
        approval_id=first.approval_id,
        session_id="s",
        capability_id=22,
        params_snapshot={"target": "one"},
    )

    assert len(store._grants) == 2
    assert decision.reason == "unknown"


def test_issuance_ledger_uses_non_reversible_grant_fingerprint():
    governor, _dispatch = _governor()
    grant = _grant(governor, {"target": "documents"})
    event_type, payload = governor.ledger.events[-1]

    assert event_type == "APPROVAL_GRANTED"
    assert "approval_id" not in payload
    assert payload["approval_fingerprint"]
    assert grant.approval_id not in str(payload)


def test_real_ledger_persists_approval_before_grant_is_returned(tmp_path):
    governor = Governor()
    path = tmp_path / "ledger.jsonl"
    governor._ledger = LedgerWriter(path)

    grant = _grant(governor, {"target": "documents"})

    records = LedgerAnalyzer(path).last_n(1)
    assert records[0]["event_type"] == "APPROVAL_GRANTED"
    assert records[0]["approval_fingerprint"]
    assert grant.approval_id not in str(records[0])


def test_real_ledger_failure_revokes_unissued_approval(tmp_path):
    governor = Governor()
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("occupied", encoding="utf-8")
    governor._ledger = LedgerWriter(blocked_parent / "ledger.jsonl")

    with pytest.raises(
        ApprovalGrantError,
        match="Approval receipt could not be persisted; approval was not issued",
    ):
        _grant(governor, {"target": "documents"})

    assert governor._approval_grants._grants == {}


def test_issuance_audit_failure_does_not_leave_execution_authority():
    governor, dispatch = _governor()
    governor._ledger.log_event = Mock(side_effect=RuntimeError("ledger unavailable"))

    with pytest.raises(ApprovalGrantError):
        _grant(governor, {"target": "documents"})

    assert governor._approval_grants._grants == {}
    dispatch.assert_not_called()


@pytest.mark.parametrize("confirmed", [True, False, "yes"])
def test_caller_supplied_confirmed_metadata_never_authorizes(confirmed):
    governor, dispatch = _governor()

    result = governor.handle_governed_invocation(
        22,
        {"target": "documents", "confirmed": confirmed},
        session_id="session-a",
    )

    assert result.success is False
    assert result.data["approval_reason"] == "caller_confirmation_metadata"
    dispatch.assert_not_called()


def test_approval_id_inside_action_params_is_untrusted_metadata():
    governor, dispatch = _governor()

    result = governor.handle_governed_invocation(
        22,
        {"target": "documents", "approval_id": "forged"},
        session_id="session-a",
    )

    assert result.success is False
    assert result.data["approval_reason"] == "untrusted_approval_metadata"
    dispatch.assert_not_called()


def test_destructive_memory_action_requires_grant_but_read_only_memory_does_not():
    governor, dispatch = _governor()

    refused = governor.handle_governed_invocation(
        61,
        {"action": "delete", "item_id": "MEM-1"},
        session_id="session-a",
    )
    allowed = governor.handle_governed_invocation(
        61,
        {"action": "list"},
        session_id="session-a",
    )

    assert refused.success is False
    assert refused.data["approval_reason"] == "missing"
    assert allowed.success is True
    assert dispatch.call_count == 1
