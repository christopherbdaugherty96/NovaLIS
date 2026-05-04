"""
Plan My Week — everyday workflow demo with an explicit approval boundary.

This is the second governed RoutineGraph and the first to include an
ApprovalBoundary block. The routine assembles a structured weekly plan
from memory, calendar, and session state, then surfaces it for user
approval before recording a receipt.

Non-authorizing at every stage:
- no LLM calls
- no capability invocations
- no external effects
- the plan is a proposal only — it does not save, schedule, or execute anything
- the receipt records the user's decision, not the execution of the plan
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

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
# Helpers
# ---------------------------------------------------------------------------

_MAX_ITEMS = 7
_TASK_CATEGORIES = {"task", "todo", "next_action", "next", "action"}
_LOOP_CATEGORIES = {"open_loop", "loop", "open", "pending", "unresolved"}
_PRIORITY_CATEGORIES = {"priority", "goal", "focus", "objective", "aim"}


def _prop_id() -> str:
    return f"PROP-{uuid.uuid4().hex[:8].upper()}"


def _apr_id() -> str:
    return f"APR-{uuid.uuid4().hex[:8].upper()}"


def _week_label() -> str:
    return f"Week of {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"


def _clean(value: Any, *, limit: int = 160) -> str:
    text = str(value or "").strip()
    return text[:limit] if len(text) > limit else text


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WeeklyPlanItem:
    """A single item in a WeeklyPlan section."""

    title: str
    description: str = ""
    priority: int = 3       # 1 = highest, 3 = normal, 5 = lowest
    source: str = ""        # "memory", "calendar", "session", "suggestion"

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "source": self.source,
        }


@dataclass(frozen=True)
class WeeklyPlan:
    """
    Assembled weekly plan. Non-authorizing — a proposal only.

    execution_performed and authorization_granted are enforced False
    via __post_init__ and cannot be overridden by callers.
    """

    week_label: str
    timestamp_utc: str
    focus_items: tuple[WeeklyPlanItem, ...]
    tasks: tuple[WeeklyPlanItem, ...]
    calendar_events: tuple[WeeklyPlanItem, ...]
    open_loops: tuple[WeeklyPlanItem, ...]
    recommended_actions: tuple[str, ...]
    sources_consulted: tuple[str, ...]
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)

    @property
    def has_content(self) -> bool:
        return bool(
            self.focus_items or self.tasks or self.calendar_events or self.open_loops
        )

    @property
    def total_items(self) -> int:
        return (
            len(self.focus_items)
            + len(self.tasks)
            + len(self.calendar_events)
            + len(self.open_loops)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "week_label": self.week_label,
            "timestamp_utc": self.timestamp_utc,
            "focus_items": [i.to_dict() for i in self.focus_items],
            "tasks": [i.to_dict() for i in self.tasks],
            "calendar_events": [i.to_dict() for i in self.calendar_events],
            "open_loops": [i.to_dict() for i in self.open_loops],
            "recommended_actions": list(self.recommended_actions),
            "sources_consulted": list(self.sources_consulted),
            "execution_performed": False,
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class PlanMyWeekProposal:
    """
    Proposal surfaced to the user at the approval boundary.

    approval_required is always True — enforced in __post_init__.
    execution_performed and authorization_granted are always False — enforced.

    The proposal does not save, schedule, or execute anything.
    It must be passed to record_plan_approval() for the decision to be recorded.
    """

    proposal_id: str
    plan: WeeklyPlan
    approval_required: bool = True
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "approval_required", True)
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)
        if not self.proposal_id.strip():
            raise ValueError("PlanMyWeekProposal proposal_id must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "plan": self.plan.to_dict(),
            "approval_required": True,
            "execution_performed": False,
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class PlanApprovalRecord:
    """
    Non-authorizing record of a user's approval decision on a PlanMyWeekProposal.

    decision must be one of: "approved", "rejected", "modified".
    execution_performed and authorization_granted are always False — enforced.
    """

    VALID_DECISIONS = frozenset({"approved", "rejected", "modified"})

    approval_id: str
    proposal_id: str
    decision: str       # "approved" | "rejected" | "modified"
    notes: str = ""
    decided_at: str = ""
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)
        if not self.approval_id.strip():
            raise ValueError("PlanApprovalRecord approval_id must not be empty.")
        if not self.proposal_id.strip():
            raise ValueError("PlanApprovalRecord proposal_id must not be empty.")
        if self.decision not in self.VALID_DECISIONS:
            raise ValueError(
                f"PlanApprovalRecord decision must be one of "
                f"{sorted(self.VALID_DECISIONS)}, got {self.decision!r}."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "proposal_id": self.proposal_id,
            "decision": self.decision,
            "notes": self.notes,
            "decided_at": self.decided_at,
            "execution_performed": False,
            "authorization_granted": False,
        }


# ---------------------------------------------------------------------------
# Block definitions
# ---------------------------------------------------------------------------

BLOCK_GATHER_SESSION = RoutineBlock(
    name="gather_session_state",
    description="Load session continuity fields: topic, goal, mode, open loops.",
    output_label="session_state",
)

BLOCK_GATHER_TASKS = RoutineBlock(
    name="gather_tasks_and_priorities",
    description="Load tasks, todos, and priority goals from memory items.",
    output_label="tasks_and_priorities",
)

BLOCK_GATHER_CALENDAR = RoutineBlock(
    name="gather_calendar",
    description="Consume pre-fetched calendar events (caller-supplied).",
    output_label="calendar_data",
)

BLOCK_GATHER_LOOPS = RoutineBlock(
    name="gather_open_loops",
    description="Load open loops from memory and session conversation context.",
    output_label="open_loops",
)

BLOCK_GATHER_RECEIPTS = RoutineBlock(
    name="gather_receipts",
    description="Load recent action receipts for context.",
    output_label="recent_receipts",
)

BLOCK_ASSEMBLE_PLAN = RoutineBlock(
    name="assemble_plan",
    description="Build WeeklyPlan from gathered inputs. Deterministic — no LLM.",
    output_label="weekly_plan",
)

BLOCK_REQUEST_APPROVAL = RoutineBlock(
    name="request_approval",
    description="Surface PlanMyWeekProposal to the user. Approval boundary — "
                "no action taken until record_plan_approval() is called.",
    output_label="proposal",
)

BLOCK_WRITE_RECEIPT = RoutineBlock(
    name="write_receipt",
    description="Produce a RoutineReceipt recording that the proposal was assembled.",
    output_label="routine_receipt",
)


# ---------------------------------------------------------------------------
# Graph definition
# ---------------------------------------------------------------------------

PLAN_MY_WEEK_GRAPH = RoutineGraph(
    name="plan_my_week",
    description=(
        "Everyday workflow: assemble a weekly plan from memory, calendar, and "
        "session state, then surface it for approval. Non-authorizing. No LLM calls."
    ),
    blocks=(
        BLOCK_GATHER_SESSION,
        BLOCK_GATHER_TASKS,
        BLOCK_GATHER_CALENDAR,
        BLOCK_GATHER_LOOPS,
        BLOCK_GATHER_RECEIPTS,
        BLOCK_ASSEMBLE_PLAN,
        BLOCK_REQUEST_APPROVAL,
        BLOCK_WRITE_RECEIPT,
    ),
)


# ---------------------------------------------------------------------------
# Assembly helpers
# ---------------------------------------------------------------------------

def _extract_tasks(memory_items: list[dict[str, Any]]) -> list[WeeklyPlanItem]:
    items: list[WeeklyPlanItem] = []
    for mem in memory_items:
        if not isinstance(mem, dict):
            continue
        category = _clean(mem.get("category") or mem.get("type") or "").lower()
        content = _clean(mem.get("content") or mem.get("text") or "")
        if not content or category not in _TASK_CATEGORIES:
            continue
        priority_raw = mem.get("priority")
        try:
            priority = int(priority_raw) if priority_raw is not None else 3
        except (ValueError, TypeError):
            priority = 3
        items.append(WeeklyPlanItem(
            title=content,
            source="memory",
            priority=max(1, min(5, priority)),
        ))
        if len(items) >= _MAX_ITEMS:
            break
    return items


def _extract_priorities(memory_items: list[dict[str, Any]]) -> list[WeeklyPlanItem]:
    items: list[WeeklyPlanItem] = []
    for mem in memory_items:
        if not isinstance(mem, dict):
            continue
        category = _clean(mem.get("category") or mem.get("type") or "").lower()
        content = _clean(mem.get("content") or mem.get("text") or "")
        if not content or category not in _PRIORITY_CATEGORIES:
            continue
        items.append(WeeklyPlanItem(title=content, source="memory", priority=1))
        if len(items) >= _MAX_ITEMS:
            break
    return items


def _extract_session_focus(session_state: dict[str, Any]) -> list[WeeklyPlanItem]:
    items: list[WeeklyPlanItem] = []
    conv_ctx = _as_dict(session_state.get("conversation_context"))

    goal = _clean(conv_ctx.get("user_goal") or session_state.get("task_goal") or "")
    if goal:
        items.append(WeeklyPlanItem(title=goal, source="session", priority=1))

    topic = _clean(conv_ctx.get("topic") or session_state.get("active_topic") or "")
    if topic and topic != goal:
        items.append(WeeklyPlanItem(title=f"Active topic: {topic}", source="session", priority=2))

    return items[:_MAX_ITEMS]


def _extract_calendar_events(calendar_data: dict[str, Any] | None) -> list[WeeklyPlanItem]:
    if not isinstance(calendar_data, dict) or not calendar_data.get("connected"):
        return []
    events: list[WeeklyPlanItem] = []
    for event in _as_list(calendar_data.get("events"))[:_MAX_ITEMS]:
        if not isinstance(event, dict):
            continue
        title = _clean(event.get("title") or "Untitled event")
        time_label = _clean(event.get("time") or event.get("date") or "", limit=30)
        desc = f"{time_label} — {title}" if time_label else title
        events.append(WeeklyPlanItem(title=desc, source="calendar", priority=2))
    return events


def _extract_open_loops(
    memory_items: list[dict[str, Any]],
    session_state: dict[str, Any],
) -> list[WeeklyPlanItem]:
    loops: list[WeeklyPlanItem] = []
    seen: set[str] = set()

    # Memory-sourced open loops
    for mem in memory_items:
        if not isinstance(mem, dict):
            continue
        category = _clean(mem.get("category") or mem.get("type") or "").lower()
        content = _clean(mem.get("content") or mem.get("text") or "")
        if not content or content in seen or category not in _LOOP_CATEGORIES:
            continue
        loops.append(WeeklyPlanItem(title=content, source="memory", priority=3))
        seen.add(content)
        if len(loops) >= _MAX_ITEMS:
            break

    # Conversation-context open loops
    conv_ctx = _as_dict(session_state.get("conversation_context"))
    for loop_text in _as_list(conv_ctx.get("open_loops"))[:3]:
        text = _clean(str(loop_text))
        if text and text not in seen:
            loops.append(WeeklyPlanItem(title=text, source="session", priority=3))
            seen.add(text)

    return loops[:_MAX_ITEMS]


def _build_recommendations(
    tasks: list[WeeklyPlanItem],
    loops: list[WeeklyPlanItem],
    focus: list[WeeklyPlanItem],
) -> list[str]:
    recs: list[str] = []
    if focus:
        recs.append(f"Start with your top priority: {focus[0].title}")
    if tasks:
        recs.append(f"First task to complete: {tasks[0].title}")
    if loops:
        recs.append(f"Oldest open loop to resolve: {loops[0].title}")
    if not recs:
        recs.append("Review your memory items and add tasks to get personalised recommendations.")
    return recs[:3]


def _assemble_weekly_plan(
    session_state: dict[str, Any],
    memory_items: list[dict[str, Any]],
    calendar_data: dict[str, Any] | None,
) -> WeeklyPlan:
    tasks = _extract_tasks(memory_items)
    priorities = _extract_priorities(memory_items)
    session_focus = _extract_session_focus(session_state)
    calendar_events = _extract_calendar_events(calendar_data)
    loops = _extract_open_loops(memory_items, session_state)

    # Focus = explicit priorities + session focus, deduplicated by title
    seen_titles: set[str] = set()
    focus_items: list[WeeklyPlanItem] = []
    for item in priorities + session_focus:
        if item.title not in seen_titles:
            focus_items.append(item)
            seen_titles.add(item.title)
    focus_items = focus_items[:_MAX_ITEMS]

    recommendations = _build_recommendations(tasks, loops, focus_items)

    sources: list[str] = []
    if memory_items:
        sources.append("memory")
    if calendar_events:
        sources.append("calendar")
    if session_state:
        sources.append("session")

    return WeeklyPlan(
        week_label=_week_label(),
        timestamp_utc=_utc_now(),
        focus_items=tuple(focus_items),
        tasks=tuple(tasks),
        calendar_events=tuple(calendar_events),
        open_loops=tuple(loops),
        recommended_actions=tuple(recommendations),
        sources_consulted=tuple(sources),
    )


# ---------------------------------------------------------------------------
# Runner — Phase 1: assemble and propose
# ---------------------------------------------------------------------------

def run_plan_my_week_routine(
    *,
    session_state: dict[str, Any] | None = None,
    memory_items: list[dict[str, Any]] | None = None,
    calendar_data: dict[str, Any] | None = None,
    recent_receipts: list[dict[str, Any]] | None = None,
) -> tuple[RoutineRun, PlanMyWeekProposal]:
    """
    Execute Phase 1 of the Plan My Week routine: gather data and assemble a proposal.

    Returns (RoutineRun, PlanMyWeekProposal).
    The proposal must be presented to the user and passed to record_plan_approval()
    to record the decision. Nothing is saved or executed until the user approves.

    Non-authorizing: no capabilities invoked, no LLM calls, no external effects.
    """
    started_at = _utc_now()
    run_id = _run_id()
    blocks_run: list[str] = []
    outputs: dict[str, Any] = {}
    warnings: list[str] = []

    _session = dict(session_state or {})
    _memory = list(memory_items or [])
    _receipts = list(recent_receipts or [])

    # Block: gather_session_state
    blocks_run.append(BLOCK_GATHER_SESSION.name)
    outputs[BLOCK_GATHER_SESSION.output_label] = _session

    # Block: gather_tasks_and_priorities
    blocks_run.append(BLOCK_GATHER_TASKS.name)
    task_items = _extract_tasks(_memory)
    priority_items = _extract_priorities(_memory)
    outputs[BLOCK_GATHER_TASKS.output_label] = {
        "tasks": [t.to_dict() for t in task_items],
        "priorities": [p.to_dict() for p in priority_items],
    }
    if not task_items and not priority_items:
        warnings.append("no_tasks_or_priorities")

    # Block: gather_calendar
    blocks_run.append(BLOCK_GATHER_CALENDAR.name)
    outputs[BLOCK_GATHER_CALENDAR.output_label] = calendar_data

    # Block: gather_open_loops
    blocks_run.append(BLOCK_GATHER_LOOPS.name)
    loop_items = _extract_open_loops(_memory, _session)
    outputs[BLOCK_GATHER_LOOPS.output_label] = [l.to_dict() for l in loop_items]

    # Block: gather_receipts
    blocks_run.append(BLOCK_GATHER_RECEIPTS.name)
    outputs[BLOCK_GATHER_RECEIPTS.output_label] = _receipts

    # Block: assemble_plan
    blocks_run.append(BLOCK_ASSEMBLE_PLAN.name)
    plan = _assemble_weekly_plan(_session, _memory, calendar_data)
    outputs[BLOCK_ASSEMBLE_PLAN.output_label] = plan.to_dict()
    if not plan.has_content:
        warnings.append("plan_has_no_content")

    # Block: request_approval  ← approval boundary
    blocks_run.append(BLOCK_REQUEST_APPROVAL.name)
    proposal = PlanMyWeekProposal(
        proposal_id=_prop_id(),
        plan=plan,
    )
    outputs[BLOCK_REQUEST_APPROVAL.output_label] = proposal.to_dict()

    # Block: write_receipt
    blocks_run.append(BLOCK_WRITE_RECEIPT.name)
    completed_at = _utc_now()
    receipt = RoutineReceipt(
        receipt_id=_receipt_id(),
        run_id=run_id,
        graph_name=PLAN_MY_WEEK_GRAPH.name,
        completed_at=completed_at,
        blocks_run=tuple(blocks_run),
        sources_consulted=plan.sources_consulted,
        warnings=tuple(warnings),
    )
    outputs[BLOCK_WRITE_RECEIPT.output_label] = receipt.to_dict()

    run = RoutineRun(
        run_id=run_id,
        graph_name=PLAN_MY_WEEK_GRAPH.name,
        started_at=started_at,
        completed_at=completed_at,
        blocks_run=tuple(blocks_run),
        outputs=outputs,
        warnings=tuple(warnings),
    )

    return run, proposal


# ---------------------------------------------------------------------------
# Runner — Phase 2: record approval decision
# ---------------------------------------------------------------------------

def record_plan_approval(
    proposal: PlanMyWeekProposal,
    *,
    decision: str,
    notes: str = "",
) -> tuple[RoutineRun, RoutineReceipt]:
    """
    Record the user's approval decision for a PlanMyWeekProposal.

    decision must be one of: "approved", "rejected", "modified".
    notes is optional free-text from the user.

    Returns (RoutineRun, RoutineReceipt).
    The RoutineRun outputs["approval_record"] contains the PlanApprovalRecord.

    Non-authorizing: records the decision only; does not execute the plan,
    save memory items, or invoke any capability.
    """
    started_at = _utc_now()
    run_id = _run_id()

    approval = PlanApprovalRecord(
        approval_id=_apr_id(),
        proposal_id=proposal.proposal_id,
        decision=decision,
        notes=_clean(notes, limit=500),
        decided_at=started_at,
    )

    completed_at = _utc_now()
    outputs: dict[str, Any] = {
        "proposal_id": proposal.proposal_id,
        "approval_record": approval.to_dict(),
    }

    receipt = RoutineReceipt(
        receipt_id=_receipt_id(),
        run_id=run_id,
        graph_name=f"{PLAN_MY_WEEK_GRAPH.name}_approval",
        completed_at=completed_at,
        blocks_run=("record_approval",),
        sources_consulted=(),
        warnings=(),
    )

    run = RoutineRun(
        run_id=run_id,
        graph_name=f"{PLAN_MY_WEEK_GRAPH.name}_approval",
        started_at=started_at,
        completed_at=completed_at,
        blocks_run=("record_approval",),
        outputs=outputs,
        warnings=(),
    )

    return run, receipt
