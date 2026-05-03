"""Tests for daily_brief_routine.py — Daily Brief as RoutineGraph v0.

Invariants under test:
  1. run_daily_brief_routine() returns (RoutineRun, RoutineReceipt)
  2. All eight expected blocks run in order
  3. outputs["daily_brief"] has correct non-authorizing shape
  4. execution_performed=False and authorization_granted=False in run and receipt
  5. run_id is shared between run and receipt
  6. Warnings emitted correctly (e.g. no_memory_items)
  7. sources_consulted in receipt matches brief sources
  8. Works on empty inputs without raising
"""

from __future__ import annotations

from src.routine.daily_brief_routine import (
    DAILY_BRIEF_GRAPH,
    run_daily_brief_routine,
)
from src.routine.routine_graph import RoutineReceipt, RoutineRun

_EXPECTED_BLOCKS = (
    "gather_session_state",
    "gather_memory",
    "gather_receipts",
    "gather_weather",
    "gather_calendar",
    "gather_email",
    "build_brief",
    "write_receipt",
)


def _run_with_content():
    return run_daily_brief_routine(
        session_state={
            "session_id": "sess-1",
            "conversation_context": {"topic": "project planning", "user_goal": "ship Stage 6"},
        },
        memory_items=[
            {"id": "m1", "content": "finish RoutineGraph", "category": "task", "source": "explicit_user_save"},
        ],
        recent_receipts=[
            {"event_type": "MEMORY_ITEM_SAVED", "timestamp_utc": "2026-05-03T09:00:00+00:00"},
        ],
    )


# ---------------------------------------------------------------------------
# Return types
# ---------------------------------------------------------------------------

def test_returns_run_and_receipt():
    run, receipt = run_daily_brief_routine()
    assert isinstance(run, RoutineRun)
    assert isinstance(receipt, RoutineReceipt)


# ---------------------------------------------------------------------------
# Block execution
# ---------------------------------------------------------------------------

def test_all_blocks_run():
    run, _ = run_daily_brief_routine()
    assert run.blocks_run == _EXPECTED_BLOCKS


def test_graph_has_correct_block_names():
    assert DAILY_BRIEF_GRAPH.block_names == _EXPECTED_BLOCKS


def test_graph_has_eight_blocks():
    assert len(DAILY_BRIEF_GRAPH.blocks) == 8


def test_graph_name_is_daily_brief():
    assert DAILY_BRIEF_GRAPH.name == "daily_brief"


# ---------------------------------------------------------------------------
# ID linkage
# ---------------------------------------------------------------------------

def test_run_id_shared_between_run_and_receipt():
    run, receipt = run_daily_brief_routine()
    assert run.run_id == receipt.run_id


def test_run_id_starts_with_run_prefix():
    run, _ = run_daily_brief_routine()
    assert run.run_id.startswith("RUN-")


def test_receipt_id_starts_with_rr_prefix():
    _, receipt = run_daily_brief_routine()
    assert receipt.receipt_id.startswith("RR-")


def test_run_and_receipt_graph_name_match():
    run, receipt = run_daily_brief_routine()
    assert run.graph_name == "daily_brief"
    assert receipt.graph_name == "daily_brief"


def test_run_and_receipt_blocks_run_match():
    run, receipt = run_daily_brief_routine()
    assert run.blocks_run == receipt.blocks_run


# ---------------------------------------------------------------------------
# Non-authorizing invariants
# ---------------------------------------------------------------------------

def test_run_execution_performed_is_false():
    run, _ = run_daily_brief_routine()
    assert run.execution_performed is False


def test_run_authorization_granted_is_false():
    run, _ = run_daily_brief_routine()
    assert run.authorization_granted is False


def test_receipt_execution_performed_is_false():
    _, receipt = run_daily_brief_routine()
    assert receipt.execution_performed is False


def test_receipt_authorization_granted_is_false():
    _, receipt = run_daily_brief_routine()
    assert receipt.authorization_granted is False


def test_brief_output_execution_performed_is_false():
    run, _ = _run_with_content()
    brief_dict = run.outputs["daily_brief"]
    assert brief_dict["execution_performed"] is False


def test_brief_output_authorization_granted_is_false():
    run, _ = _run_with_content()
    brief_dict = run.outputs["daily_brief"]
    assert brief_dict["authorization_granted"] is False


# ---------------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------------

def test_all_output_keys_present():
    run, _ = _run_with_content()
    expected = {
        "session_state", "memory_items", "recent_receipts",
        "weather_data", "calendar_data", "important_emails",
        "daily_brief", "routine_receipt",
    }
    assert set(run.outputs.keys()) == expected


def test_outputs_daily_brief_key_present():
    run, _ = run_daily_brief_routine()
    assert "daily_brief" in run.outputs


def test_outputs_daily_brief_has_date_covered():
    run, _ = run_daily_brief_routine()
    brief_dict = run.outputs["daily_brief"]
    assert "date_covered" in brief_dict
    assert brief_dict["date_covered"]


def test_outputs_daily_brief_has_sections():
    run, _ = _run_with_content()
    brief_dict = run.outputs["daily_brief"]
    assert "sections" in brief_dict
    assert isinstance(brief_dict["sections"], list)


def test_outputs_routine_receipt_key_present():
    run, _ = run_daily_brief_routine()
    assert "routine_receipt" in run.outputs


def test_outputs_routine_receipt_matches_returned_receipt():
    run, receipt = run_daily_brief_routine()
    receipt_dict = run.outputs["routine_receipt"]
    assert receipt_dict["receipt_id"] == receipt.receipt_id
    assert receipt_dict["run_id"] == receipt.run_id


# ---------------------------------------------------------------------------
# Sources and warnings
# ---------------------------------------------------------------------------

def test_sources_consulted_includes_memory_when_provided():
    _, receipt = _run_with_content()
    assert "memory" in receipt.sources_consulted


def test_sources_consulted_includes_receipts_when_provided():
    _, receipt = _run_with_content()
    assert "receipts" in receipt.sources_consulted


def test_no_memory_items_warning_when_empty():
    _, receipt = run_daily_brief_routine(memory_items=[])
    assert "no_memory_items" in receipt.warnings


def test_no_warning_when_memory_provided():
    _, receipt = _run_with_content()
    assert "no_memory_items" not in receipt.warnings


def test_warnings_match_between_run_and_receipt():
    run, receipt = run_daily_brief_routine()
    assert run.warnings == receipt.warnings


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_inputs_do_not_raise():
    run, receipt = run_daily_brief_routine()
    assert run is not None
    assert receipt is not None


def test_none_inputs_do_not_raise():
    run, receipt = run_daily_brief_routine(
        session_state=None,
        memory_items=None,
        recent_receipts=None,
        weather_data=None,
        calendar_data=None,
        important_emails=None,
    )
    assert run is not None
    assert receipt is not None


def test_malformed_memory_item_does_not_raise():
    run, receipt = run_daily_brief_routine(
        memory_items=[None, "not a dict", {"content": "valid", "category": "task"}],  # type: ignore[list-item]
    )
    assert run is not None


def test_timestamps_are_present_and_nonempty():
    run, receipt = run_daily_brief_routine()
    assert run.started_at
    assert run.completed_at
    assert receipt.completed_at


def test_unique_run_ids_across_calls():
    run1, _ = run_daily_brief_routine()
    run2, _ = run_daily_brief_routine()
    assert run1.run_id != run2.run_id


def test_unique_receipt_ids_across_calls():
    _, r1 = run_daily_brief_routine()
    _, r2 = run_daily_brief_routine()
    assert r1.receipt_id != r2.receipt_id
