"""
Daily Brief as the first governed RoutineGraph.

Wraps compose_daily_brief() as a named, receipted routine:
named blocks, a RoutineRun record, and a RoutineReceipt.

Non-authorizing: no capabilities invoked, no LLM calls, no external effects.
Caller is responsible for fetching external data (weather, calendar, email)
and injecting it as arguments.
"""

from __future__ import annotations

from typing import Any

from src.brief.daily_brief import DailyBrief, compose_daily_brief
from src.routine.routine_graph import (
    RoutineBlock,
    RoutineGraph,
    RoutineReceipt,
    RoutineRun,
    _receipt_id,
    _run_id,
    _utc_now,
)


# ---------------------------------------------------------------------------
# Block definitions
# ---------------------------------------------------------------------------

BLOCK_GATHER_SESSION = RoutineBlock(
    name="gather_session_state",
    description="Load session continuity fields: topic, goal, mode, open loops.",
    output_label="session_state",
)

BLOCK_GATHER_MEMORY = RoutineBlock(
    name="gather_memory",
    description="Load confirmed and candidate memory items.",
    output_label="memory_items",
)

BLOCK_GATHER_RECEIPTS = RoutineBlock(
    name="gather_receipts",
    description="Load recent action receipts.",
    output_label="recent_receipts",
)

BLOCK_GATHER_WEATHER = RoutineBlock(
    name="gather_weather",
    description="Consume pre-fetched weather data (caller-supplied).",
    output_label="weather_data",
)

BLOCK_GATHER_CALENDAR = RoutineBlock(
    name="gather_calendar",
    description="Consume pre-fetched calendar data (caller-supplied).",
    output_label="calendar_data",
)

BLOCK_GATHER_EMAIL = RoutineBlock(
    name="gather_email",
    description="Consume pre-fetched important emails (caller-supplied or placeholder).",
    output_label="important_emails",
)

BLOCK_BUILD_BRIEF = RoutineBlock(
    name="build_brief",
    description="Assemble DailyBrief from gathered inputs.",
    output_label="daily_brief",
)

BLOCK_WRITE_RECEIPT = RoutineBlock(
    name="write_receipt",
    description="Produce a RoutineReceipt recording what ran and what sources were consulted.",
    output_label="routine_receipt",
)


# ---------------------------------------------------------------------------
# Graph definition
# ---------------------------------------------------------------------------

DAILY_BRIEF_GRAPH = RoutineGraph(
    name="daily_brief",
    description="On-demand daily operating brief. Non-authorizing. No LLM calls.",
    blocks=(
        BLOCK_GATHER_SESSION,
        BLOCK_GATHER_MEMORY,
        BLOCK_GATHER_RECEIPTS,
        BLOCK_GATHER_WEATHER,
        BLOCK_GATHER_CALENDAR,
        BLOCK_GATHER_EMAIL,
        BLOCK_BUILD_BRIEF,
        BLOCK_WRITE_RECEIPT,
    ),
)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_daily_brief_routine(
    *,
    session_state: dict[str, Any] | None = None,
    memory_items: list[dict[str, Any]] | None = None,
    recent_receipts: list[dict[str, Any]] | None = None,
    working_context: dict[str, Any] | None = None,
    weather_data: dict[str, Any] | None = None,
    calendar_data: dict[str, Any] | None = None,
    important_emails: list[dict[str, Any]] | None = None,
) -> tuple[RoutineRun, RoutineReceipt]:
    """
    Execute the Daily Brief RoutineGraph.

    Returns (RoutineRun, RoutineReceipt).
    - RoutineRun.outputs["daily_brief"] contains the assembled DailyBrief as a dict.
    - RoutineReceipt is a slim non-authorizing proof artifact for the ledger.

    Non-authorizing: no capabilities invoked, no LLM calls, no external effects.
    """
    started_at = _utc_now()
    run_id = _run_id()
    blocks_run: list[str] = []
    outputs: dict[str, Any] = {}
    warnings: list[str] = []

    # Block: gather_session_state
    blocks_run.append(BLOCK_GATHER_SESSION.name)
    outputs[BLOCK_GATHER_SESSION.output_label] = session_state or {}

    # Block: gather_memory
    blocks_run.append(BLOCK_GATHER_MEMORY.name)
    _memory = list(memory_items or [])
    outputs[BLOCK_GATHER_MEMORY.output_label] = _memory
    if not _memory:
        warnings.append("no_memory_items")

    # Block: gather_receipts
    blocks_run.append(BLOCK_GATHER_RECEIPTS.name)
    outputs[BLOCK_GATHER_RECEIPTS.output_label] = list(recent_receipts or [])

    # Block: gather_weather
    blocks_run.append(BLOCK_GATHER_WEATHER.name)
    outputs[BLOCK_GATHER_WEATHER.output_label] = weather_data

    # Block: gather_calendar
    blocks_run.append(BLOCK_GATHER_CALENDAR.name)
    outputs[BLOCK_GATHER_CALENDAR.output_label] = calendar_data

    # Block: gather_email
    blocks_run.append(BLOCK_GATHER_EMAIL.name)
    outputs[BLOCK_GATHER_EMAIL.output_label] = important_emails

    # Block: build_brief
    blocks_run.append(BLOCK_BUILD_BRIEF.name)
    brief: DailyBrief = compose_daily_brief(
        session_state=session_state,
        memory_items=memory_items,
        recent_receipts=recent_receipts,
        working_context=working_context,
        weather_data=weather_data,
        calendar_data=calendar_data,
        important_emails=important_emails,
    )
    outputs[BLOCK_BUILD_BRIEF.output_label] = brief.to_dict()

    if not brief.has_content:
        warnings.append("brief_has_no_content")

    # Block: write_receipt
    blocks_run.append(BLOCK_WRITE_RECEIPT.name)
    completed_at = _utc_now()

    receipt = RoutineReceipt(
        receipt_id=_receipt_id(),
        run_id=run_id,
        graph_name=DAILY_BRIEF_GRAPH.name,
        completed_at=completed_at,
        blocks_run=tuple(blocks_run),
        sources_consulted=brief.sources_consulted,
        warnings=tuple(warnings),
    )
    outputs[BLOCK_WRITE_RECEIPT.output_label] = receipt.to_dict()

    run = RoutineRun(
        run_id=run_id,
        graph_name=DAILY_BRIEF_GRAPH.name,
        started_at=started_at,
        completed_at=completed_at,
        blocks_run=tuple(blocks_run),
        outputs=outputs,
        warnings=tuple(warnings),
    )

    return run, receipt
