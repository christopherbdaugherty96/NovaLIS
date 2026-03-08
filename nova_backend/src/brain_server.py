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
from src.conversation.response_style_router import InputNormalizer
from src.conversation.conversation_router import ConversationRouter
from src.voice.stt_pipeline import STTAckConfig, build_ack_payload
from src.voice.tts_engine import resolve_speakable_text, nova_speak, stop_speaking
from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.conversation.response_formatter import ResponseFormatter
from src.build_phase import BUILD_PHASE, PHASE_4_2_ENABLED
from src.audit.runtime_auditor import (
    run_runtime_truth_audit,
    render_runtime_truth_markdown,
    write_current_runtime_state_snapshot,
)

# -------------------------------------------------
# App + Logging
# -------------------------------------------------
log = logging.getLogger("nova")
app = FastAPI()

# Phase-build lock marker for runtime auditor and governance checks.
# Phase 4 keeps 4.2 modules runtime-locked unless a build promotes phase.
_ = (BUILD_PHASE, PHASE_4_2_ENABLED)


@app.on_event("startup")
async def refresh_runtime_snapshot_on_startup():
    try:
        output_path = write_current_runtime_state_snapshot()
        log.info("Runtime snapshot refreshed at startup: %s", output_path)
    except Exception:
        log.exception("Failed to refresh runtime snapshot on startup")

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
    payload = {"type": msg_type, "message": text}
    if msg_type == "weather" and isinstance(data, dict):
        payload["data"] = data
    await ws_send(ws, payload)


async def send_trust_status(ws: WebSocket, trust_status: dict) -> None:
    await ws_send(ws, {"type": "trust_status", "data": dict(trust_status or {})})

