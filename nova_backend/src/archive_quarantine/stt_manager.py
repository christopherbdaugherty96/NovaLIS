# ============================================================
# NOVA HYBRID SPEECH-TO-TEXT ENGINE (Local + Cloud)
# Final STT B version (tempfile-based, production ready)
# ============================================================

import os
import tempfile
from faster_whisper import WhisperModel
from openai import OpenAI
import soundfile as sf

# ----------------------------
# CONFIG
# ----------------------------
STT_MODE = "hybrid"   # options: "local", "cloud", "hybrid"
HYBRID_MAX_LOCAL_SECONDS = 8.0   # If audio > 8 sec → prefer cloud

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# ----------------------------
# LOCAL WHISPER MODEL
# ----------------------------
print("🎙️ Loading local Whisper model (tiny, int8)…")
local_model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)


# ------------------------------------------------------------
# Lazy OpenAI client (created only when cloud STT is used)
# ------------------------------------------------------------
_openai_client = None

def _get_openai_client():
    global _openai_client
    if _openai_client is None and OPENAI_KEY:
        _openai_client = OpenAI(api_key=OPENAI_KEY)
    return _openai_client


def _duration_of_wav(path: str) -> float:
    try:
        audio, sr = sf.read(path)
        return len(audio) / sr
    except Exception:
        return 0.0


def _local_transcribe(path: str) -> str:
    try:
        segments, info = local_model.transcribe(path, beam_size=1)
        text = " ".join([seg.text for seg in segments])
        return text.strip()
    except Exception as e:
        print("LOCAL STT ERROR:", e)
        return ""


def _cloud_transcribe(path: str) -> str:
    client = _get_openai_client()
    if not client:
        print("No OPENAI_API_KEY set; cannot use cloud STT.")
        return ""

    try:
        with open(path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        if isinstance(resp, str):
            return resp.strip()
        return str(resp)
    except Exception as e:
        print("CLOUD STT ERROR:", e)
        return ""


def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """
    Main entry: takes raw audio bytes, writes to temp file,
    runs hybrid STT, returns text.
    Temporary file is always deleted after processing.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        duration = _duration_of_wav(tmp_path)
        print(f"[HybridSTT] Audio length = {duration:.2f}s")

        # Forced modes
        if STT_MODE == "local":
            return _local_transcribe(tmp_path)

        if STT_MODE == "cloud":
            return _cloud_transcribe(tmp_path)

        # HYBRID decision
        if duration > HYBRID_MAX_LOCAL_SECONDS:
            print("→ Long audio → trying CLOUD STT")
            text = _cloud_transcribe(tmp_path)
            if text:
                return text

        print("→ Trying LOCAL STT")
        text = _local_transcribe(tmp_path)
        if text and len(text.split()) >= 2:
            return text

        print("→ Local uncertain → CLOUD fallback")
        return _cloud_transcribe(tmp_path)

    finally:
        # Always clean up temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass