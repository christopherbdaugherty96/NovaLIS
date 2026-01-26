# src/services/stt_engine.py
# Phase-3 STT Engine (LOCAL, INPUT-ONLY, FREEZE-READY)

import subprocess
import tempfile
import os
import json
from pathlib import Path

from vosk import Model, KaldiRecognizer

# --------------------------------------------------
# External binary (explicit, deterministic)
# --------------------------------------------------

FFMPEG_PATH = r"C:\Nova-Project\nova_backend\tools\ffmpeg\ffmpeg.exe"

# --------------------------------------------------
# Model loading (ONCE, deterministic, local)
# --------------------------------------------------

VOSK_MODEL_PATH = Path("models/vosk-model-small-en-us-0.15")

if not VOSK_MODEL_PATH.exists():
    raise RuntimeError(
        "Vosk model not found. "
        "Download and extract to: models/vosk-model-small-en-us-0.15"
    )

vosk_model = Model(str(VOSK_MODEL_PATH))

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

    if not audio_bytes:
        return ""

    # Ensure filename is always valid
    safe_name = filename or "audio.webm"

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, safe_name)
        wav_path = os.path.join(tmpdir, "audio.wav")

        # Write raw audio file
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # Convert to WAV via ffmpeg
        ffmpeg_cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            wav_path,
        ]

        try:
            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        except subprocess.CalledProcessError:
            return ""

        # Transcribe WAV
        recognizer = KaldiRecognizer(vosk_model, 16000)

        with open(wav_path, "rb") as wf:
            while True:
                data = wf.read(4000)
                if not data:
                    break
                recognizer.AcceptWaveform(data)

        result = recognizer.FinalResult()

        try:
            parsed = json.loads(result)
            return parsed.get("text", "").strip()
        except json.JSONDecodeError:
            return ""
