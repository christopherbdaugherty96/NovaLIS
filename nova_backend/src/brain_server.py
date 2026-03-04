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
from src.voice.stt_pipeline import STTAckConfig, build_ack_payload
from src.voice.tts_engine import resolve_speakable_text, nova_speak, stop_speaking
from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.audit.runtime_auditor import run_runtime_truth_audit, render_runtime_truth_markdown

# -------------------------------------------------
# App + Logging
# -------------------------------------------------
log = logging.getLogger("nova")
app = FastAPI()

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

# -------------------------------------------------
# Security Constants
# -------------------------------------------------
WS_INPUT_MAX_BYTES = 4096
CONVERSATIONAL_INITIATIVE_ENABLED = True
VOICE_ACK_ENABLED = True
VOICE_ACK_TEXT = "Got it."
VOICE_ACK_CONFIG = STTAckConfig(enabled=VOICE_ACK_ENABLED, text=VOICE_ACK_TEXT)

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

async def send_chat_message(ws: WebSocket, text: str, message_id: Optional[str] = None) -> None:
    payload = {"type": "chat", "message": text}
    if message_id is not None:
        payload["message_id"] = message_id
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
        "last_input_channel": "text",
        "last_response": "",
        "last_clarification_turn": None,
    }

    await send_chat_message(ws, "Hello. How can I help?")
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
            lowered = text.lower().rstrip(".?!")

            if channel == "voice" and msg_type == "chat":
                ack_payload = build_ack_payload(VOICE_ACK_CONFIG)
                if ack_payload is not None:
                    await ws_send(ws, ack_payload)

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
                            continue
                    # skill is None or forced_result is None
                    await send_chat_message(ws, "Deep analysis is unavailable right now. Please answer 'yes', 'no', or 'cancel'.")
                    await send_chat_done(ws)
                    session_state["pending_escalation"] = None
                    continue
                elif lowered in {"no", "cancel"}:
                    session_state["pending_escalation"] = None
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

                if news_skill is not None:
                    news_result = await news_skill.handle("news")
                    if news_result and news_result.success:
                        if isinstance(news_result.widget_data, dict):
                            news_summary = (news_result.widget_data.get("summary") or news_summary)
                            await ws_send(ws, news_result.widget_data)

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

                action_result = governor.handle_governed_invocation(capability_id, params)

                if capability_id != 18 and action_result.message:
                    session_state["last_response"] = action_result.message

                await send_chat_message(ws, action_result.message)

                if action_result.success and isinstance(action_result.data, dict) and "widget" in action_result.data:
                    await ws_send(ws, action_result.data["widget"])

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

                if isinstance(widget_data, dict) and "type" in widget_data:
                    await ws_send(ws, widget_data)
                elif skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    await send_widget_message(ws, "news", message, {"items": items})
                elif skill_name == "weather" and isinstance(widget_data, dict):
                    await send_widget_message(ws, "weather", message, widget_data)
                else:
                    await send_chat_message(ws, message, message_id=message_id)

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
            fallback_message = "I'm not sure how to help with that."
            session_state["last_response"] = fallback_message
            await send_chat_message(ws, fallback_message)
            await send_chat_done(ws)

            # (No auto‑speak for fallback – optional, but omitted to stay minimal)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        thought_store.clear_session(session_id)
        GovernorMediator.clear_session(session_id)
