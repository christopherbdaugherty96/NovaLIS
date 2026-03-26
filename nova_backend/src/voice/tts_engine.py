from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from src.audio.audio_task_runner import run_speech_task
from src.conversation.response_formatter import ResponseFormatter
from src.governor.exceptions import LedgerWriteFailed
from src.ledger.writer import LedgerWriter
from src.rendering.speech_formatter import SpeechFormatter
from src.speech_state import speech_state

logger = logging.getLogger(__name__)


def _voice_preferred_engine_status() -> tuple[str, str]:
    project_root = Path(__file__).resolve().parents[2]
    bundled_piper = project_root / "tools" / "piper" / "piper.exe"
    piper_bin = str(bundled_piper) if bundled_piper.exists() else shutil.which("piper")
    if not piper_bin:
        return "unavailable", "Piper CLI not found."

    model_path = os.getenv("NOVA_PIPER_MODEL_PATH", "").strip()
    if not model_path:
        return "unavailable", "NOVA_PIPER_MODEL_PATH is not set."

    model_file = Path(model_path)
    if not model_file.exists():
        return "unavailable", f"Configured model is missing: {model_path}"

    return "ready", f"Piper ready with {model_file.name}."


def _voice_fallback_engine_status() -> tuple[str, str]:
    try:
        if importlib.util.find_spec("pyttsx3") is None:
            return "unavailable", "pyttsx3 is not installed."
    except Exception:
        return "unknown", "Fallback engine availability could not be checked."
    return "ready", "pyttsx3 fallback is available."


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

    def render(self, text: str) -> bool:
        # Prevent overlapping speech playback.
        if not self._playback_lock.acquire(blocking=False):
            return False

        output_path: Optional[Path] = None
        try:
            speak_text = self.formatter.format_for_tts(text)
            if not speak_text:
                return False

            # ----- Locate Piper executable (prefer bundled, fallback to PATH) -----
            project_root = Path(__file__).resolve().parents[2]   # up to nova_backend/
            bundled_piper = project_root / "tools" / "piper" / "piper.exe"
            if bundled_piper.exists():
                piper_bin = str(bundled_piper)
            else:
                piper_bin = shutil.which("piper")
                if not piper_bin:
                    self._warn_once_missing_piper()
                    logger.error("Piper CLI not found – TTS unavailable")
                    return False

            # ----- Model path from environment -----
            model_path = os.getenv("NOVA_PIPER_MODEL_PATH", "").strip()
            if not model_path:
                self._warn_once_missing_piper()
                logger.error("NOVA_PIPER_MODEL_PATH not set – TTS unavailable")
                return False

            model_file = Path(model_path)
            if not model_file.exists():
                self._warn_once_missing_piper()
                logger.error("Model file not found: %s", model_path)
                return False

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
            return self._play_wave(output_path)
        except Exception as e:
            logger.debug("TTS render exception: %s", e)
            return False
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
    def _play_wave(cls, output_path: Path) -> bool:
        if sys.platform == "win32":
            return cls._play_wave_windows(output_path)

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
                return True
            except Exception:
                continue
        return False

    @classmethod
    def _play_wave_windows(cls, output_path: Path) -> bool:
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
                return True
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
                return True
            except Exception:
                return False
        return False

    @classmethod
    def _warn_once_missing_piper(cls) -> None:
        if cls._warned_missing_piper:
            return
        cls._warned_missing_piper = True
        logger.warning("Piper TTS is not available – speech will be disabled.")


def stop_speaking() -> None:
    """Best-effort stop of currently playing speech."""
    SpeechRenderer.stop()
    speech_state.record_attempt(engine="runtime", status="stopped")
    try:
        from src.executors.tts_executor import TTSEngine
        TTSEngine.stop()
    except Exception:
        return


