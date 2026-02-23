# src/services/stt_engine.py
# Phase-3 STT Engine (LOCAL, INPUT-ONLY, FREEZE-READY)

import asyncio
import subprocess
import tempfile
import os
import json
import shutil
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
    if ffmpeg_path is None:
        print("[STT] ffmpeg not found (PATH or bundled) — transcription disabled")
        return ""  # fail closed

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, safe_name)
        wav_path = os.path.join(tmpdir, "audio.wav")

        # Write raw audio file
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # Convert to WAV via ffmpeg asynchronously
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            wav_path,
        ]

        try:
            print("[STT] Converting audio to WAV format...")
            # Run ffmpeg without blocking the event loop
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            returncode = await process.wait()

            if returncode != 0:
                print("[STT] Audio conversion failed (ffmpeg error)")
                return ""
            print("[STT] Audio conversion successful")

        except Exception as e:
            print(f"[STT] Audio conversion exception: {e}")
            return ""

        # Transcribe WAV - use lazy-loaded model
        model = get_vosk_model()
        if model is None:
            print("[STT] Model unavailable, transcription disabled")
            return ""

        print("[STT] Model available, starting transcription...")
        recognizer = KaldiRecognizer(model, 16000)

        with open(wav_path, "rb") as wf:
            while True:
                data = wf.read(4000)
                if not data:
                    break
                recognizer.AcceptWaveform(data)

        result = recognizer.FinalResult()

        try:
            parsed = json.loads(result)
            text = parsed.get("text", "").strip()
            print(f"[STT] Transcription completed: '{text}' ({len(text)} chars)")
            return text
        except json.JSONDecodeError:
            print("[STT] JSON parse error in transcription result")
            return ""