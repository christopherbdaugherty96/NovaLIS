from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.conversation.conversation_decision import ConversationDecision
from src.conversation.conversation_router import ConversationRouter
from src.conversation.response_style_router import InputNormalizer


WEB_OPEN_CONFIRM_YES = {
    "yes",
    "open it",
    "proceed",
    "go ahead",
    "yeah",
    "yep",
    "ok",
    "okay",
    "confirm",
    "do it",
    "sure",
}

WEB_OPEN_CONFIRM_NO = {
    "no",
    "cancel",
    "stop",
    "nevermind",
    "never mind",
    "dont",
    "don't",
}


@dataclass(frozen=True)
class RouteContext:
    text: str
    lowered: str
    decision: ConversationDecision
    is_empty: bool = False


@dataclass(frozen=True)
class GateResult:
    handled: bool
    message: str = ""
    apply_override: str = ""
    clear_override: bool = False
    set_clarification_turn: bool = False


@dataclass(frozen=True)
class WebOpenDecision:
    action: str  # confirm | cancel | reprompt | none


class SessionRouter:
    """Session-level routing helpers extracted from brain server orchestration."""

    @staticmethod
    def normalize_and_route(raw_text: str, session_state: dict[str, Any]) -> RouteContext:
        text = InputNormalizer.normalize(raw_text).strip()
        if not text:
            return RouteContext(text="", lowered="", decision=ConversationRouter.route("", session_state), is_empty=True)

        decision = ConversationRouter.route(text, session_state)
        resolved_text = str(decision.resolved_text or text).strip()
        lowered = resolved_text.lower().rstrip(".?!")
        return RouteContext(text=resolved_text, lowered=lowered, decision=decision, is_empty=False)

    @staticmethod
    def evaluate_gate(
        decision: ConversationDecision,
        session_state: dict[str, Any],
        turn_count: int,
    ) -> GateResult:
        if decision.override_applied:
            return GateResult(
                handled=True,
                message=str(decision.override_confirmation or "Okay."),
                apply_override=str(decision.override_mode or ""),
            )

        if decision.override_cleared:
            return GateResult(
                handled=True,
                message=str(decision.override_confirmation or "Okay. Back to default."),
                clear_override=True,
            )

        if decision.blocked_by_policy:
            return GateResult(handled=True, message="I can't help with that request.")

        if decision.needs_clarification:
            if session_state.get("last_clarification_turn") == turn_count:
                return GateResult(handled=True, message="I still need a file or folder name to continue.")
            return GateResult(
                handled=True,
                message=str(decision.clarification_prompt or "Could you clarify that?"),
                set_clarification_turn=True,
            )

        return GateResult(handled=False)

    @staticmethod
    def route_pending_web_confirmation(lowered_text: str) -> WebOpenDecision:
        lowered = (lowered_text or "").strip().lower()
        if not lowered:
            return WebOpenDecision(action="reprompt")
        if lowered in WEB_OPEN_CONFIRM_YES:
            return WebOpenDecision(action="confirm")
        if lowered in WEB_OPEN_CONFIRM_NO:
            return WebOpenDecision(action="cancel")
        return WebOpenDecision(action="reprompt")

    @staticmethod
    def ready_prompt() -> str:
        return CLARIFY_PROMPTS["ready_prompt"]
