from __future__ import annotations

from unittest.mock import Mock

import pytest
from src.actions.action_result import ActionResult
from src.governor.approval_grants import ApprovalGrantStore, normalized_action_hash
from src.governor.governor import Governor


class _Ledger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, dict(payload or {})))


def _governor(*, clock=None) -> tuple[Governor, Mock]:
    governor = Governor()
    governor._ledger = _Ledger()
    if clock is not None:
        governor._approval_grants = ApprovalGrantStore(clock=clock)
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
    now = [1000.0]
    governor, dispatch = _governor(clock=lambda: now[0])
    params = {"target": "documents"}
    grant = _grant(governor, params, ttl=1.0)
    now[0] = 1001.0

    result = governor.handle_governed_invocation(
        22,
        params,
        session_id="session-a",
        approval_id=grant.approval_id,
    )

    assert result.success is False
    assert result.data["approval_reason"] == "expired"
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
