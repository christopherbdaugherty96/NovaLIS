from __future__ import annotations

import importlib
import logging
import threading

from src.actions.action_result import ActionResult
from src.ledger.writer import LedgerWriter
from src.rendering.speech_formatter import SpeechFormatter
from src.speech_state import speech_state
from src.voice.tts_engine import try_render_tts

log = logging.getLogger("nova")


class TTSEngine:
    """Singleton offline TTS engine using pyttsx3."""

    _engine = None
    _lock = threading.RLock()

    @classmethod
    def speak(cls, text: str) -> None:
        with cls._lock:
            if cls._engine is None:
                pyttsx3 = importlib.import_module("pyttsx3")
                cls._engine = pyttsx3.init()

            if cls._engine.isBusy():
                cls._engine.stop()

            cls._engine.say(text)
            cls._engine.runAndWait()

    @classmethod
    def stop(cls) -> None:
        with cls._lock:
            if cls._engine is None:
                return
            try:
                cls._engine.stop()
            except Exception:
                return


def execute_tts(req, action_result_cls=ActionResult) -> ActionResult:
    text = (req.params or {}).get("text", "")
    text = (text or "").strip()
    session_id = str((req.params or {}).get("session_id") or "").strip() or None

    if not text:
        log.warning("TTS called with empty text")
        return action_result_cls.failure(
            "I don't have anything to speak.",
            request_id=req.request_id,
        )

    try:
        speak_text = SpeechFormatter().format_for_tts(text)
        if not speak_text:
            return action_result_cls.failure(
                "I couldn't find anything readable to speak after formatting the text.",
                request_id=req.request_id,
            )

        log.info("Speaking text (length %d chars)", len(speak_text))
        rendered = try_render_tts(speak_text)
        if not rendered:
            TTSEngine.speak(speak_text)
            speech_state.record_attempt(engine="pyttsx3", status="rendered", spoken_text=speak_text)
        try:
            metadata = {
                "request_id": req.request_id,
                "character_count": len(speak_text),
                "source": "capability_18",
                "engine": "piper" if rendered else "pyttsx3",
            }
            if session_id:
                metadata["session_id"] = session_id
            LedgerWriter().log_event(
                "SPEECH_RENDERED",
                metadata,
            )
        except Exception:
            log.debug("Unexpected speech ledger error in capability_18 path", exc_info=True)
        return action_result_cls(
            success=True,
            message="I read that aloud.",
            data={
                "spoken_text": speak_text,
                "character_count": len(speak_text),
            },
            request_id=req.request_id,
        )
    except Exception as error:
        speech_state.record_attempt(
            engine="runtime",
            status="failed",
            error=str(error),
            spoken_text=text,
        )
        log.error("TTS failed: %s", error)
        return action_result_cls.failure(
            "I couldn't speak that. Please try again.",
            request_id=req.request_id,
        )
