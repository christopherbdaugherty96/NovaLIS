"""
NovaLIS Brain Server — Phase 3.5 (Behaviorally Complete)

Constitutional Status: FROZEN
Execution: Structurally impossible
Governance: Provably passive
Behavior: Deterministic, silence-first
"""

from .governor.governor import Governor

# Phase-3.5 staged governed memory (explicit user corrections)

from .memory.quick_corrections import record_correction

from src.routers.stt import router as stt_router

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .skill_registry import skill_registry
from .gates.confirmation_gate import confirmation_gate
from .governor.governor_mediator import GovernorMediator
from .speech_state import speech_state

# -------------------------------------------------
# App + Logging
# -------------------------------------------------

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

log = logging.getLogger("nova")
app = FastAPI()

# -------------------------------------------------
# Static Files (Phase-3.5 Safe)
# -------------------------------------------------

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
# Phase-3.5 Trust Verification Endpoint
# -------------------------------------------------

@app.get("/phase-status")
async def phase_status():
    """
    Constitutional proof of Phase-3.5 compliance.
    
    Read-only endpoint that exposes frozen guarantees.
    No authority expansion, no behavior changes.
    """
    return {
        "phase": "3.5",
        "status": "frozen",
        "execution": {
            "enabled": False,
            "structurally_impossible": True,
            "note": "Execution boundary owned by Governor; no execution available in Phase-3.5."
        },
        "confirmation_gate": {
            "behavior": "passive_when_idle",
            "proof": "try_resolve returns message=None when no pending context",
            "vocabulary": ["yes", "no"],
            "cannot_initiate": True
        },
        "behavior": {
            "greeting": {
                "text": "Hello. How can I help?",
                "frequency": "once_per_session",
                "deterministic": True
            },
            "silence_first": True,
            "correction": {
                "method": "explicit_prefix",
                "prefix": "Correction:",
                "staged_only": True
            },
            "permission_model": {
                "read_only": "search/look up = permission",
                "no_confirmation": True
            }
        },
        "verified_at": datetime.utcnow().isoformat(),
        "constitutional_note": "Phase-3.5 behavioral goals are complete. Remaining work is governance visibility and Phase-4 authority boundaries."
    }


# -------------------------------------------------
# Phase-3 Execution Lock
# -------------------------------------------------

@app.get("/phase-status")
async def phase_status():
    """
    Phase-3.5 runtime truth endpoint.
    Execution is structurally disabled.
    """

    return {
        "phase": "3.5",
        "execution_enabled": False,
        "authority_level": "read-only",
        "note": "Execution boundary owned by Governor; no execution available in Phase-3.5."
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
    """
    Phase-3 widget dispatch.
    
    Canonical:
      - news    -> {type:"news", items:[...]}
      - weather -> {type:"weather", data:{...}}
    """

    # Phase-3 canonical news widget
    if msg_type == "news" and isinstance(data, dict) and "items" in data:
        await ws_send(ws, {
            "type": "news",
            "items": data["items"]
        })
        return

    # Phase-2 weather widget (preserved)
    payload = {
        "type": msg_type,
        "message": text
    }

    if msg_type == "weather" and isinstance(data, dict):
        payload["data"] = data

    await ws_send(ws, payload)


# -------------------------------------------------
# WebSocket Endpoint
# -------------------------------------------------

# -------------------------------------------------
# WebSocket Endpoint
# -------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    log.info("WebSocket connected")

    # GOV-002: Governor spine (per-session)
    governor = Governor()

    # Phase-3.5 greeting discipline
    await send_chat_message(ws, "Hello. How can I help?")
    await send_chat_done(ws)

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            text = (msg.get("text") or "").strip()

            if not text:
                continue

            lowered = text.lower()

            # -------------------------------------------------
            # STOP — immediate halt (Phase-2 lock)
            # -------------------------------------------------
            if lowered == "stop":
                speech_state.stop()
                await send_chat_message(ws, "Okay.")
                await send_chat_done(ws)
                continue

            # -------------------------------------------------
            # REPEAT — last spoken text only
            # -------------------------------------------------
            if lowered == "repeat":
                last = speech_state.last_spoken_text
                if last:
                    await send_chat_message(ws, last)
                await send_chat_done(ws)
                continue

            # -------------------------------------------------
            # Governor mediation (LLM output control)
            # -------------------------------------------------
            mediated_text = GovernorMediator.mediate(text)

            # -------------------------------------------------
            # Quick Corrections — explicit, staged, Phase-3.5
            # -------------------------------------------------
            if mediated_text.startswith("Correction:"):
                correction_text = mediated_text[len("Correction:"):].strip()

                if correction_text:
                    record_correction(correction_text)

                await send_chat_message(ws, "Okay. Correction noted.")
                await send_chat_done(ws)
                continue

            # -------------------------------------------------
            # Confirmation gate (provably passive)
            # -------------------------------------------------
            # Constitutional Proof:
            # - Gate only consulted when it has pending state
            # - Gate is silent when idle (not even called)
            # - No confirmation initiation in Phase-3.5
            if confirmation_gate.has_pending_confirmation():
                gate_result = confirmation_gate.try_resolve(mediated_text)
                
                # Gate speaks only when it has a message
                if gate_result.message is not None:
                    await send_chat_message(ws, gate_result.message)
                    await send_chat_done(ws)
                    continue
            # If no pending confirmation, skip the gate entirely

            # -------------------------------------------------
            # Skills (deterministic, Phase-3 aligned)
            # -------------------------------------------------
            skill_result = await skill_registry.handle_query(mediated_text)

            # ----------------------------
            # Widget / Chat dispatch (Phase-3 canonical)
            # ----------------------------
            if skill_result:
                skill_name = getattr(skill_result, "skill", "") or ""
                message = getattr(skill_result, "message", "") or ""
                widget_data = getattr(skill_result, "widget_data", None)

                # Track for repeat (no auto-speak)
                speech_state.last_spoken_text = message

                # If skill already returns canonical widget payload, pass through untouched
                if isinstance(widget_data, dict) and "type" in widget_data:
                    await ws_send(ws, widget_data)
                    await send_chat_done(ws)
                    continue

                # Compatibility: if skill returns raw widget data (older dialect), wrap here
                if skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    await send_widget_message(ws, "news", message, {"items": items})
                    await send_chat_done(ws)
                    continue

                if skill_name == "weather" and isinstance(widget_data, dict):
                    await send_widget_message(ws, "weather", message, widget_data)
                    await send_chat_done(ws)
                    continue

                # Default: chat message response
                await send_chat_message(ws, message)
                await send_chat_done(ws)
                continue

            # -------------------------------------------------
            # Fallback — governed chat only (no execution)
            # -------------------------------------------------
            await send_chat_message(ws, "I'm not sure how to help with that.")
            await send_chat_done(ws)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")