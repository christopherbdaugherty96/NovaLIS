from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from src.rendering.speech_formatter import SpeechFormatter


@dataclass(frozen=True)
class VoiceProfile:
    """Runtime-configurable voice profile for calm, butler-like delivery."""

    rate_wpm: int = 165
    volume: float = 0.92
    voice_hint: Optional[str] = None


class SpeechRenderer:
    """TTS renderer abstraction using Piper for offline neural speech."""

    _warned_missing_piper = False

    def __init__(self, profile: VoiceProfile | None = None):
        self.profile = profile or VoiceProfile()
        self.formatter = SpeechFormatter()

    def render(self, text: str) -> None:
        speak_text = self.formatter.format_for_tts(text)
        if not speak_text:
            return

        piper_bin = shutil.which("piper")
        model_path = os.getenv("NOVA_PIPER_MODEL_PATH", "").strip()
        if not piper_bin or not model_path:
            self._warn_once_missing_piper()
            return

        model_file = Path(model_path)
        if not model_file.exists():
            self._warn_once_missing_piper()
            return

        output_path = Path("/tmp") / "nova_tts.wav"
        cmd = [
            piper_bin,
            "--model",
            str(model_file),
            "--output_file",
            str(output_path),
            "--sentence_silence",
            "0.2",
        ]

        if self.profile.voice_hint:
            cmd.extend(["--speaker", self.profile.voice_hint])

        try:
            subprocess.run(
                cmd,
                input=speak_text.encode("utf-8"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=10,
            )
            self._play_wave(output_path)
        except Exception:
            return

    @staticmethod
    def _play_wave(output_path: Path) -> None:
        for player in ("aplay", "paplay", "ffplay"):
            bin_path = shutil.which(player)
            if not bin_path:
                continue
            try:
                if player == "ffplay":
                    subprocess.run(
                        [bin_path, "-nodisp", "-autoexit", "-loglevel", "quiet", str(output_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        timeout=10,
                    )
                else:
                    subprocess.run(
                        [bin_path, str(output_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        timeout=10,
                    )
                return
            except Exception:
                continue

    @classmethod
    def _warn_once_missing_piper(cls) -> None:
        if cls._warned_missing_piper:
            return
        cls._warned_missing_piper = True


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
