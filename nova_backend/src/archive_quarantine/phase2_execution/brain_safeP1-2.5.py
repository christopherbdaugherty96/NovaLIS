"""
NovaLIS Brain Server — Phase-2 Baseline

Governor and router only.
No execution logic.
No autonomy.
No memory writes.
"""

import json
import logging
import re
from typing import Optional

from fastapi import FastAPI, WebSocket

# Phase-2 relative imports (package-safe)
from .gates.confirmation_gate import confirmation_gate
from .actions.action_request import ActionRequest
from .actions.action_types import ActionType
from .execution.execute_action import execute_action

from .skill_registry import skill_registry
from .speech_state import speech_state

from .llm.llm_manager import LLMManager

# Optional audio (defensive)
try:
    from .audio_manager import audio_manager
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False
    audio_manager = None


logger = logging.getLogger("nova")
app = FastAPI()

llm_manager = LLMManager()


# ------------------------------------------------------------
# Utility helpers
# ------------------------------------------------------------

async def ws_send(ws: WebSocket, payload: dict) -> None:
    await ws.send_text(json.dumps(payload))


async def nova_speak(
    ws: WebSocket,
    text: str,
    skill: str = "system",
    data: Optional[dict] = None,
) -> None:
    """
    Single output boundary for Nova.
    Text-first; TTS is downstream only.
    """
    speech_state.last_spoken_text = text

    await ws_send(ws, {
        "type": "skill_response",
        "skill": skill,
        "message": text,
        "data": data or {},
    })

    if AUDIO_AVAILABLE and audio_manager:
        try:
            audio_manager.enqueue(text)
        except Exception:
            pass  # audio must never crash the brain


# ------------------------------------------------------------
# Recency guard (pure function)
# ------------------------------------------------------------

_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

def requires_recency_check(query: str) -> bool:
    """
    Detects queries that may require current information.
    Pure function. No side effects.
    """
    q = query.lower()
    if _YEAR_RE.search(q):
        return False

    recency_terms = {"latest", "current", "today", "now", "recent"}
    return any(term in q for term in recency_terms)


# ------------------------------------------------------------
# WebSocket endpoint
# ------------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()

    while True:
        try:
            raw = await ws.receive_text()
        except Exception:
            break

        text = raw.strip().lower()

        # --------------------------------------------
        # STOP — highest priority
        # --------------------------------------------
        if text == "stop":
            confirmation_gate.clear()
            if AUDIO_AVAILABLE and audio_manager:
                try:
                    audio_manager.stop()
                except Exception:
                    pass
            await ws_send(ws, {"type": "chat_done"})
            continue

        # --------------------------------------------
        # REPEAT — immediate
        # --------------------------------------------
        if text in {"repeat", "repeat that", "say that again"}:
            if speech_state.last_spoken_text:
                await nova_speak(ws, speech_state.last_spoken_text)
            else:
                await nova_speak(ws, "There's nothing to repeat yet.")
            await ws_send(ws, {"type": "chat_done"})
            continue

        # --------------------------------------------
        # TIME / DATE — deterministic
        # --------------------------------------------
        if text in {"what time is it", "what's the time"}:
            from datetime import datetime
            await nova_speak(ws, datetime.now().strftime("%I:%M %p"))
            await ws_send(ws, {"type": "chat_done"})
            continue

        if text in {"what's the date", "what date is it"}:
            from datetime import datetime
            await nova_speak(ws, datetime.now().strftime("%B %d, %Y"))
            await ws_send(ws, {"type": "chat_done"})
            continue

        # --------------------------------------------
        # Confirmation resolution (Phase-2 safe)
        # --------------------------------------------
        gate_result = confirmation_gate.try_resolve(text)
        if gate_result.handled:
            if gate_result.action:
                result = execute_action(gate_result.action)
                await nova_speak(ws, result.message)
            await ws_send(ws, {"type": "chat_done"})
            continue

        # --------------------------------------------
        # Skills (Phase-1 preserved)
        # --------------------------------------------
        skill_result = await skill_registry.handle_query(text)
        if skill_result:
            await nova_speak(
                ws,
                skill_result.message,
                skill=skill_result.skill,
                data=skill_result.data,
            )
            await ws_send(ws, {"type": "chat_done"})
            continue

        # --------------------------------------------
        # Recency guard (permission only, no ActionRequest)
        # --------------------------------------------
        if requires_recency_check(text):
            await nova_speak(
                ws,
                "That may require current information. I can give a general answer, but it may not be current."
            )
            await ws_send(ws, {"type": "chat_done"})
            continue

        # --------------------------------------------
        # LLM fallback (non-authoritative)
        #
        # Last resort only.
        # - No execution
        # - No memory writes
        # - No retries
        # - No follow-up prompts
        # - Text-only response
        # --------------------------------------------
        try:
            response = llm_manager.generate(text)

            if not isinstance(response, str) or not response.strip():
                response = "I’m not sure right now."

        except Exception as exc:
            logger.warning(f"LLM fallback failed: {exc}")
            response = "I’m not sure right now."

        await nova_speak(ws, response)
        await ws_send(ws, {"type": "chat_done"})
        continue