def inspect_voice_runtime() -> dict[str, str]:
    preferred_status, preferred_note = _voice_preferred_engine_status()
    fallback_status, fallback_note = _voice_fallback_engine_status()
    snapshot = speech_state.snapshot()
    summary_parts = [
        f"Preferred engine {preferred_status}.",
        f"Fallback engine {fallback_status}.",
    ]
    last_engine = str(snapshot.get("last_engine") or "").strip()
    last_status = str(snapshot.get("last_attempt_status") or "").strip()
    last_attempt_at = str(snapshot.get("last_attempt_at") or "").strip()
    if last_engine and last_status:
        recent = f"Last attempt {last_status} via {last_engine}"
        if last_attempt_at:
            recent += f" at {last_attempt_at}"
        summary_parts.append(recent + ".")
    elif last_attempt_at:
        summary_parts.append(f"Last voice attempt recorded at {last_attempt_at}.")
    if snapshot.get("last_error"):
        summary_parts.append(f"Last error: {snapshot['last_error']}.")
    else:
        summary_parts.append("Run a voice check on this device to confirm audible output.")
    return {
        "summary": " ".join(part for part in summary_parts if part).strip(),
        "preferred_engine": "piper",
        "preferred_status": preferred_status,
        "preferred_note": preferred_note,
        "fallback_engine": "pyttsx3",
        "fallback_status": fallback_status,
        "fallback_note": fallback_note,
        "last_engine": str(snapshot.get("last_engine") or ""),
        "last_attempt_status": str(snapshot.get("last_attempt_status") or ""),
        "last_attempt_at": str(snapshot.get("last_attempt_at") or ""),
        "last_error": str(snapshot.get("last_error") or ""),
        "last_spoken_text": str(snapshot.get("last_spoken_text") or ""),
    }


def nova_speak(text: str) -> None:
    """Default runtime speech path with profile-based rendering (non-blocking)."""
    speak_text = (text or "").strip()
    if not speak_text:
        return
    speech_state.record_attempt(engine="pending", status="queued", spoken_text=speak_text)
    try:
        LedgerWriter().log_event(
            "SPEECH_RENDERED",
            {
                "character_count": len(speak_text),
                "source": "nova_speak",
            },
        )
    except LedgerWriteFailed:
        # Speech rendering is best-effort and should not raise to callers.
        logger.debug("SPEECH_RENDERED ledger write failed")
    except Exception:
        logger.debug("Unexpected speech ledger error", exc_info=True)

    def _render_with_fallback() -> None:
        rendered = SpeechRenderer().render(speak_text)
        if rendered:
            speech_state.record_attempt(engine="piper", status="rendered", spoken_text=speak_text)
            return
        try:
            tts_executor = importlib.import_module("src.executors.tts_executor")
            engine_cls = getattr(tts_executor, "TTSEngine", None)
            if engine_cls is None:
                speech_state.record_attempt(
                    engine="runtime",
                    status="failed",
                    error="Fallback TTSEngine is unavailable.",
                    spoken_text=speak_text,
                )
                return
            speak_fn = getattr(engine_cls, "speak", None)
            if callable(speak_fn):
                speak_fn(speak_text)
                speech_state.record_attempt(engine="pyttsx3", status="rendered", spoken_text=speak_text)
            else:
                speech_state.record_attempt(
                    engine="runtime",
                    status="failed",
                    error="Fallback TTSEngine.speak is unavailable.",
                    spoken_text=speak_text,
                )
        except Exception:
            speech_state.record_attempt(
                engine="runtime",
                status="failed",
                error="Fallback speech render failed.",
                spoken_text=speak_text,
            )
            logger.debug("Fallback speech render failed", exc_info=True)

    # Use audio task helper to avoid direct threading outside allowed files.
    run_speech_task(_render_with_fallback)


def resolve_speakable_text(action_result: Any) -> str:
    """Resolve text suitable for speech output from an action result object."""
    if action_result is None:
        return ""

    data: Dict[str, Any] = getattr(action_result, "data", {}) or {}
    speakable = (data.get("speakable_text") or "").strip()
    if speakable:
        return ResponseFormatter.to_speakable_text(speakable)

    message = getattr(action_result, "user_message", "") or getattr(action_result, "message", "")
    return ResponseFormatter.to_speakable_text((message or "").strip())


def try_render_tts(text: str) -> bool:
    """Attempt synchronous Piper-backed playback and report whether audio started."""
    rendered = SpeechRenderer().render(text)
    speech_state.record_attempt(
        engine="piper" if rendered else "piper",
        status="rendered" if rendered else "failed",
        error="" if rendered else "Preferred Piper renderer could not play audio.",
        spoken_text=text,
    )
    return rendered
