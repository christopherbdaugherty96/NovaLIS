import asyncio
import io
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from starlette.datastructures import UploadFile


def test_safe_upload_filename_strips_paths():
    from src.services import stt_engine

    assert stt_engine._safe_upload_filename(r"..\\evil name?.webm") == "evil_name_.webm"
    assert stt_engine._safe_upload_filename(r"C:\\temp\\voice.wav") == "voice.wav"


def test_transcribe_bytes_sanitizes_uploaded_filename(monkeypatch):
    from src.services import stt_engine

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = list(cmd)
        return SimpleNamespace(returncode=0, stderr=b"")

    monkeypatch.setattr(stt_engine, "_resolve_ffmpeg", lambda: "ffmpeg")
    monkeypatch.setattr(stt_engine.subprocess, "run", fake_run)
    monkeypatch.setattr(stt_engine, "_vosk_transcribe_wav_sync", lambda _wav: "hello")

    out = asyncio.run(stt_engine.transcribe_bytes(b"audio-bytes", r"C:\temp\evil.webm"))

    assert out == "hello"
    input_path = Path(captured["cmd"][3]).as_posix().lower()
    assert input_path.endswith("/evil.webm")
    assert "c:/temp/evil.webm" not in input_path


def test_transcribe_bytes_returns_empty_on_ffmpeg_timeout(monkeypatch):
    from src.services import stt_engine

    def fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="ffmpeg", timeout=1)

    monkeypatch.setattr(stt_engine, "_resolve_ffmpeg", lambda: "ffmpeg")
    monkeypatch.setattr(stt_engine.subprocess, "run", fake_run)

    out = asyncio.run(stt_engine.transcribe_bytes(b"audio-bytes", "speech.webm"))
    assert out == ""


def test_stt_router_rejects_oversized_audio():
    from src.routers.stt import STT_MAX_UPLOAD_BYTES, stt_transcribe

    payload = b"x" * (STT_MAX_UPLOAD_BYTES + 1)
    upload = UploadFile(file=io.BytesIO(payload), filename="speech.webm")
    response = asyncio.run(stt_transcribe(upload))

    data = json.loads(response.body.decode("utf-8"))
    assert data["text"] == ""
    assert "too long" in data["error"].lower()
