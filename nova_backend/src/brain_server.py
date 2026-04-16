# src/brain_server.py

"""
NovaLIS Brain Server - Phase 4 Staging
- Session-aware mediator
- Dataclass-based invocation handling
- Governor mediation
- Bounded general-chat fallback isolated
"""

from src.governor.governor import Governor
from src.memory.quick_corrections import record_correction
from src.routers.stt import router as stt_router

import json
import logging
import re
import sys
import uuid
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.audit_api import build_audit_router
from src.api.bridge_api import build_bridge_router
from src.api.connections_api import build_connections_router
from src.api.live_screen_api import build_live_screen_router
from src.api.memory_api import build_memory_router
from src.api.openclaw_agent_api import build_openclaw_agent_router
from src.api.profile_api import build_profile_router
from src.api.settings_api import build_settings_router
from src.api.workspace_api import build_workspace_router
from src.connections.connections_store import connections_store
from src.conversation.general_chat_runtime import (
    build_general_chat_skill,
    resolve_pending_escalation_reply,
    run_general_chat_fallback,
)
from src.governor.governor_mediator import GovernorMediator, Invocation, Clarification
from src.utils.web_target_planner import plan_web_open
from src.speech_state import speech_state
from src.conversation.thought_store import ThoughtStore
from src.conversation.complexity_heuristics import ComplexityHeuristics
from src.conversation.session_router import SessionRouter
from src.voice.stt_pipeline import STTAckConfig
from src.voice.tts_engine import (
    inspect_voice_runtime,
    nova_speak,
    resolve_speakable_text,
    stop_speaking,
)
from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.conversation.review_followthrough import (
    build_review_followthrough_snapshot,
    build_revised_answer_from_review,
    render_original_answer,
    summarize_review_gaps,
)
from src.conversation.response_formatter import ResponseFormatter
from src.build_phase import BUILD_PHASE, PHASE_4_2_ENABLED
from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor
from src.trust.failure_ladder import FailureLadder
from src.trust.trust_contract import normalize_trust_status
from src.patterns.pattern_review_store import PatternReviewStore
from src.policies.atomic_policy_store import AtomicPolicyStore
from src.working_context.context_store import WorkingContextStore
from src.working_context.project_threads import ProjectThreadStore
from src.working_context.operational_remembrance import (
    build_operational_context_widget,
    render_operational_context_message,
)
from src.working_context.assistive_noticing import (
    apply_assistive_notice_feedback,
    build_assistive_notices_widget,
    record_auto_surfaced_notices,
    render_assistive_notices_message,
)
from src.tasks.notification_schedule_store import NotificationScheduleStore
from src.openclaw.agent_runner import openclaw_agent_runner
from src.openclaw.agent_runtime_store import openclaw_agent_runtime_store
from src.openclaw.agent_scheduler import openclaw_agent_scheduler
from src.utils.local_request_guard import describe_http_rebinding_violation
from src.personality.conversation_personality_agent import ConversationPersonalityAgent
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.nova_style_contract import NovaStyleContract
from src.personality.tone_profile_store import ToneProfileStore
from src.voice.voice_agent import VoiceExperienceAgent
from src.settings.runtime_settings_store import runtime_settings_store
from src.audit.runtime_auditor import (
    run_runtime_truth_audit,
    render_runtime_truth_markdown,
    write_current_runtime_state_snapshot,
)
from src.websocket.session_handler import run_websocket_session
from src.websocket.intent_patterns import (
    PHASE42_QUERY_RE, PHASE42_HELP_COMMANDS, CAPABILITY_HELP_RE, TIME_QUERY_RE,
    LOCAL_PROJECT_CURRENT_RE, LOCAL_PROJECT_TARGET_RE, LOCAL_PROJECT_DISK_RE,
    CODEBASE_SUMMARY_CURRENT_RE, CODEBASE_SUMMARY_TARGET_RE, CODEBASE_SUMMARY_TARGET_ONLY_RE,
    CODEBASE_DO_RE, CODEBASE_CAPABILITY_RE, LOCAL_ARCHITECTURE_REPORT_RE,
    TRUST_CENTER_RE, VOICE_CHECK_RE, VOICE_STATUS_RE, BRIDGE_STATUS_RE, CONNECTION_STATUS_RE,
    OPEN_LOCAL_PROJECT_CURRENT_RE, OPEN_LOCAL_PROJECT_TARGET_RE, LOCAL_LOCATION_HINT_RE,
    CREATE_THREAD_RE, CONTINUE_THREAD_RE, SHOW_THREADS_RE, ATTACH_THREAD_RE, ATTACH_ACTIVE_THREAD_RE,
    EXPLICIT_MEMORY_SAVE_RE, DECISION_THREAD_RE, PROJECT_STATUS_RE, BIGGEST_BLOCKER_RE,
    THREAD_DETAIL_RE, WORKSPACE_HOME_RE, WORKSPACE_BOARD_RE,
    OPERATIONAL_CONTEXT_RE, ASSISTIVE_NOTICES_RE, DISMISS_ASSISTIVE_NOTICE_RE,
    RESOLVE_ASSISTIVE_NOTICE_RE, RESET_OPERATIONAL_CONTEXT_RE, MOST_BLOCKED_PROJECT_RE,
    WHY_RECOMMENDATION_RE, TONE_STATUS_COMMANDS, TONE_SET_RE, TONE_RESET_RE,
    SHOW_SCHEDULES_COMMANDS, NOTIFICATION_SETTINGS_COMMANDS,
    SCHEDULE_BRIEF_RE, REMIND_ME_RE, CANCEL_SCHEDULE_RE, DISMISS_SCHEDULE_RE,
    RESCHEDULE_SCHEDULE_RE, SET_QUIET_HOURS_RE, CLEAR_QUIET_HOURS_RE, SET_NOTIFICATION_RATE_LIMIT_RE,
    PATTERN_STATUS_COMMANDS, PATTERN_OPT_IN_RE, PATTERN_OPT_OUT_RE, PATTERN_REVIEW_RE,
    ACCEPT_PATTERN_RE, DISMISS_PATTERN_RE, POLICY_STATUS_COMMANDS, POLICY_CAPABILITY_MAP_COMMANDS,
    POLICY_CREATE_RE, POLICY_SHOW_RE, POLICY_DELETE_RE, POLICY_SIMULATE_RE, POLICY_RUN_ONCE_RE,
    HARD_ACTION_PREFIXES, TOPIC_NOISE_TERMS, _is_hard_action_command, _extract_topic_candidate,
    _build_phase42_agents, _extract_phase42_query,
)
from src.utils.path_resolver import (
    PROJECT_SURFACE_HINTS, BACKEND_MODULE_HINTS,
    _normalize_lookup_key, _resolve_existing_local_path, _split_local_location_hint,
    _candidate_local_project_paths, _resolve_local_project_path, _local_project_markers,
    _read_small_text_file, _extract_markdown_paragraph, _extract_markdown_bullets_after_line,
    _capability_registry_snapshot, _major_project_surfaces, _major_backend_modules,
    _render_local_codebase_summary, _render_local_project_summary, _render_local_architecture_report,
    _project_tree_node, _append_project_tree_lines, _project_graph_id, _append_project_graph_data,
    _project_relationship_edges, _build_local_project_structure_map_widget,
    _render_local_project_structure_map,
)

if PHASE_4_2_ENABLED:
    from src.personality.core import PersonalityAgent as _Phase42PersonalityAgent
else:
    _Phase42PersonalityAgent = None

# -------------------------------------------------
# App + Logging
# -------------------------------------------------
log = logging.getLogger("nova")


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    try:
        output_path = write_current_runtime_state_snapshot()
        log.info("Runtime snapshot refreshed at startup: %s", output_path)
    except Exception:
        log.exception("Failed to refresh runtime snapshot on startup")
    openclaw_agent_scheduler._ledger_logger = (
        lambda event_type, metadata: _log_ledger_event(RUNTIME_GOVERNOR, event_type, metadata)
    )
    scheduler_allowed = runtime_settings_store.is_permission_enabled(
        "home_agent_enabled"
    ) and runtime_settings_store.is_permission_enabled("home_agent_scheduler_enabled")
    if scheduler_allowed:
        await openclaw_agent_scheduler.start()
    try:
        yield
    finally:
        await openclaw_agent_scheduler.stop()


app = FastAPI(lifespan=_lifespan)


@app.middleware("http")
async def _enforce_local_http_boundary(request: Request, call_next):
    violation = describe_http_rebinding_violation(request)
    if violation:
        return JSONResponse(status_code=403, content={"detail": violation})
    return await call_next(request)

# Phase-build lock marker for runtime auditor and governance checks.
# Phase 4 keeps 4.2 modules runtime-locked unless a build promotes phase.
_ = (BUILD_PHASE, PHASE_4_2_ENABLED)

# -------------------------------------------------
# Static Files
# -------------------------------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]   # nova_backend/
STATIC_DIR = BASE_DIR / "static"
INDEX_HTML = STATIC_DIR / "index.html"
LANDING_HTML = STATIC_DIR / "landing.html"

LANDING_DIR = STATIC_DIR / "landing"

if LANDING_DIR.exists():
    # Task 1.5: serve the waitlist landing page at /landing (must mount
    # before /static so the more-specific prefix wins).
    app.mount("/landing", StaticFiles(directory=LANDING_DIR, html=True), name="landing")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(stt_router)
app.include_router(build_live_screen_router())
app.include_router(build_workspace_router(sys.modules[__name__]))

# -------------------------------------------------
# Phase 4 Staging Components
# -------------------------------------------------
thought_store = ThoughtStore(ttl=300)
conversation_heuristics = ComplexityHeuristics()
response_formatter = ResponseFormatter()
failure_ladder = FailureLadder()
interface_personality_agent = PersonalityInterfaceAgent()
conversation_personality_agent = ConversationPersonalityAgent(interface_agent=interface_personality_agent)
voice_experience_agent = VoiceExperienceAgent()
RUNTIME_GOVERNOR = Governor()

# -------------------------------------------------
# Security Constants
# -------------------------------------------------
WS_INPUT_MAX_BYTES = 4096
CONVERSATIONAL_INITIATIVE_ENABLED = True
VOICE_ACK_ENABLED = True
VOICE_ACK_TEXT = "Got it."
VOICE_ACK_CONFIG = STTAckConfig(enabled=VOICE_ACK_ENABLED, text=VOICE_ACK_TEXT)
def _extract_sources_from_results(results: list[dict]) -> list[str]:
    sources: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        domain = url.split("//")[-1].split("/")[0].strip().lower()
        if domain and domain not in sources:
            sources.append(domain)
    return sources[:5]


def _extract_source_links(results: list[dict]) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in results:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        source = str(item.get("source") or "").strip()
        if not source:
            source = url.split("//")[-1].split("/")[0].strip().lower()
        title = str(item.get("title") or "").strip()
        links.append({"url": url, "source": source, "title": title})
    return links[:10]


def _structure_long_message(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return raw
    if "\n" in raw or len(raw) < 360:
        return raw

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]
    if len(sentences) <= 3:
        return raw

    summary = sentences[0]
    points = sentences[1:4]
    lines = ["Summary", summary, "", "Key Points"]
    lines.extend(f"- {pt}" for pt in points)
    return "\n".join(lines)


