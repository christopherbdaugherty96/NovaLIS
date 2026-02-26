from __future__ import annotations

import importlib
import logging

from src.actions.action_result import ActionResult

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


def execute_tts(req, action_result_cls=ActionResult) -> ActionResult:
    text = (req.params or {}).get("text", "")
    text = (text or "").strip()

    if not text:
        log.warning("TTS called with empty text")
        return action_result_cls.failure(
            "I don’t have anything to speak.",
            request_id=req.request_id,
        )

    try:
        log.info("Speaking text (length %d chars)", len(text))
        TTSEngine.speak(text)
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
