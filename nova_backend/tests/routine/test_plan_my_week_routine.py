"""Tests for plan_my_week_routine.py — Plan My Week everyday workflow demo.

Invariants under test:
  1. run_plan_my_week_routine() returns (RoutineRun, PlanMyWeekProposal)
  2. Proposal has approval_required=True, always enforced
  3. Proposal and plan are non-authorizing: execution_performed=False,
     authorization_granted=False enforced via __post_init__
  4. All 8 expected blocks run in order
  5. WeeklyPlan sections populated from correct memory categories
  6. record_plan_approval() returns (RoutineRun, RoutineReceipt) with correct decision
  7. PlanApprovalRecord validates decision values
  8. ID linkage: proposal_id in approval record matches proposal
  9. Edge cases: empty/None inputs, malformed memory items
"""

from __future__ import annotations

import pytest

from src.routine.plan_my_week_routine import (
    PLAN_MY_WEEK_GRAPH,
    PlanApprovalRecord,
    PlanMyWeekProposal,
    WeeklyPlan,
    WeeklyPlanItem,
    record_plan_approval,
    run_plan_my_week_routine,
)
from src.routine.routine_graph import RoutineReceipt, RoutineRun

_EXPECTED_BLOCKS = (
    "gather_session_state",
    "gather_tasks_and_priorities",
    "gather_calendar",
    "gather_open_loops",
    "gather_receipts",
    "assemble_plan",
    "request_approval",
    "write_receipt",
)

_TASK_ITEM = {"id": "m1", "content": "finish the demo", "category": "task", "source": "explicit_user_save"}
_PRIORITY_ITEM = {"id": "m2", "content": "ship Stage 6", "category": "goal", "source": "explicit_user_save"}
_LOOP_ITEM = {"id": "m3", "content": "follow up with Chris", "category": "open_loop", "source": "explicit_user_save"}


def _run_with_content():
    return run_plan_my_week_routine(
        session_state={
            "session_id": "sess-1",
            "conversation_context": {
                "topic": "project planning",
                "user_goal": "ship RoutineGraph v0",
                "open_loops": ["review PR #93", "write tests"],
            },
        },
        memory_items=[_TASK_ITEM, _PRIORITY_ITEM, _LOOP_ITEM],
        calendar_data={
            "connected": True,
            "events": [{"title": "Team sync", "time": "Mon 10:00"}],
        },
    )


# ---------------------------------------------------------------------------
# Return types
# ---------------------------------------------------------------------------

def test_returns_run_and_proposal():
    run, proposal = run_plan_my_week_routine()
    assert isinstance(run, RoutineRun)
    assert isinstance(proposal, PlanMyWeekProposal)


def test_proposal_contains_weekly_plan():
    _, proposal = run_plan_my_week_routine()
    assert isinstance(proposal.plan, WeeklyPlan)


# ---------------------------------------------------------------------------
# Block execution
# ---------------------------------------------------------------------------

def test_all_blocks_run_in_order():
    run, _ = run_plan_my_week_routine()
    assert run.blocks_run == _EXPECTED_BLOCKS


def test_graph_has_correct_block_names():
    assert PLAN_MY_WEEK_GRAPH.block_names == _EXPECTED_BLOCKS


def test_graph_has_eight_blocks():
    assert len(PLAN_MY_WEEK_GRAPH.blocks) == 8


def test_graph_name_is_plan_my_week():
    assert PLAN_MY_WEEK_GRAPH.name == "plan_my_week"


# ---------------------------------------------------------------------------
# Approval boundary — PlanMyWeekProposal
# ---------------------------------------------------------------------------

def test_proposal_approval_required_always_true():
    _, proposal = run_plan_my_week_routine()
    assert proposal.approval_required is True


def test_proposal_approval_required_cannot_be_overridden():
    plan = WeeklyPlan(
        week_label="Week of 2026-05-03",
        timestamp_utc="2026-05-03T10:00:00+00:00",
        focus_items=(), tasks=(), calendar_events=(),
        open_loops=(), recommended_actions=(), sources_consulted=(),
    )
    p = PlanMyWeekProposal(proposal_id="PROP-ABCD1234", plan=plan, approval_required=False)
    assert p.approval_required is True


def test_proposal_execution_performed_always_false():
    plan = WeeklyPlan(
        week_label="Week of 2026-05-03",
        timestamp_utc="2026-05-03T10:00:00+00:00",
        focus_items=(), tasks=(), calendar_events=(),
        open_loops=(), recommended_actions=(), sources_consulted=(),
    )
    p = PlanMyWeekProposal(proposal_id="PROP-ABCD1234", plan=plan, execution_performed=True)
    assert p.execution_performed is False


def test_proposal_authorization_granted_always_false():
    plan = WeeklyPlan(
        week_label="Week of 2026-05-03",
        timestamp_utc="2026-05-03T10:00:00+00:00",
        focus_items=(), tasks=(), calendar_events=(),
        open_loops=(), recommended_actions=(), sources_consulted=(),
    )
    p = PlanMyWeekProposal(proposal_id="PROP-ABCD1234", plan=plan, authorization_granted=True)
    assert p.authorization_granted is False