def _make_shorter_followup(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    compact = re.sub(r"\s+", " ", raw).strip()
    if len(compact) <= 220:
        return compact
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", compact) if s.strip()]
    if sentences:
        short = " ".join(sentences[:2]).strip()
        if len(short) > 240:
            short = short[:237].rstrip() + "..."
        return short
    return compact[:217].rstrip() + "..."


def _strip_action_suggestions_from_response(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    marker = re.search(r"\nTry next:\s*$", raw, flags=re.IGNORECASE | re.MULTILINE)
    if marker:
        raw = raw[: marker.start()].rstrip()
    return raw.strip()


def _build_second_opinion_review_text(session_context: list[dict] | None, session_state: dict) -> str:
    recent = list(session_context or [])[-6:]
    snippets: list[str] = []
    for item in recent:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        content = _make_shorter_followup(str(item.get("content") or ""))
        if not content:
            continue
        if role == "user":
            snippets.append(f"User: {content}")
        elif role == "assistant":
            snippets.append(f"Nova: {content}")

    last_response = _strip_action_suggestions_from_response(str(session_state.get("last_response") or ""))
    if last_response:
        snippets.append(f"Current Nova answer: {_make_shorter_followup(last_response)}")

    if not snippets:
        return ""
    return "Recent exchange for second opinion review:\n" + "\n".join(snippets)


def _derive_memory_title(body: str) -> str:
    compact = _make_shorter_followup(_strip_action_suggestions_from_response(body))
    if not compact:
        return "Saved memory"
    if len(compact) <= 72:
        return compact
    return compact[:69].rstrip() + "..."


def _prepare_explicit_memory_save_params(
    *,
    command_text: str,
    session_state: dict,
    project_threads: ProjectThreadStore,
    session_id: str,
) -> tuple[bool, dict, str]:
    match = EXPLICIT_MEMORY_SAVE_RE.match(command_text)
    if not match:
        return False, {}, ""

    explicit_body = str(match.group("body") or "").strip()
    prior_response = _strip_action_suggestions_from_response(str(session_state.get("last_response") or ""))
    memory_body = explicit_body or prior_response
    if not memory_body:
        return (
            True,
            {},
            "I can save something explicitly, but I need the content first. Say 'save this: <text>' or ask me to save a specific answer.",
        )

    active_thread = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
    active_thread_key = project_threads.active_thread_key() if active_thread else ""
    tags = ["explicit_user_save"]
    scope = "nova_core"
    if active_thread:
        scope = "project"
        tags.extend(["project_thread", active_thread_key or active_thread.lower()])

    params = {
        "action": "save",
        "title": _derive_memory_title(memory_body),
        "body": memory_body,
        "scope": scope,
        "source": "explicit_user_save",
        "session_id": session_id,
        "user_visible": True,
        "tags": [tag for tag in tags if str(tag).strip()],
    }
    if active_thread:
        params["thread_name"] = active_thread
        params["thread_key"] = active_thread_key or active_thread.lower()
    return True, params, ""


def _resolve_memory_item_reference(item_id: str, session_state: dict | None) -> str:
    raw = str(item_id or "").strip()
    if not raw:
        return ""
    if raw.lower() in {"last", "recent", "that", "this"}:
        return str((session_state or {}).get("last_memory_item_id") or "").strip()
    return raw


def _select_relevant_memory_context(
    query: str,
    *,
    session_state: dict,
    project_threads: ProjectThreadStore,
) -> list[dict[str, str]]:
    text = str(query or "").strip()
    if not text:
        return []

    lowered = text.lower()
    if lowered.startswith("memory ") or lowered in {
        "list memories",
        "show memories",
        "show saved memories",
        "what do you remember",
        "show what you remember",
        "export memory",
        "download my memory",
        "forget this",
        "forget that",
        "operational context",
        "show operational context",
        "continuity status",
        "reset operational context",
        "reset continuity",
    }:
        return []
    if EXPLICIT_MEMORY_SAVE_RE.match(text):
        return []

    try:
        from src.memory.governed_memory_store import GovernedMemoryStore

        active_thread = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
        active_thread_key = project_threads.active_thread_key() or (active_thread.lower() if active_thread else "")
        matches = GovernedMemoryStore().find_relevant_items(
            text,
            thread_name=active_thread,
            thread_key=active_thread_key,
            limit=3,
        )
    except Exception:
        matches = []

    selected: list[dict[str, str]] = []
    for item in matches[:3]:
        links = dict(item.get("links") or {})
        content = _make_shorter_followup(
            str(item.get("content_raw") or item.get("body") or item.get("content_display") or item.get("title") or "").strip()
        )
        if not content:
            continue
        selected.append(
            {
                "id": str(item.get("id") or "").strip(),
                "title": str(item.get("title") or "").strip(),
                "content": content,
                "scope": str(item.get("scope") or "").strip(),
                "thread_name": str(links.get("project_thread_name") or "").strip(),
                "source": str(item.get("source") or "explicit_user_save").strip(),
            }
        )
    return selected


def _clarification_suggestions(message: str) -> list[dict[str, str]]:
    text = str(message or "").strip()
    if not text:
        return []

    m = re.search(r"open website (.+?)' or 'open file (.+?)'", text, flags=re.IGNORECASE)
    if m:
        website_target = m.group(1).strip()
        file_target = m.group(2).strip()
        return [
            {"label": "Open website", "command": f"open website {website_target}"},
            {"label": "Open file", "command": f"open file {file_target}"},
        ]

    lower = text.lower()
    if "what should i open" in lower:
        return [
            {"label": "Open website", "command": "open website github"},
            {"label": "Open documents", "command": "open documents"},
            {"label": "Open downloads", "command": "open downloads"},
        ]
    if "what should i search" in lower:
        return [
            {"label": "Search weather", "command": "search local weather forecast"},
            {"label": "Search tech news", "command": "search latest tech news"},
            {"label": "Today's brief", "command": "today's news"},
        ]
    if "what topic should i research" in lower:
        return [
            {"label": "Research AI policy", "command": "research AI policy updates"},
            {"label": "Research market trend", "command": "research Nvidia stock movement"},
            {"label": "Daily brief", "command": "daily brief"},
        ]
    if "could you clarify" in lower or "misheard" in lower:
        return [
            {"label": "Weather", "command": "weather"},
            {"label": "Today's news", "command": "today's news"},
            {"label": "Open documents", "command": "open documents"},
        ]
    return []


def _conversation_suggestions(session_state: dict) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = [
        {"label": "Weather", "command": "weather"},
        {"label": "News", "command": "news"},
        {"label": "Today's brief", "command": "today's news"},
    ]
    if session_state.get("last_response"):
        suggestions.append({"label": "Shorter version", "command": "shorter version"})
    return suggestions[:3]


TOPIC_STACK_TTL_TURNS = 8
TOPIC_STACK_MAX_ITEMS = 6
def _prune_topic_stack(session_state: dict, turn_count: int) -> None:
    stack = session_state.get("topic_stack") or []
    if not isinstance(stack, list):
        session_state["topic_stack"] = []
        session_state["active_topic"] = ""
        return

    fresh = []
    for item in stack:
        if not isinstance(item, dict):
            continue
        topic = str(item.get("topic") or "").strip()
        seen_turn = int(item.get("turn") or 0)
        if not topic:
            continue
        if turn_count - seen_turn <= TOPIC_STACK_TTL_TURNS:
            fresh.append({"topic": topic, "turn": seen_turn})
    fresh = fresh[-TOPIC_STACK_MAX_ITEMS:]
    session_state["topic_stack"] = fresh
    session_state["active_topic"] = fresh[-1]["topic"] if fresh else ""


def _push_topic(session_state: dict, topic: str, turn_count: int) -> None:
    clean_topic = str(topic or "").strip()
    if not clean_topic:
        return
    stack = list(session_state.get("topic_stack") or [])
    deduped = [item for item in stack if str(item.get("topic") or "").strip().lower() != clean_topic.lower()]
    deduped.append({"topic": clean_topic, "turn": turn_count})
    session_state["topic_stack"] = deduped[-TOPIC_STACK_MAX_ITEMS:]
    session_state["active_topic"] = clean_topic
    _prune_topic_stack(session_state, turn_count)


def _remember_topic(session_state: dict, text: str, intent_family: str, turn_count: int) -> None:
    _prune_topic_stack(session_state, turn_count)
    if intent_family == "followup":
        active = str(session_state.get("active_topic") or "").strip()
        if active:
            _push_topic(session_state, active, turn_count)
        return

    if intent_family not in {"research", "question", "task", "work", "analysis"}:
        return
    candidate = _extract_topic_candidate(text)
    if candidate:
        _push_topic(session_state, candidate, turn_count)


def _topic_stack_message(session_state: dict, turn_count: int) -> str:
    _prune_topic_stack(session_state, turn_count)
    stack = list(session_state.get("topic_stack") or [])
    if not stack:
        return "We are not locked to a topic right now."

    lines = [f"Current topic: {stack[-1]['topic']}"]
    if len(stack) > 1:
        lines.append("Recent topics:")
        for entry in reversed(stack[:-1][-3:]):
            lines.append(f"- {entry['topic']}")
    return "\n".join(lines)


def _build_thread_attachment_summary(
    *,
    session_state: dict,
    working_context: WorkingContextStore,
    action_result: Optional[object] = None,
) -> tuple[str, list[str], str]:
    context = working_context.to_dict()
    task_goal = str(context.get("task_goal") or "").strip()
    last_obj = str(context.get("last_relevant_object") or "").strip()
    summary = ""
    next_steps: list[str] = []
    default_category = "artifact"

    if action_result is not None:
        message = _action_result_message(action_result)
        summary = _make_shorter_followup(message)
        data = _action_result_payload(action_result)
        if isinstance(data, dict):
            analysis = data.get("analysis")
            if isinstance(analysis, dict):
                next_steps = [
                    str(item).strip()
                    for item in list(analysis.get("next_steps") or [])
                    if str(item).strip()
                ][:4]
                diagnostic = str(dict(analysis.get("signals") or {}).get("diagnostic") or "").strip().lower()
                if diagnostic in {"module_not_found", "key_error"}:
                    default_category = "blocker"
            if str(data.get("document_id") or "").strip():
                default_category = "decision"

    if not summary:
        summary = _make_shorter_followup(str(session_state.get("last_response") or ""))
    if not summary:
        summary = task_goal or last_obj or "Captured update from current session context."

    if not next_steps:
        followup_target = working_context.followup_target()
        if followup_target:
            next_steps = [f"Continue with focus: {followup_target}."]

    return summary, next_steps, default_category


def _derive_recommendation_reason(
    *,
    capability_id: int,
    action_result: object,
    working_context: WorkingContextStore,
) -> str:
    reasons: list[str] = []
    context = working_context.to_dict()
    task_goal = str(context.get("task_goal") or "").strip()
    if task_goal:
        reasons.append(f"your active goal is '{task_goal}'")

    followup_target = working_context.followup_target()
    if followup_target:
        reasons.append(f"the current context target is '{followup_target}'")

    data = _action_result_payload(action_result)
    if isinstance(data, dict):
        analysis = data.get("analysis")
        if isinstance(analysis, dict):
            signals = dict(analysis.get("signals") or {})
            diagnostic = str(signals.get("diagnostic") or "").strip()
            if diagnostic:
                reasons.append(f"analysis detected '{diagnostic}'")
        if capability_id == 54 and str(data.get("document_id") or "").strip():
            reasons.append("an analysis document is active in this session")

    if capability_id in {59, 60} and not reasons:
        reasons.append("screen/context analysis was the latest action")

    if not reasons:
        return ""
    if len(reasons) == 1:
        return f"I suggested that based on {reasons[0]}."
    return "I suggested that based on " + "; ".join(reasons[:3]) + "."


def _action_result_message(action_result: object | None) -> str:
    if action_result is None:
        return ""
    return str(
        getattr(action_result, "user_message", getattr(action_result, "message", "")) or ""
    ).strip()


def _action_result_payload(action_result: object | None) -> dict[str, Any]:
    if action_result is None:
        return {}
    try:
        structured = getattr(action_result, "structured_data", None)
    except Exception:
        structured = None
    if isinstance(structured, dict) and structured:
        return dict(structured)
    data = getattr(action_result, "data", None)
    if isinstance(data, dict):
        nested = data.get("structured_data")
        if isinstance(nested, dict) and nested:
            return dict(nested)
        return dict(data)
    if isinstance(structured, dict):
        return dict(structured)
    return {}


def _prepare_memory_bridge_params(
    *,
    params: dict,
    project_threads: ProjectThreadStore,
    session_state: dict | None = None,
    session_id: str = "",
) -> tuple[bool, dict, str]:
    action = str(params.get("action") or "").strip().lower()
    state = session_state or {}
    if action == "save_thread_snapshot":
        requested = str(params.get("thread_name") or "").strip()
        if _canonical_thread_reference(requested) in {"this", "it", "thread", "project"}:
            requested = project_threads.active_thread_name()
        found, brief = project_threads.render_brief(requested)
        if not found:
            return False, params, brief

        resolved_name = project_threads.active_thread_name()
        resolved_key = project_threads.active_thread_key()
        tags_raw = params.get("tags")
        tags: list[str]
        if isinstance(tags_raw, list):
            tags = [str(item).strip() for item in tags_raw if str(item).strip()]
        elif isinstance(tags_raw, str):
            tags = [token.strip() for token in tags_raw.split(",") if token.strip()]
        else:
            tags = []
        if "project_thread" not in tags:
            tags.append("project_thread")
        if resolved_key and resolved_key not in tags:
            tags.append(resolved_key)

        prepared = dict(params)
        prepared["action"] = "save"
        prepared["title"] = f"Thread Snapshot: {resolved_name}"
        prepared["body"] = brief
        prepared["scope"] = "project"
        prepared["thread_name"] = resolved_name
        prepared["thread_key"] = resolved_key
        prepared["tags"] = tags
        return True, prepared, ""

    if action == "save_thread_decision":
        requested = str(params.get("thread_name") or "").strip()
        if _canonical_thread_reference(requested) in {"this", "it", "thread", "project"}:
            requested = project_threads.active_thread_name()
        found, resolved_name, resolved_key = project_threads.resolve_thread_identity(requested)
        if not found:
            return False, params, "I could not find that project thread yet."

        decision_text = str(params.get("decision") or "").strip()
        if not decision_text:
            return False, params, "Please include the decision text after ':'."
        project_threads.add_decision(thread_name=resolved_name, decision=decision_text)

        tags_raw = params.get("tags")
        tags: list[str]
        if isinstance(tags_raw, list):
            tags = [str(item).strip() for item in tags_raw if str(item).strip()]
        elif isinstance(tags_raw, str):
            tags = [token.strip() for token in tags_raw.split(",") if token.strip()]
        else:
            tags = []
        for value in ("project_thread", "decision", resolved_key):
            if value and value not in tags:
                tags.append(value)

        prepared = dict(params)
        prepared["action"] = "save"
        prepared["title"] = f"Decision: {resolved_name}"
        prepared["body"] = f"Project thread: {resolved_name}\n\nDecision\n{decision_text}"
        prepared["scope"] = "project"
        prepared["thread_name"] = resolved_name
        prepared["thread_key"] = resolved_key
        prepared["tags"] = tags
        return True, prepared, ""

    if action == "list" and str(params.get("thread_name") or "").strip():
        requested = str(params.get("thread_name") or "").strip()
        if _canonical_thread_reference(requested) in {"this", "it", "thread", "project"}:
            requested = project_threads.active_thread_name()
        prepared = dict(params)
        found, resolved_name, resolved_key = project_threads.resolve_thread_identity(requested)
        if found:
            prepared["thread_name"] = resolved_name
            prepared["thread_key"] = resolved_key
        else:
            prepared["thread_name"] = requested
        return True, prepared, ""

    if action in {"show", "lock", "defer", "unlock", "delete", "supersede"}:
        requested_item_id = str(params.get("item_id") or "").strip()
        resolved_item_id = _resolve_memory_item_reference(requested_item_id, state)
        if not resolved_item_id:
            if requested_item_id.lower() in {"last", "recent", "that", "this"} or not requested_item_id:
                return False, params, "I do not have a recent memory item yet. Try 'list memories' first."
            return False, params, "Please provide a memory item ID."

        prepared = dict(params)
        prepared["item_id"] = resolved_item_id
        if action == "supersede":
            prepared.setdefault("source", "explicit_user_edit")
            prepared.setdefault("user_visible", True)
            if session_id:
                prepared.setdefault("session_id", session_id)
        return True, prepared, ""

    return True, params, ""


def _memory_confirmation_prompt(action: str, params: dict) -> str:
    item_id = str(params.get("item_id") or "that memory").strip()
    item_title = item_id
    try:
        from src.memory.governed_memory_store import GovernedMemoryStore

        item = GovernedMemoryStore().get_item(item_id)
        if isinstance(item, dict):
            item_title = str(item.get("title") or item.get("content_display") or item_id).strip() or item_id
    except Exception:
        item_title = item_id

    if action == "delete":
        return (
            f"Delete memory {item_id} ({item_title})?\n"
            "This action needs confirmation.\n"
            "Reply 'yes' to proceed or 'no' to cancel."
        )
    if action == "unlock":
        return (
            f"Unlock memory {item_id} ({item_title})?\n"
            "This action needs confirmation.\n"
            "Reply 'yes' to proceed or 'no' to cancel."
        )
    if action == "supersede":
        preview = _make_shorter_followup(str(params.get("new_body") or "").strip())
        preview_line = f"New content: {preview}\n" if preview else ""
        return (
            f"Update memory {item_id} ({item_title})?\n"
            f"{preview_line}"
            "This action needs confirmation.\n"
            "Reply 'yes' to proceed or 'no' to cancel."
        )
    return (
        f"Proceed with memory action on {item_id}?\n"
        "This action needs confirmation.\n"
        "Reply 'yes' to proceed or 'no' to cancel."
    )


def _enrich_thread_map_widget_memory(widget: dict) -> dict:
    if not isinstance(widget, dict):
        return widget
    if str(widget.get("type") or "").strip() != "thread_map":
        return widget

    threads = list(widget.get("threads") or [])
    if not threads:
        return widget

    insights: dict[str, dict] = {}
    try:
        from src.memory.governed_memory_store import GovernedMemoryStore

        insights = GovernedMemoryStore().summarize_thread_insights()
    except Exception:
        insights = {}

    enriched_threads: list[dict] = []
    for item in threads:
        row = dict(item or {})
        key = str(row.get("key") or "").strip().lower()
        insight = dict(insights.get(key) or {})
        row["memory_count"] = int(insight.get("memory_count") or 0)
        row["last_memory_updated_at"] = str(insight.get("last_memory_updated_at") or "")
        row["latest_decision"] = str(insight.get("latest_decision") or "")
        enriched_threads.append(row)

    enriched = dict(widget)
    enriched["threads"] = enriched_threads
    return enriched


def _compute_thread_change_summary(current: dict, previous: dict | None) -> str:
    if previous is None:
        return "Changed: new thread activity recorded."

    current_decision = str(current.get("latest_decision") or "").strip()
    previous_decision = str(previous.get("latest_decision") or "").strip()
    current_memory_count = int(current.get("memory_count") or 0)
    previous_memory_count = int(previous.get("memory_count") or 0)
    current_blocker = str(current.get("latest_blocker") or "").strip()
    previous_blocker = str(previous.get("latest_blocker") or "").strip()
    current_memory_updated = str(current.get("last_memory_updated_at") or "")
    previous_memory_updated = str(previous.get("last_memory_updated_at") or "")
    current_thread_updated = str(current.get("updated_at") or "")
    previous_thread_updated = str(previous.get("updated_at") or "")

    if current_decision and current_decision != previous_decision:
        return "Changed: decision updated."
    if current_blocker and current_blocker != previous_blocker:
        return "Changed: blocker updated."
    if current_memory_count > previous_memory_count:
        return "Changed: memory entry added."
    if current_memory_updated > previous_memory_updated:
        return "Changed: memory updated."
    if current_thread_updated > previous_thread_updated:
        return "Changed: thread status updated."
    return "Changed: no major updates."


def _build_thread_detail_widget(
    *,
    detail: dict,
    memory_items: list[dict],
) -> dict:
    detail_payload = dict(detail or {})
    latest_next = str(detail.get("latest_next_action") or "").strip()
    health_reason = str(detail.get("health_reason") or "").strip()
    blocker = str(detail.get("latest_blocker") or "").strip()
    why_blocked = ""
    if blocker:
        if health_reason:
            why_blocked = f"Blocked because {blocker} (health signal: {health_reason})."
        else:
            why_blocked = f"Blocked because {blocker}."
    else:
        why_blocked = "No blocker is currently recorded."

    next_step = latest_next or "No next step recorded."
    why_next = ""
    if latest_next and blocker:
        why_next = f"This next step is recommended to address the current blocker: {blocker}."
    elif latest_next:
        why_next = f"This next step is recommended from current thread context ({health_reason or 'at-risk'})."
    else:
        why_next = "No recommendation yet because no next step is recorded."

    trimmed_memory = []
    latest_memory_updated = ""
    for item in memory_items[:5]:
        row = dict(item or {})
        updated_at = str(row.get("updated_at") or "")
        if updated_at > latest_memory_updated:
            latest_memory_updated = updated_at
        trimmed_memory.append(
            {
                "id": str(row.get("id") or ""),
                "title": str(row.get("title") or ""),
                "tier": str(row.get("tier") or ""),
                "updated_at": updated_at,
            }
        )
    if latest_memory_updated:
        detail_payload["last_memory_updated_at"] = latest_memory_updated

    return {
        "type": "thread_detail",
        "thread": detail_payload,
        "why_blocked": why_blocked,
        "next_step": next_step,
        "memory_items": trimmed_memory,
        "recent_decisions": list(detail.get("recent_decisions") or [])[-5:],
        "why_next_step": why_next,
    }


def _build_memory_overview_widget(overview: dict | None) -> dict:
    payload = dict(overview or {})
    tier_counts = dict(payload.get("tier_counts") or {})
    scope_counts = dict(payload.get("scope_counts") or {})
    total_count = int(payload.get("total_count") or 0)
    active_count = int(tier_counts.get("active") or 0)
    locked_count = int(tier_counts.get("locked") or 0)
    deferred_count = int(tier_counts.get("deferred") or 0)

    recent_items: list[dict] = []
    for item in list(payload.get("recent_items") or [])[:5]:
        row = dict(item or {})
        recent_items.append(
            {
                "id": str(row.get("id") or ""),
                "title": str(row.get("title") or ""),
                "tier": str(row.get("tier") or ""),
                "scope": str(row.get("scope") or ""),
                "updated_at": str(row.get("updated_at") or ""),
                "thread_name": str(row.get("thread_name") or ""),
            }
        )

    linked_threads: list[dict] = []
    for thread in list(payload.get("linked_threads") or [])[:5]:
        row = dict(thread or {})
        linked_threads.append(
            {
                "thread_key": str(row.get("thread_key") or ""),
                "thread_name": str(row.get("thread_name") or row.get("thread_key") or ""),
                "memory_count": int(row.get("memory_count") or 0),
                "last_memory_updated_at": str(row.get("last_memory_updated_at") or ""),
                "latest_title": str(row.get("latest_title") or ""),
                "latest_tier": str(row.get("latest_tier") or ""),
            }
        )

    if total_count <= 0:
        summary = "No durable memory saved yet. Memory becomes persistent only when you explicitly save it."
    else:
        summary = (
            f"Total {total_count} durable item"
            f"{'' if total_count == 1 else 's'} | "
            f"Active {active_count} | Locked {locked_count} | Deferred {deferred_count}"
        )

    return {
        "type": "memory_overview",
        "summary": summary,
        "total_count": total_count,
        "tier_counts": {
            "active": active_count,
            "locked": locked_count,
            "deferred": deferred_count,
        },
        "scope_counts": {
            "nova_core": int(scope_counts.get("nova_core") or scope_counts.get("general") or 0),
            "general": int(scope_counts.get("general") or 0),
            "project": int(scope_counts.get("project") or 0),
            "ops": int(scope_counts.get("ops") or 0),
        },
        "recent_items": recent_items,
        "linked_threads": linked_threads,
        "inspectability_note": "Memory is explicit, inspectable, and revocable.",
    }


def _build_memory_list_widget(
    items: list[dict] | None,
    *,
    filters: dict | None = None,
) -> dict:
    normalized_items: list[dict[str, object]] = []
    for item in list(items or [])[:30]:
        row = dict(item or {})
        links = dict(row.get("links") or {})
        normalized_items.append(
            {
                "id": str(row.get("id") or ""),
                "title": str(row.get("title") or ""),
                "tier": str(row.get("tier") or ""),
                "status": str(row.get("status") or row.get("tier") or "active"),
                "scope": str(row.get("scope") or ""),
                "source": str(row.get("source") or ""),
                "updated_at": str(row.get("updated_at") or ""),
                "created_at": str(row.get("created_at") or ""),
                "thread_name": str(links.get("project_thread_name") or ""),
                "thread_key": str(links.get("project_thread_key") or ""),
                "preview": str(row.get("content_display") or row.get("title") or ""),
                "deleted": bool(row.get("deleted")),
            }
        )

    filter_payload = dict(filters or {})
    tier = str(filter_payload.get("tier") or "").strip().lower()
    scope = str(filter_payload.get("scope") or "").strip().lower()
    thread_name = str(filter_payload.get("thread_name") or "").strip()
    thread_key = str(filter_payload.get("thread_key") or "").strip()

    summary_parts = [f"{len(normalized_items)} item{'s' if len(normalized_items) != 1 else ''}"]
    if tier:
        summary_parts.append(f"tier {tier}")
    if scope:
        summary_parts.append(f"scope {scope}")
    if thread_name:
        summary_parts.append(f"thread {thread_name}")
    elif thread_key:
        summary_parts.append(f"thread {thread_key}")

    return {
        "type": "memory_list",
        "summary": " | ".join(summary_parts),
        "items": normalized_items,
        "filters": {
            "tier": tier,
            "scope": scope,
            "thread_name": thread_name,
            "thread_key": thread_key,
        },
    }


def _build_memory_item_widget(item: dict | None) -> dict:
    payload = dict(item or {})
    links = dict(payload.get("links") or {})
    lock = dict(payload.get("lock") or {})
    return {
        "type": "memory_item",
        "item": {
            "id": str(payload.get("id") or ""),
            "title": str(payload.get("title") or ""),
            "body": str(payload.get("body") or ""),
            "tier": str(payload.get("tier") or ""),
            "status": str(payload.get("status") or payload.get("tier") or "active"),
            "scope": str(payload.get("scope") or ""),
            "source": str(payload.get("source") or ""),
            "updated_at": str(payload.get("updated_at") or ""),
            "created_at": str(payload.get("created_at") or ""),
            "version": int(payload.get("version") or 0),
            "tags": [str(tag) for tag in list(payload.get("tags") or []) if str(tag).strip()],
            "thread_name": str(links.get("project_thread_name") or ""),
            "thread_key": str(links.get("project_thread_key") or ""),
            "is_locked": bool(lock.get("is_locked")),
            "unlock_policy": str(lock.get("unlock_policy") or ""),
            "supersedes": [str(value) for value in list(lock.get("supersedes") or []) if str(value).strip()],
            "superseded_by": str(lock.get("superseded_by") or ""),
            "deleted": bool(payload.get("deleted")),
            "deleted_at": str(payload.get("deleted_at") or ""),
            "content_display": str(payload.get("content_display") or payload.get("title") or ""),
        },
    }


def _build_workspace_home_widget(
    *,
    session_state: dict,
    project_threads: ProjectThreadStore,
) -> dict[str, object]:
    threads = [dict(item or {}) for item in project_threads.list_summaries()]
    active_thread_name = str(project_threads.active_thread_name() or "").strip()
    try:
        from src.memory.governed_memory_store import GovernedMemoryStore

        thread_insights = GovernedMemoryStore().summarize_thread_insights()
    except Exception:
        thread_insights = {}
    for item in threads:
        key = str(item.get("key") or "").strip().lower()
        insight = dict(thread_insights.get(key) or {})
        item["memory_count"] = int(insight.get("memory_count") or 0)
        item["last_memory_updated_at"] = str(insight.get("last_memory_updated_at") or "")
        item["latest_decision"] = str(insight.get("latest_decision") or item.get("latest_decision") or "")

    memory_overview: dict[str, Any] = {}
    recent_memory_items: list[dict[str, str]] = []
    try:
        from src.memory.governed_memory_store import GovernedMemoryStore

        memory_store = GovernedMemoryStore()
        memory_overview = memory_store.summarize_overview(recent_limit=3, thread_limit=5)
    except Exception:
        memory_overview = {}

    focus_thread: dict[str, Any] = {}
    if active_thread_name:
        focus_thread = next(
            (
                row
                for row in threads
                if str(row.get("name") or "").strip().lower() == active_thread_name.lower()
            ),
            {},
        )
    if not focus_thread and threads:
        focus_thread = dict(threads[0])

    focus_thread_name = str(focus_thread.get("name") or "").strip()
    focus_thread_key = str(focus_thread.get("key") or "").strip()
    if focus_thread_name:
        try:
            from src.memory.governed_memory_store import GovernedMemoryStore

            recent_memory_items = [
                {
                    "id": str(item.get("id") or ""),
                    "title": str(item.get("title") or ""),
                    "tier": str(item.get("tier") or ""),
                    "updated_at": str(item.get("updated_at") or ""),
                }
                for item in GovernedMemoryStore().list_items(
                    thread_name=focus_thread_name,
                    thread_key=focus_thread_key,
                    limit=3,
                )
            ]
        except Exception:
            recent_memory_items = []

    trust_snapshot = _build_trust_review_snapshot()
    recent_activity = [dict(item or {}) for item in list(trust_snapshot.get("recent_runtime_activity") or [])[:4]]

    analysis_documents = list(session_state.get("analysis_documents") or [])
    analysis_documents = sorted(
        [dict(item or {}) for item in analysis_documents],
        key=lambda row: int(row.get("id") or 0),
        reverse=True,
    )
    recent_documents = [
        {
            "id": int(item.get("id") or 0),
            "title": str(item.get("title") or f"Doc {item.get('id') or '?'}"),
            "topic": str(item.get("topic") or ""),
            "summary": str(item.get("summary") or ""),
        }
        for item in analysis_documents[:3]
    ]

    tier_counts = dict(memory_overview.get("tier_counts") or {})
    scope_counts = dict(memory_overview.get("scope_counts") or {})
    total_memory = int(memory_overview.get("total_count") or 0)
    project_memory_total = int(scope_counts.get("project") or 0)
    linked_thread_count = len(list(memory_overview.get("linked_threads") or []))
    recent_decisions_feed = [
        {
            "thread_name": str(item.get("name") or ""),
            "decision": str(item.get("latest_decision") or ""),
            "updated_at": str(item.get("updated_at") or ""),
        }
        for item in threads
        if str(item.get("latest_decision") or "").strip()
    ]
    recent_decisions_feed = sorted(
        recent_decisions_feed,
        key=lambda row: str(row.get("updated_at") or ""),
        reverse=True,
    )[:6]

    if focus_thread_name:
        health_state = str(focus_thread.get("health_state") or "at-risk").strip().upper()
        summary = (
            f"Active workspace: {focus_thread_name}. "
            f"Health {health_state}. "
            f"{project_memory_total} project memory item{'s' if project_memory_total != 1 else ''} "
            f"and {len(recent_documents)} recent report{'s' if len(recent_documents) != 1 else ''} are available."
        )
    elif threads:
        summary = (
            f"{len(threads)} project thread{'s' if len(threads) != 1 else ''} available. "
            f"{project_memory_total} project memory item{'s' if project_memory_total != 1 else ''} tracked."
        )
    else:
        summary = (
            "No active project thread yet. Use project summaries, thread saves, or analysis reports to start a calmer "
            "workspace history."
        )

    recommended_actions: list[dict[str, str]] = []
    if focus_thread_name:
        recommended_actions.extend(
            [
                {"label": f"Continue {focus_thread_name}", "command": f"continue my {focus_thread_name}"},
                {"label": "Project status", "command": f"project status {focus_thread_name}"},
                {"label": "Thread memory", "command": f"memory list thread {focus_thread_name}"},
            ]
        )
    else:
        recommended_actions.extend(
            [
                {"label": "Show threads", "command": "show threads"},
                {"label": "Create report", "command": "create analysis report on this repo architecture"},
                {"label": "Memory overview", "command": "memory overview"},
            ]
        )
    recommended_actions.extend(
        [
            {"label": "Operational context", "command": "operational context"},
            {"label": "List analysis docs", "command": "list analysis docs"},
            {"label": "Memory Center", "command": "list memories"},
        ]
    )

    operational_context = build_operational_context_widget(
        session_state=session_state,
        working_context_snapshot=dict(session_state.get("working_context") or {}),
        project_threads=project_threads,
        trust_snapshot=trust_snapshot,
    )

    return {
        "type": "workspace_home",
        "summary": summary,
        "active_thread": active_thread_name,
        "thread_count": len(threads),
        "linked_thread_count": linked_thread_count,
        "memory_total": total_memory,
        "project_memory_total": project_memory_total,
        "locked_memory_total": int(tier_counts.get("locked") or 0),
        "deferred_memory_total": int(tier_counts.get("deferred") or 0),
        "focus_thread": {
            "name": focus_thread_name,
            "goal": str(focus_thread.get("goal") or ""),
            "health_state": str(focus_thread.get("health_state") or ""),
            "health_reason": str(focus_thread.get("health_reason") or ""),
            "latest_blocker": str(focus_thread.get("latest_blocker") or ""),
            "latest_next_action": str(focus_thread.get("latest_next_action") or ""),
            "latest_decision": str(focus_thread.get("latest_decision") or ""),
            "memory_count": int(focus_thread.get("memory_count") or 0),
            "last_memory_updated_at": str(focus_thread.get("last_memory_updated_at") or ""),
            "updated_at": str(focus_thread.get("updated_at") or ""),
        },
        "recent_threads": [
            {
                "name": str(item.get("name") or ""),
                "key": str(item.get("key") or ""),
                "goal": str(item.get("goal") or ""),
                "health_state": str(item.get("health_state") or ""),
                "health_reason": str(item.get("health_reason") or ""),
                "latest_blocker": str(item.get("latest_blocker") or ""),
                "latest_next_action": str(item.get("latest_next_action") or ""),
                "latest_decision": str(item.get("latest_decision") or ""),
                "blocker_count": int(item.get("blocker_count") or 0),
                "memory_count": int(item.get("memory_count") or 0),
                "updated_at": str(item.get("updated_at") or ""),
            }
            for item in threads[:6]
        ],
        "recent_decisions_feed": recent_decisions_feed,
        "recent_memory_items": recent_memory_items,
        "recent_documents": recent_documents,
        "recent_activity": recent_activity,
        "operational_context": operational_context,
        "recommended_actions": recommended_actions[:5],
        "blocked_conditions": [dict(item or {}) for item in list(trust_snapshot.get("blocked_conditions") or [])[:3]],
    }


def _render_workspace_home_message(widget: dict[str, object]) -> str:
    payload = dict(widget or {})
    focus = dict(payload.get("focus_thread") or {})
    thread_name = str(focus.get("name") or "").strip()
    summary = str(payload.get("summary") or "").strip()
    lines = ["Workspace Home", ""]
    if summary:
        lines.append(summary)
        lines.append("")
    if thread_name:
        lines.append(f"Focus project: {thread_name}")
        health_state = str(focus.get("health_state") or "").strip().upper()
        if health_state:
            lines.append(f"Health: {health_state}")
        latest_blocker = str(focus.get("latest_blocker") or "").strip()
        if latest_blocker:
            lines.append(f"Current blocker: {latest_blocker}")
        latest_next_action = str(focus.get("latest_next_action") or "").strip()
        if latest_next_action:
            lines.append(f"Next step: {latest_next_action}")
    else:
        lines.append("No focus project is active yet.")
    return "\n".join(lines).strip()


def _reset_operational_session_state(
    session_state: dict[str, Any],
    *,
    working_context_snapshot: dict[str, Any] | None = None,
) -> None:
    session_state["last_response"] = ""
    session_state["last_object"] = ""
    session_state["analysis_documents"] = []
    session_state["last_analysis_doc_id"] = None
    session_state["last_intent_family"] = ""
    session_state["last_mode"] = ""
    session_state["session_mode_override"] = ""
    session_state["topic_stack"] = []
    session_state["active_topic"] = ""
    session_state["pending_web_open"] = None
    session_state["pending_governed_confirm"] = None
    session_state["pending_interpret_confirm"] = None
    session_state["last_calendar_summary"] = ""
    session_state["last_calendar_events"] = []
    session_state["working_context"] = dict(working_context_snapshot or {})
    session_state["project_thread_active"] = ""
    session_state["last_recommendation_reason"] = ""
    session_state["thread_map_last"] = {}
    session_state["last_workspace_home"] = {}
    session_state["last_project_structure_map"] = {}
    session_state["last_thread_detail"] = {}
    session_state["last_memory_context"] = []
    session_state["last_operational_context"] = {}
    session_state["last_assistive_notices"] = {}
    session_state["assistive_notice_state"] = {"items": {}}
    session_state["general_chat_context"] = []
    session_state["general_chat_summary"] = {}
    session_state["conversation_context"] = {}


def _build_tone_profile_widget(snapshot: dict | None) -> dict:
    payload = dict(snapshot or {})
    return {
        "type": "tone_profile",
        "summary": str(payload.get("summary") or "Global tone: balanced.").strip(),
        "global_profile": str(payload.get("global_profile") or "balanced").strip().lower(),
        "global_profile_label": str(payload.get("global_profile_label") or "Balanced").strip(),
        "override_count": int(payload.get("override_count") or 0),
        "updated_at": str(payload.get("updated_at") or ""),
        "domain_overrides": [dict(item or {}) for item in list(payload.get("domain_overrides") or [])[:8]],
        "history": [dict(item or {}) for item in list(payload.get("history") or [])[:6]],
        "profile_options": [dict(item or {}) for item in list(payload.get("profile_options") or [])],
        "domain_options": [dict(item or {}) for item in list(payload.get("domain_options") or [])],
        "inspectability_note": "Tone changes are explicit, inspectable, and resettable.",
    }


def _render_tone_profile_message(snapshot: dict | None) -> str:
    payload = dict(snapshot or {})
    global_label = str(payload.get("global_profile_label") or "Balanced").strip()
    overrides = list(payload.get("domain_overrides") or [])
    history = list(payload.get("history") or [])

    lines = ["Response Style Settings", ""]
    lines.append(f"Global tone: {global_label}")
    if overrides:
        lines.append("Domain overrides:")
        for item in overrides[:5]:
            label = str(item.get("label") or item.get("domain") or "Domain").strip()
            profile_label = str(item.get("profile_label") or item.get("profile") or "Balanced").strip()
            lines.append(f"- {label}: {profile_label}")
    else:
        lines.append("Domain overrides: none")

    if history:
        lines.append("")
        lines.append("Recent changes")
        for item in history[:4]:
            summary = str(item.get("summary") or "").strip()
            if summary:
                lines.append(f"- {summary}")

    lines.extend(
        [
            "",
            "Try next:",
            "- tone set concise",
            "- tone set research detailed",
            "- tone reset research",
            "- tone reset all",
        ]
    )
    return "\n".join(lines)


def _log_ledger_event(governor: Governor, event_type: str, metadata: dict) -> None:
    try:
        governor.ledger.log_event(event_type, metadata)
    except Exception:
        return


def _tone_domain_for_capability(capability_id: int) -> str:
    if capability_id in {32}:
        return "system"
    if capability_id in {55, 56, 57}:
        return "daily"
    if capability_id in {31, 49, 50, 51, 54}:
        return "research"
    if capability_id in {58, 59, 60, 61}:
        return "continuity"
    return "general"


def _tone_domain_for_skill(skill_name: str) -> str:
    lowered = str(skill_name or "").strip().lower()
    if lowered in {"system"}:
        return "system"
    if lowered in {"weather", "news", "calendar"}:
        return "daily"
    return "general"


def _parse_tone_set_body(raw_body: str) -> tuple[str, str, bool]:
    body = str(raw_body or "").strip().lower().rstrip(".?!").strip()
    if not body:
        return "", "", False

    if " to " in body:
        left, right = body.rsplit(" to ", 1)
        body = f"{left.strip()} {right.strip()}".strip()

    parts = [part for part in body.split() if part]
    if not parts:
        return "", "", False

    valid_profiles = set(ToneProfileStore.PROFILE_DEFINITIONS.keys())
    valid_domains = set(ToneProfileStore.DOMAIN_DEFINITIONS.keys()) | {"global"}

    if len(parts) == 1 and parts[0] in valid_profiles:
        return "global", parts[0], True

    profile = parts[-1].rstrip(".?!").strip()
    domain = " ".join(parts[:-1]).strip().lower().rstrip(".?!").strip()
    if profile not in valid_profiles:
        return "", "", False
    if domain not in valid_domains:
        return "", "", False
    return domain, profile, True


async def send_tone_profile_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    snapshot: dict | None = None,
) -> None:
    payload = dict(snapshot or interface_personality_agent.tone_snapshot() or {})
    session_state["last_tone_snapshot"] = payload
    await ws_send(ws, _build_tone_profile_widget(payload))


def _local_now() -> datetime:
    return datetime.now().astimezone()


def _format_local_schedule_time(value: datetime | None) -> str:
    if value is None:
        return ""
    local = value.astimezone()
    rendered = local.strftime("%b %d, %I:%M %p")
    return re.sub(r"(?<=\s)0(\d:)", r"\1", rendered)


def _capability_help_runtime_snapshot() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    try:
        provider_items = connections_store.snapshot()
    except Exception:
        provider_items = []
    providers = {
        str(item.get("id") or "").strip(): dict(item)
        for item in list(provider_items or [])
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    try:
        runtime = dict(openclaw_agent_runtime_store.snapshot() or {})
    except Exception:
        runtime = {}
    return providers, runtime


def _capability_help_actions() -> list[dict[str, str]]:
    providers, runtime = _capability_help_runtime_snapshot()
    actions: list[dict[str, str]] = []

    weather_live = bool((providers.get("weather") or {}).get("connected"))
    calendar_live = bool((providers.get("calendar") or {}).get("connected"))
    news_live = bool((providers.get("news") or {}).get("connected") or (providers.get("brave") or {}).get("connected"))
    active_run = dict(runtime.get("active_run") or {})

    def _add(label: str, command: str) -> None:
        if any(str(item.get("command") or "").strip().lower() == command.strip().lower() for item in actions):
            return
        actions.append({"label": label, "command": command})

    if active_run:
        _add("Check active run", "openclaw status")
    if weather_live and calendar_live:
        _add("Morning brief", "morning brief")
    if calendar_live:
        _add("Today's schedule", "today's schedule")
    if news_live:
        _add("Today's news", "today's news")
    if weather_live and len(actions) < 4:
        _add("Today's weather", "weather")
    if len(actions) < 4:
        _add("Explain this", "explain this")
    if len(actions) < 4:
        _add("Audit this repo", "audit this repo")
    return actions[:4]


def _capability_help_message() -> str:
    providers, runtime = _capability_help_runtime_snapshot()
    active_run_summary = str(runtime.get("active_run_summary") or "No home-agent runs are active right now.").strip()

    weather_live = bool((providers.get("weather") or {}).get("connected"))
    calendar_live = bool((providers.get("calendar") or {}).get("connected"))
    news_live = bool((providers.get("news") or {}).get("connected"))
    brave_live = bool((providers.get("brave") or {}).get("connected"))
    openai_live = bool((providers.get("openai") or {}).get("connected"))

    connected_labels: list[str] = []
    for provider_id in ("weather", "calendar", "news", "brave", "openai", "bridge"):
        item = providers.get(provider_id) or {}
        if bool(item.get("connected")):
            connected_labels.append(str(item.get("label") or provider_id).strip())

    lines = [
        "Nova Capabilities Right Now",
        "",
        "Here's what is actually live on this device right now:",
        "- Local-first everyday help is ready: explain things, help with project work, save memory, open local folders, and check system status.",
        "- Research and reporting: I can search the web, summarize headlines, build intelligence briefs, and create multi-source reports.",
        "- Verification and review: I can verify an answer or run a governed second-opinion pass without turning that into action.",
        "- Story tracking: I can follow a topic over time, refresh it, compare shifts, and show relationship views for tracked stories.",
        "- Analysis and explanation: I can create analysis docs, explain a page or file, and help you understand what you're looking at.",
        "- Screen help: I can capture the current screen on request, inspect it, and walk through what matters on it.",
        "- Memory and continuity: I can save, list, edit, lock, defer, export, and reuse governed memory and project context.",
        "- Local device help: I can open websites or allowed folders, read text aloud, and adjust volume, media, brightness, and system status.",
    ]

    if connected_labels:
        lines.append(f"- Connected live sources: {', '.join(connected_labels)}.")
    else:
        lines.append("- No live sources are connected yet, so I'll stay local-first until you add weather, news, calendar, or cloud reasoning in Settings.")

    if weather_live and calendar_live:
        lines.append("- Best daily-use flow: I can give you a proper morning brief with weather, schedule, and headline context.")
    elif calendar_live:
        lines.append("- Calendar is live, so I can answer things like today's schedule, tomorrow's schedule, and what's coming up.")
    elif weather_live:
        lines.append("- Weather is live, so I can give you forecast-aware check-ins and fold that into briefings.")
    elif news_live or brave_live:
        lines.append("- News and search are live, so I can help with current events, topic research, and answer-first news summaries.")
    else:
        lines.append("- Even without extra connections, I'm still useful for explanation, writing, memory, project continuity, and local device help.")

    if openai_live:
        lines.append("- Cloud reasoning is connected when you want it, but I still stay local-first by default.")

    lines.extend(
        [
            f"- OpenClaw status: {active_run_summary}",
            "",
            "Good things to try next:",
        ]
    )

    suggestions = _capability_help_actions()
    if suggestions:
        for item in suggestions:
            lines.append(f"- {item['command']}")
    else:
        lines.extend(
            [
                "- explain this",
                "- weather",
                "- today's news",
                "- audit this repo",
            ]
        )

    lines.append("")
    lines.append(
        "If you want, ask about a specific lane like research, verification, story tracking, screen help, memory, local controls, or OpenClaw."
    )
    return "\n".join(lines)


def _render_local_time_message() -> str:
    rendered = _local_now().strftime("%I:%M %p").lstrip("0")
    return f"It's {rendered}."


def _maybe_handle_local_project_structure_map_request(
    text: str,
    *,
    working_context: WorkingContextStore,
    session_state: dict[str, Any],
) -> tuple[str, list[dict[str, str]], str, dict[str, Any]] | None:
    lowered = re.sub(r"\s+", " ", str(text or "").strip().lower())
    if not lowered:
        return None

    current_phrases = {
        "show structure map",
        "show repo map",
        "show project map",
        "show codebase map",
        "create structure map",
        "generate structure map",
        "visualize this repo",
        "visualise this repo",
        "visualize this project",
        "visualise this project",
        "visualize this codebase",
        "visualise this codebase",
    }
    if lowered not in current_phrases and "structure map" not in lowered and "repo map" not in lowered:
        return None

    target_hint = "this repo"
    targeted_match = re.match(
        r"^\s*(?:show|create|generate|visual(?:ize|ise))\s+(?P<target>.+?)\s+(?:repo|project|codebase)\s+(?:structure\s+map|repo\s+map|project\s+map|codebase\s+map)\s*$",
        str(text or ""),
        re.IGNORECASE,
    )
    if targeted_match:
        target_hint = str(targeted_match.group("target") or "").strip()
    resolved_path = _resolve_local_project_path(
        target_hint,
        working_context=working_context,
        session_state=session_state,
    )
    if resolved_path is None:
        return None

    message, suggestions, widget = _render_local_project_structure_map(resolved_path)
    return message, suggestions, str(resolved_path), widget


def _render_trust_center_message(trust_status: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    payload = normalize_trust_status(trust_status)
    payload.update(_build_trust_review_snapshot())
    activity = [dict(item or {}) for item in list(payload.get("recent_runtime_activity") or [])[:3]]
    blocked = [dict(item or {}) for item in list(payload.get("blocked_conditions") or [])[:3]]
    lines = [
        "Trust Center",
        "",
        f"Mode: {payload.get('mode') or 'Local-only'}",
        f"Last external call: {payload.get('last_external_call') or 'None'}",
        f"Data egress: {payload.get('data_egress') or 'Read-only requests only'}",
        f"Failure state: {payload.get('failure_state') or 'Normal'}",
        "",
        str(payload.get("trust_review_summary") or "Recent governed actions and blocked conditions will appear here.").strip(),
    ]
    if activity:
        lines.append("")
        lines.append("Recent actions:")
        for item in activity:
            title = str(item.get("title") or "Runtime event").strip()
            detail = str(item.get("detail") or item.get("kind") or "").strip()
            outcome = str(item.get("outcome") or "info").strip()
            rendered = f"- {title}"
            if detail:
                rendered += f" - {detail}"
            if outcome:
                rendered += f" [{outcome}]"
            lines.append(rendered)
    if blocked:
        lines.append("")
        lines.append("Currently blocked:")
        for item in blocked:
            label = str(item.get("label") or item.get("area") or "Condition").strip()
            status = str(item.get("status") or "unknown").strip()
            reason = str(item.get("reason") or "").strip()
            rendered = f"- {label}: {status}"
            if reason:
                rendered += f" - {reason}"
            lines.append(rendered)
    suggestions = [
        {"label": "Workspace Home", "command": "workspace home"},
        {"label": "Operational context", "command": "operational context"},
        {"label": "System status", "command": "system status"},
        {"label": "Memory overview", "command": "memory overview"},
        {"label": "Policy map", "command": "what can policies run"},
    ]
    return "\n".join(lines).strip(), suggestions


def _build_policy_capability_readiness_snapshot() -> dict[str, Any]:
    try:
        return dict(OSDiagnosticsExecutor._policy_capability_readiness() or {})
    except Exception:
        return {
            "summary": "Capability delegation rules are unavailable right now.",
            "current_authority_limit": "unknown",
            "safe_now": [],
            "allowed_later": [],
            "manual_only": [],
        }


def _render_policy_capability_map_message(snapshot: dict[str, Any] | None) -> tuple[str, list[dict[str, str]]]:
    payload = dict(snapshot or {})
    safe_now = [dict(item or {}) for item in list(payload.get("safe_now") or [])[:5]]
    allowed_later = [dict(item or {}) for item in list(payload.get("allowed_later") or [])[:5]]
    manual_only = [dict(item or {}) for item in list(payload.get("manual_only") or [])[:5]]
    current_limit = str(payload.get("current_authority_limit") or "unknown").strip() or "unknown"

    lines = ["Capability Authority Map", ""]
    lines.append(
        str(
            payload.get("summary")
            or "Capability delegation rules are visible here so users can see what is safe now, later, or explicit-only."
        ).strip()
    )
    lines.append(f"Current delegated authority limit: {current_limit}")

    if safe_now:
        lines.extend(["", "Safe for manual review runs now"])
        for item in safe_now:
            lines.append(
                f"- {str(item.get('name') or '').strip()} "
                f"({str(item.get('authority_class') or 'unknown').strip()} · "
                f"{str(item.get('delegation_class') or 'observational').strip()})"
            )

    if allowed_later:
        lines.extend(["", "Lawful later when delegation widens"])
        for item in allowed_later:
            notes = str(item.get("envelope_notes") or item.get("why") or "").strip()
            rendered = f"- {str(item.get('name') or '').strip()} ({str(item.get('authority_class') or 'unknown').strip()})"
            if notes:
                rendered += f" - {notes}"
            lines.append(rendered)

    if manual_only:
        lines.extend(["", "Explicit-user only right now"])
        for item in manual_only[:4]:
            lines.append(
                f"- {str(item.get('name') or '').strip()} "
                f"({str(item.get('authority_class') or 'unknown').strip()})"
            )

    suggestions = [
        {"label": "Policy center", "command": "policy overview"},
        {"label": "Trust center", "command": "trust center"},
        {"label": "System status", "command": "system status"},
    ]
    return "\n".join(lines).strip(), suggestions


def _render_voice_runtime_message(snapshot: dict[str, Any], *, check_mode: bool) -> tuple[str, list[dict[str, str]]]:
    payload = dict(snapshot or {})
    lines = ["Voice check" if check_mode else "Voice status", ""]
    lines.append(str(payload.get("summary") or "Voice runtime status is unavailable.").strip())
    lines.append("")
    lines.append(
        f"Preferred engine: {str(payload.get('preferred_engine') or 'piper')} "
        f"({str(payload.get('preferred_status') or 'unknown')})"
    )
    lines.append(
        f"Fallback engine: {str(payload.get('fallback_engine') or 'pyttsx3')} "
        f"({str(payload.get('fallback_status') or 'unknown')})"
    )
    if str(payload.get("stt_status") or "").strip():
        lines.append(f"Speech input: {str(payload.get('stt_status') or '').strip()}")
    if str(payload.get("stt_converter_status") or "").strip():
        lines.append(
            f"Speech input converter: {str(payload.get('stt_converter_status') or '').strip()}"
        )
    if str(payload.get("stt_model_status") or "").strip():
        lines.append(
            f"Speech input model: {str(payload.get('stt_model_status') or '').strip()}"
        )
    if str(payload.get("last_engine") or "").strip():
        lines.append(f"Last runtime engine: {str(payload.get('last_engine') or '').strip()}")
    if str(payload.get("last_attempt_status") or "").strip():
        lines.append(f"Last runtime status: {str(payload.get('last_attempt_status') or '').strip()}")
    if str(payload.get("last_attempt_at") or "").strip():
        lines.append(f"Last attempt: {str(payload.get('last_attempt_at') or '').strip()}")
    if str(payload.get("last_error") or "").strip():
        lines.append(f"Last error: {str(payload.get('last_error') or '').strip()}")
    if str(payload.get("stt_converter_note") or "").strip():
        lines.append(f"Speech input note: {str(payload.get('stt_converter_note') or '').strip()}")
    if str(payload.get("stt_model_note") or "").strip():
        lines.append(f"Model note: {str(payload.get('stt_model_note') or '').strip()}")
    if check_mode:
        lines.extend(
            [
                "",
                "If you heard Nova's voice check phrase, spoken output is working on this device.",
                "If you did not hear it, open Settings and run the check again after reviewing the voice status note.",
            ]
        )
    suggestions = [
        {"label": "Trust center", "command": "trust center"},
        {"label": "Speak that", "command": "speak that"},
        {"label": "System status", "command": "system status"},
    ]
    return "\n".join(lines).strip(), suggestions


def _maybe_handle_local_project_request(
    text: str,
    *,
    working_context: WorkingContextStore,
    session_state: dict[str, Any],
) -> tuple[str, list[dict[str, str]], str] | None:
    raw_target = ""
    matched_kind = ""

    current_match = LOCAL_PROJECT_CURRENT_RE.match(text)
    if current_match:
        matched_kind = str(current_match.group("kind") or "").strip().lower()
    else:
        targeted_match = LOCAL_PROJECT_TARGET_RE.match(text)
        if targeted_match:
            raw_target = str(targeted_match.group("target") or "").strip()
            matched_kind = str(targeted_match.group("kind") or "").strip().lower()
        else:
            disk_match = LOCAL_PROJECT_DISK_RE.match(text)
            if not disk_match:
                return None
            raw_target = str(disk_match.group("target") or "").strip()
            matched_kind = "project"

    resolved_path = _resolve_local_project_path(
        raw_target,
        working_context=working_context,
        session_state=session_state,
    )
    if resolved_path is None:
        target_label = raw_target or f"this {matched_kind or 'project'}"
        workspace_path = ""
        paths = _candidate_local_project_paths(working_context, session_state)
        if paths:
            workspace_path = str(paths[0])
        lines = [
            f"I can review a local {matched_kind or 'project'}, but I need a concrete path or a clearly identified current workspace for '{target_label}'.",
        ]
        if workspace_path:
            lines.append(f"If you mean the current workspace, try: audit this repo")
            lines.append(f"Current workspace: {workspace_path}")
        lines.extend(
            [
                "",
                "Try next:",
                "- audit this repo",
                r"- audit folder C:\path\to\your\project",
                "- open documents",
            ]
        )
        suggestions = [
            {"label": "Audit this repo", "command": "audit this repo"},
            {"label": "Open documents", "command": "open documents"},
            {"label": "What can you do?", "command": "what can you do"},
        ]
        return "\n".join(lines), suggestions, ""

    message, suggestions = _render_local_project_summary(resolved_path)
    return message, suggestions, str(resolved_path)


def _maybe_handle_local_architecture_report_request(
    text: str,
    *,
    working_context: WorkingContextStore,
    session_state: dict[str, Any],
) -> tuple[str, list[dict[str, str]], str] | None:
    match = LOCAL_ARCHITECTURE_REPORT_RE.match(text)
    if not match:
        return None

    raw_target = str(match.group("target") or "").strip()
    resolved_path = _resolve_local_project_path(
        raw_target,
        working_context=working_context,
        session_state=session_state,
    )
    if resolved_path is None:
        return None

    message, suggestions = _render_local_architecture_report(resolved_path)
    return message, suggestions, str(resolved_path)


def _maybe_handle_local_codebase_summary_request(
    text: str,
    *,
    working_context: WorkingContextStore,
    session_state: dict[str, Any],
) -> tuple[str, list[dict[str, str]], str] | None:
    raw_target = ""
    matched_kind = "repo"
    location_hint = ""

    current_match = CODEBASE_SUMMARY_CURRENT_RE.match(text)
    if current_match:
        matched_kind = str(current_match.group("kind") or "repo").strip().lower()
    else:
        targeted_match = CODEBASE_SUMMARY_TARGET_RE.match(text)
        if targeted_match:
            raw_target = str(targeted_match.group("target") or "").strip()
            matched_kind = str(targeted_match.group("kind") or "repo").strip().lower()
        else:
            do_match = CODEBASE_DO_RE.match(text)
            if do_match:
                raw_target = str(do_match.group("target") or "").strip()
                matched_kind = str(do_match.group("kind") or "repo").strip().lower()
            else:
                capability_match = CODEBASE_CAPABILITY_RE.match(text)
                if capability_match:
                    raw_target = str(capability_match.group("target") or "").strip()
                    matched_kind = "codebase"
                else:
                    bare_match = CODEBASE_SUMMARY_TARGET_ONLY_RE.match(text)
                    if not bare_match:
                        return None
                    raw_target = str(bare_match.group("target") or "").strip()

    raw_target, location_hint = _split_local_location_hint(raw_target)
    normalized_target = _normalize_lookup_key(raw_target)
    if normalized_target in {
        "nova",
        "novalis",
        "novaproject",
        "this",
        "the",
        "local",
        "thisrepo",
        "thisproject",
        "thiscodebase",
    }:
        raw_target = "this repo"

    resolved_path = _resolve_local_project_path(
        raw_target,
        working_context=working_context,
        session_state=session_state,
    )
    if resolved_path is None:
        if raw_target and not location_hint:
            return None
        paths = _candidate_local_project_paths(working_context, session_state)
        workspace_path = str(paths[0]) if paths else ""
        lines = [
            f"I can summarize a local {matched_kind or 'project'}, but I need a concrete path or a clearly identified current workspace.",
        ]
        if raw_target:
            lines.append(f"Requested target: {raw_target}")
        if location_hint:
            lines.append(f"I treated '{location_hint}' as a local location hint, but I still need a path or a workspace I can match.")
        if workspace_path:
            lines.append("If you mean the current workspace, try: summarize this repo")
            lines.append(f"Current workspace: {workspace_path}")
        lines.extend(
            [
                "",
                "Try next:",
                "- summarize this repo",
                r"- summarize C:\path\to\your\project",
                "- audit this repo",
            ]
        )
        suggestions = [
            {"label": "Summarize this repo", "command": "summarize this repo"},
            {"label": "Audit this repo", "command": "audit this repo"},
            {"label": "Open documents", "command": "open documents"},
        ]
        return "\n".join(lines), suggestions, ""

    message, suggestions = _render_local_codebase_summary(resolved_path)
    return message, suggestions, str(resolved_path)


def _maybe_prepare_local_open_request(
    text: str,
    *,
    working_context: WorkingContextStore,
    session_state: dict[str, Any],
) -> tuple[str, list[dict[str, str]], dict[str, Any] | None] | None:
    raw_target = ""
    matched_kind = ""

    current_match = OPEN_LOCAL_PROJECT_CURRENT_RE.match(text)
    if current_match:
        matched_kind = str(current_match.group("kind") or "").strip().lower()
    else:
        targeted_match = OPEN_LOCAL_PROJECT_TARGET_RE.match(text)
        if targeted_match:
            raw_target = str(targeted_match.group("target") or "").strip()
            matched_kind = str(targeted_match.group("kind") or "").strip().lower()
        else:
            stripped_text = str(text or "").strip()
            if not stripped_text.lower().startswith("open "):
                return None
            raw_target = stripped_text[5:].strip()
            direct_path = _resolve_existing_local_path(raw_target)
            if direct_path is None:
                return None
            matched_kind = "folder"

    resolved_path = _resolve_local_project_path(
        raw_target,
        working_context=working_context,
        session_state=session_state,
    )
    if resolved_path is None:
        target_label = raw_target or f"this {matched_kind or 'folder'}"
        workspace_path = ""
        paths = _candidate_local_project_paths(working_context, session_state)
        if paths:
            workspace_path = str(paths[0])
        lines = [
            f"I can open a local {matched_kind or 'folder'}, but I need a concrete path or a clearly identified current workspace for '{target_label}'.",
        ]
        if workspace_path:
            lines.append("If you mean the current workspace, try: open this repo")
            lines.append(f"Current workspace: {workspace_path}")
        lines.extend(
            [
                "",
                "Try next:",
                "- open this repo",
                r"- open folder C:\path\to\your\project",
                "- audit this repo",
            ]
        )
        suggestions = [
            {"label": "Open this repo", "command": "open this repo"},
            {"label": "Audit this repo", "command": "audit this repo"},
            {"label": "Open documents", "command": "open documents"},
        ]
        return "\n".join(lines), suggestions, None

    open_path = resolved_path if resolved_path.is_dir() else resolved_path.parent
    resource = str(open_path)
    message = (
        f"Open {resource}?\n"
        "This action needs confirmation.\n"
        "Reply 'yes' to proceed or 'no' to cancel."
    )
    suggestions = [
        {"label": "Open folder", "command": f"open {open_path}"},
        {"label": "Audit this repo", "command": "audit this repo"},
        {"label": "Explain this", "command": "explain this"},
    ]
    return message, suggestions, {"path": resource}


def _canonical_thread_reference(value: str) -> str:
    return str(value or "").strip().lower().rstrip(".?!")


def _parse_iso_datetime(raw: str) -> datetime | None:
    value = str(raw or "").strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.astimezone()
    return parsed


def _parse_clock_time(raw: str) -> tuple[int, int]:
    value = str(raw or "").strip().lower().replace(".", "")
    value = re.sub(r"(?<=\d)(am|pm)$", r" \1", value)
    for fmt in ("%I:%M %p", "%I %p", "%H:%M", "%H"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.hour, parsed.minute
        except ValueError:
            continue
    raise ValueError("I couldn't parse that time yet. Try forms like 8:00 am, 14:30, or 9 pm.")


def _parse_schedule_datetime(raw: str, *, recurrence: str) -> datetime:
    value = str(raw or "").strip().lower()
    explicit_today = value.startswith("today ")
    explicit_tomorrow = value.startswith("tomorrow ")
    if explicit_today:
        value = value[len("today "):].strip()
    elif explicit_tomorrow:
        value = value[len("tomorrow "):].strip()

    hour, minute = _parse_clock_time(value)
    now = _local_now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if recurrence == "daily":
        if target <= now:
            target = target + timedelta(days=1)
        return target

    if explicit_tomorrow:
        return target + timedelta(days=1)
    if explicit_today:
        if target <= now:
            raise ValueError("That time has already passed for today. Try 'tomorrow <time>' or a later time.")
        return target
    if target <= now:
        target = target + timedelta(days=1)
    return target


def _format_policy_clock_value(raw: str) -> str:
    value = str(raw or "").strip()
    if not value:
        return ""
    try:
        hour, minute = _parse_clock_time(value)
    except ValueError:
        return value
    rendered = _local_now().replace(hour=hour, minute=minute, second=0, microsecond=0).strftime("%I:%M %p")
    return rendered.lstrip("0")


def _compile_atomic_policy_template(schedule_kind: str, action_label: str, time_text: str) -> dict:
    normalized_schedule = str(schedule_kind or "").strip().lower()
    normalized_action = re.sub(r"\s+", " ", str(action_label or "").strip().lower())
    formatted_time = _format_policy_clock_value(time_text)
    if not formatted_time:
        raise ValueError("I couldn't parse that policy time yet. Try forms like 8:00 am, 14:30, or 9 pm.")

    hour, minute = _parse_clock_time(time_text)
    time_24h = f"{hour:02d}:{minute:02d}"

    action_map = {
        "calendar snapshot": {
            "capability_id": 57,
            "input": {"mode": "today"},
            "network_allowed": False,
            "title": "calendar snapshot",
        },
        "weather snapshot": {
            "capability_id": 55,
            "input": {},
            "network_allowed": True,
            "title": "weather snapshot",
        },
        "news snapshot": {
            "capability_id": 56,
            "input": {},
            "network_allowed": True,
            "title": "news snapshot",
        },
        "system status": {
            "capability_id": 32,
            "input": {},
            "network_allowed": False,
            "title": "system status",
        },
    }
    action_config = action_map.get(normalized_action)
    if action_config is None:
        raise ValueError("That policy action is not available in the Phase-6 foundation yet.")

    if normalized_schedule == "weekday":
        trigger = {
            "type": "time_weekly",
            "days": ["MO", "TU", "WE", "TH", "FR"],
            "time": time_24h,
        }
        label_prefix = "Weekday"
    else:
        trigger = {
            "type": "time_daily",
            "time": time_24h,
        }
        label_prefix = "Daily"

    envelope = {
        "max_runs_per_hour": 1,
        "max_runs_per_day": 1,
        "timeout_seconds": 30,
        "retry_budget": 0,
        "suspend_after_failures": 3,
        "network_allowed": bool(action_config["network_allowed"]),
    }

    return {
        "name": f"{label_prefix} {action_config['title']} at {formatted_time}",
        "created_by": "user",
        "enabled": False,
        "state": "draft",
        "trigger": trigger,
        "action": {
            "capability_id": int(action_config["capability_id"]),
            "input": dict(action_config["input"]),
        },
        "envelope": envelope,
    }


def _describe_policy_trigger(trigger: dict | None) -> str:
    payload = dict(trigger or {})
    trigger_type = str(payload.get("type") or "").strip().lower()
    if trigger_type == "time_weekly":
        return f"Weekdays at {_format_policy_clock_value(str(payload.get('time') or '')) or str(payload.get('time') or '').strip()}"
    if trigger_type == "time_daily":
        return f"Daily at {_format_policy_clock_value(str(payload.get('time') or '')) or str(payload.get('time') or '').strip()}"
    if trigger_type == "time_once":
        return str(payload.get("at") or "").strip()
    if trigger_type == "calendar_event":
        return f"Calendar event offset {int(payload.get('offset_minutes') or 0)} minute(s)"
    if trigger_type == "device_event":
        return f"Device event {str(payload.get('event_key') or '').strip()}"
    return "Unknown trigger"


def _describe_policy_action(action: dict | None) -> str:
    payload = dict(action or {})
    capability_id = int(payload.get("capability_id") or 0)
    if capability_id == 57:
        return "Calendar snapshot"
    if capability_id == 55:
        return "Weather snapshot"
    if capability_id == 56:
        return "News snapshot"
    if capability_id == 32:
        return "System status"
    return f"Capability {capability_id}"


def _policy_yes_no_label(value: bool) -> str:
    return "yes" if bool(value) else "no"


def _render_policy_overview_message(snapshot: dict | None) -> str:
    payload = dict(snapshot or {})
    items = list(payload.get("items") or [])
    readiness = dict(payload.get("policy_capability_readiness") or {})
    lines = ["Policy Drafts", ""]
    lines.append(str(payload.get("summary") or "No policy drafts yet.").strip())
    lines.append(
        "Activity: "
        f"{int(payload.get('simulation_count') or 0)} simulation(s) · "
        f"{int(payload.get('manual_run_count') or 0)} manual run(s)"
    )

    if items:
        lines.append("")
        lines.append("Current drafts")
        for item in items[:5]:
            policy_id = str(item.get("policy_id") or "").strip()
            title = str(item.get("name") or "").strip()
            trigger = _describe_policy_trigger(item.get("trigger"))
            lines.append(
                f"- {policy_id}: {title} ({trigger}) | "
                f"sim {int(item.get('simulation_count') or 0)} | "
                f"runs {int(item.get('manual_run_count') or 0)}"
            )

    note = str(payload.get("inspectability_note") or "").strip()
    if note:
        lines.append("")
        lines.append(note)

    readiness_summary = str(readiness.get("summary") or "").strip()
    if readiness_summary:
        lines.extend(
            [
                "",
                "Delegation readiness",
                readiness_summary,
                f"Current delegated authority limit: {str(readiness.get('current_authority_limit') or 'unknown').strip() or 'unknown'}",
            ]
        )

    lines.extend(
        [
            "",
            "Try next:",
            "- policy create weekday calendar snapshot at 8:00 am",
            "- policy create daily weather snapshot at 7:30 am",
            "- policy create weekday system status at 8:00 am",
            "- policy show <id>",
            "- policy simulate <id>",
            "- policy run <id> once",
            "- policy delete <id> confirm",
            "- what can policies run",
        ]
    )
    return "\n".join(lines)


def _render_policy_detail_message(item: dict | None) -> str:
    payload = dict(item or {})
    validation = dict(payload.get("last_validation") or {})
    topology = dict(payload.get("topology") or {})
    warnings = list(validation.get("warnings") or [])
    lines = [
        "Policy Draft",
        "",
        f"ID: {str(payload.get('policy_id') or '').strip()}",
        f"Name: {str(payload.get('name') or '').strip()}",
        f"State: {str(payload.get('state') or 'draft').strip()}",
        f"Trigger: {_describe_policy_trigger(payload.get('trigger'))}",
        f"Action: {_describe_policy_action(payload.get('action'))}",
        f"Created by: {str(payload.get('created_by') or 'user').strip()}",
        "",
        "Envelope",
        (
            f"- max {int(dict(payload.get('envelope') or {}).get('max_runs_per_hour') or 0)} per hour | "
            f"{int(dict(payload.get('envelope') or {}).get('max_runs_per_day') or 0)} per day"
        ),
        (
            f"- timeout {int(dict(payload.get('envelope') or {}).get('timeout_seconds') or 0)}s | "
            f"retries {int(dict(payload.get('envelope') or {}).get('retry_budget') or 0)} | "
            f"suspend after {int(dict(payload.get('envelope') or {}).get('suspend_after_failures') or 0)} failures"
        ),
        f"- network allowed: {'yes' if bool(dict(payload.get('envelope') or {}).get('network_allowed')) else 'no'}",
        "",
        "Foundation note",
        "This policy is stored as a disabled draft. Manual simulation and one-shot review runs are available. Trigger execution is not active yet.",
    ]

    if topology:
        lines.extend(
            [
                "",
                "Delegation fit",
                f"- authority class: {str(topology.get('authority_class') or 'unknown').strip()}",
                f"- delegation class: {str(topology.get('delegation_class') or 'observational').strip()}",
                f"- policy delegatable: {'yes' if bool(topology.get('policy_delegatable')) else 'no'}",
                f"- within current limit: {'yes' if bool(topology.get('within_current_limit')) else 'no'}",
                f"- network required: {'yes' if bool(topology.get('network_required')) else 'no'}",
            ]
        )
        topology_note = str(topology.get("envelope_notes") or topology.get("why") or "").strip()
        if topology_note:
            lines.append(f"- note: {topology_note}")

    if warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"- {str(warning).strip()}" for warning in warnings if str(warning).strip())

    simulation_count = int(payload.get("simulation_count") or 0)
    manual_run_count = int(payload.get("manual_run_count") or 0)
    last_simulated_at = str(payload.get("last_simulated_at") or "").strip()
    last_manual_run_at = str(payload.get("last_manual_run_at") or "").strip()
    if simulation_count or manual_run_count:
        lines.extend(
            [
                "",
                "Review activity",
                f"- simulations: {simulation_count}",
                f"- manual runs: {manual_run_count}",
            ]
        )
        if last_simulated_at:
            lines.append(f"- last simulated: {last_simulated_at}")
        if last_manual_run_at:
            lines.append(f"- last manual run: {last_manual_run_at}")

    policy_id = str(payload.get("policy_id") or "").strip()
    lines.extend(
        [
            "",
            "Try next:",
            "- policy overview",
            f"- policy simulate {policy_id}",
            f"- policy run {policy_id} once",
            f"- policy delete {policy_id} confirm",
        ]
    )
    return "\n".join(lines)


def _render_policy_simulation_message(decision: dict | None) -> str:
    payload = dict(decision or {})
    risk_summary = dict(payload.get("risk_summary") or {})
    lines = [
        "Policy Simulation",
        "",
        f"Policy ID: {str(payload.get('policy_id') or '').strip()}",
        f"Trigger: {str(payload.get('trigger') or '').strip()}",
        f"Action: {str(payload.get('action') or '').strip()}",
        "",
        "Delegation Review",
        f"- capability: {str(payload.get('capability_name') or payload.get('action') or 'unknown').strip()}",
        f"- capability class: {str(payload.get('capability_class') or 'unknown').strip()}",
        f"- delegation class: {str(payload.get('delegation_class') or 'observational').strip()}",
        f"- policy delegatable: {_policy_yes_no_label(bool(payload.get('policy_delegatable')))}",
        f"- network required: {_policy_yes_no_label(bool(payload.get('network_required')))}",
        f"- estimated runtime: {str(payload.get('estimated_runtime') or 'unknown').strip()}",
        f"- envelope: {str(payload.get('envelope_summary') or 'unknown').strip()}",
        f"- current authority limit: {str(payload.get('current_authority_limit') or 'unknown').strip()}",
        "",
        "Risk Summary",
        f"- local system impact: {str(risk_summary.get('local_system_impact') or payload.get('local_system_impact') or 'none').strip()}",
        f"- network activity: {str(risk_summary.get('network_activity') or payload.get('network_activity') or 'none').strip()}",
        f"- persistent change: {str(risk_summary.get('persistent_change') or payload.get('persistent_changes') or 'none').strip()}",
        f"- external effect: {str(risk_summary.get('external_effect') or payload.get('external_effects') or 'none').strip()}",
        "",
        "Governor Verdict",
        str(payload.get("governor_verdict") or "").strip(),
        f"Readiness: {str(payload.get('readiness_label') or '').strip()}",
    ]

    reasoning = [str(item).strip() for item in list(payload.get("reasoning") or []) if str(item).strip()]
    blocked_reason = str(payload.get("blocked_reason") or "").strip()
    if blocked_reason:
        lines.append(f"Blocked reason: {blocked_reason}")
    if reasoning:
        lines.extend(["", "Reasoning"])
        lines.extend(f"- {item}" for item in reasoning)

    policy_id = str(payload.get("policy_id") or "").strip()
    lines.extend(
        [
            "",
            "Try next:",
            f"- policy show {policy_id}",
            f"- policy run {policy_id} once",
            "- policy overview",
        ]
    )
    return "\n".join(lines)


def _render_policy_run_message(decision: dict | None, action_result: object | None) -> str:
    payload = dict(decision or {})
    result_data = _action_result_payload(action_result)
    lines = [
        "Policy Manual Run",
        "",
        f"Policy ID: {str(payload.get('policy_id') or '').strip()}",
        f"Trigger: {str(payload.get('trigger') or '').strip()}",
        f"Action: {str(payload.get('action') or '').strip()}",
        "",
        "Governor Verdict",
        str(payload.get("governor_verdict") or "").strip(),
        f"Readiness: {str(payload.get('readiness_label') or '').strip()}",
        "",
        "Run Result",
        f"- success: {_policy_yes_no_label(bool(getattr(action_result, 'success', False)))}",
        f"- authority class: {str(getattr(action_result, 'authority_class', 'read_only') or 'read_only').strip()}",
        f"- external effect: {_policy_yes_no_label(bool(getattr(action_result, 'external_effect', False)))}",
        f"- reversible: {_policy_yes_no_label(bool(getattr(action_result, 'reversible', True)))}",
        f"- status: {str(getattr(action_result, 'status', 'unknown') or 'unknown').strip()}",
        f"- message: {_action_result_message(action_result)}",
    ]

    request_id = str(getattr(action_result, "request_id", "") or "").strip()
    if request_id:
        lines.append(f"- request id: {request_id}")
    outcome_reason = str(getattr(action_result, "outcome_reason", "") or "").strip()
    if outcome_reason:
        lines.append(f"- outcome reason: {outcome_reason}")

    reasoning = [str(item).strip() for item in list(payload.get("reasoning") or []) if str(item).strip()]
    if reasoning:
        lines.extend(["", "Delegation Review"])
        lines.extend(f"- {item}" for item in reasoning)

    policy_id = str(payload.get("policy_id") or "").strip()
    lines.extend(
        [
            "",
            "Try next:",
            f"- policy simulate {policy_id}",
            f"- policy show {policy_id}",
            "- policy overview",
        ]
    )
    return "\n".join(lines)


def _build_policy_overview_widget(snapshot: dict | None) -> dict[str, Any]:
    payload = dict(snapshot or {})
    items = []
    for item in list(payload.get("items") or [])[:8]:
        entry = dict(item or {})
        items.append(
            {
                "policy_id": str(entry.get("policy_id") or "").strip(),
                "name": str(entry.get("name") or "").strip(),
                "state": str(entry.get("state") or "draft").strip(),
                "trigger_summary": _describe_policy_trigger(entry.get("trigger")),
                "action_summary": _describe_policy_action(entry.get("action")),
                "simulation_count": int(entry.get("simulation_count") or 0),
                "manual_run_count": int(entry.get("manual_run_count") or 0),
                "last_simulated_at": str(entry.get("last_simulated_at") or "").strip(),
                "last_manual_run_at": str(entry.get("last_manual_run_at") or "").strip(),
            }
        )

    return {
        "type": "policy_overview",
        "summary": str(payload.get("summary") or "No policy drafts yet.").strip(),
        "active_count": int(payload.get("active_count") or 0),
        "draft_count": int(payload.get("draft_count") or 0),
        "disabled_count": int(payload.get("disabled_count") or 0),
        "deleted_count": int(payload.get("deleted_count") or 0),
        "simulation_count": int(payload.get("simulation_count") or 0),
        "manual_run_count": int(payload.get("manual_run_count") or 0),
        "items": items,
        "inspectability_note": str(payload.get("inspectability_note") or "").strip(),
        "review_mode": "manual_review_only",
        "policy_capability_readiness": dict(payload.get("policy_capability_readiness") or {}),
    }


def _build_policy_item_widget(item: dict | None) -> dict[str, Any]:
    payload = dict(item or {})
    envelope = dict(payload.get("envelope") or {})
    validation = dict(payload.get("last_validation") or {})
    topology_snapshot = _build_policy_capability_readiness_snapshot()
    action_capability_id = int(dict(payload.get("action") or {}).get("capability_id") or 0)
    topology_item = {}
    for collection_name in ("safe_now", "allowed_later", "manual_only"):
        for candidate in list(topology_snapshot.get(collection_name) or []):
            if str(candidate.get("capability_id") or "").strip() == str(action_capability_id):
                topology_item = dict(candidate)
                topology_item["within_current_limit"] = collection_name == "safe_now"
                break
        if topology_item:
            break
    return {
        "type": "policy_item",
        "item": {
            "policy_id": str(payload.get("policy_id") or "").strip(),
            "name": str(payload.get("name") or "").strip(),
            "state": str(payload.get("state") or "draft").strip(),
            "created_by": str(payload.get("created_by") or "user").strip(),
            "created_at": str(payload.get("created_at") or "").strip(),
            "updated_at": str(payload.get("updated_at") or "").strip(),
            "trigger_summary": _describe_policy_trigger(payload.get("trigger")),
            "action_summary": _describe_policy_action(payload.get("action")),
            "trigger": dict(payload.get("trigger") or {}),
            "action": dict(payload.get("action") or {}),
            "envelope": {
                "max_runs_per_hour": int(envelope.get("max_runs_per_hour") or 0),
                "max_runs_per_day": int(envelope.get("max_runs_per_day") or 0),
                "timeout_seconds": int(envelope.get("timeout_seconds") or 0),
                "retry_budget": int(envelope.get("retry_budget") or 0),
                "suspend_after_failures": int(envelope.get("suspend_after_failures") or 0),
                "network_allowed": bool(envelope.get("network_allowed")),
            },
            "simulation_count": int(payload.get("simulation_count") or 0),
            "manual_run_count": int(payload.get("manual_run_count") or 0),
            "last_simulated_at": str(payload.get("last_simulated_at") or "").strip(),
            "last_manual_run_at": str(payload.get("last_manual_run_at") or "").strip(),
            "warnings": [str(w).strip() for w in list(validation.get("warnings") or []) if str(w).strip()],
            "topology": topology_item,
            "foundation_note": (
                "Stored as a disabled draft. Simulation and one-shot manual review runs are available, but trigger execution is not active."
            ),
        },
    }


def _build_policy_simulation_widget(decision: dict | None) -> dict[str, Any]:
    payload = dict(decision or {})
    return {
        "type": "policy_simulation",
        "data": payload,
        "policy_id": str(payload.get("policy_id") or "").strip(),
    }


def _build_policy_run_widget(decision: dict | None, action_result: object | None) -> dict[str, Any]:
    payload = dict(decision or {})
    result_payload = _action_result_payload(action_result)
    return {
        "type": "policy_run",
        "policy_id": str(payload.get("policy_id") or "").strip(),
        "decision": payload,
        "result": {
            "success": bool(getattr(action_result, "success", False)),
            "message": _action_result_message(action_result),
            "request_id": str(getattr(action_result, "request_id", "") or "").strip(),
            "authority_class": str(getattr(action_result, "authority_class", "read_only") or "read_only").strip(),
            "external_effect": bool(getattr(action_result, "external_effect", False)),
            "reversible": bool(getattr(action_result, "reversible", True)),
            "status": str(getattr(action_result, "status", "") or "").strip(),
            "outcome_reason": str(getattr(action_result, "outcome_reason", "") or "").strip(),
            "structured_data": dict(result_payload.get("structured_data") or {}),
        },
    }


def _build_notification_note(snapshot: dict | None) -> str:
    payload = dict(snapshot or {})
    parts = [
        str(payload.get("inspectability_note") or "").strip(),
        str(payload.get("policy_summary") or "").strip(),
        str(payload.get("delivery_note") or "").strip(),
    ]
    return " ".join(part for part in parts if part)


def _notification_governor_reason_note(reason: str) -> str:
    lowered = str(reason or "").strip().lower()
    if lowered == "action_pending":
        return "Held while another governed action is still running."
    if lowered == "execution_boundary_closed":
        return "Held because the execution boundary is not accepting new work right now."
    return "Held by governor policy checks."


def _build_notification_schedule_widget(snapshot: dict | None) -> dict:
    payload = dict(snapshot or {})
    due_items: list[dict] = []
    for item in list(payload.get("due_items") or [])[:5]:
        row = dict(item or {})
        row["next_run_label"] = _format_local_schedule_time(_parse_iso_datetime(str(row.get("next_run_at") or "")))
        due_items.append(row)

    upcoming_items: list[dict] = []
    for item in list(payload.get("upcoming_items") or [])[:5]:
        row = dict(item or {})
        row["next_run_label"] = _format_local_schedule_time(_parse_iso_datetime(str(row.get("next_run_at") or "")))
        upcoming_items.append(row)

    return {
        "type": "notification_schedule",
        "summary": str(payload.get("summary") or "No schedules yet.").strip(),
        "active_count": int(payload.get("active_count") or 0),
        "due_count": int(payload.get("due_count") or 0),
        "upcoming_count": int(payload.get("upcoming_count") or 0),
        "suppressed_due_count": int(payload.get("suppressed_due_count") or 0),
        "due_items": due_items,
        "upcoming_items": upcoming_items,
        "policy_summary": str(payload.get("policy_summary") or "").strip(),
        "delivery_note": str(payload.get("delivery_note") or "").strip(),
        "inspectability_note": _build_notification_note(payload),
    }


def _render_notification_schedule_message(snapshot: dict | None) -> str:
    payload = dict(snapshot or {})
    due_items = list(payload.get("due_items") or [])
    upcoming_items = list(payload.get("upcoming_items") or [])
    lines = ["Scheduled Updates", ""]
    lines.append(str(payload.get("summary") or "No schedules yet.").strip())

    if due_items:
        lines.append("")
        lines.append("Due now")
        for item in due_items[:4]:
            next_run = _format_local_schedule_time(_parse_iso_datetime(str(item.get("next_run_at") or "")))
            title = str(item.get("title") or "").strip()
            lines.append(f"- {title} ({next_run or 'due'})")

    if upcoming_items:
        lines.append("")
        lines.append("Upcoming")
        for item in upcoming_items[:4]:
            next_run = _format_local_schedule_time(_parse_iso_datetime(str(item.get("next_run_at") or "")))
            title = str(item.get("title") or "").strip()
            lines.append(f"- {title} ({next_run})")

    policy_summary = str(payload.get("policy_summary") or "").strip()
    if policy_summary:
        lines.append("")
        lines.append("Policy")
        lines.append(policy_summary)

    delivery_note = str(payload.get("delivery_note") or "").strip()
    if delivery_note:
        lines.append("")
        lines.append("Delivery")
        lines.append(delivery_note)

    lines.extend(
        [
            "",
            "Try next:",
            "- schedule daily brief at 8:00 am",
            "- remind me at 2:00 pm to review deployment issue",
            "- notification settings",
            "- set quiet hours from 10:00 pm to 7:00 am",
            "- set notification rate limit 2 per hour",
            "- show schedules",
        ]
    )
    return "\n".join(lines)


def _render_notification_settings_message(snapshot: dict | None) -> str:
    payload = dict(snapshot or {})
    policy = dict(payload.get("policy") or {})
    quiet_label = str(policy.get("quiet_hours_label") or "Off").strip() or "Off"
    rate_limit = int(policy.get("max_deliveries_per_hour") or 0)
    delivered_last_hour = int(policy.get("deliveries_last_hour") or 0)

    lines = ["Notification Settings", ""]
    lines.append(f"Quiet hours: {quiet_label}")
    lines.append(f"Rate limit: {rate_limit} per hour")
    lines.append(f"Delivered last hour: {delivered_last_hour}")

    lines.extend(
        [
            "",
            "Try next:",
            "- set quiet hours from 10:00 pm to 7:00 am",
            "- clear quiet hours",
            "- set notification rate limit 2 per hour",
            "- show schedules",
        ]
    )
    return "\n".join(lines)


def _process_due_notification_delivery(
    governor: Governor,
    store: NotificationScheduleStore,
    snapshot: dict | None,
) -> dict:
    payload = dict(snapshot or {})
    current = _local_now()
    visible_due_items: list[dict] = []
    suppressed_counts: dict[str, int] = {}

    for item in list(payload.get("due_items") or []):
        schedule_id = str(item.get("id") or "").strip()
        next_run_at = str(item.get("next_run_at") or "").strip()
        last_surface_at = str(item.get("last_surface_at") or "").strip()
        if not schedule_id:
            continue

        if last_surface_at and next_run_at and last_surface_at >= next_run_at:
            visible_due_items.append(dict(item))
            continue

        try:
            policy_result = store.evaluate_delivery_policy(schedule_id, now=current)
        except KeyError:
            continue

        if str(policy_result.get("reason") or "") == "already_surfaced":
            visible_due_items.append(dict(item))
            continue

        _log_ledger_event(
            governor,
            "NOTIFICATION_DELIVERY_ATTEMPTED",
            {
                "schedule_id": schedule_id,
                "kind": str(item.get("kind") or ""),
                "recurrence": str(item.get("recurrence") or ""),
            },
        )
        try:
            store.record_delivery_attempt(schedule_id, now=current)
        except Exception:
            continue

        governor_allowed, governor_reason = governor.allow_notification_delivery(
            {
                "schedule_id": schedule_id,
                "kind": str(item.get("kind") or ""),
                "title": str(item.get("title") or ""),
            }
        )

        if not governor_allowed:
            note = _notification_governor_reason_note(governor_reason)
            try:
                store.record_delivery_outcome(
                    schedule_id,
                    outcome="suppressed_governor_policy",
                    note=note,
                    now=current,
                )
            except Exception:
                pass
            suppressed_counts["governor_policy"] = suppressed_counts.get("governor_policy", 0) + 1
            _log_ledger_event(
                governor,
                "NOTIFICATION_DELIVERY_SUPPRESSED",
                {
                    "schedule_id": schedule_id,
                    "kind": str(item.get("kind") or ""),
                    "reason": "governor_policy",
                    "detail": governor_reason,
                },
            )
            continue

        if not bool(policy_result.get("allowed")):
            reason = str(policy_result.get("reason") or "suppressed").strip() or "suppressed"
            note = str(policy_result.get("note") or "").strip()
            try:
                store.record_delivery_outcome(
                    schedule_id,
                    outcome=f"suppressed_{reason}",
                    note=note,
                    now=current,
                )
            except Exception:
                pass
            suppressed_counts[reason] = suppressed_counts.get(reason, 0) + 1
            _log_ledger_event(
                governor,
                "NOTIFICATION_DELIVERY_SUPPRESSED",
                {
                    "schedule_id": schedule_id,
                    "kind": str(item.get("kind") or ""),
                    "reason": reason,
                },
            )
            continue

        try:
            store.record_delivery_outcome(
                schedule_id,
                outcome="delivered",
                note="Notification surfaced in the scheduled-updates widget.",
                now=current,
                surfaced=True,
            )
        except Exception:
            continue
        _log_ledger_event(
            governor,
            "NOTIFICATION_DELIVERY_DUE",
            {
                "schedule_id": schedule_id,
                "kind": str(item.get("kind") or ""),
                    "recurrence": str(item.get("recurrence") or ""),
            },
        )
        _log_ledger_event(
            governor,
            "NOTIFICATION_DELIVERY_COMPLETED",
            {
                "schedule_id": schedule_id,
                "kind": str(item.get("kind") or ""),
                "recurrence": str(item.get("recurrence") or ""),
            },
        )
        delivered_item = dict(item)
        delivered_item["last_surface_at"] = current.isoformat()
        delivered_item["last_delivery_outcome"] = "delivered"
        visible_due_items.append(delivered_item)

    refreshed = store.summarize(now=current)
    refreshed["due_items"] = visible_due_items[:5]
    refreshed["due_count"] = len(visible_due_items)
    refreshed["suppressed_due_count"] = sum(suppressed_counts.values())
    policy_summary = str(refreshed.get("policy_summary") or "").strip()
    delivery_parts: list[str] = []
    if suppressed_counts.get("quiet_hours"):
        delivery_parts.append(
            f"{suppressed_counts['quiet_hours']} due update{'s are' if suppressed_counts['quiet_hours'] != 1 else ' is'} held by quiet hours."
        )
    if suppressed_counts.get("rate_limit"):
        delivery_parts.append(
            f"{suppressed_counts['rate_limit']} due update{'s are' if suppressed_counts['rate_limit'] != 1 else ' is'} held by the rate limit."
        )
    if suppressed_counts.get("governor_policy"):
        delivery_parts.append(
            f"{suppressed_counts['governor_policy']} due update{'s are' if suppressed_counts['governor_policy'] != 1 else ' is'} waiting for governor policy clearance."
        )
    refreshed["delivery_note"] = " ".join(part for part in delivery_parts if part)
    if refreshed.get("active_count"):
        refreshed["summary"] = (
            f"{len(visible_due_items)} surfaced due | "
            f"{int(refreshed.get('suppressed_due_count') or 0)} held | "
            f"{int(refreshed.get('upcoming_count') or 0)} upcoming"
        )
    else:
        refreshed["summary"] = "No schedules yet. Create one explicitly when you want Nova to remind you."
    refreshed["policy_summary"] = policy_summary
    refreshed["inspectability_note"] = "Schedules are explicit, inspectable, cancellable, and policy-bound."
    return refreshed


async def send_notification_schedule_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    snapshot: dict | None = None,
) -> None:
    payload = dict(snapshot or {})
    if not payload:
        payload = NotificationScheduleStore().summarize()
    session_state["last_schedule_overview"] = payload
    await ws_send(ws, _build_notification_schedule_widget(payload))


def _build_pattern_review_widget(snapshot: dict | None) -> dict:
    payload = dict(snapshot or {})
    return {
        "type": "pattern_review",
        "summary": str(payload.get("summary") or "").strip(),
        "opt_in_enabled": bool(payload.get("opt_in_enabled")),
        "active_count": int(payload.get("active_count") or 0),
        "last_generated_at": str(payload.get("last_generated_at") or ""),
        "proposals": [dict(item or {}) for item in list(payload.get("proposals") or [])[:6]],
        "recent_decisions": [dict(item or {}) for item in list(payload.get("recent_decisions") or [])[:6]],
        "inspectability_note": (
            str(payload.get("inspectability_note") or "").strip()
            or "Pattern review is opt-in, advisory, and discardable."
        ),
    }


def _render_pattern_review_message(snapshot: dict | None) -> str:
    payload = dict(snapshot or {})
    lines = ["Pattern Review", ""]
    lines.append(str(payload.get("summary") or "Pattern review is off.").strip())

    proposals = list(payload.get("proposals") or [])
    if proposals:
        lines.append("")
        lines.append("Review queue")
        for item in proposals[:4]:
            title = str(item.get("title") or "").strip()
            summary = str(item.get("summary") or "").strip()
            linked = [str(name).strip() for name in list(item.get("linked_threads") or []) if str(name).strip()]
            evidence = [str(row).strip() for row in list(item.get("evidence") or []) if str(row).strip()]
            if title:
                lines.append(f"- {title}")
            if summary:
                lines.append(f"  {summary}")
            if linked:
                lines.append(f"  Threads: {', '.join(linked[:3])}")
            if evidence:
                lines.append(f"  Evidence: {evidence[0]}")
    else:
        lines.append("")
        lines.append("No active pattern proposals are waiting for review.")

    lines.extend(
        [
            "",
            "Try next:",
            "- pattern opt in",
            "- review patterns",
            "- pattern status",
        ]
    )
    return "\n".join(lines)


async def send_pattern_review_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    snapshot: dict | None = None,
) -> None:
    payload = dict(snapshot or {})
    if not payload:
        payload = PatternReviewStore().snapshot()
    session_state["last_pattern_review"] = payload
    await ws_send(ws, _build_pattern_review_widget(payload))

# -------------------------------------------------
# API Routers
# -------------------------------------------------
app.include_router(build_audit_router(sys.modules[__name__]))
app.include_router(build_bridge_router(sys.modules[__name__]))
app.include_router(build_connections_router())
app.include_router(build_memory_router(sys.modules[__name__]))
app.include_router(build_openclaw_agent_router(sys.modules[__name__]))
app.include_router(build_profile_router(sys.modules[__name__]))
app.include_router(build_settings_router(sys.modules[__name__]))

# -------------------------------------------------
# WebSocket Utilities
# -------------------------------------------------
async def ws_send(ws: WebSocket, payload: dict) -> None:
    await ws.send_text(json.dumps(payload))


async def send_thread_map_widget(
    ws: WebSocket,
    project_threads: ProjectThreadStore,
    session_state: dict,
) -> dict[str, Any]:
    widget = _enrich_thread_map_widget_memory(project_threads.render_map_widget())
    threads = list(widget.get("threads") or [])
    previous_map = dict(session_state.get("thread_map_last") or {})
    snapshot: dict[str, dict] = {}
    enriched_threads: list[dict] = []
    for item in threads:
        row = dict(item or {})
        key = str(row.get("key") or "").strip().lower()
        previous = previous_map.get(key) if key else None
        row["change_summary"] = _compute_thread_change_summary(row, previous if isinstance(previous, dict) else None)
        if key:
            snapshot[key] = {
                "latest_decision": str(row.get("latest_decision") or ""),
                "latest_blocker": str(row.get("latest_blocker") or ""),
                "memory_count": int(row.get("memory_count") or 0),
                "last_memory_updated_at": str(row.get("last_memory_updated_at") or ""),
                "updated_at": str(row.get("updated_at") or ""),
            }
        enriched_threads.append(row)
    widget["threads"] = enriched_threads
    session_state["thread_map_last"] = snapshot
    await ws_send(ws, widget)
    return widget


async def send_memory_overview_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    overview: dict | None = None,
) -> None:
    payload = dict(overview or {})
    if not payload:
        try:
            from src.memory.governed_memory_store import GovernedMemoryStore

            payload = GovernedMemoryStore().summarize_overview()
        except Exception:
            payload = {}
    session_state["last_memory_overview"] = payload
    await ws_send(ws, _build_memory_overview_widget(payload))


