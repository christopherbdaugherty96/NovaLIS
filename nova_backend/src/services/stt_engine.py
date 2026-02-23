# src/services/stt_engine.py
# Phase-3 STT Engine (LOCAL, INPUT-ONLY, FREEZE-READY)

import subprocess
import tempfile
import os
import json
import shutil                      # ADDED for ffmpeg detection
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
    """
    Lazily load the Vosk model.
    Phase-3.5 rule:
    - STT must NEVER crash server at import time
    - If model is missing, STT fails closed (returns empty text)
    """
    global _vosk_model

    if _vosk_model is not None:
        return _vosk_model

    if not VOSK_MODEL_PATH.exists():
        # Phase-3.5 compliant: fail closed, do not raise
        print(
            "[STT] Vosk model not found at "
            "models/vosk-model-small-en-us-0.15 — STT disabled."
        )
        return None

    _vosk_model = Model(str(VOSK_MODEL_PATH))
    print("[STT] Vosk model loaded successfully")
    return _vosk_model


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

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, safe_name)
        wav_path = os.path.join(tmpdir, "audio.wav")

        # Write raw audio file
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # --- ffmpeg detection (runtime, not import time) ---
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path is None:
            print("[STT] ffmpeg not found in PATH, transcription disabled")
            return ""  # fail closed

        # Convert to WAV via ffmpeg
        ffmpeg_cmd = [
            ffmpeg_path,            # now using detected path
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            wav_path,
        ]

        try:
            print("[STT] Converting audio to WAV format...")
            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            print("[STT] Audio conversion successful")
        except subprocess.CalledProcessError:
            print("[STT] Audio conversion failed")
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