# -------------------------------------------------
# WebSocket Endpoint
# -------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    log.info("WebSocket connected")

    session_id = str(uuid.uuid4())
    governor = Governor()
    skill_registry = SkillRegistry(network=governor.network)
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
        "topic_memory_map": {},
        "analysis_documents": [],
        "last_analysis_doc_id": None,
        "last_intent_family": "",
        "last_mode": "",
        "trust_status": {
            "mode": "Local-only",
            "last_external_call": "None",
            "data_egress": "No external call in this step",
            "failure_state": "Normal",
        },
    }

    await send_chat_message(ws, "Hello. How can I help?")
    await send_trust_status(ws, session_state["trust_status"])
    await send_chat_done(ws)

    try:
        while True:
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

            text = InputNormalizer.normalize(raw_text).strip()
            decision = ConversationRouter.route(text, session_state)
            if decision.blocked_by_policy:
                await send_chat_message(ws, "I can't help with that request.")
                await send_chat_done(ws)
                continue

            if decision.needs_clarification:
                clarification_turn = session_state.get("last_clarification_turn")
                if clarification_turn == session_state["turn_count"]:
                    await send_chat_message(ws, "I still need a file or folder name to continue.")
                else:
                    await send_chat_message(ws, str(decision.clarification_prompt or "Could you clarify that?"))
                    session_state["last_clarification_turn"] = session_state["turn_count"]
                await send_chat_done(ws)
                continue

            resolved_text = str(decision.resolved_text or text).strip()
            if resolved_text:
                text = resolved_text
            lowered = text.lower().rstrip(".?!")
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

            if channel == "voice" and msg_type == "chat":
                ack_payload = build_ack_payload(VOICE_ACK_CONFIG)
                if ack_payload is not None:
                    await ws_send(ws, ack_payload)

            micro_ack = str(decision.micro_ack or "").strip()
            if micro_ack:
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

            if lowered in {"weather", "weather update", "current weather"}:
                weather_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "weather"), None)
                if weather_skill is None:
                    await send_chat_message(ws, "Weather is unavailable right now.")
                    await send_chat_done(ws)
                    continue
                weather_result = await weather_skill.handle("weather")
                if weather_result and weather_result.success:
                    message = _structure_long_message(weather_result.message)
                    session_state["last_response"] = message
                    await send_chat_message(ws, message)
                    if isinstance(weather_result.widget_data, dict):
                        await ws_send(ws, weather_result.widget_data)
                    session_state["trust_status"] = {
                        "mode": "Online",
                        "last_external_call": "Weather update",
                        "data_egress": "Read-only external request",
                        "failure_state": "Normal",
                    }
                    await send_trust_status(ws, session_state["trust_status"])
                else:
                    await send_chat_message(ws, "Weather is currently unavailable.")
                await send_chat_done(ws)
                continue

            if lowered in {"news", "headlines", "latest news", "top news"}:
                news_skill = next((s for s in skill_registry.skills if getattr(s, "name", "") == "news"), None)
                if news_skill is None:
                    await send_chat_message(ws, "News is unavailable right now.")
                    await send_chat_done(ws)
                    continue
                news_result = await news_skill.handle("news")
                if news_result and news_result.success:
                    session_state["last_response"] = news_result.message
                    await send_chat_message(ws, news_result.message)
                    if isinstance(news_result.widget_data, dict):
                        items = list(news_result.widget_data.get("items") or [])
                        session_state["news_cache"] = items
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        await ws_send(ws, news_result.widget_data)
                    session_state["trust_status"] = {
                        "mode": "Online",
                        "last_external_call": "News update",
                        "data_egress": "Read-only external request",
                        "failure_state": "Normal",
                    }
                    await send_trust_status(ws, session_state["trust_status"])
                else:
                    await send_chat_message(ws, "News is currently unavailable.")
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

                weather_summary = "Weather unavailable."
                news_summary = "No headline summary available right now."
                system_line = "System status unavailable."

                if weather_skill is not None:
                    weather_result = await weather_skill.handle("weather")
                    if weather_result and weather_result.success:
                        weather_summary = weather_result.message
                        if isinstance(weather_result.widget_data, dict):
                            await ws_send(ws, weather_result.widget_data)
                        session_state["trust_status"] = {
                            "mode": "Online",
                            "last_external_call": "Weather update",
                            "data_egress": "Read-only external request",
                            "failure_state": "Normal",
                        }
                        await send_trust_status(ws, session_state["trust_status"])

                if news_skill is not None:
                    news_result = await news_skill.handle("news")
                    if news_result and news_result.success:
                        if isinstance(news_result.widget_data, dict):
                            news_summary = (news_result.widget_data.get("summary") or news_summary)
                            session_state["news_cache"] = list(news_result.widget_data.get("items") or [])
                            await ws_send(ws, news_result.widget_data)
                        session_state["trust_status"] = {
                            "mode": "Online",
                            "last_external_call": "News update",
                            "data_egress": "Read-only external request",
                            "failure_state": "Normal",
                        }
                        await send_trust_status(ws, session_state["trust_status"])

                if system_skill is not None:
                    system_result = await system_skill.handle("system status")
                    if system_result and system_result.success:
                        system_line = system_result.message

                morning_brief = (
                    "Executive Brief\n"
                    f"- Weather: {weather_summary}\n"
                    f"- System: {system_line}\n"
                    f"- News: {news_summary}"
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
                if capability_id == 18 and not params.get("text"):
                    params["text"] = session_state.get("last_response", "")
                if capability_id == 31 and not params.get("text"):
                    params["text"] = session_state.get("last_response", "")
                if capability_id in {49, 50, 51, 52, 53}:
                    params.setdefault("headlines", list(session_state.get("news_cache") or []))
                    params.setdefault("topic_history", dict(session_state.get("topic_memory_map") or {}))
                if capability_id == 54:
                    params.setdefault("analysis_documents", list(session_state.get("analysis_documents") or []))
                    if params.get("doc_id") in {None, ""} and session_state.get("last_analysis_doc_id") is not None:
                        params["doc_id"] = session_state.get("last_analysis_doc_id")

                action_result = governor.handle_governed_invocation(capability_id, params)
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
                    analysis_docs = action_result.data.get("analysis_documents")
                    if isinstance(analysis_docs, list):
                        session_state["analysis_documents"] = analysis_docs
                    if "document_id" in action_result.data:
                        session_state["last_analysis_doc_id"] = action_result.data.get("document_id")

                if capability_id != 18 and action_result.message:
                    session_state["last_response"] = action_result.message

                if capability_id in {16, 48}:
                    session_state["trust_status"] = {
                        "mode": "Online" if action_result.success else "Local-only",
                        "last_external_call": "Governed web search",
                        "data_egress": "Read-only external request" if action_result.success else "External request failed",
                        "failure_state": "Normal" if action_result.success else "Degraded",
                    }
                else:
                    session_state["trust_status"] = {
                        "mode": "Local-only",
                        "last_external_call": session_state.get("trust_status", {}).get("last_external_call", "None"),
                        "data_egress": "No external call in this step",
                        "failure_state": "Normal" if action_result.success else "Temporary issue",
                    }
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

                outgoing_message = _structure_long_message(action_result.message)
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
                    speakable_text = resolve_speakable_text(action_result)
                    if speakable_text:
                        nova_speak(speakable_text)
                        session_state["last_input_channel"] = None   # prevent re-trigger
                continue

            elif isinstance(inv_result, Clarification):
                await send_chat_message(ws, inv_result.message)
                await send_chat_done(ws)
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
                    await ws_send(ws, widget_data)
                elif skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    session_state["news_cache"] = list(items)
                    session_state["last_sources"] = _extract_sources_from_results(list(items))
                    await send_widget_message(ws, "news", message, {"items": items})
                elif skill_name == "weather" and isinstance(widget_data, dict):
                    await send_widget_message(ws, "weather", message, widget_data)
                else:
                    await send_chat_message(ws, message, message_id=message_id)

                if skill_name in {"weather", "news", "web_search", "web_search_skill"}:
                    session_state["trust_status"] = {
                        "mode": "Online" if getattr(skill_result, "success", False) else "Local-only",
                        "last_external_call": f"{skill_name} request",
                        "data_egress": "Read-only external request" if getattr(skill_result, "success", False) else "External request failed",
                        "failure_state": "Normal" if getattr(skill_result, "success", False) else "Degraded",
                    }
                elif skill_name:
                    session_state["trust_status"] = {
                        "mode": "Local-only",
                        "last_external_call": session_state.get("trust_status", {}).get("last_external_call", "None"),
                        "data_egress": "No external call in this step",
                        "failure_state": "Normal" if getattr(skill_result, "success", False) else "Temporary issue",
                    }
                await send_trust_status(ws, session_state["trust_status"])

                await send_chat_done(ws)

                # Auto‑speak for voice input
                if (session_state.get("last_input_channel") == "voice"
                        and getattr(skill_result, "success", True)):   # assume success if not present
                    speakable_text = ""
                    if isinstance(result_data, dict):
                        speakable_text = (result_data.get("speakable_text") or "").strip()
                    if not speakable_text:
                        speakable_text = message
                    if speakable_text:
                        nova_speak(speakable_text)
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

            # (No auto‑speak for fallback – optional, but omitted to stay minimal)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        thought_store.clear_session(session_id)
        GovernorMediator.clear_session(session_id)
