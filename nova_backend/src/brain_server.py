# src/brain_server.py

"""
NovaLIS Brain Server — Phase 4 Staging
- Session‑aware mediator
- Dataclass‑based invocation handling
- Governor mediation
- Phase‑3.5 skill fallback preserved
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
from datetime import datetime
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
from src.trust.failure_ladder import FailureLadder
from src.trust.trust_contract import normalize_trust_status
from src.working_context.context_store import WorkingContextStore
from src.working_context.project_threads import ProjectThreadStore
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
# Phase‑4 Staging Components
# -------------------------------------------------
thought_store = ThoughtStore(ttl=300)
conversation_heuristics = ComplexityHeuristics()
response_formatter = ResponseFormatter()
failure_ladder = FailureLadder()
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
MOST_BLOCKED_PROJECT_RE = re.compile(
    r"^\s*(?:which(?:\s+of\s+my)?\s+projects?\s+is\s+most\s+blocked(?:\s+right\s+now)?|most\s+blocked\s+project)\s*$",
    re.IGNORECASE,
)
WHY_RECOMMENDATION_RE = re.compile(
    r"^\s*why\s+(?:this|that)\s+recommendation\s*\??\s*$",
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

# -------------------------------------------------
# Phase Status Endpoint
# -------------------------------------------------
@app.get("/phase-status")
async def phase_status():
    from src.governor.execute_boundary import GOVERNED_ACTIONS_ENABLED
    return {
        "phase": "4",
        "status": "staging" if GOVERNED_ACTIONS_ENABLED else "sealed",
        "execution_enabled": GOVERNED_ACTIONS_ENABLED,
        "note": "Phase‑4 runtime active – all actions mediated by Governor."
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

async def send_chat_message(
    ws: WebSocket,
    text: str,
    message_id: Optional[str] = None,
    confidence: Optional[str] = None,
    suggested_actions: Optional[list[dict[str, str]]] = None,
) -> None:
    payload = {"type": "chat", "message": text}
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
    await ws_send(ws, {"type": "trust_status", "data": normalize_trust_status(trust_status)})


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
                    "- project status <name>\n"
                    "- biggest blocker in <name>\n"
                    "- which project is most blocked right now\n"
                    "- why this recommendation"
                )
                await send_chat_message(ws, capability_message)
                await send_chat_done(ws)
                continue

            if SHOW_THREADS_RE.match(text):
                await ws_send(ws, project_threads.render_map_widget())
                await send_chat_message(ws, project_threads.render_map_message())
                await send_chat_done(ws)
                continue

            if MOST_BLOCKED_PROJECT_RE.match(text):
                found, blocked_message = project_threads.render_most_blocked()
                if found:
                    await ws_send(ws, project_threads.render_map_widget())
                    top_name = project_threads.most_blocked_thread_name()
                    suggested: list[dict[str, str]] = [{"label": "Show threads", "command": "show threads"}]
                    if top_name:
                        suggested = [
                            {"label": f"Continue {top_name}", "command": f"continue my {top_name}"},
                            {"label": f"Project status", "command": f"project status {top_name}"},
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
                await ws_send(ws, project_threads.render_map_widget())
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
                    await ws_send(ws, project_threads.render_map_widget())
                    await send_chat_message(
                        ws,
                        brief,
                        suggested_actions=[
                            {"label": "Save this update", "command": f"save this as part of {project_threads.active_thread_name()}"},
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
                    await ws_send(ws, project_threads.render_map_widget())
                    active = project_threads.active_thread_name()
                    await send_chat_message(
                        ws,
                        status_text,
                        suggested_actions=[
                            {"label": "Biggest blocker", "command": f"biggest blocker in {active}"},
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
                    await ws_send(ws, project_threads.render_map_widget())
                    active = project_threads.active_thread_name()
                    await send_chat_message(
                        ws,
                        blocker_text,
                        suggested_actions=[
                            {"label": "Project status", "command": f"project status {active}"},
                            {"label": "Save this update", "command": f"save this as part of {active}"},
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
                await ws_send(ws, project_threads.render_map_widget())
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
                await ws_send(ws, project_threads.render_map_widget())
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
                await ws_send(ws, project_threads.render_map_widget())
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

            # --- Phase‑2 immediate commands ---
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
                await send_chat_message(ws, phase42_message)
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
                        await send_chat_message(ws, "Weather is currently unavailable.")
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
                        await send_chat_message(ws, message)
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
                        await send_chat_message(ws, "Weather is currently unavailable.")
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
                        await send_chat_message(ws, "News is currently unavailable.")
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
                        await send_chat_message(ws, message)
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
                        await send_chat_message(ws, "News is currently unavailable.")
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
                        await send_chat_message(ws, "Calendar is currently unavailable.")
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
                        await send_chat_message(ws, message)
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
                        await send_chat_message(ws, "Calendar is currently unavailable.")
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
                        await send_chat_message(ws, failure_message)
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
                        await send_chat_message(ws, message)
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
                        await send_chat_message(ws, failure_message)
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
                await send_chat_message(ws, morning_brief)
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

            # --- Phase‑4 governed invocation detection ---
            inv_result = GovernorMediator.parse_governed_invocation(mediated_text, session_id=session_id)

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
                    if plan.get("requires_confirmation") and not params.get("confirmed"):
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
                    confidence_label = str(action_result.data.get("verification_confidence_label") or "").strip()
                    if confidence_label:
                        message_confidence = f"Verification {confidence_label}"
                    if action_result.data.get("verification_recommended") is True:
                        message_suggestions = [
                            {"label": "Re-check with sources", "command": "show sources for your last response"},
                            {"label": "Summarize risk", "command": "summarize verification risks in 3 bullets"},
                            {"label": "Revise answer", "command": "revise your last answer using this verification report"},
                        ]
                if capability_id == 49 and isinstance(action_result.data, dict):
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

                # Auto‑speak for voice input (only if not a TTS invocation)
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

            # --- inv_result is None – proceed to Phase‑3.5 handling ---

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
                    await send_chat_message(ws, message)
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
                    await send_chat_message(ws, message, message_id=message_id)

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

                # Auto‑speak for voice input
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

            # (No auto‑speak for fallback – optional, but omitted to stay minimal)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        thought_store.clear_session(session_id)
        GovernorMediator.clear_session(session_id)
