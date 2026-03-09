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
from src.personality.core import PersonalityAgent
from src.agents.builder import BuilderAgent
from src.agents.deep_audit import DeepAuditAgent
from src.agents.architect import StructuralArchitectAgent
from src.agents.memory import MemoryAgent
from src.agents.assumption import AssumptionRiskAgent
from src.agents.contradiction import ContradictionAggregatorAgent
from src.agents.adversarial import AdversarialExternalizerAgent
from src.audit.runtime_auditor import (
    run_runtime_truth_audit,
    render_runtime_truth_markdown,
    write_current_runtime_state_snapshot,
)

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


def _build_phase42_agents() -> list:
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
            {"label": "Search weather", "command": "search weather in Ann Arbor"},
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
        {"label": "Daily brief", "command": "brief"},
    ]
    if session_state.get("last_response"):
        suggestions.append({"label": "Shorter version", "command": "shorter version"})
    if session_state.get("news_cache"):
        suggestions.append({"label": "Summarize headlines", "command": "summarize all headlines"})
    return suggestions[:4]

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
        await ws_send(ws, {"type": "news", "items": data["items"], "summary": data.get("summary", "")})
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
    personality_agent = PersonalityAgent()
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
        "last_sources": [],
        "last_source_links": [],
        "topic_memory_map": {},
        "last_brief_clusters": [],
        "pending_web_open": None,
        "pending_governed_confirm": None,
        "analysis_documents": [],
        "last_analysis_doc_id": None,
        "last_intent_family": "",
        "last_mode": "",
        "session_mode_override": "",
        "trust_status": failure_ladder.initial_status(),
        "last_calendar_summary": "",
        "last_calendar_events": [],
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
            silent_widget_refresh = bool(msg.get("silent_widget_refresh"))
            if channel not in {"voice", "text"}:
                channel = "text"

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

            route_context = SessionRouter.normalize_and_route(raw_text, session_state)
            if route_context.is_empty:
                await send_chat_message(ws, SessionRouter.ready_prompt())
                await send_chat_done(ws)
                continue

            text = route_context.text
            lowered = route_context.lowered
            decision = route_context.decision

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

            if lowered in {"deep mode", "deep analysis", "go deeper", "challenge this", "pressure test this"}:
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
                    action_result = await asyncio.to_thread(
                        governor.handle_governed_invocation,
                        capability_id,
                        params,
                    )
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
                    action_result = await asyncio.to_thread(
                        governor.handle_governed_invocation,
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
                if lowered in {"yes"}:
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
                elif lowered in {"no", "cancel"}:
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
                if not PHASE_4_2_ENABLED:
                    await send_chat_message(
                        ws,
                        "Phase 4.2 runtime is locked in this build profile.",
                    )
                    await send_chat_done(ws)
                    continue

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
                weather_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "weather"), None)
                if weather_skill is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Weather is unavailable right now.")
                    await send_chat_done(ws)
                    continue
                weather_result = await weather_skill.handle("weather")
                if weather_result and weather_result.success:
                    message = _structure_long_message(weather_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message)
                    if isinstance(weather_result.widget_data, dict):
                        await ws_send(ws, weather_result.widget_data)
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "Weather update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Weather is currently unavailable.")
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
                news_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "news"), None)
                if news_skill is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "News is unavailable right now.")
                    await send_chat_done(ws)
                    continue
                news_result = await news_skill.handle("news")
                if news_result and news_result.success:
                    if not silent_widget_refresh:
                        session_state["last_response"] = news_result.message
                        await send_chat_message(ws, news_result.message)
                    if isinstance(news_result.widget_data, dict):
                        items = list(news_result.widget_data.get("items") or [])
                        session_state["news_cache"] = items
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        await ws_send(ws, news_result.widget_data)
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "News update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "News is currently unavailable.")
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
                calendar_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "calendar"), None)
                if calendar_skill is None:
                    await send_chat_message(ws, "Calendar is unavailable right now.")
                    await send_chat_done(ws)
                    continue
                calendar_result = await calendar_skill.handle("calendar")
                if calendar_result and calendar_result.success:
                    message = _structure_long_message(calendar_result.message)
                    session_state["last_response"] = message
                    await send_chat_message(ws, message)
                    if isinstance(calendar_result.widget_data, dict):
                        await send_widget_message(ws, "calendar", message, calendar_result.widget_data)
                        session_state["last_calendar_summary"] = str(
                            calendar_result.widget_data.get("summary") or ""
                        )
                        session_state["last_calendar_events"] = list(
                            calendar_result.widget_data.get("events") or []
                        )
                else:
                    await send_chat_message(ws, "Calendar is currently unavailable.")
                await send_chat_done(ws)
                continue

            if lowered in {"system", "system status", "system check"}:
                system_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "system"), None)
                if system_skill is None:
                    await send_chat_message(ws, "System diagnostics are unavailable right now.")
                    await send_chat_done(ws)
                    continue
                system_result = await system_skill.handle("system status")
                if system_result and system_result.success:
                    message = _structure_long_message(system_result.message)
                    session_state["last_response"] = message
                    await send_chat_message(ws, message)
                    if isinstance(system_result.widget_data, dict):
                        await ws_send(ws, system_result.widget_data)
                else:
                    await send_chat_message(ws, "System diagnostics are currently unavailable.")
                await send_chat_done(ws)
                continue

            if lowered in {"morning", "morning brief", "brief"}:
                weather_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "weather"), None)
                news_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "news"), None)
                system_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "system"), None)
                calendar_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "calendar"), None)

                weather_summary = "Weather unavailable."
                news_summary = "No headline summary available right now."
                system_line = "System status unavailable."
                calendar_line = "Calendar unavailable."

                if weather_skill is not None:
                    weather_result = await weather_skill.handle("weather")
                    if weather_result and weather_result.success:
                        weather_summary = weather_result.message
                        if isinstance(weather_result.widget_data, dict):
                            await ws_send(ws, weather_result.widget_data)
                        session_state["trust_status"] = failure_ladder.record_external_success(
                            session_state.get("trust_status", {}),
                            "Weather update",
                        )
                        await send_trust_status(ws, session_state["trust_status"])

                if news_skill is not None:
                    news_result = await news_skill.handle("news")
                    if news_result and news_result.success:
                        if isinstance(news_result.widget_data, dict):
                            news_summary = (news_result.widget_data.get("summary") or news_summary)
                            session_state["news_cache"] = list(news_result.widget_data.get("items") or [])
                            await ws_send(ws, news_result.widget_data)
                        session_state["trust_status"] = failure_ladder.record_external_success(
                            session_state.get("trust_status", {}),
                            "News update",
                        )
                        await send_trust_status(ws, session_state["trust_status"])

                if system_skill is not None:
                    system_result = await system_skill.handle("system status")
                    if system_result and system_result.success:
                        system_line = system_result.message

                if calendar_skill is not None:
                    calendar_result = await calendar_skill.handle("calendar")
                    if calendar_result and calendar_result.success:
                        if isinstance(calendar_result.widget_data, dict):
                            calendar_line = str(
                                calendar_result.widget_data.get("summary")
                                or calendar_result.message
                                or calendar_line
                            )
                            session_state["last_calendar_summary"] = calendar_line
                            session_state["last_calendar_events"] = list(
                                calendar_result.widget_data.get("events") or []
                            )
                            await send_widget_message(
                                ws,
                                "calendar",
                                calendar_result.message,
                                calendar_result.widget_data,
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
                        news_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "news"), None)
                        if news_skill is not None:
                            news_result = await news_skill.handle("news")
                            if news_result and news_result.success and isinstance(news_result.widget_data, dict):
                                items = list(news_result.widget_data.get("items") or [])
                                session_state["news_cache"] = items
                                session_state["last_sources"] = _extract_sources_from_results(items)
                                session_state["last_source_links"] = _extract_source_links(items)
                                await ws_send(ws, news_result.widget_data)
                    params.setdefault("headlines", list(session_state.get("news_cache") or []))
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
                    from src.executors.webpage_launch_executor import WebpageLaunchExecutor
                    plan = WebpageLaunchExecutor.plan_open(params)
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

                action_result = await asyncio.to_thread(
                    governor.handle_governed_invocation,
                    capability_id,
                    params,
                )
                if capability_id == 50 and params.get("action") == "track_cluster":
                    track_topic = ""
                    if isinstance(action_result.data, dict):
                        track_topic = str(action_result.data.get("track_topic") or "").strip()
                    if track_topic:
                        action_result = await asyncio.to_thread(
                            governor.handle_governed_invocation,
                            52,
                            {
                                "action": "track",
                                "topic": track_topic,
                                "headlines": list(session_state.get("news_cache") or []),
                                "session_id": session_id,
                            },
                        )
                if isinstance(action_result.data, dict):
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

                if capability_id != 18 and action_result.message:
                    session_state["last_response"] = action_result.message

                if capability_id in {16, 48}:
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

                outgoing_message = _structure_long_message(action_result.message)
                if not outgoing_message.strip() and capability_id == 18 and action_result.success:
                    outgoing_message = "Speaking now."
                await send_chat_message(
                    ws,
                    outgoing_message,
                    confidence=message_confidence,
                    suggested_actions=message_suggestions,
                )

                if action_result.success and isinstance(action_result.data, dict) and "widget" in action_result.data:
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
                            session_state["news_cache"] = items
                            session_state["last_sources"] = _extract_sources_from_results(items)
                            session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, widget_data)
                elif skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    session_state["news_cache"] = list(items)
                    session_state["last_sources"] = _extract_sources_from_results(list(items))
                    session_state["last_source_links"] = _extract_source_links(list(items))
                    await send_widget_message(ws, "news", message, {"items": items})
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
