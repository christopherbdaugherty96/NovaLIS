from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.rendering.speech_formatter import SpeechFormatter


@dataclass(frozen=True)
class VoiceProfile:
    """Runtime-configurable voice profile for calm, butler-like delivery."""

    rate_wpm: int = 165
    volume: float = 0.92
    voice_hint: Optional[str] = None


class SpeechRenderer:
    """TTS renderer abstraction so engine backends can be swapped later."""

    def __init__(self, profile: VoiceProfile | None = None):
        self.profile = profile or VoiceProfile()
        self.formatter = SpeechFormatter()

    def render(self, text: str) -> None:
        speak_text = self.formatter.format_for_tts(text)
        if not speak_text:
            return

        try:
            import pyttsx3

            engine = pyttsx3.init()
            self._apply_profile(engine)
            engine.say(speak_text)
            engine.runAndWait()
        except Exception:
            # Keep failure silent to preserve conversational flow.
            return

    def _apply_profile(self, engine: Any) -> None:
        try:
            engine.setProperty("rate", self.profile.rate_wpm)
            engine.setProperty("volume", max(0.0, min(1.0, self.profile.volume)))

            if self.profile.voice_hint:
                hint = self.profile.voice_hint.lower()
                for voice in engine.getProperty("voices") or []:
                    name = getattr(voice, "name", "").lower()
                    if hint in name:
                        engine.setProperty("voice", getattr(voice, "id", None))
                        break
        except Exception:
            return


def nova_speak(text: str) -> None:
    """Default runtime speech path with profile-based rendering."""
    SpeechRenderer().render(text)


def resolve_speakable_text(action_result: Any) -> str:
    """Resolve text suitable for speech output from an action result object."""
    if action_result is None:
        return ""

    data: Dict[str, Any] = getattr(action_result, "data", {}) or {}
    speakable = (data.get("speakable_text") or "").strip()
    if speakable:
        return speakable

    message = getattr(action_result, "user_message", "") or getattr(action_result, "message", "")
    return (message or "").strip()
