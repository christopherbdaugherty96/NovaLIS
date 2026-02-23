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

async def send_chat_message(ws: WebSocket, text: str) -> None:
    await ws_send(ws, {"type": "chat", "message": text})

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

            text = (msg.get("text") or "").strip()

            if not text:
                continue

            lowered = text.lower()

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
                await send_chat_message(ws, "Okay. Correction noted.")
                await send_chat_done(ws)
                continue

            # --- Confirmation gate (Phase‑3.5 passive) ---
            if confirmation_gate.has_pending_confirmation():
                gate_result = confirmation_gate.try_resolve(mediated_text)
                if gate_result.message is not None:
                    await send_chat_message(ws, gate_result.message)
                    await send_chat_done(ws)
                    continue

            # --- Skills (Phase‑3.5 deterministic routing) ---
            skill_result = await skill_registry.handle_query(mediated_text)

            if skill_result:
                skill_name = getattr(skill_result, "skill", "") or ""
                message = getattr(skill_result, "message", "") or ""
                widget_data = getattr(skill_result, "widget_data", None)

                # Track for repeat
                speech_state.last_spoken_text = message

                # Canonical widget payload
                if isinstance(widget_data, dict) and "type" in widget_data:
                    await ws_send(ws, widget_data)
                elif skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    await send_widget_message(ws, "news", message, {"items": items})
                elif skill_name == "weather" and isinstance(widget_data, dict):
                    await send_widget_message(ws, "weather", message, widget_data)
                else:
                    await send_chat_message(ws, message)

                await send_chat_done(ws)
                continue

            # --- Fallback (should never happen if GeneralChatSkill catches everything) ---
            await send_chat_message(ws, "I'm not sure how to help with that.")
            await send_chat_done(ws)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        # Clean up session‑specific clarification state
        GovernorMediator.clear_session(session_id)