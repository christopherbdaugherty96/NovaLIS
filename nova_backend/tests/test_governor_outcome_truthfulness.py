"""Truthful-outcome reporting tests (PR: fix/truthful-outcome-reporting).

Covers the Tier-1 authorization-integrity truth fixes:
  - a boundary timeout reports outcome-unknown, never "cancelled";
  - a failed completion receipt yields completed_degraded, not clean success;
  - the original executor outcome stays visible through a degraded receipt;
  - neither path re-invokes the executor (no duplicate execution).

These are outcome-truth fixes, not the deeper ApprovalGrant redesign (locked
separately for the first post-observation lane).
"""
import types


def _fake_registry(name: str):
    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name=name)

        def is_enabled(self, capability_id):
            return True

    return FakeRegistry()


class _FakeLedger:
    def __init__(self, fail_event: str | None = None):
        self.events = []
        self._fail_event = fail_event

    def log_event(self, event_type, metadata):
        if self._fail_event and event_type == self._fail_event:
            from src.governor.exceptions import LedgerWriteFailed

            raise LedgerWriteFailed(f"forced failure for {event_type}")
        self.events.append((event_type, metadata))


def test_timeout_reports_outcome_unknown_not_cancelled(monkeypatch):
    from src.governor.governor import Governor

    gov = Governor()
    gov._registry = _fake_registry("volume_up_down")
    gov._ledger = _FakeLedger()

    dispatch_calls = {"count": 0}

    def _counting_dispatch(req):
        dispatch_calls["count"] += 1
        from src.actions.action_result import ActionResult

        return ActionResult.ok("done", request_id=req.request_id)

    monkeypatch.setattr(gov, "_dispatch_capability", _counting_dispatch)

    # Force the boundary to raise TimeoutError (the started-worker path where the
    # effect may still be running and cannot be force-cancelled).
    def _raise_timeout(operation, timeout_seconds=None):
        raise TimeoutError("Execution exceeded boundary timeout.")

    monkeypatch.setattr(gov._execute_boundary, "run_with_timeout", _raise_timeout)

    result = gov.handle_governed_invocation(19, {"action": "up"})

    assert result.success is False
    # Must NOT claim the action was cancelled — that would be inference-as-fact.
    assert "cancelled" not in result.message.lower()
    assert "canceled" not in result.message.lower()
    # Must report the honest outcome-unknown state.
    assert "outcome could not be verified" in result.message.lower()
    assert result.outcome_reason == "timed_out_outcome_unknown"
    # No ACTION_COMPLETED receipt was written for an unverified outcome.
    assert not any(event == "ACTION_COMPLETED" for event, _ in gov._ledger.events)


def test_receipt_failure_yields_completed_degraded_not_clean_success(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()
    gov._registry = _fake_registry("volume_up_down")
    gov._ledger = _FakeLedger(fail_event="ACTION_COMPLETED")

    dispatch_calls = {"count": 0}

    def _counting_dispatch(req):
        dispatch_calls["count"] += 1
        return ActionResult.ok(
            "Draft opened in local mail client.",
            request_id=req.request_id,
            external_effect=True,
            reversible=False,
            structured_data={"draft": "opened"},
        )

    monkeypatch.setattr(gov, "_dispatch_capability", _counting_dispatch)
    monkeypatch.setattr(gov._execute_boundary, "run_with_timeout", lambda op, timeout_seconds=None: op())
    monkeypatch.setattr(gov._execute_boundary, "enforce_memory_limits", lambda: None)
    monkeypatch.setattr(gov._execute_boundary, "enforce_cpu_limits", lambda: None)

    result = gov.handle_governed_invocation(19, {"action": "up"})

    # 1) The completed external effect is NOT rewritten into failure or refusal.
    assert result.success is True
    # 2) But it is not presented as an ordinary clean completion either.
    assert result.status == "completed_degraded"
    assert "receipt" in result.outcome_reason.lower()
    assert result.audit_degraded is True
    # 3) The original executor outcome remains visible.
    assert result.message == "Draft opened in local mail client."
    assert result.structured_data.get("draft") == "opened"
    assert result.external_effect is True
    # 4) No duplicate execution — the executor ran exactly once.
    assert dispatch_calls["count"] == 1


def test_receipt_failure_on_failed_executor_preserves_failure(monkeypatch):
    """A failed/refused outcome must never be rewritten into a degraded success."""
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()
    gov._registry = _fake_registry("response_verification")
    gov._ledger = _FakeLedger(fail_event="ACTION_COMPLETED")

    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.failure(
            "Model inference is blocked in this runtime.",
            request_id=req.request_id,
        ),
    )
    monkeypatch.setattr(gov._execute_boundary, "run_with_timeout", lambda op, timeout_seconds=None: op())
    monkeypatch.setattr(gov._execute_boundary, "enforce_memory_limits", lambda: None)
    monkeypatch.setattr(gov._execute_boundary, "enforce_cpu_limits", lambda: None)

    result = gov.handle_governed_invocation(31, {"text": "fact check this"})

    # Original failure is preserved: status and reason are NOT overwritten.
    assert result.success is False
    assert result.status == "failed"
    assert result.outcome_reason == "Model inference is blocked in this runtime."
    # Audit degradation is recorded only in the separate metadata channel.
    assert result.audit_degraded is True
    assert "receipt" in result.audit_degraded_reason.lower()


