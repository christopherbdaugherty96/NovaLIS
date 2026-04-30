"""Planning-only Brain task understanding scaffold.

This module turns a user request plus optional local context into structured
planning metadata. It does not execute, authorize, route capabilities, call
OpenClaw, write files, or bypass the Governor.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class ContextSource(_StringEnum):
    STABLE_MEMORY = "stable_memory"
    SESSION_CONTEXT = "session_context"
    INFERRED_ASSUMPTION = "inferred_assumption"
    SYSTEM_LIMITATION = "system_limitation"


class ApprovalLevel(_StringEnum):
    NONE = "none"
    USER_REVIEW_ONLY = "user_review_only"


@dataclass(frozen=True)
class ContextUsed:
    source: ContextSource
    label: str
    value: str


@dataclass(frozen=True)
class TaskUnderstanding:
    goal: str
    context_used: tuple[ContextUsed, ...] = ()
    constraints: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    confidence: float = 0.0
    clarification_needed: bool = False
    suggested_next_step: str = ""
    authority_effect: str = "none"
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be 0.0-1.0, got {self.confidence}")
        if self.authority_effect != "none":
            raise ValueError("TaskUnderstanding is non-authorizing: authority_effect must be 'none'.")
        if self.execution_performed:
            raise ValueError("TaskUnderstanding must not record executed actions.")
        if self.authorization_granted:
            raise ValueError("TaskUnderstanding must not grant authorization.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class TaskEnvelope:
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    environment_scope: tuple[str, ...]
    step_limit: int
    approval_level: ApprovalLevel
    stop_condition: str
    failure_behavior: str
    authority_effect: str = "none"

    def __post_init__(self) -> None:
        if self.step_limit < 1:
            raise ValueError("step_limit must be at least 1")
        if self.authority_effect != "none":
            raise ValueError("TaskEnvelope is non-authorizing: authority_effect must be 'none'.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class SimpleTaskPlan:
    mode: str
    planning_only: bool
    understanding: TaskUnderstanding
    envelope: TaskEnvelope
    plan_steps: tuple[str, ...] = field(default_factory=tuple)
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if not self.planning_only:
            raise ValueError("SimpleTaskPlan must remain planning-only.")
        if self.execution_performed:
            raise ValueError("SimpleTaskPlan must not execute actions.")
        if self.authorization_granted:
            raise ValueError("SimpleTaskPlan must not grant authorization.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


_SCRIPT_PLAN_RE = re.compile(r"\b(?:turn|convert|make)\b.{0,80}\b(?:script)\b.{0,80}\b(?:scene plan|scenes?)\b", re.I)
_SUMMARY_RE = re.compile(r"\b(?:summari[sz]e|summary)\b.{0,80}\b(?:task|request|this)\b", re.I)
_CLARIFICATION_RE = re.compile(r"\b(?:clarification|clarify|missing|ambiguous|unclear)\b", re.I)
_ENVELOPE_RE = re.compile(r"\b(?:bounded task envelope|task envelope|envelope)\b", re.I)
_AMBIGUOUS_REFERENCE_RE = re.compile(r"\b(?:this|that|it|them|the above|previous)\b", re.I)
_HIGH_EFFECT_RE = re.compile(
    r"\b(?:open browser|openclaw|send email|schedule|book|purchase|buy|post|publish|delete|write files?|update account|shopify)\b",
    re.I,
)


def understand_task(
    message: str,
    *,
    session_context: dict[str, str] | None = None,
    stable_memory: Iterable[str] | None = None,
) -> TaskUnderstanding:
    """Return conservative, non-authorizing task understanding.

    `stable_memory` is caller-provided only. This module intentionally does not
    read runtime memory stores; when no memory is provided, it records that
    limitation instead of pretending memory was consulted.
    """

    text = (message or "").strip()
    session = {str(k): str(v) for k, v in (session_context or {}).items() if str(v).strip()}
    memories = tuple(str(item).strip() for item in (stable_memory or ()) if str(item).strip())
    context_used = _context_used(session, memories)
    goal = _goal_from_message(text)
    assumptions: list[str] = []
    constraints = [
        "planning-only",
        "does not execute tools or capabilities",
        "does not authorize actions",
        "does not bypass GovernorMediator",
    ]

    if _HIGH_EFFECT_RE.search(text):
        constraints.extend(
            [
                "no browser tabs opened",
                "no OpenClaw execution",
                "no email sending",
                "no scheduling or account actions",
                "no file writes",
            ]
        )

    needs_context = bool(_AMBIGUOUS_REFERENCE_RE.search(text)) or not text
    has_context = bool(session)
    clarification_needed = needs_context and not has_context

    if _SCRIPT_PLAN_RE.search(text) and not _has_context_key(session, "script"):
        clarification_needed = True
        assumptions.append("No script text was available in session context.")
    elif _SCRIPT_PLAN_RE.search(text):
        assumptions.append("The provided session script is the source material to plan from.")

    if _SUMMARY_RE.search(text) and needs_context and not has_context:
        clarification_needed = True
        assumptions.append("The task to summarize was referenced but not provided.")

    if not memories:
        context_used = context_used + (
            ContextUsed(
                source=ContextSource.SYSTEM_LIMITATION,
                label="stable_memory",
                value="No runtime memory integration was read by this planning scaffold.",
            ),
        )

    if not text:
        suggested = "Ask the user what task they want planned."
        confidence = 0.0
    elif clarification_needed:
        suggested = "Ask one focused clarification before making a plan."
        confidence = 0.42
    else:
        suggested = "Prepare a planning-only summary and bounded task envelope."
        confidence = 0.78 if has_context or memories else 0.62

    return TaskUnderstanding(
        goal=goal,
        context_used=context_used,
        constraints=tuple(dict.fromkeys(constraints)),
        assumptions=tuple(assumptions),
        confidence=confidence,
        clarification_needed=clarification_needed,
        suggested_next_step=suggested,
    )


def build_task_envelope(*, step_limit: int = 4) -> TaskEnvelope:
    """Return the default planning-only envelope for Simple Task Mode."""

    return TaskEnvelope(
        allowed_actions=(
            "summarize provided task/context",
            "identify missing clarification",
            "draft a bounded plan",
            "create a non-executing task envelope",
        ),
        blocked_actions=(
            "open browser tabs",
            "write or modify files",
            "use OpenClaw",
            "send email",
            "schedule calendar events",
            "perform account actions",
            "publish, trade, purchase, or submit forms",
            "authorize capabilities",
        ),
        environment_scope=("local_conversation", "provided_session_context", "caller_provided_stable_memory"),
        step_limit=step_limit,
        approval_level=ApprovalLevel.USER_REVIEW_ONLY,
        stop_condition="Stop after producing the planning artifact or when required context is missing.",
        failure_behavior="Ask for clarification; do not guess, execute, or escalate to tools.",
    )


def build_simple_task_plan(
    message: str,
    *,
    session_context: dict[str, str] | None = None,
    stable_memory: Iterable[str] | None = None,
    step_limit: int = 4,
) -> SimpleTaskPlan:
    """Build a planning-only Simple Task Mode result."""

    understanding = understand_task(message, session_context=session_context, stable_memory=stable_memory)
    envelope = build_task_envelope(step_limit=step_limit)
    steps = _plan_steps(message, understanding)
    return SimpleTaskPlan(
        mode="simple_task_mode",
        planning_only=True,
        understanding=understanding,
        envelope=envelope,
        plan_steps=steps,
    )


def _context_used(session: dict[str, str], memories: tuple[str, ...]) -> tuple[ContextUsed, ...]:
    used: list[ContextUsed] = []
    for key in sorted(session):
        used.append(ContextUsed(source=ContextSource.SESSION_CONTEXT, label=key, value=session[key]))
    for index, memory in enumerate(memories, start=1):
        used.append(ContextUsed(source=ContextSource.STABLE_MEMORY, label=f"memory_{index}", value=memory))
    return tuple(used)


def _goal_from_message(text: str) -> str:
    if not text:
        return "No task goal provided."
    clean = " ".join(text.split())
    return clean[:180]


def _has_context_key(session: dict[str, str], needle: str) -> bool:
    lowered = needle.lower()
    return any(lowered in key.lower() for key in session)


def _plan_steps(message: str, understanding: TaskUnderstanding) -> tuple[str, ...]:
    text = (message or "").strip()
    if understanding.clarification_needed:
        return ("Ask for the missing source material or target.",)
    if _SCRIPT_PLAN_RE.search(text):
        return (
            "Identify the core beats in the provided script.",
            "Group beats into concise scenes.",
            "Return the scene plan for user review.",
        )
    if _CLARIFICATION_RE.search(text):
        return (
            "List what is known.",
            "List what is missing or ambiguous.",
            "Ask the smallest useful clarification.",
        )
    if _ENVELOPE_RE.search(text):
        return (
            "State the planning-only scope.",
            "List allowed and blocked actions.",
            "Name the stop condition and failure behavior.",
        )
    if _SUMMARY_RE.search(text):
        return (
            "Read only the provided task/context.",
            "Summarize the goal and constraints.",
            "Suggest the next safe planning step.",
        )
    return (
        "Summarize the understood goal.",
        "State constraints and assumptions.",
        "Suggest the next safe planning step.",
    )


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    return value


__all__ = [
    "ApprovalLevel",
    "ContextSource",
    "ContextUsed",
    "SimpleTaskPlan",
    "TaskEnvelope",
    "TaskUnderstanding",
    "build_simple_task_plan",
    "build_task_envelope",
    "understand_task",
]