async def send_memory_list_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    items: list[dict] | None = None,
    filters: dict | None = None,
) -> None:
    payload = _build_memory_list_widget(items or [], filters=filters)
    session_state["last_memory_list"] = payload
    await ws_send(ws, payload)


async def send_memory_item_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    item: dict | None = None,
) -> None:
    payload = _build_memory_item_widget(item or {})
    item_id = str(dict(item or {}).get("id") or "").strip()
    if item_id:
        session_state["last_memory_item_id"] = item_id
    session_state["last_memory_item"] = payload.get("item") or {}
    await ws_send(ws, payload)


async def send_policy_overview_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    snapshot: dict | None = None,
) -> dict[str, Any]:
    payload = dict(snapshot or {})
    if not payload:
        try:
            payload = AtomicPolicyStore().overview()
        except Exception:
            payload = {}
    payload.setdefault("policy_capability_readiness", _build_policy_capability_readiness_snapshot())
    widget = _build_policy_overview_widget(payload)
    session_state["last_policy_overview"] = widget
    await ws_send(ws, widget)
    return widget


async def send_policy_item_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    item: dict | None = None,
) -> dict[str, Any]:
    widget = _build_policy_item_widget(item or {})
    policy_id = str(dict(item or {}).get("policy_id") or "").strip()
    if policy_id:
        session_state["last_policy_item_id"] = policy_id
    session_state["last_policy_item"] = widget
    await ws_send(ws, widget)
    return widget