def test_proposal_is_frozen():
    _, proposal = run_plan_my_week_routine()
    with pytest.raises((AttributeError, TypeError)):
        proposal.approval_required = False  # type: ignore[misc]


def test_proposal_id_starts_with_prop():
    _, proposal = run_plan_my_week_routine()
    assert proposal.proposal_id.startswith("PROP-")


def test_proposal_ids_are_unique():
    _, p1 = run_plan_my_week_routine()
    _, p2 = run_plan_my_week_routine()
    assert p1.proposal_id != p2.proposal_id


def test_proposal_empty_id_raises():
    plan = WeeklyPlan(
        week_label="Week of 2026-05-03",
        timestamp_utc="2026-05-03T10:00:00+00:00",
        focus_items=(), tasks=(), calendar_events=(),
        open_loops=(), recommended_actions=(), sources_consulted=(),
    )
    with pytest.raises(ValueError, match="proposal_id must not be empty"):
        PlanMyWeekProposal(proposal_id="", plan=plan)


def test_proposal_to_dict_shape():
    _, proposal = _run_with_content()
    d = proposal.to_dict()
    assert d["approval_required"] is True
    assert d["execution_performed"] is False
    assert d["authorization_granted"] is False
    assert "proposal_id" in d
    assert "plan" in d


# ---------------------------------------------------------------------------
# WeeklyPlan — non-authorizing invariants
# ---------------------------------------------------------------------------

def test_plan_execution_performed_always_false():
    run, _ = _run_with_content()
    plan_dict = run.outputs["weekly_plan"]
    assert plan_dict["execution_performed"] is False


def test_plan_authorization_granted_always_false():
    run, _ = _run_with_content()
    plan_dict = run.outputs["weekly_plan"]
    assert plan_dict["authorization_granted"] is False


def test_plan_weekly_plan_object_invariants():
    _, proposal = _run_with_content()
    assert proposal.plan.execution_performed is False
    assert proposal.plan.authorization_granted is False


# ---------------------------------------------------------------------------
# Plan content — memory category extraction
# ---------------------------------------------------------------------------

def test_tasks_extracted_from_task_category():
    _, proposal = _run_with_content()
    task_titles = [t.title for t in proposal.plan.tasks]
    assert "finish the demo" in task_titles


def test_priority_items_appear_in_focus():
    _, proposal = _run_with_content()
    focus_titles = [f.title for f in proposal.plan.focus_items]
    assert "ship Stage 6" in focus_titles


def test_open_loops_extracted_from_memory():
    _, proposal = _run_with_content()
    loop_titles = [l.title for l in proposal.plan.open_loops]
    assert "follow up with Chris" in loop_titles


def test_session_goal_appears_in_focus():
    _, proposal = _run_with_content()
    focus_titles = [f.title for f in proposal.plan.focus_items]
    assert any("RoutineGraph" in t for t in focus_titles)


def test_calendar_events_extracted_when_connected():
    _, proposal = _run_with_content()
    cal_titles = [e.title for e in proposal.plan.calendar_events]
    assert any("Team sync" in t for t in cal_titles)


def test_calendar_events_empty_when_not_connected():
    _, proposal = run_plan_my_week_routine(
        calendar_data={"connected": False, "events": [{"title": "hidden"}]},
    )
    assert proposal.plan.calendar_events == ()


def test_session_open_loops_included():
    _, proposal = _run_with_content()
    loop_titles = [l.title for l in proposal.plan.open_loops]
    # Session open loops from conversation_context
    assert any("PR #93" in t or "write tests" in t for t in loop_titles)


def test_recommended_actions_present():
    _, proposal = _run_with_content()
    assert len(proposal.plan.recommended_actions) >= 1


def test_sources_consulted_includes_memory():
    _, proposal = _run_with_content()
    assert "memory" in proposal.plan.sources_consulted


def test_sources_consulted_includes_calendar_when_connected():
    _, proposal = _run_with_content()
    assert "calendar" in proposal.plan.sources_consulted


def test_plan_has_content_with_data():
    _, proposal = _run_with_content()
    assert proposal.plan.has_content is True


def test_plan_has_no_content_with_empty_input():
    _, proposal = run_plan_my_week_routine()
    assert proposal.plan.has_content is False


# ---------------------------------------------------------------------------
# RoutineRun non-authorizing invariants
# ---------------------------------------------------------------------------

def test_run_execution_performed_is_false():
    run, _ = run_plan_my_week_routine()
    assert run.execution_performed is False


def test_run_authorization_granted_is_false():
    run, _ = run_plan_my_week_routine()
    assert run.authorization_granted is False


