# src/services/stt_engine.py
# Phase-3 STT Engine (LOCAL, INPUT-ONLY, FREEZE-READY)

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import traceback
import wave
from pathlib import Path

from vosk import Model, KaldiRecognizer

# --------------------------------------------------
# Model loading (ONCE, deterministic, local)
# Phase-3.5 SAFE: fail-closed, never crash Nova
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
VOSK_MODEL_PATH = BASE_DIR / "models" / "vosk-model-small-en-us-0.15"

_vosk_model = None


def get_vosk_model():
    """Lazily load the Vosk model."""
    global _vosk_model
    if _vosk_model is not None:
        return _vosk_model

    if not VOSK_MODEL_PATH.exists():
        print("[STT] Vosk model not found — STT disabled.")
        return None

    _vosk_model = Model(str(VOSK_MODEL_PATH))
    print("[STT] Vosk model loaded successfully")
    return _vosk_model


# --------------------------------------------------
# ffmpeg detection (PATH first, then bundled search)
# --------------------------------------------------

def _resolve_ffmpeg():
    """
    Locate ffmpeg executable.
    Priority:
    1. System PATH (shutil.which)
    2. Search recursively inside tools/ffmpeg/ for ffmpeg.exe
    Returns None if not found.
    """
    # 1) Check system PATH
    path = shutil.which("ffmpeg")
    if path:
        return path

    # 2) Search bundled directory dynamically (version‑independent)
    tools_dir = (
        Path(__file__).resolve().parents[2]
        / "tools"
        / "ffmpeg"
    )
    if tools_dir.exists():
        matches = list(tools_dir.rglob("ffmpeg.exe"))
        if matches:
            # Return the first found executable
            return str(matches[0])

    return None


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
    Convert incoming audio bytes to WAV (mono, 16k),
    then transcribe using Vosk.

    Returns:
        str: transcribed text (may be empty)
    """

    print(f"[STT] Starting transcription - Received {len(audio_bytes)} bytes")
    
    if not audio_bytes:
        print("[STT] No audio bytes received, returning empty")
        return ""

    # Ensure filename is always valid
    safe_name = filename or "audio.webm"
    print(f"[STT] Processing file: {safe_name}")

    # Resolve ffmpeg path (runtime check)
    ffmpeg_path = _resolve_ffmpeg()

    # DIAGNOSTIC: print the resolved path and whether it exists
    print("[STT] Using ffmpeg path:", ffmpeg_path)
    print("[STT] ffmpeg exists:", os.path.exists(ffmpeg_path) if ffmpeg_path else None)

    if ffmpeg_path is None:
        print("[STT] ffmpeg not found (PATH or bundled) — transcription disabled")
        return ""  # fail closed

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, safe_name)
        wav_path = os.path.join(tmpdir, "audio.wav")

        # Write raw audio file
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # Prepare ffmpeg command
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            wav_path,
        ]

        # Run ffmpeg in a thread to avoid blocking the event loop
        print("[STT] Converting audio to WAV format...")

        def run_ffmpeg():
            return subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

        try:
            result = await asyncio.to_thread(run_ffmpeg)

            if result.returncode != 0:
                print("[STT] Audio conversion failed")
                print("[STT] ffmpeg stderr:", result.stderr.decode(errors="ignore"))
                return ""
            print("[STT] Audio conversion successful")

        except Exception as e:
            print(f"[STT] Audio conversion exception: {type(e).__name__}: {e}")
            traceback.print_exc()
            return ""

        # Transcribe WAV - run Vosk in a thread to avoid blocking
        text = await asyncio.to_thread(_vosk_transcribe_wav_sync, str(wav_path))
        print(f"[STT] Transcription completed: '{text}' ({len(text)} chars)")
        return text