async def send_policy_simulation_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    decision: dict | None = None,
) -> dict[str, Any]:
    widget = _build_policy_simulation_widget(decision or {})
    session_state["last_policy_simulation"] = widget
    await ws_send(ws, widget)
    return widget


async def send_policy_run_widget(
    ws: WebSocket,
    session_state: dict,
    *,
    decision: dict | None = None,
    action_result: object | None = None,
) -> dict[str, Any]:
    widget = _build_policy_run_widget(decision or {}, action_result)
    session_state["last_policy_run"] = widget
    await ws_send(ws, widget)
    return widget


async def send_workspace_home_widget(
    ws: WebSocket,
    session_state: dict,
    project_threads: ProjectThreadStore,
) -> dict[str, object]:
    payload = _build_workspace_home_widget(
        session_state=session_state,
        project_threads=project_threads,
    )
    session_state["last_workspace_home"] = payload
    await ws_send(ws, payload)
    return payload


async def send_operational_context_widget(
    ws: WebSocket,
    session_state: dict,
    project_threads: ProjectThreadStore,
) -> dict[str, Any]:
    payload = build_operational_context_widget(
        session_state=session_state,
        working_context_snapshot=dict(session_state.get("working_context") or {}),
        project_threads=project_threads,
        trust_snapshot=_build_trust_review_snapshot(),
    )
    session_state["last_operational_context"] = payload
    _log_ledger_event(
        RUNTIME_GOVERNOR,
        "OPERATIONAL_CONTEXT_VIEWED",
        {
            "session_id": str(session_state.get("session_id") or ""),
            "active_thread": str(payload.get("active_thread") or ""),
            "turn_count": int(session_state.get("turn_count") or 0),
        },
    )
    await ws_send(ws, payload)
    return payload


