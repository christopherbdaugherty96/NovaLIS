# src/routers/stt.py
# Phase-3 STT Router (freeze-ready)

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from src.services.stt_engine import transcribe_bytes

# IMPORTANT:
# No prefix here. Full path is defined explicitly.
router = APIRouter(tags=["stt"])

STT_MAX_UPLOAD_BYTES = 8 * 1024 * 1024


@router.post("/stt/transcribe")
async def stt_transcribe(audio: UploadFile = File(...)):
    """
    Accepts recorded audio from frontend (audio/webm),
    converts + transcribes locally via ffmpeg + Vosk,
    and returns plain text only.

    No intent inference.
    No actions.
    No memory writes.
    """

    # Read uploaded audio bytes
    audio_bytes = await audio.read()

    if not audio_bytes:
        # Silence-safe failure
        return JSONResponse({"text": ""})

    if len(audio_bytes) > STT_MAX_UPLOAD_BYTES:
        return JSONResponse(
            {
                "text": "",
                "error": "That audio clip is too long. Please try a shorter recording.",
            }
        )

    # Transcribe (stateless, local)
    try:
        text = await transcribe_bytes(audio_bytes, audio.filename)
    except Exception as e:
        # Fail closed, never crash Nova
        print("STT error:", e)
        return JSONResponse({"text": "", "error": "I couldn't process that recording."})

    # Return text only
    return JSONResponse({"text": (text or "").strip()})
