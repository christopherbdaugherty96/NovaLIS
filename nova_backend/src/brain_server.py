# src/brain_server.py

"""
NovaLIS Brain Server â€” Phase 4 Staging
- Sessionâ€‘aware mediator
- Dataclassâ€‘based invocation handling
- Governor mediation
- Phaseâ€‘3.5 skill fallback preserved
"""

from src.governor.governor import Governor
from src.memory.quick_corrections import record_correction
from src.routers.stt import router as stt_router

import json
import logging
import re
import uuid
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse

from src.skill_registry import SkillRegistry
from src.gates.confirmation_gate import confirmation_gate
from src.governor.governor_mediator import GovernorMediator, Invocation, Clarification
from src.utils.web_target_planner import plan_web_open
from src.speech_state import speech_state
from src.conversation.thought_store import ThoughtStore
from src.conversation.complexity_heuristics import ComplexityHeuristics
from src.conversation.session_router import SessionRouter
from src.voice.stt_pipeline import STTAckConfig, build_ack_payload
from src.voice.tts_engine import stop_speaking
from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.conversation.response_formatter import ResponseFormatter
from src.build_phase import BUILD_PHASE, PHASE_4_2_ENABLED
from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor
from src.trust.failure_ladder import FailureLadder
from src.trust.trust_contract import normalize_trust_status
from src.patterns.pattern_review_store import PatternReviewStore
from src.policies.atomic_policy_store import AtomicPolicyStore
from src.working_context.context_store import WorkingContextStore
from src.working_context.project_threads import ProjectThreadStore
from src.tasks.notification_schedule_store import NotificationScheduleStore
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.tone_profile_store import ToneProfileStore
from src.audit.runtime_auditor import (
    run_runtime_truth_audit,
    render_runtime_truth_markdown,
    write_current_runtime_state_snapshot,
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
    yield


app = FastAPI(lifespan=_lifespan)

# Phase-build lock marker for runtime auditor and governance checks.
# Phase 4 keeps 4.2 modules runtime-locked unless a build promotes phase.
_ = (BUILD_PHASE, PHASE_4_2_ENABLED)

# -------------------------------------------------
# Static Files
# -------------------------------------------------
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]   # nova_backend/
STATIC_DIR = BASE_DIR / "static"
INDEX_HTML = STATIC_DIR / "index.html"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {"error": "static/index.html not found"}

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(stt_router)

# -------------------------------------------------
# Phaseâ€‘4 Staging Components
# -------------------------------------------------
thought_store = ThoughtStore(ttl=300)
conversation_heuristics = ComplexityHeuristics()
response_formatter = ResponseFormatter()
failure_ladder = FailureLadder()
interface_personality_agent = PersonalityInterfaceAgent()
RUNTIME_GOVERNOR = Governor()

# -------------------------------------------------
# Security Constants
# -------------------------------------------------
WS_INPUT_MAX_BYTES = 4096
CONVERSATIONAL_INITIATIVE_ENABLED = True
VOICE_ACK_ENABLED = True
VOICE_ACK_TEXT = "Got it."
VOICE_ACK_CONFIG = STTAckConfig(enabled=VOICE_ACK_ENABLED, text=VOICE_ACK_TEXT)
PHASE42_QUERY_RE = re.compile(
    r"^\s*(?:phase\s*4\.?2|phase42|orthogonal(?:\s+analysis)?)\s*(?:[:\-]\s*|\s+)(?P<query>.+)\s*$",
    re.IGNORECASE,
)
PHASE42_HELP_COMMANDS = {
    "phase42",
    "phase 4.2",
    "orthogonal analysis",
    "phase42 help",
    "orthogonal help",
}

CREATE_THREAD_RE = re.compile(
    r"^\s*(?:create|start)\s+(?:project\s+)?thread\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
CONTINUE_THREAD_RE = re.compile(
    r"^\s*continue(?:\s+my)?\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
SHOW_THREADS_RE = re.compile(
    r"^\s*(?:show|list)\s+(?:my\s+)?(?:project\s+)?threads?\s*$",
    re.IGNORECASE,
)
ATTACH_THREAD_RE = re.compile(
    r"^\s*(?:save|attach)\s+this(?:\s+(?:as\s+part\s+of|to|for))\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
ATTACH_ACTIVE_THREAD_RE = re.compile(
    r"^\s*(?:save|attach)\s+this\s*$",
    re.IGNORECASE,
)
DECISION_THREAD_RE = re.compile(
    r"^\s*(?:remember|record)\s+decision\s+(?P<decision>.+?)\s+for\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
PROJECT_STATUS_RE = re.compile(
    r"^\s*(?:project\s+status|status\s+for|status\s+of)\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
BIGGEST_BLOCKER_RE = re.compile(
    r"^\s*(?:what(?:'s| is)\s+(?:the\s+)?)?(?:biggest|main|current)\s+blocker(?:\s+in|\s+for)?\s*(?P<name>.*)\s*$",
    re.IGNORECASE,
)
THREAD_DETAIL_RE = re.compile(
    r"^\s*(?:thread\s+detail|show\s+thread\s+detail|show\s+thread|thread\s+snapshot|details?\s+for)\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
MOST_BLOCKED_PROJECT_RE = re.compile(
    r"^\s*(?:which(?:\s+of\s+my)?\s+projects?\s+is\s+most\s+blocked(?:\s+right\s+now)?|most\s+blocked\s+project)\s*$",
    re.IGNORECASE,
)
WHY_RECOMMENDATION_RE = re.compile(
    r"^\s*why\s+(?:this|that)\s+recommendation\s*\??\s*$",
    re.IGNORECASE,
)
TONE_STATUS_COMMANDS = {
    "tone",
    "tone status",
    "tone settings",
    "tone profile",
    "response style",
    "response style settings",
}
TONE_SET_RE = re.compile(r"^\s*tone\s+set\s+(?P<body>.+?)\s*$", re.IGNORECASE)
TONE_RESET_RE = re.compile(r"^\s*tone\s+reset(?:\s+(?P<body>.+?))?\s*$", re.IGNORECASE)
SHOW_SCHEDULES_COMMANDS = {
    "show schedules",
    "list schedules",
    "notification status",
    "notification schedules",
    "scheduled updates",
    "reminders",
}
NOTIFICATION_SETTINGS_COMMANDS = {
    "notification settings",
    "show notification settings",
    "show schedule settings",
    "schedule settings",
    "notification policy",
}
SCHEDULE_BRIEF_RE = re.compile(
    r"^\s*schedule\s+(?:a\s+)?(?:(?:daily|morning)\s+brief)\s+at\s+(?P<time>.+?)\s*$",
    re.IGNORECASE,
)
REMIND_ME_RE = re.compile(
    r"^\s*remind\s+me(?:\s+(?P<daily>daily))?\s+at\s+(?P<time>.+?)\s+to\s+(?P<body>.+?)\s*$",
    re.IGNORECASE,
)
CANCEL_SCHEDULE_RE = re.compile(
    r"^\s*(?:cancel|delete|remove)\s+schedule\s+(?P<schedule_id>SCH-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
DISMISS_SCHEDULE_RE = re.compile(
    r"^\s*(?:dismiss|clear)\s+schedule\s+(?P<schedule_id>SCH-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
RESCHEDULE_SCHEDULE_RE = re.compile(
    r"^\s*reschedule\s+schedule\s+(?P<schedule_id>SCH-[A-Z0-9\-]+)\s+to\s+(?P<time>.+?)\s*$",
    re.IGNORECASE,
)
SET_QUIET_HOURS_RE = re.compile(
    r"^\s*(?:set\s+)?(?:notification\s+)?quiet\s+hours\s+(?:from\s+)?(?P<start>.+?)\s+(?:to|-)\s+(?P<end>.+?)\s*$",
    re.IGNORECASE,
)
CLEAR_QUIET_HOURS_RE = re.compile(
    r"^\s*(?:clear|disable|turn\s+off)\s+(?:notification\s+)?quiet\s+hours\s*$",
    re.IGNORECASE,
)
SET_NOTIFICATION_RATE_LIMIT_RE = re.compile(
    r"^\s*(?:set\s+)?(?:notification\s+)?rate\s+limit\s+(?P<count>\d{1,2})\s+per\s+hour\s*$",
    re.IGNORECASE,
)
PATTERN_STATUS_COMMANDS = {
    "pattern status",
    "patterns status",
    "pattern review status",
    "pattern queue",
}
PATTERN_OPT_IN_RE = re.compile(
    r"^\s*(?:pattern|patterns)\s+opt\s+in\s*$|^\s*enable\s+pattern\s+review\s*$",
    re.IGNORECASE,
)
PATTERN_OPT_OUT_RE = re.compile(
    r"^\s*(?:pattern|patterns)\s+opt\s+out\s*$|^\s*disable\s+pattern\s+review\s*$",
    re.IGNORECASE,
)
PATTERN_REVIEW_RE = re.compile(
    r"^\s*(?:review|show)\s+(?:patterns?|pattern\s+review)(?:\s+for\s+(?P<name>.+?))?\s*$",
    re.IGNORECASE,
)
ACCEPT_PATTERN_RE = re.compile(
    r"^\s*(?:accept|approve|keep)\s+pattern\s+(?P<pattern_id>PAT-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
DISMISS_PATTERN_RE = re.compile(
    r"^\s*(?:dismiss|discard|reject)\s+pattern\s+(?P<pattern_id>PAT-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
POLICY_STATUS_COMMANDS = {
    "policy overview",
    "policy status",
    "policy list",
    "policies",
    "policy drafts",
}
POLICY_CREATE_RE = re.compile(
    r"^\s*policy\s+(?:create|draft)\s+(?P<schedule>daily|weekday)\s+"
    r"(?P<action>calendar\s+snapshot|weather\s+snapshot|news\s+snapshot|system\s+status)\s+at\s+(?P<time>.+?)\s*$",
    re.IGNORECASE,
)
POLICY_SHOW_RE = re.compile(
    r"^\s*policy\s+show\s+(?P<policy_id>POL-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
POLICY_DELETE_RE = re.compile(
    r"^\s*policy\s+delete\s+(?P<policy_id>POL-[A-Z0-9\-]+)(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
POLICY_SIMULATE_RE = re.compile(
    r"^\s*policy\s+simulate\s+(?P<policy_id>POL-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
POLICY_RUN_ONCE_RE = re.compile(
    r"^\s*policy\s+run\s+(?P<policy_id>POL-[A-Z0-9\-]+)(?:\s+(?P<once>once))?\s*$",
    re.IGNORECASE,
)


def _build_phase42_agents() -> list:
    if not PHASE_4_2_ENABLED:
        return []

    from src.agents.builder import BuilderAgent
    from src.agents.deep_audit import DeepAuditAgent
    from src.agents.architect import StructuralArchitectAgent
    from src.agents.memory import MemoryAgent
    from src.agents.assumption import AssumptionRiskAgent
    from src.agents.contradiction import ContradictionAggregatorAgent
    from src.agents.adversarial import AdversarialExternalizerAgent

    return [
        BuilderAgent(),
        DeepAuditAgent(),
        StructuralArchitectAgent(),
        MemoryAgent(),
        AssumptionRiskAgent(),
        ContradictionAggregatorAgent(),
        AdversarialExternalizerAgent(),
    ]


def _extract_phase42_query(text: str) -> str | None:
    match = PHASE42_QUERY_RE.match((text or "").strip())
    if not match:
        return None
    query = (match.group("query") or "").strip()
    return query or None


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
HARD_ACTION_PREFIXES = (
    "open ",
    "volume ",
    "set volume ",
    "brightness ",
    "set brightness ",
    "mute",
    "unmute",
    "play",
    "pause",
    "stop playback",
)
TOPIC_NOISE_TERMS = {
    "please",
    "nova",
    "today",
    "now",
    "quickly",
    "brief",
}


def _is_hard_action_command(text: str) -> bool:
    lowered = (text or "").strip().lower().rstrip(".?!")
    if not lowered:
        return False
    return any(lowered.startswith(prefix) for prefix in HARD_ACTION_PREFIXES)


def _extract_topic_candidate(text: str) -> str:
    lowered = (text or "").strip().lower().rstrip(".?!")
    if not lowered:
        return ""

    for prefix in ("research ", "search ", "summarize ", "compare ", "track ", "open "):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix):].strip()
            break

    lowered = re.sub(r"\b(the|a|an|about|for)\b", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    if not lowered:
        return ""

    terms = [term for term in re.findall(r"[a-z0-9']+", lowered) if term and term not in TOPIC_NOISE_TERMS]
    if len(terms) < 2:
        return ""

    candidate = " ".join(terms[:8]).strip()
    return candidate[:80]


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
        message = str(getattr(action_result, "message", "") or "").strip()
        summary = _make_shorter_followup(message)
        data = getattr(action_result, "data", None)
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

    if isinstance(getattr(action_result, "data", None), dict):
        data = dict(getattr(action_result, "data") or {})
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


def _prepare_memory_bridge_params(
    *,
    params: dict,
    project_threads: ProjectThreadStore,
) -> tuple[bool, dict, str]:
    action = str(params.get("action") or "").strip().lower()
    if action == "save_thread_snapshot":
        requested = str(params.get("thread_name") or "").strip()
        if requested.lower() in {"this", "it", "thread", "project"}:
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
        if requested.lower() in {"this", "it", "thread", "project"}:
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
        if requested.lower() in {"this", "it", "thread", "project"}:
            requested = project_threads.active_thread_name()
        prepared = dict(params)
        found, resolved_name, resolved_key = project_threads.resolve_thread_identity(requested)
        if found:
            prepared["thread_name"] = resolved_name
            prepared["thread_key"] = resolved_key
        else:
            prepared["thread_name"] = requested
        return True, prepared, ""

    return True, params, ""


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
            "general": int(scope_counts.get("general") or 0),
            "project": int(scope_counts.get("project") or 0),
            "ops": int(scope_counts.get("ops") or 0),
        },
        "recent_items": recent_items,
        "linked_threads": linked_threads,
        "inspectability_note": "Memory is explicit, inspectable, and revocable.",
    }


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
    if lowered in {"web_search", "web_search_skill"}:
        return "research"
    return "general"


def _parse_tone_set_body(raw_body: str) -> tuple[str, str, bool]:
    body = str(raw_body or "").strip().lower()
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

    profile = parts[-1]
    domain = " ".join(parts[:-1]).strip().lower()
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

    lines.extend(
        [
            "",
            "Try next:",
            "- policy create weekday calendar snapshot at 8:00 am",
            "- policy create daily weather snapshot at 7:30 am",
            "- policy show <id>",
            "- policy simulate <id>",
            "- policy run <id> once",
            "- policy delete <id> confirm",
        ]
    )
    return "\n".join(lines)


def _render_policy_detail_message(item: dict | None) -> str:
    payload = dict(item or {})
    validation = dict(payload.get("last_validation") or {})
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
        f"- capability class: {str(payload.get('capability_class') or 'unknown').strip()}",
        f"- delegation class: {str(payload.get('delegation_class') or 'observational').strip()}",
        f"- policy delegatable: {_policy_yes_no_label(bool(payload.get('policy_delegatable')))}",
        f"- network required: {_policy_yes_no_label(bool(payload.get('network_required')))}",
        f"- estimated runtime: {str(payload.get('estimated_runtime') or 'unknown').strip()}",
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
    result_data = getattr(action_result, "data", None)
    if not isinstance(result_data, dict):
        result_data = {}
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
        f"- message: {str(getattr(action_result, 'message', '') or '').strip()}",
    ]

    request_id = str(getattr(action_result, "request_id", "") or "").strip()
    if request_id:
        lines.append(f"- request id: {request_id}")

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
# Phase Status Endpoint
# -------------------------------------------------
@app.get("/phase-status")
async def phase_status():
    from src.governor.execute_boundary import GOVERNED_ACTIONS_ENABLED
    return {
        "phase": str(BUILD_PHASE),
        "phase_display": "5 closed / 6 foundation" if BUILD_PHASE >= 5 else f"{BUILD_PHASE}",
        "status": "active" if GOVERNED_ACTIONS_ENABLED else "sealed",
        "execution_enabled": GOVERNED_ACTIONS_ENABLED,
        "delegated_runtime_enabled": False,
        "note": (
            "Phase-5 trust layer is active. "
            "Phase-6 policy foundation exists, but delegated execution remains disabled."
        ),
    }
@app.get("/system/audit/runtime-truth")
async def audit_runtime_truth():
    """Read-only runtime-truth audit report (JSON)."""
    return run_runtime_truth_audit()


@app.get("/system/audit/runtime-truth.md", response_class=PlainTextResponse)
async def audit_runtime_truth_markdown():
    """Read-only runtime-truth audit report (Markdown)."""
    report = run_runtime_truth_audit()
    return render_runtime_truth_markdown(report)

# -------------------------------------------------
# WebSocket Utilities
# -------------------------------------------------
async def ws_send(ws: WebSocket, payload: dict) -> None:
    await ws.send_text(json.dumps(payload))


async def send_thread_map_widget(
    ws: WebSocket,
    project_threads: ProjectThreadStore,
    session_state: dict,
) -> None:
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

async def send_chat_message(
    ws: WebSocket,
    text: str,
    message_id: Optional[str] = None,
    confidence: Optional[str] = None,
    suggested_actions: Optional[list[dict[str, str]]] = None,
    apply_personality: bool = True,
    tone_domain: str = "general",
) -> None:
    presented = str(text or "").strip()
    if apply_personality:
        presented = interface_personality_agent.present(presented, domain=tone_domain)
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
    payload.update(_build_trust_review_snapshot())
    await ws_send(ws, {"type": "trust_status", "data": payload})


def _build_trust_review_snapshot() -> dict[str, object]:
    try:
        enabled_entries = OSDiagnosticsExecutor._enabled_capability_entries()
        recent_runtime_activity, trust_review_summary = OSDiagnosticsExecutor._recent_runtime_activity(
            enabled_entries
        )
        model_availability, _, _, _ = OSDiagnosticsExecutor._model_status_details()
        blocked_conditions = OSDiagnosticsExecutor._blocked_conditions(
            model_availability=model_availability
        )
    except Exception:
        return {}

    return {
        "trust_review_summary": trust_review_summary,
        "recent_runtime_activity": recent_runtime_activity,
        "blocked_conditions": blocked_conditions,
    }


async def invoke_governed_capability(
    governor: Governor,
    capability_id: int,
    params: dict,
) -> object:
    return await asyncio.to_thread(
        governor.handle_governed_invocation,
        capability_id,
        params,
    )


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
    await ws.accept()
    log.info("WebSocket connected")

    session_id = str(uuid.uuid4())
    governor = RUNTIME_GOVERNOR
    skill_registry = SkillRegistry(network=governor.network)
    personality_agent = _Phase42PersonalityAgent() if _Phase42PersonalityAgent is not None else None
    working_context = WorkingContextStore(session_id=session_id, ledger=governor.ledger)
    project_threads = ProjectThreadStore(session_id=session_id, ledger=governor.ledger)
    notification_schedules = NotificationScheduleStore()
    pattern_reviews = PatternReviewStore()
    policy_drafts = AtomicPolicyStore()
    session_context = []
    session_state = {
        "turn_count": 0,
        "escalation_count": 0,
        "last_escalation_turn": None,
        "deep_mode_disabled": False,
        "show_thinking_hints": True,
        "presence_mode": False,
        "pending_escalation": None,
        "deep_mode_armed": False,
        "deep_mode_last_armed_turn": None,
        "last_input_channel": "text",
        "last_response": "",
        "last_clarification_turn": None,
        "last_object": "",
        "news_cache": [],
        "news_categories": {},
        "last_sources": [],
        "last_source_links": [],
        "last_news_story_index": None,
        "topic_memory_map": {},
        "last_brief_clusters": [],
        "pending_web_open": None,
        "pending_governed_confirm": None,
        "pending_interpret_confirm": None,
        "analysis_documents": [],
        "last_analysis_doc_id": None,
        "last_intent_family": "",
        "last_mode": "",
        "session_mode_override": "",
        "topic_stack": [],
        "active_topic": "",
        "trust_status": failure_ladder.initial_status(),
        "last_calendar_summary": "",
        "last_calendar_events": [],
        "working_context": working_context.to_dict(),
        "project_thread_active": "",
        "last_recommendation_reason": "",
        "thread_map_last": {},
        "last_memory_overview": {},
        "last_tone_snapshot": {},
        "last_schedule_overview": {},
        "last_pattern_review": {},
    }

    await send_chat_message(ws, "Hello. How can I help?")
    await send_trust_status(ws, session_state["trust_status"])
    await send_chat_done(ws)

    try:
        while True:
            GovernorMediator.clear_stale_sessions()
            raw = await ws.receive_text()
            raw_bytes = raw.encode("utf-8")
            if len(raw_bytes) > WS_INPUT_MAX_BYTES:
                log.warning("WebSocket input rejected: %d bytes exceeds limit %d", len(raw_bytes), WS_INPUT_MAX_BYTES)
                await ws_send(ws, {"type": "error", "code": "input_too_long", "message": "Input exceeds maximum allowed length."})
                continue

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                log.warning("WebSocket input rejected: malformed JSON")
                await ws_send(ws, {"type": "error", "code": "invalid_json", "message": "Malformed request."})
                continue

            msg_type = (msg.get("type") or "chat").strip().lower()
            channel = (msg.get("channel") or "text").strip().lower()
            invocation_source = (msg.get("invocation_source") or "").strip().lower()
            silent_widget_refresh = bool(msg.get("silent_widget_refresh"))
            if channel not in {"voice", "text"}:
                channel = "text"
            if invocation_source not in {"voice", "text", "ui"}:
                invocation_source = "voice" if channel == "voice" else "text"

            if msg_type == "get_thought":
                message_id = (msg.get("message_id") or "").strip()
                thought_data = thought_store.get(session_id, message_id) if message_id else None
                if thought_data is None:
                    await ws_send(ws, {"type": "error", "message": "Thought data not found or expired"})
                else:
                    await ws_send(ws, {"type": "thought", "data": thought_data, "message_id": message_id})
                continue

            raw_text = (msg.get("text") or "").strip()
            if not raw_text:
                await send_chat_message(ws, CLARIFY_PROMPTS["ready_prompt"])
                await send_chat_done(ws)
                continue

            session_state["last_input_channel"] = channel
            interpreted_confirmation_consumed = False

            pending_interpret_confirm = session_state.get("pending_interpret_confirm")
            if pending_interpret_confirm:
                interpret_decision = SessionRouter.route_pending_web_confirmation(raw_text)
                if interpret_decision.action == "confirm":
                    raw_text = str(pending_interpret_confirm.get("interpreted_text") or "").strip()
                    session_state["pending_interpret_confirm"] = None
                    interpreted_confirmation_consumed = True
                    if not raw_text:
                        await send_chat_message(
                            ws,
                            "Thanks. I lost the interpreted command. Please say it again.",
                        )
                        await send_chat_done(ws)
                        continue
                elif interpret_decision.action == "cancel":
                    session_state["pending_interpret_confirm"] = None
                    await send_chat_message(
                        ws,
                        "No problem. I canceled that action. Please say it again in your own words.",
                    )
                    await send_chat_done(ws)
                    continue
                else:
                    await send_chat_message(
                        ws,
                        "I want to make sure I heard you right. Reply 'yes' to continue or 'no' to cancel.",
                    )
                    await send_chat_done(ws)
                    continue

            route_context = SessionRouter.normalize_and_route(raw_text, session_state)
            if route_context.is_empty:
                await send_chat_message(ws, SessionRouter.ready_prompt())
                await send_chat_done(ws)
                continue

            text = route_context.text
            lowered = route_context.lowered
            decision = route_context.decision
            _prune_topic_stack(session_state, session_state["turn_count"])

            gate = SessionRouter.evaluate_gate(decision, session_state, session_state["turn_count"])
            if gate.handled:
                if gate.apply_override:
                    session_state["session_mode_override"] = gate.apply_override
                if gate.clear_override:
                    session_state["session_mode_override"] = ""
                if gate.set_clarification_turn:
                    session_state["last_clarification_turn"] = session_state["turn_count"]
                await send_chat_message(
                    ws,
                    gate.message,
                    suggested_actions=_clarification_suggestions(gate.message),
                )
                await send_chat_done(ws)
                continue
            if not decision.blocked_by_policy and not decision.needs_clarification:
                session_state["last_intent_family"] = decision.intent_family
                session_state["last_mode"] = decision.mode.value
            working_context.apply_user_turn(
                text=text,
                channel=invocation_source,
                intent_family=decision.intent_family,
            )
            session_state["working_context"] = working_context.to_dict()

            if (
                channel == "voice"
                and not interpreted_confirmation_consumed
                and route_context.normalization_changed
                and _is_hard_action_command(text)
            ):
                interpreted_text = text.rstrip(".").strip()
                session_state["pending_interpret_confirm"] = {"interpreted_text": interpreted_text}
                await send_chat_message(
                    ws,
                    (
                        f'I heard: "{interpreted_text}".\n'
                        "Should I run that action?\n"
                        "Reply 'yes' to continue or 'no' to cancel."
                    ),
                )
                await send_chat_done(ws)
                continue

            if lowered in {
                "topic stack",
                "current topic",
                "what are we discussing",
                "what topic are we on",
            }:
                await send_chat_message(
                    ws,
                    _topic_stack_message(session_state, session_state["turn_count"]),
                )
                await send_chat_done(ws)
                continue

            if lowered in {
                "what can you do",
                "nova what can you do",
                "show capabilities",
                "capabilities",
                "help capabilities",
            }:
                capability_message = (
                    "Nova Capabilities\n"
                    "Research\n"
                    "- search for <topic>\n"
                    "- research <topic>\n"
                    "- summarize all headlines\n\n"
                    "Explain Anything\n"
                    "- explain this\n"
                    "- what is this\n"
                    "- help me do this\n"
                    "- take a screenshot\n\n"
                    "Document Analysis\n"
                    "- create analysis report on <topic>\n"
                    "- list analysis docs\n"
                    "- summarize doc <id>\n"
                    "- explain section <n> of doc <id>\n\n"
                    "System Diagnostics\n"
                    "- system status\n"
                    "- morning brief\n\n"
                    "Web Search\n"
                    "- search for <query>\n"
                    "- open source <n>\n\n"
                    "Reports\n"
                    "- daily brief\n"
                    "- today's news\n"
                    "- phase42: <analysis request>\n\n"
                    "Project Continuity\n"
                    "- create thread <name>\n"
                    "- save this as part of <name>\n"
                    "- continue my <name>\n"
                    "- show threads\n"
                    "- thread detail <name>\n"
                    "- project status <name>\n"
                    "- biggest blocker in <name>\n"
                    "- which project is most blocked right now\n"
                    "- why this recommendation\n\n"
                    "Governed Memory\n"
                    "- memory overview\n"
                    "- memory save <title>: <content>\n"
                    "- memory save thread <name>\n"
                    "- memory save decision for <thread>: <text>\n"
                    "- memory list [active|locked|deferred]\n"
                    "- memory list thread <name>\n"
                    "- memory show <id>\n"
                    "- memory lock <id>\n"
                    "- memory defer <id>\n"
                    "- memory unlock <id> confirm\n"
                    "- memory delete <id> confirm\n\n"
                    "Pattern Review\n"
                    "- pattern opt in\n"
                    "- pattern status\n"
                    "- review patterns\n"
                    "- review patterns for <thread>\n"
                    "- accept pattern <id>\n"
                    "- dismiss pattern <id>\n\n"
                    "Policy Drafts (Phase-6 foundation)\n"
                    "- policy overview\n"
                    "- policy create weekday calendar snapshot at 8:00 am\n"
                    "- policy create daily weather snapshot at 7:30 am\n"
                    "- policy show <id>\n"
                    "- policy simulate <id>\n"
                    "- policy run <id> once\n"
                    "- policy delete <id> confirm"
                )
                await send_chat_message(ws, capability_message)
                await send_chat_done(ws)
                continue

            if SHOW_THREADS_RE.match(text):
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(ws, project_threads.render_map_message())
                await send_chat_done(ws)
                continue

            if MOST_BLOCKED_PROJECT_RE.match(text):
                found, blocked_message = project_threads.render_most_blocked()
                if found:
                    await send_thread_map_widget(ws, project_threads, session_state)
                    top_name = project_threads.most_blocked_thread_name()
                    suggested: list[dict[str, str]] = [{"label": "Show threads", "command": "show threads"}]
                    if top_name:
                        suggested = [
                            {"label": f"Continue {top_name}", "command": f"continue my {top_name}"},
                            {"label": f"Project status", "command": f"project status {top_name}"},
                            {"label": "Save thread memory", "command": f"memory save thread {top_name}"},
                            {"label": "Show threads", "command": "show threads"},
                        ]
                    await send_chat_message(ws, blocked_message, suggested_actions=suggested)
                else:
                    await send_chat_message(ws, blocked_message)
                await send_chat_done(ws)
                continue

            if WHY_RECOMMENDATION_RE.match(text):
                reason = str(session_state.get("last_recommendation_reason") or "").strip()
                if reason:
                    await send_chat_message(ws, f"Why this recommendation\n\n{reason}")
                else:
                    await send_chat_message(
                        ws,
                        "I do not have a recent recommendation context yet. Ask for analysis first (for example, 'explain this').",
                    )
                await send_chat_done(ws)
                continue

            create_thread_match = CREATE_THREAD_RE.match(text)
            if create_thread_match:
                thread_name = str(create_thread_match.group("name") or "").strip()
                created = project_threads.ensure_thread(
                    thread_name,
                    goal=str(working_context.to_dict().get("task_goal") or "").strip(),
                )
                session_state["project_thread_active"] = created.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    (
                        f"Thread ready: {created.name}.\n"
                        "You can now say 'save this as part of "
                        f"{created.name}' to attach progress updates."
                    ),
                )
                await send_chat_done(ws)
                continue

            continue_thread_match = CONTINUE_THREAD_RE.match(text)
            if continue_thread_match:
                thread_name = str(continue_thread_match.group("name") or "").strip()
                if thread_name.lower() in {"this", "it", "thread"}:
                    thread_name = project_threads.active_thread_name() or session_state.get("project_thread_active") or ""
                found, brief = project_threads.render_brief(thread_name)
                if found:
                    session_state["project_thread_active"] = project_threads.active_thread_name()
                    await send_thread_map_widget(ws, project_threads, session_state)
                    await send_chat_message(
                        ws,
                        brief,
                        suggested_actions=[
                            {"label": "Save this update", "command": f"save this as part of {project_threads.active_thread_name()}"},
                            {"label": "Save thread memory", "command": f"memory save thread {project_threads.active_thread_name()}"},
                            {"label": "List thread memory", "command": f"memory list thread {project_threads.active_thread_name()}"},
                            {"label": "Show threads", "command": "show threads"},
                        ],
                    )
                else:
                    if not project_threads.has_threads() and decision.intent_family == "followup":
                        pass
                    else:
                        await send_chat_message(ws, brief)
                        await send_chat_done(ws)
                        continue
                if found:
                    await send_chat_done(ws)
                    continue

            status_thread_match = PROJECT_STATUS_RE.match(text)
            if status_thread_match:
                thread_name = str(status_thread_match.group("name") or "").strip()
                if thread_name.lower() in {"this", "it", "thread", "project"}:
                    thread_name = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                found, status_text = project_threads.render_status(thread_name)
                if found:
                    session_state["project_thread_active"] = project_threads.active_thread_name()
                    await send_thread_map_widget(ws, project_threads, session_state)
                    active = project_threads.active_thread_name()
                    await send_chat_message(
                        ws,
                        status_text,
                        suggested_actions=[
                            {"label": "Thread detail", "command": f"thread detail {active}"},
                            {"label": "Biggest blocker", "command": f"biggest blocker in {active}"},
                            {"label": "Save thread memory", "command": f"memory save thread {active}"},
                            {"label": "List thread memory", "command": f"memory list thread {active}"},
                            {"label": "Continue thread", "command": f"continue my {active}"},
                            {"label": "Show threads", "command": "show threads"},
                        ],
                    )
                    await send_chat_done(ws)
                    continue
                if not project_threads.has_threads() and decision.intent_family == "followup":
                    pass
                else:
                    await send_chat_message(ws, status_text)
                    await send_chat_done(ws)
                    continue

            blocker_thread_match = BIGGEST_BLOCKER_RE.match(text)
            if blocker_thread_match:
                thread_name = str(blocker_thread_match.group("name") or "").strip()
                if not thread_name or thread_name.lower() in {"this", "it", "thread", "project"}:
                    thread_name = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                found, blocker_text = project_threads.render_biggest_blocker(thread_name)
                if found:
                    session_state["project_thread_active"] = project_threads.active_thread_name()
                    await send_thread_map_widget(ws, project_threads, session_state)
                    active = project_threads.active_thread_name()
                    await send_chat_message(
                        ws,
                        blocker_text,
                        suggested_actions=[
                            {"label": "Thread detail", "command": f"thread detail {active}"},
                            {"label": "Project status", "command": f"project status {active}"},
                            {"label": "Save this update", "command": f"save this as part of {active}"},
                            {"label": "Save decision memory", "command": f"memory save decision for {active}: "},
                            {"label": "Save thread memory", "command": f"memory save thread {active}"},
                            {"label": "Show threads", "command": "show threads"},
                        ],
                    )
                    await send_chat_done(ws)
                    continue
                if not project_threads.has_threads() and decision.intent_family == "followup":
                    pass
                else:
                    await send_chat_message(ws, blocker_text)
                    await send_chat_done(ws)
                    continue

            detail_thread_match = THREAD_DETAIL_RE.match(text)
            if detail_thread_match:
                thread_name = str(detail_thread_match.group("name") or "").strip()
                if thread_name.lower() in {"this", "it", "thread", "project"}:
                    thread_name = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                found, detail = project_threads.get_thread_detail(thread_name)
                if found:
                    session_state["project_thread_active"] = str(detail.get("name") or "")
                    await send_thread_map_widget(ws, project_threads, session_state)
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
                    await ws_send(
                        ws,
                        _build_thread_detail_widget(
                            detail=detail,
                            memory_items=memory_items,
                        ),
                    )
                    latest_decision = str(detail.get("latest_decision") or "").strip() or "No decision recorded yet."
                    latest_blocker = str(detail.get("latest_blocker") or "").strip() or "No blocker recorded."
                    await send_chat_message(
                        ws,
                        (
                            f"{str(detail.get('name') or 'Thread')} - Detail Snapshot\n\n"
                            f"Latest decision: {latest_decision}\n"
                            f"Latest blocker: {latest_blocker}"
                        ),
                        suggested_actions=[
                            {"label": "Project status", "command": f"project status {str(detail.get('name') or '').strip()}"},
                            {"label": "Biggest blocker", "command": f"biggest blocker in {str(detail.get('name') or '').strip()}"},
                            {"label": "List memory", "command": f"memory list thread {str(detail.get('name') or '').strip()}"},
                            {"label": "Save decision", "command": f"memory save decision for {str(detail.get('name') or '').strip()}: "},
                        ],
                    )
                    await send_chat_done(ws)
                    continue
                if not project_threads.has_threads() and decision.intent_family == "followup":
                    pass
                else:
                    await send_chat_message(ws, "I could not find that project thread yet.")
                    await send_chat_done(ws)
                    continue

            attach_thread_match = ATTACH_THREAD_RE.match(text)
            if ATTACH_ACTIVE_THREAD_RE.match(text):
                active_thread = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                if not active_thread:
                    await send_chat_message(
                        ws,
                        "I do not have an active thread yet. Say 'create thread <name>' first.",
                    )
                    await send_chat_done(ws)
                    continue
                summary, next_steps, default_category = _build_thread_attachment_summary(
                    session_state=session_state,
                    working_context=working_context,
                )
                attached = project_threads.attach_update(
                    thread_name=active_thread,
                    summary=summary,
                    category=default_category,
                    goal_hint=str(working_context.to_dict().get("task_goal") or "").strip(),
                    next_steps=next_steps,
                )
                session_state["project_thread_active"] = attached.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    f"Saved to active thread {attached.name}: {summary}",
                )
                await send_chat_done(ws)
                continue

            if attach_thread_match:
                thread_name = str(attach_thread_match.group("name") or "").strip()
                summary, next_steps, default_category = _build_thread_attachment_summary(
                    session_state=session_state,
                    working_context=working_context,
                )
                attached = project_threads.attach_update(
                    thread_name=thread_name,
                    summary=summary,
                    category=default_category,
                    goal_hint=str(working_context.to_dict().get("task_goal") or "").strip(),
                    next_steps=next_steps,
                )
                session_state["project_thread_active"] = attached.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    (
                        f"Saved to thread: {attached.name}.\n"
                        f"Update: {summary}"
                    ),
                )
                await send_chat_done(ws)
                continue

            decision_thread_match = DECISION_THREAD_RE.match(text)
            if decision_thread_match:
                decision_text = str(decision_thread_match.group("decision") or "").strip()
                thread_name = str(decision_thread_match.group("name") or "").strip()
                attached = project_threads.add_decision(thread_name=thread_name, decision=decision_text)
                session_state["project_thread_active"] = attached.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    f"Decision recorded in {attached.name}: {decision_text}",
                )
                await send_chat_done(ws)
                continue

            if not decision.blocked_by_policy and not decision.needs_clarification:
                _remember_topic(
                    session_state,
                    text,
                    decision.intent_family,
                    session_state["turn_count"],
                )

            if lowered in {
                "deep mode",
                "deep analysis",
                "deep thought",
                "deep think",
                "go deeper",
                "think deeper",
                "challenge this",
                "pressure test this",
            }:
                session_state["deep_mode_armed"] = True
                session_state["deep_mode_last_armed_turn"] = session_state.get("turn_count", 0)
                await send_chat_message(
                    ws,
                    "Deep analysis is armed for your next request. Ask your question when ready.",
                )
                await send_chat_done(ws)
                continue

            if lowered in {"stop deep mode", "cancel deep mode", "reset deep mode"}:
                session_state["deep_mode_armed"] = False
                session_state["pending_escalation"] = None
                await send_chat_message(ws, "Deep analysis canceled.")
                await send_chat_done(ws)
                continue

            pending_web_open = session_state.get("pending_web_open")
            pending_governed_confirm = session_state.get("pending_governed_confirm")
            if pending_governed_confirm:
                confirm_decision = SessionRouter.route_pending_web_confirmation(lowered)
                if confirm_decision.action == "confirm":
                    capability_id = int(pending_governed_confirm.get("capability_id") or 0)
                    params = dict(pending_governed_confirm.get("params") or {})
                    params["confirmed"] = True
                    params.setdefault("session_id", session_id)
                    action_result = await invoke_governed_capability(governor, capability_id, params)
                    session_state["pending_governed_confirm"] = None
                    outgoing_message = _structure_long_message(action_result.message)
                    await send_chat_message(ws, outgoing_message)
                    await send_chat_done(ws)
                    continue
                if confirm_decision.action == "cancel":
                    session_state["pending_governed_confirm"] = None
                    await send_chat_message(ws, "Cancelled pending action.")
                    await send_chat_done(ws)
                    continue
                await send_chat_message(
                    ws,
                    "I still have a confirmation pending. Reply 'yes' to proceed or 'no' to cancel.",
                )
                await send_chat_done(ws)
                continue

            if pending_web_open:
                web_decision = SessionRouter.route_pending_web_confirmation(lowered)
                if web_decision.action == "confirm":
                    action_result = await invoke_governed_capability(
                        governor,
                        17,
                        {**pending_web_open, "confirmed": True, "session_id": session_id},
                    )
                    session_state["pending_web_open"] = None
                    outgoing_message = _structure_long_message(action_result.message)
                    if action_result.success and isinstance(action_result.data, dict):
                        opened_domain = str(action_result.data.get("opened_domain") or "").strip()
                        if opened_domain:
                            session_state["last_sources"] = [opened_domain]
                    await send_chat_message(ws, outgoing_message)
                    await send_chat_done(ws)
                    continue
                if web_decision.action == "cancel":
                    session_state["pending_web_open"] = None
                    await send_chat_message(ws, "Cancelled website open request.")
                    await send_chat_done(ws)
                    continue
                await send_chat_message(
                    ws,
                    "I still have your website open request pending. Reply 'yes' to open or 'no' to cancel.",
                )
                await send_chat_done(ws)
                continue

            if channel == "voice" and msg_type == "chat":
                ack_payload = build_ack_payload(VOICE_ACK_CONFIG)
                if ack_payload is not None:
                    await ws_send(ws, ack_payload)

            micro_ack = str(decision.micro_ack or "").strip()
            if micro_ack and not silent_widget_refresh:
                await send_chat_message(ws, micro_ack)

            if lowered in {"open downloads", "open documents"}:
                session_state["last_object"] = lowered.replace("open ", "")

            # --- Escalation handling (fixed: clear pending on all outcomes) ---
            if session_state["pending_escalation"]:
                pending = session_state["pending_escalation"]
                escalate_decision = SessionRouter.route_pending_web_confirmation(lowered)
                if escalate_decision.action == "confirm":
                    original_query, context_snapshot, heuristic_result = pending
                    skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "general_chat"), None)
                    if skill is not None:
                        forced_state = dict(session_state)
                        forced_state["escalation_count"] = 0
                        forced_state["last_escalation_turn"] = None
                        forced_state["turn_count"] = 999
                        forced_state["deep_mode_disabled"] = False
                        forced_state["deep_mode_armed"] = True
                        forced_result = await skill.handle(original_query, context_snapshot, forced_state)
                        message_id = None
                        if forced_result is not None:
                            esc = (forced_result.data or {}).get("escalation", {})
                            if esc.get("escalated") and esc.get("thought_data"):
                                message_id = str(uuid.uuid4())
                                thought_store.put(session_id, message_id, esc["thought_data"])
                                session_state["escalation_count"] += 1
                                session_state["last_escalation_turn"] = session_state["turn_count"]
                            await send_chat_message(ws, forced_result.message, message_id=message_id)
                            await send_chat_done(ws)
                            session_context.extend([{"role": "user", "content": original_query}, {"role": "assistant", "content": forced_result.message}])
                            context_limit = 40 if session_state.get("presence_mode") else 20
                            session_context = session_context[-context_limit:]
                            session_state["turn_count"] += 1
                            session_state["pending_escalation"] = None
                            session_state["deep_mode_armed"] = False
                            continue
                    # skill is None or forced_result is None
                    await send_chat_message(ws, "Deep analysis is unavailable right now. Please answer 'yes', 'no', or 'cancel'.")
                    await send_chat_done(ws)
                    session_state["pending_escalation"] = None
                    session_state["deep_mode_armed"] = False
                    continue
                elif escalate_decision.action == "cancel":
                    session_state["pending_escalation"] = None
                    session_state["deep_mode_armed"] = False
                    await send_chat_message(ws, "Okay, keeping it brief.")
                    await send_chat_done(ws)
                    continue
                else:
                    await send_chat_message(ws, "Please answer 'yes', 'no', or 'cancel'.")
                    await send_chat_done(ws)
                    continue

            # --- Phaseâ€‘2 immediate commands ---
            if lowered == "stop":
                speech_state.stop()
                stop_speaking()
                await send_chat_message(ws, "Okay.")
                await send_chat_done(ws)
                continue

            if lowered == "repeat":
                last = speech_state.last_spoken_text
                if last:
                    await send_chat_message(ws, last)
                await send_chat_done(ws)
                continue

            if lowered in {"thanks", "thank you", "thank you nova", "thank you, nova"}:
                await send_chat_message(ws, "You're welcome.")
                await send_chat_done(ws)
                continue

            if lowered in {"show sources", "show sources for your last response", "sources"}:
                last_sources = list(session_state.get("last_sources") or [])
                if not last_sources:
                    await send_chat_message(
                        ws,
                        "I don't have citation sources for the last response. "
                        "Use a governed web search or news request, then ask for sources.",
                    )
                else:
                    lines = ["Sources for last response:"]
                    lines.extend(f"{i + 1}. {src}" for i, src in enumerate(last_sources))
                    await send_chat_message(ws, "\n".join(lines))
                await send_chat_done(ws)
                continue

            if lowered in {
                "shorter",
                "shorter version",
                "make that shorter",
                "simplify that",
                "summarize your last response",
                "shorter version of your last response",
                "tldr",
                "tl;dr",
            }:
                prior = str(session_state.get("last_response") or "").strip()
                if not prior:
                    await send_chat_message(ws, "I don't have a previous response to shorten yet.")
                else:
                    short = _make_shorter_followup(prior)
                    session_state["last_response"] = short
                    await send_chat_message(ws, short)
                await send_chat_done(ws)
                continue

            if lowered in {
                "confirm model update",
                "confirm model",
                "approve model update",
                "unlock model",
            }:
                try:
                    from src.llm.llm_gateway import (
                        confirm_model_update as confirm_llm_model_update,
                        is_model_update_pending as llm_model_update_pending,
                    )

                    was_pending_update = llm_model_update_pending()
                    did_confirm_update = confirm_llm_model_update()
                except Exception:
                    was_pending_update = False
                    did_confirm_update = False

                if did_confirm_update:
                    await send_chat_message(
                        ws,
                        "Model update confirmed. Local model responses are now unblocked.",
                    )
                elif was_pending_update:
                    await send_chat_message(
                        ws,
                        "Model update confirmation is still pending. Please try again.",
                    )
                else:
                    await send_chat_message(ws, "No model update confirmation is pending.")
                await send_chat_done(ws)
                continue

            if lowered in PHASE42_HELP_COMMANDS:
                await send_chat_message(
                    ws,
                    (
                        "Use 'phase42: <question>' or 'orthogonal analysis: <question>' "
                        "to run the orthogonal agent stack."
                    ),
                )
                await send_chat_done(ws)
                continue

            phase42_query = _extract_phase42_query(text)
            if phase42_query is not None:
                if not PHASE_4_2_ENABLED or personality_agent is None:
                    await send_chat_message(
                        ws,
                        "Phase 4.2 runtime is locked in this build profile.",
                    )
                    await send_chat_done(ws)
                    continue

                if session_state.get("deep_mode_armed"):
                    personality_agent.arm_deep_mode()
                    session_state["deep_mode_armed"] = False
                    session_state["deep_mode_last_armed_turn"] = session_state.get("turn_count", 0)

                context_payload = {
                    "session_id": session_id,
                    "turn_count": session_state.get("turn_count", 0),
                    "last_response": session_state.get("last_response", ""),
                    "last_sources": list(session_state.get("last_sources") or []),
                    "last_mode": session_state.get("last_mode", ""),
                    "last_intent_family": session_state.get("last_intent_family", ""),
                }

                try:
                    phase42_message = await asyncio.to_thread(
                        personality_agent.run,
                        phase42_query,
                        _build_phase42_agents(),
                        context_payload,
                    )
                except RuntimeError:
                    phase42_message = "Phase 4.2 runtime is locked in this build profile."
                except Exception:
                    phase42_message = "Phase 4.2 analysis is currently unavailable."

                session_state["last_response"] = phase42_message
                speech_state.last_spoken_text = phase42_message
                session_state["trust_status"] = failure_ladder.record_local_success(
                    session_state.get("trust_status", {})
                )
                await send_chat_message(ws, phase42_message, apply_personality=False)
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)

                session_context.extend(
                    [
                        {"role": "user", "content": text},
                        {"role": "assistant", "content": phase42_message},
                    ]
                )
                context_limit = 40 if session_state.get("presence_mode") else 20
                session_context = session_context[-context_limit:]
                session_state["turn_count"] += 1
                continue

            if lowered in {"weather", "weather update", "current weather"}:
                _, weather_result = await invoke_governed_text_command(
                    governor,
                    "weather",
                    session_id,
                )
                if weather_result is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Weather is currently unavailable.", tone_domain="daily")
                    await ws_send(
                        ws,
                        {
                            "type": "weather",
                            "data": {
                                "summary": "Weather is currently unavailable.",
                                "temperature": None,
                                "condition": "Unavailable",
                                "location": "Local",
                                "forecast": "",
                                "alerts": [],
                            },
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="Weather update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                    await send_chat_done(ws)
                    continue
                weather_widget = {}
                if isinstance(weather_result.data, dict):
                    weather_widget = dict(weather_result.data.get("widget") or {})

                if weather_result.success:
                    message = _structure_long_message(weather_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="daily")
                    if isinstance(weather_widget, dict) and weather_widget.get("type") == "weather":
                        await ws_send(ws, weather_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "weather",
                                "data": {
                                    "summary": message,
                                    "temperature": None,
                                    "condition": "",
                                    "location": "Local",
                                    "forecast": "",
                                    "alerts": [],
                                },
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "Weather update",
                    )
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Weather is currently unavailable.", tone_domain="daily")
                    if isinstance(weather_widget, dict) and weather_widget.get("type") == "weather":
                        await ws_send(ws, weather_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "weather",
                                "data": {
                                    "summary": "Weather is currently unavailable.",
                                    "temperature": None,
                                    "condition": "Unavailable",
                                    "location": "Local",
                                    "forecast": "",
                                    "alerts": [],
                                },
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="Weather update",
                    )
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                continue

            if lowered in {"news", "headlines", "latest news", "top news"}:
                _, news_result = await invoke_governed_text_command(
                    governor,
                    "news",
                    session_id,
                )
                if news_result is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "News is currently unavailable.", tone_domain="daily")
                    await ws_send(
                        ws,
                        {
                            "type": "news",
                            "items": [],
                            "summary": "News is currently unavailable.",
                            "categories": {},
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="News update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                    await send_chat_done(ws)
                    continue
                news_widget = {}
                if isinstance(news_result.data, dict):
                    news_widget = dict(news_result.data.get("widget") or {})

                if news_result.success:
                    message = _structure_long_message(news_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="daily")
                    if isinstance(news_widget, dict) and news_widget.get("type") == "news":
                        items = list(news_widget.get("items") or [])
                        categories = dict(news_widget.get("categories") or {})
                        session_state["news_cache"] = items
                        session_state["news_categories"] = categories
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, news_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "news",
                                "items": [],
                                "summary": "News is currently unavailable.",
                                "categories": {},
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "News update",
                    )
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "News is currently unavailable.", tone_domain="daily")
                    if isinstance(news_widget, dict) and news_widget.get("type") == "news":
                        await ws_send(ws, news_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "news",
                                "items": [],
                                "summary": "News is currently unavailable.",
                                "categories": {},
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="News update",
                    )
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                continue

            if lowered in {
                "calendar",
                "calendar update",
                "agenda",
                "schedule",
                "todays schedule",
                "today's schedule",
                "todays calendar",
                "today's calendar",
            }:
                _, calendar_result = await invoke_governed_text_command(
                    governor,
                    "calendar",
                    session_id,
                )
                if calendar_result is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Calendar is currently unavailable.", tone_domain="daily")
                    await send_widget_message(
                        ws,
                        "calendar",
                        "Calendar is currently unavailable.",
                        {"type": "calendar", "summary": "Unavailable.", "events": []},
                    )
                    await send_chat_done(ws)
                    continue
                calendar_widget = {}
                if isinstance(calendar_result.data, dict):
                    calendar_widget = dict(calendar_result.data.get("widget") or {})
                if calendar_result.success:
                    message = _structure_long_message(calendar_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="daily")
                    if isinstance(calendar_widget, dict) and calendar_widget.get("type") == "calendar":
                        await send_widget_message(ws, "calendar", message, calendar_widget)
                        session_state["last_calendar_summary"] = str(calendar_widget.get("summary") or "")
                        session_state["last_calendar_events"] = list(calendar_widget.get("events") or [])
                    else:
                        await send_widget_message(
                            ws,
                            "calendar",
                            message,
                            {"type": "calendar", "summary": message, "events": []},
                        )
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Calendar is currently unavailable.", tone_domain="daily")
                    if isinstance(calendar_widget, dict) and calendar_widget.get("type") == "calendar":
                        await send_widget_message(
                            ws,
                            "calendar",
                            "Calendar is currently unavailable.",
                            calendar_widget,
                        )
                    else:
                        await send_widget_message(
                            ws,
                            "calendar",
                            "Calendar is currently unavailable.",
                            {"type": "calendar", "summary": "Unavailable.", "events": []},
                        )
                await send_chat_done(ws)
                continue

            if lowered in {"system", "system status", "system check"}:
                _, action_result = await invoke_governed_text_command(
                    governor,
                    "system status",
                    session_id,
                )
                if action_result is None:
                    failure_message = "System diagnostics are currently unavailable."
                    if not silent_widget_refresh:
                        await send_chat_message(ws, failure_message, tone_domain="system")
                    await ws_send(
                        ws,
                        {
                            "type": "system",
                            "summary": failure_message,
                            "data": {"status": "unavailable"},
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=False,
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                    await send_chat_done(ws)
                    continue
                if action_result.success:
                    message = _structure_long_message(action_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="system")
                    await ws_send(
                        ws,
                        {
                            "type": "system",
                            "summary": message,
                            "data": dict(action_result.data or {}),
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_local_success(
                        session_state.get("trust_status", {})
                    )
                else:
                    failure_message = "System diagnostics are currently unavailable."
                    if not silent_widget_refresh:
                        await send_chat_message(ws, failure_message, tone_domain="system")
                    await ws_send(
                        ws,
                        {
                            "type": "system",
                            "summary": failure_message,
                            "data": {"status": "unavailable"},
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=False,
                    )
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                continue

            if lowered in TONE_STATUS_COMMANDS:
                snapshot = interface_personality_agent.tone_snapshot()
                _log_ledger_event(
                    governor,
                    "TONE_PROFILE_VIEWED",
                    {
                        "global_profile": str(snapshot.get("global_profile") or "balanced"),
                        "override_count": int(snapshot.get("override_count") or 0),
                    },
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_tone_profile_message(snapshot),
                        tone_domain="system",
                    )
                await send_tone_profile_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            tone_set_match = TONE_SET_RE.match(text)
            if tone_set_match:
                domain, profile, ok = _parse_tone_set_body(tone_set_match.group("body"))
                if not ok:
                    await send_chat_message(
                        ws,
                        "I couldn't parse that tone setting yet.\n\nTry next:\n- tone set concise\n- tone set research detailed\n- tone set system formal",
                        tone_domain="system",
                    )
                    await send_chat_done(ws)
                    continue

                if domain == "global":
                    snapshot = interface_personality_agent.set_global_tone(profile)
                    message = f"Global tone set to {profile}."
                else:
                    snapshot = interface_personality_agent.set_domain_tone(domain, profile)
                    label = ToneProfileStore.DOMAIN_DEFINITIONS.get(domain, domain.title())
                    message = f"{label} tone set to {profile}."

                _log_ledger_event(
                    governor,
                    "TONE_PROFILE_UPDATED",
                    {
                        "domain": domain,
                        "profile": profile,
                        "global_profile": str(snapshot.get("global_profile") or "balanced"),
                        "override_count": int(snapshot.get("override_count") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"{message}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_tone_profile_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            tone_reset_match = TONE_RESET_RE.match(text)
            if tone_reset_match:
                body = str(tone_reset_match.group("body") or "").strip().lower()
                body = re.sub(r"^(?:domain|for)\s+", "", body).strip()
                if not body or body == "all":
                    snapshot = interface_personality_agent.reset_all_tone()
                    message = "Tone settings reset to the default profile."
                    reset_domain = "all"
                else:
                    if body not in ToneProfileStore.DOMAIN_DEFINITIONS:
                        await send_chat_message(
                            ws,
                            "I couldn't find that tone domain yet.\n\nTry next:\n- tone reset research\n- tone reset system\n- tone reset all",
                            tone_domain="system",
                        )
                        await send_chat_done(ws)
                        continue
                    snapshot = interface_personality_agent.reset_domain_tone(body)
                    label = ToneProfileStore.DOMAIN_DEFINITIONS.get(body, body.title())
                    message = f"{label} tone reset to the global profile."
                    reset_domain = body

                _log_ledger_event(
                    governor,
                    "TONE_PROFILE_RESET",
                    {
                        "domain": reset_domain,
                        "global_profile": str(snapshot.get("global_profile") or "balanced"),
                        "override_count": int(snapshot.get("override_count") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"{message}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_tone_profile_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in SHOW_SCHEDULES_COMMANDS:
                snapshot = notification_schedules.summarize()
                if silent_widget_refresh:
                    snapshot = _process_due_notification_delivery(governor, notification_schedules, snapshot)
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_VIEWED",
                    {
                        "active_count": int(snapshot.get("active_count") or 0),
                        "due_count": int(snapshot.get("due_count") or 0),
                    },
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_notification_schedule_message(snapshot),
                        tone_domain="system",
                    )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in NOTIFICATION_SETTINGS_COMMANDS:
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_VIEWED",
                    {
                        "active_count": int(snapshot.get("active_count") or 0),
                        "due_count": int(snapshot.get("due_count") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    _render_notification_settings_message(snapshot),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            set_quiet_hours_match = SET_QUIET_HOURS_RE.match(text)
            if set_quiet_hours_match:
                try:
                    start_hour, start_minute = _parse_clock_time(set_quiet_hours_match.group("start"))
                    end_hour, end_minute = _parse_clock_time(set_quiet_hours_match.group("end"))
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                policy = notification_schedules.update_policy(
                    quiet_hours_enabled=True,
                    quiet_hours_start=f"{start_hour:02d}:{start_minute:02d}",
                    quiet_hours_end=f"{end_hour:02d}:{end_minute:02d}",
                )
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_POLICY_UPDATED",
                    {
                        "quiet_hours_enabled": True,
                        "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
                        "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
                        "max_deliveries_per_hour": int(policy.get("max_deliveries_per_hour") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        "Quiet hours updated.\n"
                        f"Window: {_format_policy_clock_value(str(policy.get('quiet_hours_start') or ''))} to "
                        f"{_format_policy_clock_value(str(policy.get('quiet_hours_end') or ''))}\n\n"
                        f"{_render_notification_settings_message(snapshot)}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if CLEAR_QUIET_HOURS_RE.match(text):
                policy = notification_schedules.update_policy(quiet_hours_enabled=False)
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_POLICY_UPDATED",
                    {
                        "quiet_hours_enabled": False,
                        "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
                        "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
                        "max_deliveries_per_hour": int(policy.get("max_deliveries_per_hour") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"Quiet hours cleared.\n\n{_render_notification_settings_message(snapshot)}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            set_rate_limit_match = SET_NOTIFICATION_RATE_LIMIT_RE.match(text)
            if set_rate_limit_match:
                rate_limit = max(1, min(int(set_rate_limit_match.group("count") or 1), 12))
                policy = notification_schedules.update_policy(max_deliveries_per_hour=rate_limit)
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_POLICY_UPDATED",
                    {
                        "quiet_hours_enabled": bool(policy.get("quiet_hours_enabled")),
                        "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
                        "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
                        "max_deliveries_per_hour": int(policy.get("max_deliveries_per_hour") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"Notification rate limit updated to {rate_limit} per hour.\n\n{_render_notification_settings_message(snapshot)}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            schedule_brief_match = SCHEDULE_BRIEF_RE.match(text)
            if schedule_brief_match:
                try:
                    scheduled_for = _parse_schedule_datetime(
                        schedule_brief_match.group("time"),
                        recurrence="daily",
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                item = notification_schedules.create_schedule(
                    kind="daily_brief",
                    title="Daily brief",
                    body="Run your scheduled daily brief.",
                    recurrence="daily",
                    next_run_at=scheduled_for,
                    command="morning brief",
                )
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_CREATED",
                    {
                        "schedule_id": item["id"],
                        "kind": item["kind"],
                        "recurrence": item["recurrence"],
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Daily brief scheduled: {item['id']}\n"
                        f"Next run: {_format_local_schedule_time(scheduled_for)}\n\n"
                        f"{str(snapshot.get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            remind_me_match = REMIND_ME_RE.match(text)
            if remind_me_match:
                recurrence = "daily" if remind_me_match.group("daily") else "once"
                try:
                    scheduled_for = _parse_schedule_datetime(
                        remind_me_match.group("time"),
                        recurrence=recurrence,
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                reminder_body = str(remind_me_match.group("body") or "").strip()
                item = notification_schedules.create_schedule(
                    kind="reminder",
                    title=f"Reminder: {reminder_body[:80]}",
                    body=reminder_body,
                    recurrence=recurrence,
                    next_run_at=scheduled_for,
                )
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_CREATED",
                    {
                        "schedule_id": item["id"],
                        "kind": item["kind"],
                        "recurrence": item["recurrence"],
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Reminder scheduled: {item['id']}\n"
                        f"Text: {reminder_body}\n"
                        f"Next run: {_format_local_schedule_time(scheduled_for)}\n\n"
                        f"{str(snapshot.get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            reschedule_schedule_match = RESCHEDULE_SCHEDULE_RE.match(text)
            if reschedule_schedule_match:
                schedule_id = str(reschedule_schedule_match.group("schedule_id") or "").strip().upper()
                existing = notification_schedules.get_schedule(schedule_id)
                if existing is None:
                    await send_chat_message(ws, "I could not find that schedule ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                recurrence = str(existing.get("recurrence") or "once").strip().lower() or "once"
                try:
                    scheduled_for = _parse_schedule_datetime(
                        reschedule_schedule_match.group("time"),
                        recurrence=recurrence,
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                item = notification_schedules.reschedule_schedule(schedule_id, next_run_at=scheduled_for)
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_UPDATED",
                    {
                        "schedule_id": schedule_id,
                        "kind": str(item.get("kind") or ""),
                        "recurrence": str(item.get("recurrence") or ""),
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Schedule updated: {schedule_id}\n"
                        f"Next run: {_format_local_schedule_time(scheduled_for)}\n\n"
                        f"{str(snapshot.get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            cancel_schedule_match = CANCEL_SCHEDULE_RE.match(text)
            if cancel_schedule_match:
                schedule_id = str(cancel_schedule_match.group("schedule_id") or "").strip().upper()
                try:
                    item = notification_schedules.cancel_schedule(schedule_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that schedule ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_CANCELLED",
                    {"schedule_id": schedule_id, "kind": str(item.get("kind") or "")},
                )
                await send_chat_message(
                    ws,
                    f"Schedule cancelled: {schedule_id}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            dismiss_schedule_match = DISMISS_SCHEDULE_RE.match(text)
            if dismiss_schedule_match:
                schedule_id = str(dismiss_schedule_match.group("schedule_id") or "").strip().upper()
                try:
                    item = notification_schedules.dismiss_schedule(schedule_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that schedule ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_DISMISSED",
                    {"schedule_id": schedule_id, "kind": str(item.get("kind") or "")},
                )
                if bool(item.get("active")):
                    _log_ledger_event(
                        governor,
                        "NOTIFICATION_SCHEDULE_UPDATED",
                        {
                            "schedule_id": schedule_id,
                            "kind": str(item.get("kind") or ""),
                            "recurrence": str(item.get("recurrence") or ""),
                        },
                    )
                await send_chat_message(
                    ws,
                    f"Schedule dismissed: {schedule_id}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if PATTERN_OPT_IN_RE.match(text):
                snapshot = pattern_reviews.set_opt_in(True)
                _log_ledger_event(
                    governor,
                    "PATTERN_DETECTION_OPTED_IN",
                    {"active_count": int(snapshot.get("active_count") or 0)},
                )
                await send_chat_message(
                    ws,
                    (
                        "Pattern review enabled.\n\n"
                        "Nova will only generate pattern proposals when you explicitly ask for them.\n"
                        "Try next:\n"
                        "- review patterns\n"
                        "- review patterns for deployment issue\n"
                        "- pattern status"
                    ),
                    tone_domain="system",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if PATTERN_OPT_OUT_RE.match(text):
                snapshot = pattern_reviews.set_opt_in(False)
                _log_ledger_event(
                    governor,
                    "PATTERN_DETECTION_OPTED_OUT",
                    {"active_count": int(snapshot.get("active_count") or 0)},
                )
                await send_chat_message(
                    ws,
                    "Pattern review disabled. Existing queued proposals have been cleared.",
                    tone_domain="system",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in PATTERN_STATUS_COMMANDS:
                snapshot = pattern_reviews.snapshot()
                _log_ledger_event(
                    governor,
                    "PATTERN_REVIEW_VIEWED",
                    {
                        "opt_in_enabled": bool(snapshot.get("opt_in_enabled")),
                        "active_count": int(snapshot.get("active_count") or 0),
                    },
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_pattern_review_message(snapshot),
                        tone_domain="system",
                    )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            pattern_review_match = PATTERN_REVIEW_RE.match(text)
            if pattern_review_match:
                snapshot = pattern_reviews.snapshot()
                if not bool(snapshot.get("opt_in_enabled")):
                    await send_chat_message(
                        ws,
                        "Pattern review is off right now. Say 'pattern opt in' first if you want Nova to generate advisory pattern proposals.",
                        tone_domain="system",
                    )
                    await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                    await send_chat_done(ws)
                    continue

                requested_thread = str(pattern_review_match.group("name") or "").strip()
                resolved_thread_name = ""
                if requested_thread:
                    found, resolved_name, _ = project_threads.resolve_thread_identity(requested_thread)
                    resolved_thread_name = resolved_name if found else requested_thread

                from src.memory.governed_memory_store import GovernedMemoryStore

                thread_summaries = project_threads.list_summaries()
                memory_insights = GovernedMemoryStore().summarize_thread_insights()
                snapshot = pattern_reviews.generate_review(
                    thread_summaries=thread_summaries,
                    memory_insights=memory_insights,
                    thread_name=resolved_thread_name,
                )
                _log_ledger_event(
                    governor,
                    "PATTERN_REVIEW_GENERATED",
                    {
                        "active_count": int(snapshot.get("active_count") or 0),
                        "thread_name": resolved_thread_name,
                    },
                )
                await send_chat_message(
                    ws,
                    _render_pattern_review_message(snapshot),
                    tone_domain="continuity",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            accept_pattern_match = ACCEPT_PATTERN_RE.match(text)
            if accept_pattern_match:
                pattern_id = str(accept_pattern_match.group("pattern_id") or "").strip().upper()
                try:
                    snapshot, proposal = pattern_reviews.accept_proposal(pattern_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that pattern ID in the current review queue.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "PATTERN_PROPOSAL_ACCEPTED",
                    {"pattern_id": pattern_id, "kind": str(proposal.get("kind") or "")},
                )
                suggested_commands = [
                    {"label": command.title(), "command": command}
                    for command in list(proposal.get("suggested_commands") or [])[:3]
                ]
                await send_chat_message(
                    ws,
                    (
                        f"Pattern accepted for review: {str(proposal.get('title') or '').strip()}\n\n"
                        "No action has been taken automatically. Use an explicit command if you want to act on this proposal."
                    ),
                    tone_domain="continuity",
                    suggested_actions=suggested_commands or None,
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            dismiss_pattern_match = DISMISS_PATTERN_RE.match(text)
            if dismiss_pattern_match:
                pattern_id = str(dismiss_pattern_match.group("pattern_id") or "").strip().upper()
                try:
                    snapshot, proposal = pattern_reviews.dismiss_proposal(pattern_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that pattern ID in the current review queue.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "PATTERN_PROPOSAL_DISMISSED",
                    {"pattern_id": pattern_id, "kind": str(proposal.get("kind") or "")},
                )
                await send_chat_message(
                    ws,
                    f"Pattern dismissed: {str(proposal.get('title') or '').strip()}",
                    tone_domain="continuity",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in POLICY_STATUS_COMMANDS:
                snapshot = policy_drafts.overview()
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_VIEWED",
                    {"active_count": int(snapshot.get("active_count") or 0)},
                )
                await send_chat_message(
                    ws,
                    _render_policy_overview_message(snapshot),
                    tone_domain="system",
                )
                await send_chat_done(ws)
                continue

            policy_create_match = POLICY_CREATE_RE.match(text)
            if policy_create_match:
                try:
                    compiled_policy = _compile_atomic_policy_template(
                        policy_create_match.group("schedule"),
                        policy_create_match.group("action"),
                        policy_create_match.group("time"),
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue

                validation = governor.validate_atomic_policy(compiled_policy)
                _log_ledger_event(
                    governor,
                    "POLICY_VALIDATED",
                    {
                        "valid": bool(validation.valid),
                        "capability_id": int(dict(compiled_policy.get("action") or {}).get("capability_id") or 0),
                        "trigger_type": str(dict(compiled_policy.get("trigger") or {}).get("type") or ""),
                    },
                )
                if not validation.valid:
                    _log_ledger_event(
                        governor,
                        "POLICY_VALIDATION_REJECTED",
                        {
                            "reason_count": len(list(validation.reasons or [])),
                            "capability_id": int(dict(compiled_policy.get("action") or {}).get("capability_id") or 0),
                        },
                    )
                    rejection_lines = ["Policy draft rejected", ""]
                    rejection_lines.extend(f"- {str(reason).strip()}" for reason in list(validation.reasons or []) if str(reason).strip())
                    rejection_lines.extend(
                        [
                            "",
                            "Try next:",
                            "- policy create weekday calendar snapshot at 8:00 am",
                            "- policy create daily weather snapshot at 7:30 am",
                        ]
                    )
                    await send_chat_message(ws, "\n".join(rejection_lines), tone_domain="system")
                    await send_chat_done(ws)
                    continue

                item = policy_drafts.create_draft(policy=compiled_policy, validation_result=validation)
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_CREATED",
                    {
                        "policy_id": str(item.get("policy_id") or ""),
                        "capability_id": int(dict(item.get("action") or {}).get("capability_id") or 0),
                        "trigger_type": str(dict(item.get("trigger") or {}).get("type") or ""),
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Policy draft created: {str(item.get('policy_id') or '').strip()}\n"
                        f"Trigger: {_describe_policy_trigger(item.get('trigger'))}\n"
                        f"Action: {_describe_policy_action(item.get('action'))}\n"
                        "State: draft (disabled)\n\n"
                        "This slice stores and validates draft policies. You can now simulate them and manually review-run safe ones once, but trigger execution is not active yet.\n\n"
                        f"{str(policy_drafts.overview().get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_chat_done(ws)
                continue

            policy_show_match = POLICY_SHOW_RE.match(text)
            if policy_show_match:
                policy_id = str(policy_show_match.group("policy_id") or "").strip().upper()
                item = policy_drafts.get_policy(policy_id)
                if item is None or str(item.get("state") or "") == "deleted":
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_VIEWED",
                    {"policy_id": policy_id, "state": str(item.get("state") or "draft")},
                )
                await send_chat_message(
                    ws,
                    _render_policy_detail_message(item),
                    tone_domain="system",
                )
                await send_chat_done(ws)
                continue

            policy_simulate_match = POLICY_SIMULATE_RE.match(text)
            if policy_simulate_match:
                policy_id = str(policy_simulate_match.group("policy_id") or "").strip().upper()
                item = policy_drafts.get_policy(policy_id)
                if item is None or str(item.get("state") or "") == "deleted":
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue

                decision = governor.simulate_atomic_policy(item)
                item = policy_drafts.record_simulation(policy_id, decision.as_dict())
                await send_chat_message(
                    ws,
                    _render_policy_simulation_message(decision.as_dict()),
                    tone_domain="system",
                )
                await send_chat_done(ws)
                continue

            policy_run_match = POLICY_RUN_ONCE_RE.match(text)
            if policy_run_match:
                policy_id = str(policy_run_match.group("policy_id") or "").strip().upper()
                if not str(policy_run_match.group("once") or "").strip():
                    await send_chat_message(
                        ws,
                        f"Manual delegated review runs need explicit confirmation.\n\nTry next:\n- policy run {policy_id} once",
                        tone_domain="system",
                    )
                    await send_chat_done(ws)
                    continue

                item = policy_drafts.get_policy(policy_id)
                if item is None or str(item.get("state") or "") == "deleted":
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue

                decision, policy_result = governor.run_atomic_policy_once(item)
                item = policy_drafts.record_manual_run(
                    policy_id,
                    decision.as_dict(),
                    {
                        "success": bool(policy_result.success),
                        "message": str(policy_result.message or "").strip(),
                        "request_id": str(policy_result.request_id or "").strip(),
                        "authority_class": str(policy_result.authority_class or "read_only").strip(),
                        "external_effect": bool(policy_result.external_effect),
                        "reversible": bool(policy_result.reversible),
                    },
                )
                await send_chat_message(
                    ws,
                    _render_policy_run_message(decision.as_dict(), policy_result),
                    tone_domain="system",
                )

                if (
                    isinstance(policy_result.data, dict)
                    and "widget" in policy_result.data
                    and policy_result.success
                ):
                    await ws_send(ws, policy_result.data["widget"])
                elif int(dict(item.get("action") or {}).get("capability_id") or 0) == 32 and policy_result.success:
                    if isinstance(policy_result.data, dict):
                        await ws_send(ws, {"type": "system", "data": policy_result.data, "summary": policy_result.message})

                await send_chat_done(ws)
                continue

            policy_delete_match = POLICY_DELETE_RE.match(text)
            if policy_delete_match:
                policy_id = str(policy_delete_match.group("policy_id") or "").strip().upper()
                confirmed = bool(str(policy_delete_match.group("confirm") or "").strip())
                if not confirmed:
                    await send_chat_message(
                        ws,
                        f"Deleting a policy draft needs confirmation.\n\nTry next:\n- policy delete {policy_id} confirm",
                        tone_domain="system",
                    )
                    await send_chat_done(ws)
                    continue
                try:
                    item = policy_drafts.delete_policy(policy_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_DELETED",
                    {"policy_id": policy_id, "state": str(item.get("state") or "deleted")},
                )
                await send_chat_message(
                    ws,
                    f"Policy draft deleted: {policy_id}\n\n{str(policy_drafts.overview().get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_chat_done(ws)
                continue

            if lowered in {"morning", "morning brief", "brief"}:
                weather_summary = "Weather unavailable."
                news_summary = "No headline summary available right now."
                system_line = "System status unavailable."
                calendar_line = "Calendar unavailable."

                _, weather_result = await invoke_governed_text_command(
                    governor,
                    "weather",
                    session_id,
                )
                if weather_result is not None and weather_result.success:
                    weather_summary = weather_result.message
                    if isinstance(weather_result.data, dict):
                        widget = weather_result.data.get("widget")
                        if isinstance(widget, dict):
                            await ws_send(ws, widget)
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "Weather update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])

                _, news_result = await invoke_governed_text_command(
                    governor,
                    "news",
                    session_id,
                )
                if news_result is not None and news_result.success and isinstance(news_result.data, dict):
                    news_widget = news_result.data.get("widget")
                    if isinstance(news_widget, dict):
                        news_summary = str(news_widget.get("summary") or news_summary)
                        items = list(news_widget.get("items") or [])
                        session_state["news_cache"] = items
                        session_state["news_categories"] = dict(news_widget.get("categories") or {})
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, news_widget)
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "News update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])

                _, system_result = await invoke_governed_text_command(
                    governor,
                    "system status",
                    session_id,
                )
                if system_result is not None and system_result.success:
                    system_line = system_result.message
                    if isinstance(system_result.data, dict):
                        await ws_send(
                            ws,
                            {
                                "type": "system",
                                "summary": system_line,
                                "data": dict(system_result.data),
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_local_success(
                        session_state.get("trust_status", {})
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                else:
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=False,
                    )
                    await send_trust_status(ws, session_state["trust_status"])

                _, calendar_result = await invoke_governed_text_command(
                    governor,
                    "calendar",
                    session_id,
                )
                if calendar_result is not None and calendar_result.success and isinstance(calendar_result.data, dict):
                    calendar_widget = calendar_result.data.get("widget")
                    if isinstance(calendar_widget, dict):
                        calendar_line = str(
                            calendar_widget.get("summary")
                            or calendar_result.message
                            or calendar_line
                        )
                        session_state["last_calendar_summary"] = calendar_line
                        session_state["last_calendar_events"] = list(calendar_widget.get("events") or [])
                        await send_widget_message(
                            ws,
                            "calendar",
                            calendar_result.message,
                            calendar_widget,
                        )
                    else:
                        calendar_line = calendar_result.message

                morning_brief = (
                    "Executive Brief\n"
                    f"- Weather: {weather_summary}\n"
                    f"- System: {system_line}\n"
                    f"- News: {news_summary}\n"
                    f"- Calendar: {calendar_line}"
                )
                await send_chat_message(ws, morning_brief, tone_domain="daily")
                await send_chat_done(ws)
                continue

            # --- Manual Session Presence Mode Controls (Tier-B explicit only) ---
            if lowered in {"stay in conversation mode", "conversation mode on", "enable conversation mode"}:
                session_state["presence_mode"] = True
                await send_chat_message(ws, "Conversation mode enabled for this session.")
                await send_chat_done(ws)
                continue

            if lowered in {"conversation mode off", "disable conversation mode", "exit conversation mode"}:
                session_state["presence_mode"] = False
                await send_chat_message(ws, "Conversation mode disabled for this session.")
                await send_chat_done(ws)
                continue

            # --- Governor mediation ---
            mediated_text = GovernorMediator.mediate(text)

            # --- Phaseâ€‘4 governed invocation detection ---
            inv_result = GovernorMediator.parse_governed_invocation(mediated_text, session_id=session_id)
            if inv_result is None and lowered in {"more", "tell me more", "more please"}:
                try:
                    last_story_index = int(session_state.get("last_news_story_index") or 0)
                except Exception:
                    last_story_index = 0
                if last_story_index > 0:
                    inv_result = Invocation(
                        capability_id=49,
                        params={"action": "story_page_summary", "story_index": last_story_index},
                    )

            if isinstance(inv_result, Invocation):
                capability_id = inv_result.capability_id
                params = dict(inv_result.params)
                params.setdefault("session_id", session_id)
                if capability_id == 18 and not params.get("text"):
                    params["text"] = session_state.get("last_response", "")
                if capability_id == 31 and not params.get("text"):
                    params["text"] = session_state.get("last_response", "")
                if capability_id in {49, 50, 51, 52, 53}:
                    if not session_state.get("news_cache"):
                        _, snapshot_result = await invoke_governed_text_command(
                            governor,
                            "news",
                            session_id,
                        )
                        if (
                            snapshot_result is not None
                            and snapshot_result.success
                            and isinstance(snapshot_result.data, dict)
                        ):
                            snapshot_widget = snapshot_result.data.get("widget")
                            if isinstance(snapshot_widget, dict):
                                items = list(snapshot_widget.get("items") or [])
                                categories = dict(snapshot_widget.get("categories") or {})
                                session_state["news_cache"] = items
                                session_state["news_categories"] = categories
                                session_state["last_sources"] = _extract_sources_from_results(items)
                                session_state["last_source_links"] = _extract_source_links(items)
                                await ws_send(ws, snapshot_widget)
                    params.setdefault("headlines", list(session_state.get("news_cache") or []))
                    params.setdefault("categories", dict(session_state.get("news_categories") or {}))
                    params.setdefault("topic_history", dict(session_state.get("topic_memory_map") or {}))
                    if capability_id == 49 and str(params.get("action") or "").strip().lower() == "story_page_summary":
                        try:
                            resolved_story_index = int(params.get("story_index") or 0)
                        except Exception:
                            resolved_story_index = 0
                        if resolved_story_index <= 0:
                            try:
                                resolved_story_index = int(session_state.get("last_news_story_index") or 0)
                            except Exception:
                                resolved_story_index = 0
                        if resolved_story_index <= 0:
                            await send_chat_message(
                                ws,
                                "I need a story number first. Try 'summary of story 1' after loading news headlines.",
                            )
                            await send_chat_done(ws)
                            continue
                        params["story_index"] = resolved_story_index
                    if capability_id == 50:
                        params.setdefault("brief_clusters", list(session_state.get("last_brief_clusters") or []))
                if capability_id == 17:
                    source_index = params.get("source_index")
                    if source_index is not None:
                        try:
                            source_idx = int(source_index) - 1
                        except Exception:
                            source_idx = -1
                        source_links = session_state.get("last_source_links") or []
                        if 0 <= source_idx < len(source_links):
                            params["resolved_url"] = str(source_links[source_idx].get("url") or "")
                            params["source_label"] = str(source_links[source_idx].get("source") or "")
                        else:
                            await send_chat_message(ws, "I couldn't find that source index. Ask for sources first.")
                            await send_chat_done(ws)
                            continue
                if capability_id == 54:
                    params.setdefault("analysis_documents", list(session_state.get("analysis_documents") or []))
                    if params.get("doc_id") in {None, ""} and session_state.get("last_analysis_doc_id") is not None:
                        params["doc_id"] = session_state.get("last_analysis_doc_id")
                if capability_id in {58, 59, 60}:
                    params["invocation_source"] = invocation_source
                    if capability_id == 60:
                        params.setdefault("working_context", working_context.for_explain())
                    else:
                        params.setdefault("working_context", working_context.to_dict())
                if capability_id == 61:
                    prepared_ok, prepared_params, prepared_message = _prepare_memory_bridge_params(
                        params=params,
                        project_threads=project_threads,
                    )
                    if not prepared_ok:
                        await send_chat_message(ws, prepared_message)
                        await send_chat_done(ws)
                        continue
                    params = prepared_params

                if capability_id == 22 and not params.get("confirmed"):
                    target = str(params.get("target") or "").strip()
                    path = str(params.get("path") or "").strip()
                    resource = path or target or "that location"
                    session_state["pending_governed_confirm"] = {
                        "capability_id": capability_id,
                        "params": dict(params),
                    }
                    await send_chat_message(
                        ws,
                        (
                            f"Open {resource}?\n"
                            "This action needs confirmation.\n"
                            "Reply 'yes' to proceed or 'no' to cancel."
                        ),
                    )
                    await send_chat_done(ws)
                    continue

                if capability_id == 17:
                    plan = plan_web_open(params)
                    if not plan.get("ok"):
                        await send_chat_message(ws, str(plan.get("message") or "I couldn't resolve that website."))
                        await send_chat_done(ws)
                        continue
                    if plan.get("requires_confirmation") and not params.get("confirmed") and not params.get("preview"):
                        session_state["pending_web_open"] = {
                            "target": params.get("target", ""),
                            "resolved_url": plan.get("url", ""),
                            "preview": bool(params.get("preview")),
                        }
                        await send_chat_message(
                            ws,
                            (
                                f"Open {plan.get('domain', plan.get('url', 'this website'))}?\n"
                                f"URL: {plan.get('url', '')}\n"
                                "Reply 'yes' to open or 'no' to cancel."
                            ),
                        )
                        await send_chat_done(ws)
                        continue

                action_result = await invoke_governed_capability(governor, capability_id, params)
                track_topic_hint = ""
                if capability_id == 50 and params.get("action") == "track_cluster":
                    if isinstance(action_result.data, dict):
                        track_topic_hint = str(action_result.data.get("track_topic") or "").strip()
                if isinstance(action_result.data, dict):
                    context_snapshot = action_result.data.get("context_snapshot")
                    if isinstance(context_snapshot, dict):
                        working_context.apply_snapshot(context_snapshot)
                    working_context_delta = action_result.data.get("working_context_delta")
                    if isinstance(working_context_delta, dict):
                        working_context.apply_patch(
                            working_context_delta,
                            source=f"capability_{capability_id}",
                        )
                    topic_map = action_result.data.get("topic_map")
                    if isinstance(topic_map, dict):
                        session_state["topic_memory_map"] = topic_map
                    widget = action_result.data.get("widget")
                    if isinstance(widget, dict) and widget.get("type") == "search":
                        search_data = widget.get("data") if isinstance(widget.get("data"), dict) else {}
                        results = search_data.get("results") if isinstance(search_data, dict) else []
                        if isinstance(results, list):
                            session_state["last_sources"] = _extract_sources_from_results(results)
                            session_state["last_source_links"] = _extract_source_links(results)
                    if isinstance(widget, dict) and widget.get("type") == "news":
                        items = list(widget.get("items") or [])
                        session_state["news_cache"] = items
                        session_state["news_categories"] = dict(widget.get("categories") or {})
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        session_state["last_source_links"] = _extract_source_links(items)
                    if isinstance(widget, dict) and widget.get("type") == "calendar":
                        session_state["last_calendar_summary"] = str(widget.get("summary") or "")
                        session_state["last_calendar_events"] = list(widget.get("events") or [])
                    analysis_docs = action_result.data.get("analysis_documents")
                    if isinstance(analysis_docs, list):
                        session_state["analysis_documents"] = analysis_docs
                    if capability_id == 61:
                        memory_item = action_result.data.get("memory_item")
                        if isinstance(memory_item, dict):
                            item_id = str(memory_item.get("id") or "").strip()
                            if item_id:
                                session_state["last_memory_item_id"] = item_id
                            links = dict(memory_item.get("links") or {})
                            linked_thread = str(links.get("project_thread_name") or "").strip()
                            if linked_thread:
                                session_state["project_thread_active"] = linked_thread
                        overview_data = action_result.data.get("memory_overview")
                        if isinstance(overview_data, dict):
                            await send_memory_overview_widget(
                                ws,
                                session_state,
                                overview=overview_data,
                            )
                        elif action_result.success:
                            await send_memory_overview_widget(ws, session_state)
                    sources = action_result.data.get("sources")
                    if isinstance(sources, list) and sources:
                        session_state["last_sources"] = [str(src) for src in sources[:10]]
                    if capability_id == 17 and isinstance(action_result.data.get("opened_domain"), str):
                        session_state["last_sources"] = [action_result.data.get("opened_domain")]
                    brief_clusters = action_result.data.get("brief_clusters")
                    if isinstance(brief_clusters, list):
                        session_state["last_brief_clusters"] = brief_clusters
                        flattened_links: list[dict[str, str]] = []
                        for cluster in brief_clusters:
                            if not isinstance(cluster, dict):
                                continue
                            for item in (cluster.get("items") or []):
                                if not isinstance(item, dict):
                                    continue
                                url = str(item.get("url") or "").strip()
                                if not url:
                                    continue
                                flattened_links.append(
                                    {
                                        "url": url,
                                        "source": str(item.get("source") or "").strip(),
                                        "title": str(item.get("title") or "").strip(),
                                    }
                                )
                        if flattened_links:
                            session_state["last_source_links"] = _extract_source_links(flattened_links)
                    if "document_id" in action_result.data:
                        session_state["last_analysis_doc_id"] = action_result.data.get("document_id")
                        working_context.set_open_report_id(action_result.data.get("document_id"))

                if capability_id == 22 and action_result.success:
                    opened_path = str(params.get("path") or "").strip()
                    if opened_path:
                        working_context.set_selected_file(opened_path)

                session_state["working_context"] = working_context.to_dict()

                if capability_id != 18 and action_result.message:
                    session_state["last_response"] = action_result.message

                if capability_id in {16, 48, 55, 56}:
                    if action_result.success:
                        session_state["trust_status"] = failure_ladder.record_external_success(
                            session_state.get("trust_status", {}),
                            "Governed web search",
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=True,
                            last_external_call="Governed web search",
                        )
                else:
                    if action_result.success:
                        session_state["trust_status"] = failure_ladder.record_local_success(
                            session_state.get("trust_status", {})
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=False,
                        )
                await send_trust_status(ws, session_state["trust_status"])

                message_confidence: Optional[str] = None
                message_suggestions: list[dict[str, str]] | None = None
                if capability_id == 31 and isinstance(action_result.data, dict):
                    accuracy_label = str(action_result.data.get("verification_accuracy_label") or "").strip()
                    confidence_label = str(action_result.data.get("verification_confidence_label") or "").strip()
                    if accuracy_label:
                        message_confidence = f"Claim reliability {accuracy_label}"
                    elif confidence_label:
                        message_confidence = f"Verification {confidence_label}"
                    if action_result.data.get("verification_recommended") is True:
                        message_suggestions = [
                            {"label": "Re-check with sources", "command": "show sources for your last response"},
                            {"label": "Summarize risk", "command": "summarize verification risks in 3 bullets"},
                            {"label": "Revise answer", "command": "revise your last answer using this verification report"},
                        ]
                if capability_id == 49 and isinstance(action_result.data, dict):
                    story_index = int(action_result.data.get("story_index") or 0)
                    if story_index > 0:
                        session_state["last_news_story_index"] = story_index
                        if not message_suggestions:
                            message_suggestions = [
                                {"label": "More", "command": "more"},
                                {"label": "Summarize all", "command": "summarize all headlines"},
                                {"label": "Today's brief", "command": "today's news"},
                            ]
                    elif action_result.success:
                        widget = action_result.data.get("widget")
                        if isinstance(widget, dict):
                            widget_data = widget.get("data")
                            if isinstance(widget_data, dict):
                                indices = widget_data.get("indices")
                                if isinstance(indices, list) and indices:
                                    try:
                                        session_state["last_news_story_index"] = int(indices[0])
                                    except Exception:
                                        pass
                    related_pairs = action_result.data.get("related_pairs")
                    if isinstance(related_pairs, list) and related_pairs:
                        pair = next((p for p in related_pairs if isinstance(p, dict)), {})
                        left = int(pair.get("left_index") or 0)
                        right = int(pair.get("right_index") or 0)
                        if left > 0 and right > 0:
                            message_suggestions = [
                                {"label": f"Compare {left} vs {right}", "command": f"compare headlines {left} and {right}"},
                                {"label": "Summarize all", "command": "summarize all headlines"},
                                {"label": "Today's brief", "command": "today's news"},
                            ]
                if capability_id == 50 and track_topic_hint and not message_suggestions:
                    message_suggestions = [
                        {"label": "Track this story", "command": f"track story {track_topic_hint}"},
                        {"label": "Show topic map", "command": "show topic map"},
                        {"label": "Today's brief", "command": "today's news"},
                    ]
                if capability_id == 61 and action_result.success and isinstance(action_result.data, dict):
                    memory_item = action_result.data.get("memory_item")
                    if isinstance(memory_item, dict):
                        item_id = str(memory_item.get("id") or "").strip()
                        links = dict(memory_item.get("links") or {})
                        linked_thread = str(links.get("project_thread_name") or "").strip()
                        suggestion_items: list[dict[str, str]] = []
                        if item_id:
                            suggestion_items.append({"label": "Show memory item", "command": f"memory show {item_id}"})
                        if linked_thread:
                            suggestion_items.append(
                                {"label": f"Continue {linked_thread}", "command": f"continue my {linked_thread}"}
                            )
                            suggestion_items.append(
                                {"label": f"Memory for {linked_thread}", "command": f"memory list thread {linked_thread}"}
                            )
                        suggestion_items.append({"label": "Memory overview", "command": "memory overview"})
                        if suggestion_items:
                            message_suggestions = suggestion_items

                recommendation_reason = ""
                if action_result.success and capability_id in {54, 59, 60}:
                    suggested_thread = project_threads.suggest_thread_name(
                        preferred_name=str(session_state.get("project_thread_active") or ""),
                        context_hint=working_context.followup_target(),
                    )
                    extra_actions: list[dict[str, str]] = []
                    if suggested_thread:
                        extra_actions.append(
                            {
                                "label": f"Save to {suggested_thread}",
                                "command": f"save this as part of {suggested_thread}",
                            }
                        )
                        extra_actions.append(
                            {
                                "label": f"Continue {suggested_thread}",
                                "command": f"continue my {suggested_thread}",
                            }
                        )
                    else:
                        thread_hint = _extract_topic_candidate(str(working_context.followup_target() or text)) or "current project"
                        extra_actions.append(
                            {
                                "label": "Create project thread",
                                "command": f"create thread {thread_hint}",
                            }
                        )
                    recommendation_reason = _derive_recommendation_reason(
                        capability_id=capability_id,
                        action_result=action_result,
                        working_context=working_context,
                    )
                    if recommendation_reason:
                        session_state["last_recommendation_reason"] = recommendation_reason
                        extra_actions.append(
                            {"label": "Why this recommendation", "command": "why this recommendation"}
                        )
                    extra_actions.append({"label": "Show threads", "command": "show threads"})
                    if message_suggestions:
                        merged = list(message_suggestions) + extra_actions
                    else:
                        merged = extra_actions
                    deduped: list[dict[str, str]] = []
                    seen_commands: set[str] = set()
                    for item in merged:
                        cmd = str(item.get("command") or "").strip().lower()
                        if not cmd or cmd in seen_commands:
                            continue
                        seen_commands.add(cmd)
                        deduped.append(item)
                    message_suggestions = deduped[:4]

                outgoing_message = _structure_long_message(action_result.message)
                if not outgoing_message.strip() and capability_id == 18 and action_result.success:
                    outgoing_message = "Speaking now."
                if recommendation_reason:
                    outgoing_message = (
                        f"{outgoing_message}\n\n"
                        "Why this recommendation\n"
                        f"- {recommendation_reason}"
                    )
                await send_chat_message(
                    ws,
                    outgoing_message,
                    confidence=message_confidence,
                    suggested_actions=message_suggestions,
                    tone_domain=_tone_domain_for_capability(capability_id),
                )

                if (
                    isinstance(action_result.data, dict)
                    and "widget" in action_result.data
                    and (action_result.success or capability_id in {55, 56, 57})
                ):
                    await ws_send(ws, action_result.data["widget"])
                elif capability_id == 32 and action_result.success and isinstance(action_result.data, dict):
                    await ws_send(ws, {"type": "system", "data": action_result.data, "summary": action_result.message})

                await send_chat_done(ws)

                # Autoâ€‘speak for voice input (only if not a TTS invocation)
                if (session_state.get("last_input_channel") == "voice"
                        and action_result.success
                        and capability_id != 18):
                    session_state["last_input_channel"] = None   # prevent re-trigger
                session_state["turn_count"] += 1
                continue

            elif isinstance(inv_result, Clarification):
                await send_chat_message(
                    ws,
                    inv_result.message,
                    suggested_actions=_clarification_suggestions(inv_result.message),
                )
                await send_chat_done(ws)
                session_state["turn_count"] += 1
                continue

            # --- inv_result is None â€“ proceed to Phaseâ€‘3.5 handling ---

            # --- Quick Corrections ---
            if mediated_text.startswith("Correction:"):
                correction_text = mediated_text[len("Correction:"):].strip()
                if correction_text:
                    record_correction(correction_text)
                await send_chat_message(ws, "Okay. Correction noted.")
                await send_chat_done(ws)
                continue

            # --- Confirmation gate ---
            if confirmation_gate.has_pending_confirmation():
                gate_result = confirmation_gate.try_resolve(mediated_text)
                if gate_result.message is not None:
                    await send_chat_message(ws, gate_result.message)
                    await send_chat_done(ws)
                    continue

            # --- Skills ---
            skill_result = None
            for skill in skill_registry.skills:
                skill_name = str(getattr(skill, "name", "") or "").strip().lower()
                if skill_name in {"weather", "news", "calendar", "system"}:
                    # These flows are capability-routed and must remain governed.
                    continue
                if not skill.can_handle(mediated_text):
                    continue
                if getattr(skill, "name", "") == "general_chat":
                    skill_result = await skill.handle(mediated_text, session_context, session_state)
                else:
                    maybe = skill.handle(mediated_text)
                    skill_result = await maybe if hasattr(maybe, "__await__") else maybe
                break

            if skill_result:
                skill_name = getattr(skill_result, "skill", "") or ""
                skill_tone_domain = _tone_domain_for_skill(skill_name)
                message = getattr(skill_result, "message", "") or ""
                widget_data = getattr(skill_result, "widget_data", None)
                result_data = getattr(skill_result, "data", {}) or {}

                payload = response_formatter.format_payload(
                    message,
                    speakable_text=(result_data.get("speakable_text") or ""),
                    structured_data=(result_data.get("structured_data") or {}),
                )
                message = _structure_long_message(payload["user_message"])
                result_data["speakable_text"] = payload["speakable_text"]
                result_data["structured_data"] = payload["structured_data"]

                speech_state.last_spoken_text = message
                session_state["last_response"] = message

                escalation = result_data.get("escalation", {})
                if escalation.get("ask_user"):
                    session_state["pending_escalation"] = (
                        escalation.get("original_query", mediated_text),
                        escalation.get("context_snapshot", session_context[-5:]),
                        escalation.get("heuristic_result", {}),
                    )
                    await send_chat_message(ws, message, tone_domain=skill_tone_domain)
                    await send_chat_done(ws)
                    continue

                message_id = None
                if escalation.get("escalated") and escalation.get("thought_data"):
                    message_id = str(uuid.uuid4())
                    thought_store.put(session_id, message_id, escalation["thought_data"])
                    session_state["escalation_count"] += 1
                    session_state["last_escalation_turn"] = session_state["turn_count"]
                    session_state["deep_mode_armed"] = False

                    if isinstance(widget_data, dict) and "type" in widget_data:
                        if widget_data.get("type") == "news":
                            items = list(widget_data.get("items") or [])
                            categories = dict(widget_data.get("categories") or {})
                            session_state["news_cache"] = items
                            session_state["news_categories"] = categories
                            session_state["last_sources"] = _extract_sources_from_results(items)
                            session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, widget_data)
                elif skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    session_state["news_cache"] = list(items)
                    session_state["news_categories"] = dict(widget_data.get("categories") or {})
                    session_state["last_sources"] = _extract_sources_from_results(list(items))
                    session_state["last_source_links"] = _extract_source_links(list(items))
                    await send_widget_message(ws, "news", message, widget_data)
                elif skill_name == "weather" and isinstance(widget_data, dict):
                    await send_widget_message(ws, "weather", message, widget_data)
                elif skill_name == "calendar" and isinstance(widget_data, dict):
                    session_state["last_calendar_summary"] = str(widget_data.get("summary") or "")
                    session_state["last_calendar_events"] = list(widget_data.get("events") or [])
                    await send_widget_message(ws, "calendar", message, widget_data)
                else:
                    await send_chat_message(
                        ws,
                        message,
                        message_id=message_id,
                        tone_domain=skill_tone_domain,
                    )

                if skill_name in {"weather", "news", "web_search", "web_search_skill"}:
                    if getattr(skill_result, "success", False):
                        session_state["trust_status"] = failure_ladder.record_external_success(
                            session_state.get("trust_status", {}),
                            f"{skill_name} request",
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=True,
                            last_external_call=f"{skill_name} request",
                        )
                elif skill_name:
                    if getattr(skill_result, "success", False):
                        session_state["trust_status"] = failure_ladder.record_local_success(
                            session_state.get("trust_status", {})
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=False,
                        )
                await send_trust_status(ws, session_state["trust_status"])

                await send_chat_done(ws)

                # Autoâ€‘speak for voice input
                if (session_state.get("last_input_channel") == "voice"
                        and getattr(skill_result, "success", True)):   # assume success if not present
                    session_state["last_input_channel"] = None   # prevent re-trigger

                session_context.extend([{"role": "user", "content": mediated_text}, {"role": "assistant", "content": message}])
                context_limit = 40 if session_state.get("presence_mode") else 20
                session_context = session_context[-context_limit:]
                session_state["turn_count"] += 1
                continue

            # --- Fallback ---
            fallback_message = response_formatter.friendly_fallback()
            session_state["last_response"] = fallback_message
            await send_chat_message(
                ws,
                fallback_message,
                suggested_actions=_conversation_suggestions(session_state),
            )
            await send_chat_done(ws)
            session_state["turn_count"] += 1

            # (No autoâ€‘speak for fallback â€“ optional, but omitted to stay minimal)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        thought_store.clear_session(session_id)
        GovernorMediator.clear_session(session_id)