def test_clean_success_path_is_unchanged_when_receipt_persists(monkeypatch):
    """Guard: the degraded status only appears when the receipt actually fails."""
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    gov = Governor()
    gov._registry = _fake_registry("volume_up_down")
    gov._ledger = _FakeLedger()  # no forced failure

    monkeypatch.setattr(
        gov,
        "_dispatch_capability",
        lambda req: ActionResult.ok("done", request_id=req.request_id),
    )
    monkeypatch.setattr(gov._execute_boundary, "run_with_timeout", lambda op, timeout_seconds=None: op())
    monkeypatch.setattr(gov._execute_boundary, "enforce_memory_limits", lambda: None)
    monkeypatch.setattr(gov._execute_boundary, "enforce_cpu_limits", lambda: None)

    result = gov.handle_governed_invocation(19, {"action": "up"})

    assert result.success is True
    assert result.status == "completed"
    assert any(event == "ACTION_COMPLETED" for event, _ in gov._ledger.events)


def test_cap22_accepted_unverified_outcome_persists_in_completion_receipt(
    monkeypatch, tmp_path
):
    from src.executors.open_folder_executor import OpenFolderExecutor
    from src.governor.governor import Governor

    documents = tmp_path / "Documents"
    documents.mkdir()
    monkeypatch.setattr(
        "src.executors.open_folder_executor.PRESET_FOLDERS",
        {"documents": documents},
    )
    monkeypatch.setattr(
        "src.system_control.system_control_executor.SystemControlExecutor.open_path",
        lambda self, path: path == documents,
    )
    monkeypatch.setattr(
        OpenFolderExecutor,
        "_visible_folder_verified",
        lambda self, path: False,
    )

    gov = Governor()
    gov._ledger = _FakeLedger()
    params = {"target": "documents"}
    session_id = "cap22-outcome-receipt"
    grant = gov.issue_approval_grant(
        session_id=session_id,
        capability_id=22,
        params=params,
    )

    result = gov.handle_governed_invocation(
        22,
        params,
        session_id=session_id,
        approval_id=grant.approval_id,
    )
    completion = next(
        metadata
        for event_type, metadata in gov._ledger.events
        if event_type == "ACTION_COMPLETED"
    )

    assert result.success is True
    assert result.data["outcome_state"] == "accepted_unverified"
    assert completion["success"] is True
    assert completion["status"] == "completed"
    assert completion["outcome_state"] == "accepted_unverified"
    assert completion["launch_request_accepted"] is True
    assert completion["visible_effect_verified"] is False
    assert "could not be verified" in completion["outcome_reason"].lower()


def test_action_result_mark_audit_degraded_on_success():
    from src.actions.action_result import ActionResult

    result = ActionResult.ok("Effect happened.", external_effect=True)
    returned = result.mark_audit_degraded("receipt failed to persist")

    assert returned is result
    assert result.success is True
    assert result.status == "completed_degraded"
    assert result.message == "Effect happened."
    assert result.external_effect is True
    assert result.outcome_reason == "receipt failed to persist"
    assert result.audit_degraded is True
    # Survives the contract serializer without collapsing back to "completed".
    contract = result.to_contract_dict()
    assert contract["status"] == "completed_degraded"
    assert contract["audit_degraded"] is True


def test_action_result_mark_audit_degraded_on_failure_preserves_status():
    from src.actions.action_result import ActionResult

    result = ActionResult.failure("It broke.", status="failed")
    result.mark_audit_degraded("receipt failed to persist")

    # Failure is never rewritten into a degraded success.
    assert result.success is False
    assert result.status == "failed"
    assert result.outcome_reason == "It broke."
    # Degradation is recorded only on the separate channel.
    assert result.audit_degraded is True
    assert result.audit_degraded_reason == "receipt failed to persist"
    assert result.to_contract_dict()["status"] == "failed"