async def send_assistive_notices_widget(
    ws: WebSocket,
    session_state: dict,
    project_threads: ProjectThreadStore,
    *,
    explicit_request: bool = False,
    log_surface: bool = False,
) -> dict[str, Any]:
    payload = build_assistive_notices_widget(
        session_state=session_state,
        working_context_snapshot=dict(session_state.get("working_context") or {}),
        project_threads=project_threads,
        trust_snapshot=_build_trust_review_snapshot(),
        assistive_notice_mode=runtime_settings_store.assistive_notice_mode(),
        explicit_request=explicit_request,
    )
    if not explicit_request and int(payload.get("notice_count") or 0) > 0:
        session_state["assistive_notice_state"] = record_auto_surfaced_notices(
            session_state.get("assistive_notice_state"),
            notices=list(payload.get("notices") or []),
        )
    session_state["last_assistive_notices"] = payload
    if explicit_request:
        _log_ledger_event(
            RUNTIME_GOVERNOR,
            "ASSISTIVE_NOTICE_VIEWED",
            {
                "session_id": str(session_state.get("session_id") or ""),
                "assistive_notice_mode": str(payload.get("assistive_notice_mode") or ""),
                "notice_count": int(payload.get("notice_count") or 0),
            },
        )
    elif log_surface and int(payload.get("notice_count") or 0) > 0:
        _log_ledger_event(
            RUNTIME_GOVERNOR,
            "ASSISTIVE_NOTICE_SURFACED",
            {
                "session_id": str(session_state.get("session_id") or ""),
                "assistive_notice_mode": str(payload.get("assistive_notice_mode") or ""),
                "notice_count": int(payload.get("notice_count") or 0),
            },
        )
    await ws_send(ws, payload)
    return payload


