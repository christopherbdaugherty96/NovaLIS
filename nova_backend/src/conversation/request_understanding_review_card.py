"""Request Understanding review-card payload contract.

This module adapts existing public planning-preview/session state into a
read-only review artifact. It does not execute, authorize, call capabilities,
call the Governor, query OpenClaw, read/write files, or create persistence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from src.brain.brain_mode import BrainMode
from src.brain.task_understanding import SimpleTaskPlan
from src.conversation.planning_run_preview import PlanningRunPreview
from src.conversation.request_understanding import RequestUnderstanding


_AUTHORITY_EFFECT_NONE = "none"
_HISTORY_NOT_AVAILABLE = "not_available"


@dataclass(frozen=True)
class RequestUnderstandingReviewCard:
    request_text: str
    request_type: str
    detected_mode: str
    goal: str
    context_used: tuple[dict[str, Any], ...] = ()
    constraints: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    confidence: float = 0.0
    clarification_needed: bool = False
    suggested_next_step: str = ""
    allowed_planning_actions: tuple[str, ...] = ()
    blocked_execution_actions: tuple[str, ...] = ()
    relevant_receipts: tuple[dict[str, Any], ...] = ()
    relevant_action_history: tuple[dict[str, Any], ...] = ()
    history_status: str = _HISTORY_NOT_AVAILABLE
    authority_effect: str = _AUTHORITY_EFFECT_NONE
    execution_performed: bool = False
    authorization_granted: bool = False
    private_reasoning_exposed: bool = False

    def __post_init__(self) -> None:
        if self.authority_effect != _AUTHORITY_EFFECT_NONE:
            raise ValueError("RequestUnderstandingReviewCard must remain non-authorizing.")
        if self.execution_performed:
            raise ValueError("RequestUnderstandingReviewCard must not record execution.")
        if self.authorization_granted:
            raise ValueError("RequestUnderstandingReviewCard must not grant authorization.")
        if self.private_reasoning_exposed:
            raise ValueError("RequestUnderstandingReviewCard must not expose private reasoning.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


def build_request_understanding_review_card(
    *,
    request_text: str,
    request_understanding: RequestUnderstanding,
    task_understanding_preview: SimpleTaskPlan | None,
    planning_run_preview: PlanningRunPreview | dict[str, Any] | None = None,
    detected_mode: BrainMode | str | None = None,
    relevant_receipts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    relevant_action_history: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    history_status: str = _HISTORY_NOT_AVAILABLE,
) -> RequestUnderstandingReviewCard | None:
    """Return a review-card payload when a planning preview exists.

    The card is built only from caller-provided state. Empty receipt/history
    inputs are represented explicitly as unavailable rather than inventing a new
    history layer.
    """

    if task_understanding_preview is None:
        return None

    understanding = task_understanding_preview.understanding
    envelope = task_understanding_preview.envelope
    receipts = tuple(_copy_public_mapping(item) for item in (relevant_receipts or ()))
    action_history = tuple(_copy_public_mapping(item) for item in (relevant_action_history or ()))
    safe_history_status = str(history_status or _HISTORY_NOT_AVAILABLE).strip() or _HISTORY_NOT_AVAILABLE
    if not receipts and not action_history:
        safe_history_status = _HISTORY_NOT_AVAILABLE

    return RequestUnderstandingReviewCard(
        request_text=str(request_text or "").strip(),
        request_type=str(request_understanding.request_type or ""),
        detected_mode=_mode_value(detected_mode),
        goal=understanding.goal,
        context_used=tuple(_to_primitive(item) for item in understanding.context_used),
        constraints=tuple(understanding.constraints),
        assumptions=tuple(understanding.assumptions),
        confidence=float(understanding.confidence),
        clarification_needed=bool(understanding.clarification_needed),
        suggested_next_step=understanding.suggested_next_step,
        allowed_planning_actions=tuple(envelope.allowed_actions),
        blocked_execution_actions=tuple(envelope.blocked_actions),
        relevant_receipts=receipts,
        relevant_action_history=action_history,
        history_status=safe_history_status,
        authority_effect=_AUTHORITY_EFFECT_NONE,
        execution_performed=False,
        authorization_granted=False,
        private_reasoning_exposed=False,
    )


def _mode_value(mode: BrainMode | str | None) -> str:
    if isinstance(mode, BrainMode):
        return mode.value
    return str(mode or "").strip()


def _copy_public_mapping(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _to_primitive(item) for key, item in value.items()}


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
    "RequestUnderstandingReviewCard",
    "build_request_understanding_review_card",
]
