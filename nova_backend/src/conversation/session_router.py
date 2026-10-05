from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.brain.task_clarifier import clarify_task
from src.brief.daily_loop import DailyLoopProjection, render_daily_loop_answer
from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.conversation.conversation_decision import ConversationDecision
from src.conversation.conversation_router import ConversationRouter
from src.conversation.personal_operations_intent import unavailable_personal_operations_response
from src.conversation.response_style_router import InputNormalizer
from src.personality.nova_style_contract import NovaStyleContract

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
    "do that",
    "sure",
}

WEB_OPEN_CONFIRM_NO = {
    "no",
    "no thanks",
    "nope",
    "nah",
    "cancel",
    "abort",
    "stop",
    "wait",
    "hold on",
    "hang on",
    "never",
    "nevermind",
    "never mind",
    "dont",
    "don't",
}

_CONFIRMATION_NEGATION_RE = re.compile(
    r"\b(?:no|not|nope|nah|cancel|abort|stop|wait|hold\s+on|hang\s+on|never|"
    r"nevermind|never\s+mind|dont|don't|do\s+not|cannot|can't|wont|won't)\b"
)
_CONFIRMATION_YES_RE = re.compile(
    r"^(?:yes|yeah|yep|ok|okay|sure|confirm|proceed|go\s+ahead|"
    r"open\s+it|do\s+it|do\s+that)\b"
)


@dataclass(frozen=True)
class RouteContext:
    raw_text: str
    text: str
    lowered: str
    decision: ConversationDecision
    normalization_changed: bool = False
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
    def _canonical_text(value: str) -> str:
        clean = (value or "").strip().lower()
        clean = clean.rstrip(".?!")
        return " ".join(clean.split())

    @staticmethod
    def normalize_and_route(raw_text: str, session_state: dict[str, Any]) -> RouteContext:
        raw = (raw_text or "").strip()
        text = InputNormalizer.normalize(raw).strip()
        normalization_changed = SessionRouter._canonical_text(raw) != SessionRouter._canonical_text(text)
        if not text:
            return RouteContext(
                raw_text=raw,
                text="",
                lowered="",
                decision=ConversationRouter.route("", session_state),
                normalization_changed=normalization_changed,
                is_empty=True,
            )

        decision = ConversationRouter.route(text, session_state)
        resolved_text = str(decision.resolved_text or text).strip()
        lowered = resolved_text.lower().rstrip(".?!")
        return RouteContext(
            raw_text=raw,
            text=resolved_text,
            lowered=lowered,
            decision=decision,
            normalization_changed=normalization_changed,
            is_empty=False,
        )

    @staticmethod
    def evaluate_gate(
        decision: ConversationDecision,
        session_state: dict[str, Any],
        turn_count: int,
        daily_loop_projection: DailyLoopProjection | None = None,
    ) -> GateResult:
        if decision.personal_operations_intent is not None:
            if daily_loop_projection is not None:
                return GateResult(
                    handled=True,
                    message=render_daily_loop_answer(
                        decision.personal_operations_intent,
                        daily_loop_projection,
                    ),
                )
            return GateResult(
                handled=True,
                message=unavailable_personal_operations_response(decision.personal_operations_intent),
            )

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
                return GateResult(
                    handled=True,
                    message=SessionRouter._spoken_gate_message("I still need a file or folder name to continue."),
                )
            return GateResult(
                handled=True,
                message=SessionRouter._spoken_gate_message(str(decision.clarification_prompt or "Could you clarify that?")),
                set_clarification_turn=True,
            )

        return GateResult(handled=False)

    @staticmethod
    def evaluate_brain_task_clarifier(text: str) -> GateResult:
        clarification = clarify_task(text)
        if not clarification.matched:
            return GateResult(handled=False)
        return GateResult(handled=True, message=clarification.response)

    @staticmethod
    def route_pending_web_confirmation(
        lowered_text: str,
        *,
        whole_reply_only: bool = False,
    ) -> WebOpenDecision:
        text = str(lowered_text or "").lower().translate(str.maketrans({"’": "'", "‘": "'"}))
        normalized = re.sub(r"[^\w\s']", " ", text)
        normalized = " ".join(normalized.split())
        if not normalized:
            return WebOpenDecision(action="reprompt")

        has_yes = _CONFIRMATION_YES_RE.search(normalized) is not None
        has_no = _CONFIRMATION_NEGATION_RE.search(normalized) is not None
        if has_yes and has_no:
            return WebOpenDecision(action="reprompt")
        if has_no:
            if normalized in WEB_OPEN_CONFIRM_NO:
                return WebOpenDecision(action="cancel")
            if whole_reply_only:
                return WebOpenDecision(action="none")
            if len(normalized.split()) <= 4:
                return WebOpenDecision(action="cancel")
            return WebOpenDecision(action="none")
        if whole_reply_only:
            if normalized in WEB_OPEN_CONFIRM_YES:
                return WebOpenDecision(action="confirm")
            return WebOpenDecision(action="none")
        if has_yes and len(normalized.split()) <= 4:
            return WebOpenDecision(action="confirm")
        if has_yes:
            return WebOpenDecision(action="reprompt")
        return WebOpenDecision(action="none")

    @staticmethod
    def ready_prompt() -> str:
        return CLARIFY_PROMPTS["ready_prompt"]

    @staticmethod
    def _spoken_gate_message(message: str) -> str:
        clean = str(message or "").strip()
        if not clean:
            return NovaStyleContract.spoken_repeat_prompt()

        lowered = clean.lower()
        if lowered.startswith("which file or folder do you mean"):
            return NovaStyleContract.prefix_with_acknowledgement(clean, kind="understood")
        if lowered.startswith("what should i continue from"):
            return NovaStyleContract.prefix_with_acknowledgement(clean, kind="understood")
        if lowered.startswith("i still need a file or folder name"):
            return NovaStyleContract.prefix_with_acknowledgement(clean, kind="understood")
        if lowered.startswith("i might have misheard that"):
            parts = clean.split(".", 1)
            remainder = parts[1].strip() if len(parts) > 1 else ""
            if remainder:
                return f"{NovaStyleContract.spoken_repeat_prompt()} {remainder}".strip()
            return NovaStyleContract.spoken_repeat_prompt()
        if lowered.startswith("could you clarify that"):
            return NovaStyleContract.spoken_repeat_prompt()
        return clean
