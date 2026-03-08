from __future__ import annotations

import importlib
import logging

from src.actions.action_result import ActionResult
from src.rendering.speech_formatter import SpeechFormatter

log = logging.getLogger("nova")


class TTSEngine:
    """Singleton offline TTS engine using pyttsx3."""

    _engine = None

    @classmethod
    def speak(cls, text: str) -> None:
        if cls._engine is None:
            pyttsx3 = importlib.import_module("pyttsx3")
            cls._engine = pyttsx3.init()

        if cls._engine.isBusy():
            cls._engine.stop()

        cls._engine.say(text)
        cls._engine.runAndWait()

    @classmethod
    def stop(cls) -> None:
        if cls._engine is None:
            return
        try:
            cls._engine.stop()
        except Exception:
            return


def execute_tts(req, action_result_cls=ActionResult) -> ActionResult:
    text = (req.params or {}).get("text", "")
    text = (text or "").strip()

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
                "I don't have anything to speak.",
                request_id=req.request_id,
            )

        log.info("Speaking text (length %d chars)", len(speak_text))
        TTSEngine.speak(speak_text)
        return action_result_cls(
            success=True,
            message="",
            data=None,
            request_id=req.request_id,
        )
    except Exception as error:
        log.error("TTS failed: %s", error)
        return action_result_cls.failure(
            "Speech failed.",
            request_id=req.request_id,
        )