def apply_assistive_notice_state_update(
    session_state: dict[str, Any],
    *,
    notice_id: str,
    status: str,
) -> tuple[bool, dict[str, Any] | None]:
    notice_id_clean = str(notice_id or "").strip()
    payload = dict(session_state.get("last_assistive_notices") or {})
    notices = [dict(item or {}) for item in list(payload.get("notices") or []) if isinstance(item, dict)]
    match = next((item for item in notices if str(item.get("id") or "").strip() == notice_id_clean), None)
    if match is None:
        return False, None
    session_state["assistive_notice_state"] = apply_assistive_notice_feedback(
        session_state.get("assistive_notice_state"),
        notice=match,
        status=status,
    )
    return True, match


async def send_thread_detail_widget(
    ws: WebSocket,
    session_state: dict,
    project_threads: ProjectThreadStore,
    *,
    thread_name: str,
) -> dict[str, Any] | None:
    found, detail = project_threads.get_thread_detail(thread_name)
    if not found:
        return None

    memory_items: list[dict] = []
    try:
        from src.memory.governed_memory_store import GovernedMemoryStore

        memory_items = GovernedMemoryStore().list_items(
            thread_name=str(detail.get("name") or ""),
            thread_key=str(detail.get("key") or ""),
            limit=5,
        )
    except Exception:
        memory_items = []

    payload = _build_thread_detail_widget(detail=detail, memory_items=memory_items)
    session_state["project_thread_active"] = str(detail.get("name") or "")
    session_state["last_thread_detail"] = payload
    await send_thread_map_widget(ws, project_threads, session_state)
    await ws_send(ws, payload)
    return payload

