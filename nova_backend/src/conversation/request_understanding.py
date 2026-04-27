from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from src.conversation.conversation_decision import ConversationDecision
from src.conversation.conversation_router import ConversationRouter

_AUTHORITY_EFFECT_NONE = "none"


class CapabilityStatus(str, Enum):
    """User-facing ability state for a request.

    This is deliberately non-authorizing. It explains what Nova appears able to
    help with in conversation; it does not grant capability execution.
    """

    CAN_DO_NOW = "can_do_now"
    CAN_DRAFT_ONLY = "can_draft_only"
    CAN_HELP_MANUALLY = "can_help_manually"
    CAN_EXPLAIN = "can_explain"
    CAN_SUMMARIZE_IF_PROVIDED = "can_summarize_if_provided"
    REQUIRES_CONNECTOR = "requires_connector"
    REQUIRES_APPROVAL = "requires_approval"
    PLANNED_NOT_BUILT = "planned_not_built"
    PAUSED = "paused"
    BLOCKED = "blocked"
    NOT_ALLOWED = "not_allowed"
    NEEDS_CLARIFICATION = "needs_clarification"
    UNKNOWN = "unknown"


class UnderstandingConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class RequestUnderstanding:
    """Structured understanding of a user request.

    The contract closes the user-facing loop:

    1. What Nova understood.
    2. What class of request this is.
    3. What Nova can/cannot do now.
    4. What safe next step is available.
    5. What Nova must not do.

    It is intentionally conversation-only. `authority_effect` must remain
    "none" so this object cannot be mistaken for a governor approval.
    """

    understood_goal: str
    request_type: str
    capability_status: CapabilityStatus
    confidence: UnderstandingConfidence
    needs_clarification: bool
    safe_next_step: str
    must_not_do: tuple[str, ...]
    notes: tuple[str, ...] = ()
    authority_effect: str = _AUTHORITY_EFFECT_NONE

    def __post_init__(self) -> None:
        if self.authority_effect != _AUTHORITY_EFFECT_NONE:
            raise ValueError("RequestUnderstanding must remain non-authorizing: authority_effect must be 'none'.")


_DEFAULT_ACTIVE_FOCUS = (
    "Cap 64 P5 live signoff and lock",
    "Windows installer/bootstrap validation",
    "trust/action-history dashboard proof",
)
_DEFAULT_PAUSED = (
    "Auralis / website merger work",
    "Shopify / Cap 65 P5 live work",
)


_EMAIL_RE = re.compile(r"\b(email|e-mail|mail|reply|message)\b", re.IGNORECASE)
_SEND_RE = re.compile(r"\b(send|sent|transmit|deliver)\b", re.IGNORECASE)
_DRAFT_RE = re.compile(r"\b(draft|write|compose|prepare)\b", re.IGNORECASE)
_SHOPIFY_RE = re.compile(r"\b(shopify|cap\s*65)\b", re.IGNORECASE)
_AURALIS_RE = re.compile(r"\b(auralis|website merger|websites?\s+merger|merge\s+website|nova lead console)\b", re.IGNORECASE)
_STATUS_RE = re.compile(r"\b(current status|status|ground me|where are we|what is next|next steps?)\b", re.IGNORECASE)
_CLAUDE_RE = re.compile(r"\b(claude|codex|prompt)\b", re.IGNORECASE)
_MEMORY_RE = re.compile(
    r"\b(save (this|that)?\s*(to )?memory|remember|memory|learn|from now on|do not do that again)\b",
    re.IGNORECASE,
)
_DOC_RE = re.compile(r"\b(add to docs|document this|update docs|commit|repo|github)\b", re.IGNORECASE)
_BACKGROUND_RE = re.compile(r"\b(background|while I'?m away|later|process behind the scenes)\b", re.IGNORECASE)
_REASONING_RE = re.compile(r"\b(reason|think|analy[sz]e|summari[sz]e|review|process)\b", re.IGNORECASE)
_AUTOMATION_RE = re.compile(
    r"\b(send|post|delete|submit|book|purchase|buy|move|rename|change|update customer|run openclaw)\b",
    re.IGNORECASE,
)
_EXPLAIN_RE = re.compile(r"\b(explain|what is|why|how do|how can|what does)\b", re.IGNORECASE)


