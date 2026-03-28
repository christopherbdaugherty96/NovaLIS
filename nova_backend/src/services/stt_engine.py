# src/services/stt_engine.py
# Phase-3 STT Engine (LOCAL, INPUT-ONLY, FREEZE-READY)

from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from vosk import KaldiRecognizer, Model

# --------------------------------------------------
# Model loading (ONCE, deterministic, local)
# Phase-3.5 SAFE: fail-closed, never crash Nova
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
VOSK_MODEL_PATH = BASE_DIR / "models" / "vosk-model-small-en-us-0.15"

FFMPEG_TIMEOUT_SECONDS = 15
MAX_UPLOAD_FILENAME_CHARS = 120

_vosk_model = None
log = logging.getLogger("nova.stt")


def get_vosk_model():
    """Lazily load the Vosk model."""
    global _vosk_model
    if _vosk_model is not None:
        return _vosk_model

    if not VOSK_MODEL_PATH.exists():
        log.warning("Vosk model not found; STT disabled.")
        return None

    _vosk_model = Model(str(VOSK_MODEL_PATH))
    log.info("Vosk model loaded successfully")
    return _vosk_model


def _stt_converter_status() -> tuple[str, str]:
    ffmpeg_path = _resolve_ffmpeg()
    if not ffmpeg_path:
        return "unavailable", "ffmpeg is not installed or bundled."
    return "ready", f"ffmpeg ready from {Path(ffmpeg_path).name}."


def _stt_model_status() -> tuple[str, str]:
    if not VOSK_MODEL_PATH.exists():
        return "unavailable", f"Vosk model is missing: {VOSK_MODEL_PATH.name}."
    return "ready", f"Vosk model ready: {VOSK_MODEL_PATH.name}."


def inspect_stt_runtime() -> dict[str, str]:
    converter_status, converter_note = _stt_converter_status()
    model_status, model_note = _stt_model_status()
    if converter_status == "ready" and model_status == "ready":
        status = "ready"
    elif converter_status == "ready" or model_status == "ready":
        status = "degraded"
    else:
        status = "unavailable"
    summary_parts = [
        f"Speech input {status}.",
        converter_note,
        model_note,
    ]
    return {
        "status": status,
        "summary": " ".join(part for part in summary_parts if part).strip(),
        "converter_status": converter_status,
        "converter_note": converter_note,
        "model_status": model_status,
        "model_note": model_note,
    }


# --------------------------------------------------
# ffmpeg detection (PATH first, then bundled search)
# --------------------------------------------------

def _resolve_ffmpeg() -> str | None:
    """
    Locate ffmpeg executable.
    Priority:
    1. System PATH (shutil.which)
    2. Search recursively inside tools/ffmpeg/ for ffmpeg.exe
    Returns None if not found.
    """
    path = shutil.which("ffmpeg")
    if path:
        return path

    tools_dir = Path(__file__).resolve().parents[2] / "tools" / "ffmpeg"
    if tools_dir.exists():
        matches = list(tools_dir.rglob("ffmpeg.exe"))
        if matches:
            return str(matches[0])

    return None


def _safe_upload_filename(filename: str | None) -> str:
    raw = (filename or "audio.webm").strip()
    basename = Path(raw).name.strip() or "audio.webm"
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", basename)
    if not safe:
        safe = "audio.webm"
    if "." not in safe:
        safe = f"{safe}.webm"
    return safe[:MAX_UPLOAD_FILENAME_CHARS]


# --------------------------------------------------
# Synchronous Vosk transcription (to be run in thread)
# --------------------------------------------------

def _vosk_transcribe_wav_sync(wav_path: str) -> str:
    """
    Synchronous Vosk transcription for a .wav file.
    Runs in a worker thread via asyncio.to_thread to avoid blocking the event loop.
    Must fail-closed and return "" on any error.
    """
    try:
        model = get_vosk_model()
        if model is None:
            return ""

        recognizer = KaldiRecognizer(model, 16000)

        with wave.open(wav_path, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                recognizer.AcceptWaveform(data)

        result = json.loads(recognizer.FinalResult() or "{}")
        text = (result.get("text") or "").strip()
        return text
    except Exception:
        return ""


# --------------------------------------------------
# Core transcription function
# --------------------------------------------------

async def transcribe_bytes(audio_bytes: bytes, filename: str | None) -> str:
    """
    Convert incoming audio bytes to WAV (mono, 16k), then transcribe using Vosk.

    Returns:
        str: transcribed text (may be empty)
    """
    if not audio_bytes:
        return ""

    safe_name = _safe_upload_filename(filename)
    ffmpeg_path = _resolve_ffmpeg()

    if ffmpeg_path is None:
        log.warning("ffmpeg not found (PATH or bundled); STT disabled for this request.")
        return ""

    if not VOSK_MODEL_PATH.exists():
        log.warning("Vosk model not found; STT disabled for this request.")
        return ""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir).resolve()
        input_path = (tmp_root / safe_name).resolve()
        wav_path = (tmp_root / "audio.wav").resolve()

        # Fail closed if a crafted name attempts to escape temp directory.
        if tmp_root not in input_path.parents:
            return ""

        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(input_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "wav",
            str(wav_path),
        ]

        def run_ffmpeg():
            return subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=FFMPEG_TIMEOUT_SECONDS,
            )

        try:
            result = await asyncio.to_thread(run_ffmpeg)
            if result.returncode != 0:
                log.warning("STT audio conversion failed with return code %s", result.returncode)
                log.debug("ffmpeg stderr: %s", result.stderr.decode(errors="ignore"))
                return ""
        except subprocess.TimeoutExpired:
            log.warning("STT audio conversion timed out after %ss", FFMPEG_TIMEOUT_SECONDS)
            return ""
        except Exception:
            log.exception("STT audio conversion exception")
            return ""

        text = await asyncio.to_thread(_vosk_transcribe_wav_sync, str(wav_path))
        log.debug("STT transcription completed (%d chars)", len(text))
        return text
