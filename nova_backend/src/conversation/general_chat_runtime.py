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
from src.brief.daily_brief import (
    brief_to_action_result,
    compose_daily_brief,
    is_daily_brief_request,
)
from src.memory.memory_skill import MemorySkill
from src.skills.calendar import CalendarSkill
from src.conversation.planning_run_preview import create_planning_run_preview
from src.conversation.request_understanding import build_request_understanding
from src.conversation.request_understanding_formatter import format_request_understanding_block
from src.conversation.session_router import SessionRouter
from src.conversation.task_understanding_preview import build_task_understanding_preview
from src.governor.network_mediator import NetworkMediator
from src.services.weather_service import WeatherService
from src.personality.tone_profile_store import ToneProfileStore
from src.skills.general_chat import GeneralChatSkill
from src.trust.receipt_store import get_recent_receipts
from src.working_context.project_threads import ProjectThreadStore


@dataclass
class PendingEscalationOutcome:
    handled: bool
    message: str = ""
    skill_result: Optional[SkillResult] = None
    context_entries: list[dict[str, str]] = field(default_factory=list)


async def run_daily_brief_if_requested(
    query: str,
    *,
    session_state: dict[str, Any],
    project_threads: ProjectThreadStore,
    select_relevant_memory_context: Callable[..., list[dict[str, Any]]],
    network: Optional[NetworkMediator] = None,
) -> Optional[SkillResult]:
    """
    Return a SkillResult containing a DailyBrief when the query is a brief
    request. Returns None otherwise so the caller falls through to its normal
    routing path.

    Fetches weather (async, falls back on failure) and calendar (local ICS,
    sync). Memory context and recent receipts are read locally. No LLM calls,
    no writes, no capability invocations beyond read-only data access.
    """
    normalized = str(query or "").strip()
    if not normalized or not is_daily_brief_request(normalized):
        return None

    memory_items = select_relevant_memory_context(
        normalized,
        session_state=session_state,
        project_threads=project_threads,
    )
    recent_receipts = get_recent_receipts(limit=10)
    weather_data = await _fetch_weather_for_brief(network)
    calendar_data = _fetch_calendar_for_brief()

    brief = compose_daily_brief(
        session_state=session_state,
        memory_items=memory_items,
        recent_receipts=recent_receipts,
        weather_data=weather_data,
        calendar_data=calendar_data,
    )
    result = brief_to_action_result(brief)

    return SkillResult(
        success=True,
        message=result.speakable_text,
        data=result.structured_data,
        widget_data={"type": "daily_brief", "brief": brief.to_dict()},
        skill="daily_brief",
    )


async def _fetch_weather_for_brief(
    network: Optional[NetworkMediator],
) -> Optional[dict[str, Any]]:
    """Fetch current weather for the brief. Returns None on any failure."""
    try:
        service = WeatherService(network=network)
        data = await service.get_current_weather()
        return dict(data) if isinstance(data, dict) else None
    except Exception:
        return None


def _fetch_calendar_for_brief() -> Optional[dict[str, Any]]:
    """Read today's calendar events from the local ICS file. Returns None if not configured."""
    try:
        skill = CalendarSkill()
        path = skill._calendar_path()
        if path is None:
            return {
                "connected": False,
                "status": "not_connected",
                "events": [],
                "setup_hint": "Add a local .ics file in Settings to enable calendar.",
                "scope": "today",
                "source_label": "",
            }
        from datetime import date
        today = date.today()
        events = skill._read_events_for_range(path, today, today)
        return {
            "connected": True,
            "status": "ok",
            "events": events,
            "setup_hint": "",
            "scope": "today",
            "source_label": path.name,
        }
    except Exception:
        return None


async def run_memory_skill_if_requested(
    query: str,
    *,
    session_state: dict[str, Any],
    ledger=None,
) -> Optional[SkillResult]:
    """
    Intercept explicit memory operations before general-chat fallback.

    Returns a SkillResult when the query is a memory intent
    (remember / review / forget / update / why-used). Returns None otherwise.

    Non-authorizing: no LLM calls, no capability invocations, no external effects.
    """
    normalized = str(query or "").strip()
    if not normalized:
        return None
    skill = MemorySkill(ledger=ledger)
    if not skill.can_handle(normalized):
        return None
    return await skill.handle(normalized, session_state=session_state)


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
    skill_state.pop("_planning_run_manager", None)
    for transient_key in (
        "task_understanding_preview",
        "task_understanding_prompt_block",
        "task_understanding_envelope",
        "planning_run_preview",
    ):
        skill_state.pop(transient_key, None)
    skill_state["relevant_memory_context"] = relevant_memory_context

    understanding = build_request_understanding(normalized_query)
    skill_state["request_understanding"] = understanding
    request_block = format_request_understanding_block(understanding)

    task_preview = build_task_understanding_preview(
        normalized_query,
        session_context=_task_preview_session_context(skill_state, chat_context),
        stable_memory=_task_preview_memory_context(relevant_memory_context),
    )
    skill_state["task_understanding_preview"] = task_preview.plan
    skill_state["task_understanding_prompt_block"] = task_preview.prompt_block
    if task_preview.plan is not None:
        skill_state["task_understanding_envelope"] = task_preview.plan.envelope
        run_preview = create_planning_run_preview(
            task_preview.plan,
            session_state=session_state,
            focused_run_id=str(session_state.get("focused_run_id") or ""),
        )
        if run_preview is not None:
            skill_state["planning_run_preview"] = run_preview.to_dict()
            skill_state["last_interacted_run_id"] = run_preview.last_interacted_run_id
            skill_state["focused_run_id"] = run_preview.focused_run_id

    skill_state["request_understanding_prompt_block"] = "\n\n".join(
        block for block in (request_block, task_preview.prompt_block) if block
    )

    return await general_chat_skill.handle(normalized_query, chat_context, skill_state)


def _task_preview_session_context(
    session_state: dict[str, Any],
    chat_context: list[dict[str, Any]],
) -> dict[str, str]:
    context: dict[str, str] = {}
    conversation_context = dict(session_state.get("conversation_context") or {})
    for key in ("topic", "user_goal", "open_question", "latest_recommendation"):
        value = str(conversation_context.get(key) or "").strip()
        if value:
            context[key] = value

    for entry in reversed(chat_context[-4:]):
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("role") or "").strip().lower()
        content = str(entry.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            context[f"recent_{role}"] = content[:240]
            break
    return context


def _task_preview_memory_context(memory_context: list[dict[str, Any]]) -> tuple[str, ...]:
    memories: list[str] = []
    for entry in memory_context[:3]:
        if not isinstance(entry, dict):
            continue
        text = str(
            entry.get("content")
            or entry.get("text")
            or entry.get("summary")
            or entry.get("value")
            or ""
        ).strip()
        if text:
            memories.append(text[:240])
    return tuple(memories)


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