def test_all_output_keys_present():
    run, _ = _run_with_content()
    expected = {
        "session_state", "tasks_and_priorities", "calendar_data",
        "open_loops", "recent_receipts", "weekly_plan",
        "proposal", "routine_receipt",
    }
    assert set(run.outputs.keys()) == expected


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def test_no_tasks_warning_when_no_memory():
    run, _ = run_plan_my_week_routine(memory_items=[])
    assert "no_tasks_or_priorities" in run.warnings


def test_no_tasks_warning_absent_when_tasks_provided():
    run, _ = _run_with_content()
    assert "no_tasks_or_priorities" not in run.warnings


def test_plan_no_content_warning_with_empty_input():
    run, _ = run_plan_my_week_routine()
    assert "plan_has_no_content" in run.warnings


# ---------------------------------------------------------------------------
# record_plan_approval — Phase 2
# ---------------------------------------------------------------------------

def test_record_approval_returns_run_and_receipt():
    _, proposal = run_plan_my_week_routine()
    run, receipt = record_plan_approval(proposal, decision="approved")
    assert isinstance(run, RoutineRun)
    assert isinstance(receipt, RoutineReceipt)


def test_approval_decision_recorded_correctly():
    _, proposal = run_plan_my_week_routine()
    run, _ = record_plan_approval(proposal, decision="approved", notes="Looks good")
    approval = run.outputs["approval_record"]
    assert approval["decision"] == "approved"
    assert approval["notes"] == "Looks good"
    assert approval["proposal_id"] == proposal.proposal_id


def test_approval_proposal_id_matches():
    _, proposal = run_plan_my_week_routine()
    run, _ = record_plan_approval(proposal, decision="rejected")
    assert run.outputs["proposal_id"] == proposal.proposal_id


def test_approval_receipt_graph_name():
    _, proposal = run_plan_my_week_routine()
    _, receipt = record_plan_approval(proposal, decision="approved")
    assert "plan_my_week" in receipt.graph_name
    assert "approval" in receipt.graph_name


def test_approval_record_non_authorizing():
    _, proposal = run_plan_my_week_routine()
    run, receipt = record_plan_approval(proposal, decision="modified", notes="tweaked tasks")
    approval = run.outputs["approval_record"]
    assert approval["execution_performed"] is False
    assert approval["authorization_granted"] is False
    assert run.execution_performed is False
    assert receipt.execution_performed is False


def test_invalid_decision_raises():
    _, proposal = run_plan_my_week_routine()
    with pytest.raises(ValueError, match="decision must be one of"):
        record_plan_approval(proposal, decision="maybe")


def test_all_three_valid_decisions_accepted():
    for decision in ("approved", "rejected", "modified"):
        _, proposal = run_plan_my_week_routine()
        run, _ = record_plan_approval(proposal, decision=decision)
        assert run.outputs["approval_record"]["decision"] == decision


# ---------------------------------------------------------------------------
# PlanApprovalRecord direct tests
# ---------------------------------------------------------------------------

def test_plan_approval_record_enforces_false():
    rec = PlanApprovalRecord(
        approval_id="APR-ABCD1234",
        proposal_id="PROP-ABCD1234",
        decision="approved",
        execution_performed=True,
        authorization_granted=True,
    )
    assert rec.execution_performed is False
    assert rec.authorization_granted is False


def test_plan_approval_record_empty_approval_id_raises():
    with pytest.raises(ValueError, match="approval_id must not be empty"):
        PlanApprovalRecord(approval_id="", proposal_id="PROP-X", decision="approved")


def test_plan_approval_record_empty_proposal_id_raises():
    with pytest.raises(ValueError, match="proposal_id must not be empty"):
        PlanApprovalRecord(approval_id="APR-X", proposal_id="", decision="approved")


# ---------------------------------------------------------------------------
# WeeklyPlanItem
# ---------------------------------------------------------------------------

def test_weekly_plan_item_to_dict():
    item = WeeklyPlanItem(title="ship it", description="done", priority=1, source="memory")
    d = item.to_dict()
    assert d["title"] == "ship it"
    assert d["priority"] == 1
    assert d["source"] == "memory"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_inputs_do_not_raise():
    run, proposal = run_plan_my_week_routine()
    assert run is not None
    assert proposal is not None


def test_none_inputs_do_not_raise():
    run, proposal = run_plan_my_week_routine(
        session_state=None,
        memory_items=None,
        calendar_data=None,
        recent_receipts=None,
    )
    assert run is not None


def test_malformed_memory_items_do_not_raise():
    run, proposal = run_plan_my_week_routine(
        memory_items=[None, "not a dict", 42, {"content": "valid task", "category": "task"}],  # type: ignore[list-item]
    )
    assert run is not None


def test_unique_run_ids_across_calls():
    r1, _ = run_plan_my_week_routine()
    r2, _ = run_plan_my_week_routine()
    assert r1.run_id != r2.run_id


def test_timestamps_present_and_nonempty():
    run, _ = run_plan_my_week_routine()
    assert run.started_at
    assert run.completed_at
