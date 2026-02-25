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

from src.skill_registry import SkillRegistry
from src.gates.confirmation_gate import confirmation_gate
from src.governor.governor_mediator import GovernorMediator, Invocation, Clarification
from src.speech_state import speech_state
from src.conversation.thought_store import ThoughtStore

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
# No global NetworkMediator – Governor creates its own lazily.
skill_registry = SkillRegistry()            # Phase‑3.5 skills (unchanged)
thought_store = ThoughtStore(ttl=300)

# -------------------------------------------------
# Security Constants
# -------------------------------------------------
WS_INPUT_MAX_BYTES = 4096  # BUG-S2: Guard against oversized WebSocket input (UTF-8 bytes)

# -------------------------------------------------
# Phase Status Endpoint (Updated for Phase‑4 Staging)
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
        await ws_send(ws, {"type": "news", "items": data["items"]})
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

    # Unique session ID for clarification state
    session_id = str(uuid.uuid4())

    # Governor instance (per‑session)
    governor = Governor()

    session_context = []
    session_state = {
        "turn_count": 0,
        "escalation_count": 0,
        "last_escalation_turn": None,
        "deep_mode_disabled": False,
        "show_thinking_hints": True,
        "pending_escalation": None,
    }

    # Phase‑3.5 greeting
    await send_chat_message(ws, "Hello. How can I help?")
    await send_chat_done(ws)

    try:
        while True:
            raw = await ws.receive_text()

            # --- BUG-S2: WebSocket input length guard (bytes, UTF-8 safe) ---
            raw_bytes = raw.encode("utf-8")
            if len(raw_bytes) > WS_INPUT_MAX_BYTES:
                log.warning(
                    "WebSocket input rejected: %d bytes exceeds limit %d",
                    len(raw_bytes),
                    WS_INPUT_MAX_BYTES,
                )
                await ws_send(ws, {
                    "type": "error",
                    "code": "input_too_long",
                    "message": "Input exceeds maximum allowed length.",
                })
                continue

            # --- JSON safety guard ---
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                log.warning("WebSocket input rejected: malformed JSON")
                await ws_send(ws, {
                    "type": "error",
                    "code": "invalid_json",
                    "message": "Malformed request.",
                })
                continue

            msg_type = (msg.get("type") or "chat").strip().lower()

            if msg_type == "get_thought":
                message_id = (msg.get("message_id") or "").strip()
                thought_data = thought_store.get(session_id, message_id) if message_id else None
                if thought_data is None:
                    await ws_send(ws, {"type": "error", "message": "Thought data not found or expired"})
                else:
                    await ws_send(ws, {"type": "thought", "data": thought_data, "message_id": message_id})
                continue

            text = (msg.get("text") or "").strip()

            if not text:
                continue

            lowered = text.lower()

            if session_state["pending_escalation"]:
                pending = session_state["pending_escalation"]
                session_state["pending_escalation"] = None
                if lowered in {"yes", "yeah", "sure", "ok", "go ahead"}:
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
                            session_context = session_context[-20:]
                            session_state["turn_count"] += 1
                            continue
                elif lowered in {"no", "cancel", "never mind"}:
                    await send_chat_message(ws, "Okay, keeping it brief.")
                    await send_chat_done(ws)
                    continue

            # --- Phase‑2 immediate commands ---
            if lowered == "stop":
                speech_state.stop()
                await send_chat_message(ws, "Okay.")
                await send_chat_done(ws)
                continue

            if lowered == "repeat":
                last = speech_state.last_spoken_text
                if last:
                    await send_chat_message(ws, last)
                await send_chat_done(ws)
                continue

            # --- Governor mediation (sanitization) ---
            mediated_text = GovernorMediator.mediate(text)

            # --- Phase‑4: governed invocation detection ---
            inv_result = GovernorMediator.parse_governed_invocation(
                mediated_text, session_id=session_id
            )

            if isinstance(inv_result, Invocation):
                # ✅ FIXED: use .message, not .user_message; send widget separately
                action_result = governor.handle_governed_invocation(
                    inv_result.capability_id, inv_result.params
                )

                # Always send the chat message first
                await send_chat_message(ws, action_result.message)

                # If a widget payload exists, send it as a separate message
                if (
                    action_result.success
                    and isinstance(action_result.data, dict)
                    and "widget" in action_result.data
                ): 
                    await ws_send(ws, action_result.data["widget"])

                await send_chat_done(ws)
                continue

            elif isinstance(inv_result, Clarification):
                # Need more info – send clarification question
                await send_chat_message(ws, inv_result.message)
                await send_chat_done(ws)
                continue

            # --- inv_result is None – proceed to Phase‑3.5 handling ---

            # --- Quick Corrections ---
            if mediated_text.startswith("Correction:"):
                correction_text = mediated_text[len("Correction:"):].strip()
                if correction_text:
                    record_correction(correction_text)
                await send_chat_message(ws, "Thanks, I've noted that correction.")
                await send_chat_done(ws)
                continue

            # --- Confirmation gate (Phase‑3.5 passive) ---
            if confirmation_gate.has_pending_confirmation():
                gate_result = confirmation_gate.try_resolve(mediated_text)
                if gate_result.message is not None:
                    await send_chat_message(ws, gate_result.message)
                    await send_chat_done(ws)
                    continue

            # --- Skills (Phase‑3.5 deterministic routing + Phase‑4.2 chat context) ---
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

                session_context.extend([{"role": "user", "content": mediated_text}, {"role": "assistant", "content": message}])
                session_context = session_context[-20:]
                session_state["turn_count"] += 1
                continue

            # --- Fallback (should never happen if GeneralChatSkill catches everything) ---
            await send_chat_message(ws, "I'm not sure how to help with that. Could you rephrase?")
            await send_chat_done(ws)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        # Clean up session‑specific state
        thought_store.clear_session(session_id)
        GovernorMediator.clear_session(session_id)