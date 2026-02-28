from __future__ import annotations

from typing import Any, Dict

def nova_speak(text: str) -> None:
    """
    Temporary direct TTS execution.
    Replace with governed Capability 18 routing if needed.
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

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