def build_request_understanding(
    user_text: str,
    decision: ConversationDecision | None = None,
    *,
    active_focus: Iterable[str] | None = None,
    paused_scopes: Iterable[str] | None = None,
) -> RequestUnderstanding:
    """Return a deterministic user-facing understanding contract.

    This function may be called by conversation/UI layers before answering.
    It must not be used as a capability authorization decision.
    """

    text = (user_text or "").strip()
    lowered = text.lower()
    routed = decision or ConversationRouter.route(text)
    active = tuple(active_focus or _DEFAULT_ACTIVE_FOCUS)
    paused = tuple(paused_scopes or _DEFAULT_PAUSED)

    if routed.blocked_by_policy:
        return RequestUnderstanding(
            understood_goal="User requested something that matches a blocked policy pattern.",
            request_type="blocked_request",
            capability_status=CapabilityStatus.NOT_ALLOWED,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=False,
            safe_next_step="Refuse the unsafe request and offer a safe alternative if appropriate.",
            must_not_do=(
                "bypass GovernorMediator",
                "bypass ExecuteBoundary",
                "execute unsafe or policy-blocked instructions",
            ),
            notes=(routed.policy_reason or "policy_blocked_phrase",),
        )

    if routed.needs_clarification:
        return RequestUnderstanding(
            understood_goal="User request is ambiguous or missing a required target.",
            request_type="clarification_needed",
            capability_status=CapabilityStatus.NEEDS_CLARIFICATION,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=True,
            safe_next_step=routed.clarification_prompt or "Ask a focused clarification before continuing.",
            must_not_do=("guess the target", "execute a real action without clarification"),
        )

    if _AURALIS_RE.search(lowered):
        return RequestUnderstanding(
            understood_goal="User is referring to Auralis / website merger work.",
            request_type="paused_work_reference",
            capability_status=CapabilityStatus.PAUSED,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=False,
            safe_next_step=(
                "State that Auralis / website merger work is paused and redirect to "
                "the active Nova runtime stabilization path unless the owner explicitly unpauses it."
            ),
            must_not_do=(
                "delete existing Auralis documents",
                "expand Auralis merger planning",
                "shift active Nova work away from runtime stabilization",
            ),
            notes=("paused_scope: Auralis / website merger work", *paused),
        )

    if _SHOPIFY_RE.search(lowered):
        return RequestUnderstanding(
            understood_goal="User is referring to Shopify / Cap 65 work.",
            request_type="paused_work_reference",
            capability_status=CapabilityStatus.PAUSED,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=False,
            safe_next_step="State that Shopify / Cap 65 P5 live work is paused until the owner explicitly unpauses it and prepares credentials.",
            must_not_do=(
                "run Shopify live P5 tests",
                "request or add Shopify credentials",
                "lock Cap 65",
                "expand Shopify capability scope",
            ),
            notes=("paused_scope: Shopify / Cap 65 P5 live work", *paused),
        )

    if _EMAIL_RE.search(lowered) and (_DRAFT_RE.search(lowered) or _SEND_RE.search(lowered)):
        return RequestUnderstanding(
            understood_goal="User wants help preparing or sending an email/message.",
            request_type="email_draft_boundary",
            capability_status=CapabilityStatus.CAN_DRAFT_ONLY,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=False,
            safe_next_step="Use the Cap 64 pattern: prepare a draft for review; the user sends or explicitly approves the governed draft flow.",
            must_not_do=(
                "send email automatically",
                "transmit without confirmation",
                "claim an email was sent when only a draft was prepared",
            ),
            notes=("Cap 64 pattern: Nova drafts, user sends.",),
        )

    if _BACKGROUND_RE.search(lowered) and _REASONING_RE.search(lowered):
        status = CapabilityStatus.PLANNED_NOT_BUILT
        if _AUTOMATION_RE.search(lowered):
            status = CapabilityStatus.REQUIRES_APPROVAL
        return RequestUnderstanding(
            understood_goal="User wants background reasoning or processing.",
            request_type="background_reasoning_boundary",
            capability_status=status,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=False,
            safe_next_step="Prepare or explain a reasoning-only workflow with visible review cards; do not perform background automation.",
            must_not_do=(
                "send, post, delete, book, buy, or change anything in the background",
                "execute OpenClaw tasks silently",
                "hide provider usage or costs",
            ),
            notes=("Nova may think in the background; Nova must not act in the background.",),
        )

    if _MEMORY_RE.search(lowered) and not _DOC_RE.search(lowered):
        return RequestUnderstanding(
            understood_goal="User wants Nova to remember, learn, or apply a conversational preference/correction.",
            request_type="memory_or_learning_request",
            capability_status=CapabilityStatus.REQUIRES_APPROVAL,
            confidence=UnderstandingConfidence.MEDIUM,
            needs_clarification=False,
            safe_next_step="Treat this as governed learning/memory behavior, not a GitHub documentation update, unless the user explicitly asks for docs or repo changes.",
            must_not_do=(
                "create GitHub files unless docs/repo/commit is explicitly requested",
                "persist sensitive data without explicit user intent",
                "use learning to change action authority",
            ),
            notes=("authority_effect: none",),
        )

    if _DOC_RE.search(lowered):
        return RequestUnderstanding(
            understood_goal="User wants a documentation or repository update/review.",
            request_type="doc_or_repo_update",
            capability_status=CapabilityStatus.CAN_HELP_MANUALLY,
            confidence=UnderstandingConfidence.MEDIUM,
            needs_clarification=False,
            safe_next_step="Review the relevant files, make minimal doc-only changes if requested, and avoid runtime authority changes unless explicitly scoped.",
            must_not_do=(
                "confuse docs updates with memory saves",
                "touch paused Auralis or Shopify work unless explicitly unpaused",
                "change runtime code without clear implementation scope",
            ),
        )

    if _STATUS_RE.search(lowered) or _CLAUDE_RE.search(lowered):
        return RequestUnderstanding(
            understood_goal="User wants current project status, next steps, or a Claude/Codex direction.",
            request_type="project_status_or_next_step",
            capability_status=CapabilityStatus.CAN_EXPLAIN,
            confidence=UnderstandingConfidence.HIGH,
            needs_clarification=False,
            safe_next_step="Answer in current truth / done / blocked-or-paused / highest-ROI next action format.",
            must_not_do=(
                "recommend paused Auralis work",
                "recommend paused Shopify work",
                "overstate future plans as current runtime truth",
            ),
            notes=("active_focus", *active),
        )

    if _EXPLAIN_RE.search(lowered):
        return RequestUnderstanding(
            understood_goal="User wants an explanation or conceptual help.",
            request_type="explanation",
            capability_status=CapabilityStatus.CAN_EXPLAIN,
            confidence=UnderstandingConfidence.MEDIUM,
            needs_clarification=False,
            safe_next_step="Explain plainly, distinguish current truth from future plan, and give one useful next step if relevant.",
            must_not_do=("claim execution happened", "overstate current implementation"),
        )

    return RequestUnderstanding(
        understood_goal="User request appears conversational or general.",
        request_type="general",
        capability_status=CapabilityStatus.CAN_HELP_MANUALLY,
        confidence=UnderstandingConfidence.LOW,
        needs_clarification=False,
        safe_next_step="Answer helpfully, and clarify if the user is asking for a real-world action or repo change.",
        must_not_do=("execute actions without the governed capability path",),
    )


__all__ = [
    "CapabilityStatus",
    "RequestUnderstanding",
    "UnderstandingConfidence",
    "build_request_understanding",
]