async def send_chat_message(
    ws: WebSocket,
    text: str,
    message_id: Optional[str] = None,
    confidence: Optional[str] = None,
    suggested_actions: Optional[list[dict[str, str]]] = None,
    apply_personality: bool = True,
    tone_domain: str = "general",
) -> str:
    presented = str(text or "").strip()
    if apply_personality:
        presented = conversation_personality_agent.present(presented, domain=tone_domain)
    if not presented and text:
        presented = str(text).strip()
    payload = {"type": "chat", "message": presented}
    if message_id is not None:
        payload["message_id"] = message_id
    if confidence:
        payload["confidence"] = confidence
    if suggested_actions:
        payload["suggested_actions"] = suggested_actions
    await ws_send(ws, payload)
    return presented

async def send_chat_done(ws: WebSocket) -> None:
    await ws_send(ws, {"type": "chat_done"})

async def send_widget_message(
    ws: WebSocket,
    msg_type: str,
    text: str,
    data: Optional[dict] = None
) -> None:
    if msg_type == "news" and isinstance(data, dict) and "items" in data:
        await ws_send(
            ws,
            {
                "type": "news",
                "items": data.get("items", []),
                "summary": data.get("summary", ""),
                "categories": data.get("categories", {}),
            },
        )
        return
    if msg_type == "calendar" and isinstance(data, dict):
        await ws_send(
            ws,
            {
                "type": "calendar",
                "summary": data.get("summary", ""),
                "events": data.get("events", []),
            },
        )
        return
    payload = {"type": msg_type, "message": text}
    if msg_type == "weather" and isinstance(data, dict):
        payload["data"] = data
    await ws_send(ws, payload)


