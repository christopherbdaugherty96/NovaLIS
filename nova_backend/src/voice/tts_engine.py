from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

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
    _playback_lock = threading.Lock()
    _active_player: Optional[subprocess.Popen] = None

    def __init__(self, profile: VoiceProfile | None = None):
        self.profile = profile or VoiceProfile()
        self.formatter = SpeechFormatter()

    def render(self, text: str) -> None:
        # Prevent overlapping speech playback.
        if not self._playback_lock.acquire(blocking=False):
            return

        output_path: Optional[Path] = None
        try:
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

            temp_dir = Path(os.getenv("TEMP") or tempfile.gettempdir() or "/tmp")
            output_path = temp_dir / f"nova_tts_{uuid4().hex}.wav"
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
        finally:
            if output_path:
                try:
                    output_path.unlink(missing_ok=True)
                except Exception:
                    pass
            self._active_player = None
            self._playback_lock.release()

    @classmethod
    def stop(cls) -> None:
        player = cls._active_player
        if player is None:
            return
        try:
            if player.poll() is None:
                player.terminate()
        except Exception:
            return

    @classmethod
    def _play_wave(cls, output_path: Path) -> None:
        if sys.platform == "win32":
            cls._play_wave_windows(output_path)
            return

        for player in ("aplay", "paplay", "ffplay"):
            bin_path = shutil.which(player)
            if not bin_path:
                continue
            try:
                if player == "ffplay":
                    proc = subprocess.Popen(
                        [bin_path, "-nodisp", "-autoexit", "-loglevel", "quiet", str(output_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    proc = subprocess.Popen(
                        [bin_path, str(output_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                cls._active_player = proc
                proc.wait(timeout=10)
                return
            except Exception:
                continue

    @classmethod
    def _play_wave_windows(cls, output_path: Path) -> None:
        # Primary: Windows native SoundPlayer via PowerShell
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell:
            script = f"(New-Object Media.SoundPlayer '{str(output_path)}').PlaySync();"
            try:
                proc = subprocess.Popen(
                    [powershell, "-NoProfile", "-Command", script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                cls._active_player = proc
                proc.wait(timeout=10)
                return
            except Exception:
                pass

        ffplay = shutil.which("ffplay")
        if ffplay:
            try:
                proc = subprocess.Popen(
                    [ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet", str(output_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                cls._active_player = proc
                proc.wait(timeout=10)
            except Exception:
                return

    @classmethod
    def _warn_once_missing_piper(cls) -> None:
        if cls._warned_missing_piper:
            return
        cls._warned_missing_piper = True


def stop_speaking() -> None:
    """Best-effort stop of currently playing speech."""
    SpeechRenderer.stop()


def nova_speak(text: str) -> None:
    """Default runtime speech path with profile-based rendering (non-blocking)."""
    threading.Thread(target=SpeechRenderer().render, args=(text,), daemon=True).start()


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
