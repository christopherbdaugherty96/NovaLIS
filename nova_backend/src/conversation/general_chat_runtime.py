"""
Helpers for keeping general-chat fallback behavior out of the websocket monolith.

These helpers preserve Nova's bounded advisory fallback after governed routing
finds no explicit capability match, while reducing the live runtime's
dependency on the broader Phase 3.5 skill stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from src.base_skill import SkillResult
from src.conversation.session_router import SessionRouter
from src.governor.network_mediator import NetworkMediator
from src.personality.tone_profile_store import ToneProfileStore
from src.skills.general_chat import GeneralChatSkill
from src.working_context.project_threads import ProjectThreadStore


@dataclass
class PendingEscalationOutcome:
    handled: bool
    message: str = ""
    skill_result: Optional[SkillResult] = None
    context_entries: list[dict[str, str]] = field(default_factory=list)


def build_general_chat_skill(
    *,
    network: NetworkMediator | None = None,
    tone_store: ToneProfileStore | None = None,
) -> GeneralChatSkill:
    return GeneralChatSkill(network=network, tone_store=tone_store)


async def run_general_chat_fallback(
    query: str,
    *,
    general_chat_skill: GeneralChatSkill,
    session_state: dict[str, Any],
    session_context: list[dict[str, Any]],
    project_threads: ProjectThreadStore,
    select_relevant_memory_context: Callable[..., list[dict[str, Any]]],
) -> Optional[SkillResult]:
    normalized_query = str(query or "").strip()
    if not normalized_query or not general_chat_skill.can_handle(normalized_query):
        return None

    relevant_memory_context = select_relevant_memory_context(
        normalized_query,
        session_state=session_state,
        project_threads=project_threads,
    )
    session_state["last_memory_context"] = relevant_memory_context

    chat_context = list(session_state.get("general_chat_context") or session_context)
    skill_state = dict(session_state)
    skill_state["relevant_memory_context"] = relevant_memory_context
    return await general_chat_skill.handle(normalized_query, chat_context, skill_state)


async def resolve_pending_escalation_reply(
    reply_text: str,
    *,
    session_state: dict[str, Any],
    general_chat_skill: GeneralChatSkill,
) -> PendingEscalationOutcome:
    pending = session_state.get("pending_escalation")
    if not pending:
        return PendingEscalationOutcome(handled=False)

    decision = SessionRouter.route_pending_web_confirmation(str(reply_text or ""))

    if decision.action == "confirm":
        original_query, context_snapshot, _heuristic_result = pending
        forced_state = dict(session_state)
        forced_state["escalation_count"] = 0
        forced_state["last_escalation_turn"] = None
        forced_state["turn_count"] = 999
        forced_state["deep_mode_disabled"] = False
        forced_state["deep_mode_armed"] = True

        forced_result = await general_chat_skill.handle(
            original_query,
            context_snapshot,
            forced_state,
        )

        session_state["pending_escalation"] = None
        session_state["deep_mode_armed"] = False

        if forced_result is None:
            return PendingEscalationOutcome(
                handled=True,
                message="Deep analysis is unavailable right now, so I kept the brief version.",
            )

        session_state["last_response"] = forced_result.message
        conversation_context = (forced_result.data or {}).get("conversation_context")
        if isinstance(conversation_context, dict):
            session_state["conversation_context"] = dict(conversation_context)

        escalation = (forced_result.data or {}).get("escalation", {})
        if escalation.get("escalated") and escalation.get("thought_data"):
            session_state["escalation_count"] = int(session_state.get("escalation_count") or 0) + 1
            session_state["last_escalation_turn"] = session_state.get("turn_count")

        return PendingEscalationOutcome(
            handled=True,
            skill_result=forced_result,
            context_entries=[
                {"role": "user", "content": original_query},
                {"role": "assistant", "content": forced_result.message},
            ],
        )

    if decision.action == "cancel":
        session_state["pending_escalation"] = None
        session_state["deep_mode_armed"] = False
        return PendingEscalationOutcome(
            handled=True,
            message="Okay, keeping it brief.",
        )

    return PendingEscalationOutcome(
        handled=True,
        message="Please answer 'yes', 'no', or 'cancel'.",
    )