async def send_trust_status(ws: WebSocket, trust_status: dict) -> None:
    payload = normalize_trust_status(trust_status)
    cached_snapshot = _get_cached_trust_review_snapshot()
    if cached_snapshot:
        payload.update(cached_snapshot)
    await ws_send(ws, {"type": "trust_status", "data": payload})
    if not cached_snapshot:
        await _maybe_send_trust_review_snapshot(ws, trust_status)


async def send_token_budget_update(ws: WebSocket, action_result: object | None = None) -> None:
    """Emit a token_budget_update WebSocket event after a budget-gated action completes.

    Reads the budget snapshot from action_result.data if present (set by governor for
    budget-gated caps), otherwise falls back to a fresh provider_usage_store snapshot.
    """
    try:
        from src.usage.provider_usage_store import provider_usage_store

        data = getattr(action_result, "data", None) or {}
        budget_state = str(data.get("budget_state") or "").strip()
        if budget_state:
            snapshot = {
                "budget_state": budget_state,
                "budget_remaining_tokens": int(data.get("budget_remaining_tokens") or 0),
                "budget_state_label": str(data.get("budget_state_label") or "Normal"),
                "budget_warning": bool(data.get("budget_warning", False)),
            }
        else:
            snap = provider_usage_store.snapshot()
            snapshot = {
                "budget_state": str(snap.get("budget_state") or "normal"),
                "budget_remaining_tokens": int(snap.get("budget_remaining_tokens") or 0),
                "budget_state_label": str(snap.get("budget_state_label") or "Normal"),
                "budget_warning": str(snap.get("budget_state") or "normal") == "warning",
                "estimated_total_tokens": int(snap.get("estimated_total_tokens") or 0),
                "budget_tokens": int(snap.get("budget_tokens") or 0),
            }
        await ws_send(ws, {"type": "token_budget_update", "data": snapshot})
    except Exception:
        pass


def _build_trust_review_snapshot() -> dict[str, object]:
    try:
        enabled_entries = OSDiagnosticsExecutor._enabled_capability_entries()
        recent_runtime_activity, trust_review_summary = OSDiagnosticsExecutor._recent_runtime_activity(
            enabled_entries,
            limit=12,
        )
        model_availability, _, _, _ = OSDiagnosticsExecutor._model_status_details()
        blocked_conditions = OSDiagnosticsExecutor._blocked_conditions(
            model_availability=model_availability
        )
        ledger_integrity, ledger_entries_today, ledger_last_event = OSDiagnosticsExecutor._ledger_status_details()
        voice_runtime = inspect_voice_runtime()
        policy_capability_readiness = OSDiagnosticsExecutor._policy_capability_readiness()
        reasoning_runtime = OSDiagnosticsExecutor._external_reasoning_status_details()
        bridge_runtime = OSDiagnosticsExecutor._bridge_status_details()
        connection_runtime = OSDiagnosticsExecutor._connection_status_details()
    except Exception:
        return {}

    return {
        "trust_review_summary": trust_review_summary,
        "recent_runtime_activity": recent_runtime_activity,
        "blocked_conditions": blocked_conditions,
        "ledger_integrity": ledger_integrity,
        "ledger_entries_today": ledger_entries_today,
        "ledger_last_event": ledger_last_event,
        "voice_runtime": voice_runtime,
        "policy_capability_readiness": policy_capability_readiness,
        "reasoning_runtime": reasoning_runtime,
        "bridge_runtime": bridge_runtime,
        "connection_runtime": connection_runtime,
    }


_TRUST_REVIEW_CACHE: dict[str, object] = {}
_TRUST_REVIEW_CACHE_TS = 0.0
_TRUST_REVIEW_CACHE_TTL_SECONDS = 15.0
_TRUST_REVIEW_CACHE_LOCK = asyncio.Lock()


def _get_cached_trust_review_snapshot() -> dict[str, object]:
    if not _TRUST_REVIEW_CACHE:
        return {}
    age = time.monotonic() - _TRUST_REVIEW_CACHE_TS
    if age > _TRUST_REVIEW_CACHE_TTL_SECONDS:
        return {}
    return dict(_TRUST_REVIEW_CACHE)


async def _maybe_send_trust_review_snapshot(ws: WebSocket, trust_status: dict) -> None:
    async def _refresh_and_push() -> None:
        global _TRUST_REVIEW_CACHE_TS, _TRUST_REVIEW_CACHE
        snapshot: dict[str, object] = {}
        try:
            async with _TRUST_REVIEW_CACHE_LOCK:
                cached = _get_cached_trust_review_snapshot()
                if cached:
                    snapshot = cached
                else:
                    snapshot = await asyncio.to_thread(_build_trust_review_snapshot)
                    if snapshot:
                        _TRUST_REVIEW_CACHE = dict(snapshot)
                        _TRUST_REVIEW_CACHE_TS = time.monotonic()
        except Exception:
            return
        if not snapshot:
            return
        payload = normalize_trust_status(trust_status)
        payload.update(snapshot)
        try:
            await ws_send(ws, {"type": "trust_status", "data": payload})
        except Exception:
            return

    asyncio.create_task(_refresh_and_push())


def _render_bridge_status_message(snapshot: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    payload = dict(snapshot or {})
    lines = ["OpenClaw Bridge", ""]
    lines.append(str(payload.get("summary") or "Bridge status is unavailable.").strip())
    lines.append("")
    lines.append(f"Status: {str(payload.get('status_label') or payload.get('status') or 'Unknown').strip()}")
    lines.append(f"Auth: {str(payload.get('auth') or 'Unknown').strip()}")
    lines.append(f"Scope: {str(payload.get('scope') or 'Read and reasoning only').strip()}")
    lines.append(f"Effectful actions: {str(payload.get('effectful_actions') or 'Blocked').strip()}")
    lines.append(f"Continuity: {str(payload.get('continuity') or 'Stateless').strip()}")
    suggestions = [
        {"label": "Open Settings", "command": "settings"},
        {"label": "Open Trust", "command": "trust center"},
        {"label": "Connection status", "command": "connection status"},
    ]
    return "\n".join(lines), suggestions


def _render_connection_status_message(snapshot: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    payload = dict(snapshot or {})
    items = [dict(item or {}) for item in list(payload.get("items") or [])[:6]]
    lines = ["Provider and Connector Status", ""]
    lines.append(str(payload.get("summary") or "Connection status is unavailable.").strip())
    if items:
        lines.append("")
        for item in items:
            label = str(item.get("label") or "").strip()
            value = str(item.get("value") or "").strip()
            note = str(item.get("note") or "").strip()
            if label and value:
                lines.append(f"- {label}: {value}")
            elif label:
                lines.append(f"- {label}")
            if note:
                lines.append(f"  {note}")
    suggestions = [
        {"label": "Open Settings", "command": "settings"},
        {"label": "Bridge status", "command": "bridge status"},
        {"label": "System status", "command": "system status"},
    ]
    return "\n".join(lines), suggestions


def _maybe_auto_speak_for_voice_turn(
    session_state: dict[str, Any],
    text: str,
) -> None:
    if session_state.get("last_input_channel") != "voice":
        return
    session_state["last_input_channel"] = None
    presented = conversation_personality_agent.present(str(text or "").strip(), domain="general")
    speakable = voice_experience_agent.prepare_spoken_reply(
        presented,
        mode=str(session_state.get("last_mode") or "casual"),
    )
    if not speakable:
        return
    speech_state.last_spoken_text = speakable
    try:
        nova_speak(speakable)
    except Exception:
        log.debug("Auto-speak failed", exc_info=True)


async def invoke_governed_capability(
    governor: Governor,
    capability_id: int,
    params: dict,
) -> object:
    try:
        return await asyncio.to_thread(
            governor.handle_governed_invocation,
            capability_id,
            params,
        )
    except Exception:
        log.exception("Governed capability %s raised unexpectedly — returning failure result", capability_id)
        from src.actions.action_result import ActionResult as _ActionResult
        return _ActionResult(success=False, message="An internal error occurred while running that capability.")


async def invoke_governed_text_command(
    governor: Governor,
    command_text: str,
    session_id: str,
    *,
    extra_params: Optional[dict] = None,
) -> tuple[Optional[int], Optional[object]]:
    """
    Parse a governed command via GovernorMediator and execute the mapped capability.

    This keeps invocation routing explicit and deterministic while allowing
    orchestration code to request known governed commands safely.
    """
    parsed = GovernorMediator.parse_governed_invocation(command_text, session_id=None)
    if not isinstance(parsed, Invocation):
        return None, None

    params = dict(parsed.params)
    if extra_params:
        params.update(extra_params)
    params.setdefault("session_id", session_id)

    action_result = await invoke_governed_capability(governor, parsed.capability_id, params)
    return parsed.capability_id, action_result

# -------------------------------------------------
# WebSocket Endpoint
# -------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await run_websocket_session(ws, sys.modules[__name__])


async def _run_bridge_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from src.api.bridge_api import _run_bridge_messages as _bridge_runner

    return await _bridge_runner(websocket_endpoint, messages)


# -------------------------------------------------
# Console entry point (pyproject `nova-start`)
# -------------------------------------------------
def main() -> None:
    """Launch the Nova FastAPI app via uvicorn.

    Mirrors the invocation in ``start_nova.bat`` / ``start_nova.sh``
    (``python -m uvicorn src.brain_server:app --host 127.0.0.1 --port 8000``).
    This wrapper exists so the ``nova-start`` console script declared in
    ``pyproject.toml`` has a resolvable target. Keep it thin: no side effects
    beyond starting the server so imports of this module stay cheap.
    """
    import os

    import uvicorn

    host = os.environ.get("NOVA_HOST", "127.0.0.1")
    port = int(os.environ.get("NOVA_PORT", "8000"))
    uvicorn.run("src.brain_server:app", host=host, port=port)


if __name__ == "__main__":
    main()
