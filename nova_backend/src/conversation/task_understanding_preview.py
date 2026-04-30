"""Conversation-facing Task Understanding preview helpers.

These helpers expose the Brain planning scaffold to conversation code without
turning it into a route, approval, or execution path.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from src.brain.task_understanding import SimpleTaskPlan, build_simple_task_plan


_TASK_LIKE_RE = re.compile(
    r"\b("
    r"task|plan|planning|scene plan|summari[sz]e|summary|clarif(?:y|ication)|"
    r"bounded|envelope|assumptions?|constraints?|next step|steps?|run scaffold|"
    r"turn this|convert this|make this"
    r")\b",
    re.IGNORECASE,
)
_CASUAL_RE = re.compile(
    r"^\s*(?:hi|hello|hey|thanks|thank you|that sounds good|ok|okay|yes|no|sure)\s*[.!?]*\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TaskUnderstandingPreview:
    enabled: bool
    plan: SimpleTaskPlan | None = None
    prompt_block: str = ""

    @property
    def authority_effect(self) -> str:
        return "none"


def build_task_understanding_preview(
    message: str,
    *,
    session_context: dict[str, str] | None = None,
    stable_memory: Iterable[str] | None = None,
    include_envelope: bool = True,
) -> TaskUnderstandingPreview:
    """Return a planning-only preview for task-like requests.

    Casual/general chat returns a disabled preview. Enabled previews are still
    non-authorizing and do not execute anything.
    """

    text = (message or "").strip()
    if not _looks_task_like(text):
        return TaskUnderstandingPreview(enabled=False)

    plan = build_simple_task_plan(
        text,
        session_context=session_context,
        stable_memory=stable_memory,
    )
    return TaskUnderstandingPreview(
        enabled=True,
        plan=plan,
        prompt_block=format_task_understanding_preview(plan, include_envelope=include_envelope),
    )


def format_task_understanding_preview(plan: SimpleTaskPlan, *, include_envelope: bool = True) -> str:
    """Format a compact preview block for prompt/UI use."""

    understanding = plan.understanding
    lines = [
        "Task understanding preview (planning-only, non-authorizing):",
        f"Goal: {understanding.goal}",
        f"Context used: {_context_summary(understanding)}",
        f"Constraints: {'; '.join(understanding.constraints) or 'none'}",
        f"Assumptions: {'; '.join(understanding.assumptions) or 'none'}",
        f"Confidence: {understanding.confidence:.2f}",
        f"Clarification needed: {str(understanding.clarification_needed).lower()}",
        f"Suggested next step: {understanding.suggested_next_step}",
        "Authority effect: none. No tools, capabilities, Governor calls, OpenClaw, browser tabs, file writes, email, scheduling, or account actions.",
    ]
    if include_envelope:
        envelope = plan.envelope
        lines.extend(
            [
                "Task envelope:",
                f"Allowed actions: {'; '.join(envelope.allowed_actions)}",
                f"Blocked actions: {'; '.join(envelope.blocked_actions)}",
                f"Environment scope: {'; '.join(envelope.environment_scope)}",
                f"Step limit: {envelope.step_limit}",
                f"Approval level: {envelope.approval_level.value}",
                f"Stop condition: {envelope.stop_condition}",
                f"Failure behavior: {envelope.failure_behavior}",
            ]
        )
    return "\n".join(lines)


def _looks_task_like(text: str) -> bool:
    if not text or _CASUAL_RE.match(text):
        return False
    return bool(_TASK_LIKE_RE.search(text))


def _context_summary(plan_understanding) -> str:
    context_items = list(plan_understanding.context_used or ())
    if not context_items:
        return "none"
    return "; ".join(f"{item.source.value}:{item.label}" for item in context_items)


__all__ = [
    "TaskUnderstandingPreview",
    "build_task_understanding_preview",
    "format_task_understanding_preview",
]
