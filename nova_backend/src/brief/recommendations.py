"""Deterministic next-action recommendation selector for the Daily Brief.

Given brief state — open loops, memory items, recent receipts, and session
state — returns up to max_suggestions practical next actions as structured
suggestions.

No LLM calls, no capability invocations, no external effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NextActionSuggestion:
    action: str
    reason: str
    priority: int  # lower = higher priority

    def to_dict(self) -> dict[str, str | int]:
        return {
            "action": self.action,
            "reason": self.reason,
            "priority": self.priority,
        }


def select_next_actions(
    *,
    open_loops: list[str] | None = None,
    memory_items: list[dict[str, Any]] | None = None,
    recent_receipts: list[dict[str, Any]] | None = None,
    session_state: dict[str, Any] | None = None,
    max_suggestions: int = 3,
) -> list[NextActionSuggestion]:
    """
    Return up to max_suggestions practical next-action suggestions.

    Priority rules (applied in order; each fills one slot):
    1. open_loops exist → suggest resolving the most recent one
    2. recent receipt failed → suggest inspecting or retrying it
    3. no session goal → suggest setting today's focus
    4. no memory → suggest saving a project preference

    Returns an empty list when all slots are already filled by higher-priority
    rules or when all rules produce no suggestion.
    """
    _loops = [str(s).strip() for s in (open_loops or []) if str(s).strip()]
    _receipts = [r for r in (recent_receipts or []) if isinstance(r, dict)]
    _memory = [m for m in (memory_items or []) if isinstance(m, dict)]
    _state = _as_dict(session_state)
    suggestions: list[NextActionSuggestion] = []

    # Rule 1: open loops → resolve most recent
    if _loops and len(suggestions) < max_suggestions:
        most_recent = _loops[0][:120]
        suggestions.append(NextActionSuggestion(
            action=f"Resolve: {most_recent}",
            reason="An open question from your session is unresolved.",
            priority=1,
        ))

    # Rule 2: failed receipts → inspect or retry
    if len(suggestions) < max_suggestions:
        failed = [
            r for r in _receipts
            if str(r.get("event_type") or "").endswith("_FAILED")
            or str(r.get("outcome") or "") in {"failed", "error", "blocked"}
        ]
        if failed:
            label = str(
                failed[0].get("capability_name")
                or failed[0].get("event_type")
                or "action"
            )[:80]
            suggestions.append(NextActionSuggestion(
                action=f"Inspect failed action: {label}",
                reason="A recent action did not complete successfully.",
                priority=2,
            ))

    # Rule 3: weak search evidence → refine or compare sources
    if len(suggestions) < max_suggestions:
        search_evidence = _search_evidence_from_state(_state)
        evidence_status = str(search_evidence.get("evidence_status") or "").strip()
        confidence = str(search_evidence.get("confidence") or "").strip()
        if evidence_status in {"weak_or_no_evidence", "snippet_backed"} or confidence == "low":
            suggestions.append(NextActionSuggestion(
                action="Refine search evidence: narrow the query or compare more sources.",
                reason="Recent search evidence was weak, partial, or snippet-backed.",
                priority=3,
            ))

    # Rule 4: no session goal → suggest setting focus
    if len(suggestions) < max_suggestions:
        conv_ctx = _as_dict(_state.get("conversation_context"))
        user_goal = str(conv_ctx.get("user_goal") or conv_ctx.get("topic") or "").strip()
        session_goal = str(_state.get("task_goal") or _state.get("active_topic") or "").strip()
        if not user_goal and not session_goal:
            suggestions.append(NextActionSuggestion(
                action="Set today's focus: tell Nova your main goal for this session.",
                reason="No session goal or topic is active.",
                priority=4,
            ))

    # Rule 5: no memory → suggest saving a preference
    if len(suggestions) < max_suggestions and not _memory:
        suggestions.append(NextActionSuggestion(
            action="Save a useful preference: tell Nova something about how you like to work.",
            reason="No saved memory context was found to personalize the brief.",
            priority=5,
        ))

    return suggestions[:max_suggestions]


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _search_evidence_from_state(session_state: dict[str, Any]) -> dict[str, Any]:
    for key in ("search_evidence", "last_search_evidence"):
        evidence = session_state.get(key)
        if isinstance(evidence, dict):
            return evidence

    widget = _as_dict(session_state.get("search_widget"))
    data = _as_dict(widget.get("data"))
    evidence = data.get("evidence")
    return evidence if isinstance(evidence, dict) else {}
