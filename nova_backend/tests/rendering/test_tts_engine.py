from __future__ import annotations

import types

from src.voice import tts_engine


def test_nova_speak_falls_back_to_tts_executor_when_renderer_unavailable(monkeypatch):
    spoken: list[str] = []

    monkeypatch.setattr(tts_engine, "run_speech_task", lambda fn: fn())
    monkeypatch.setattr(tts_engine.SpeechRenderer, "render", lambda self, text: False)
    monkeypatch.setattr(
        tts_engine,
        "LedgerWriter",
        lambda: types.SimpleNamespace(log_event=lambda *args, **kwargs: None),
    )
    monkeypatch.setattr(
        tts_engine.importlib,
        "import_module",
        lambda _name: types.SimpleNamespace(TTSEngine=types.SimpleNamespace(speak=lambda text: spoken.append(text))),
    )

    tts_engine.nova_speak("Hello from Nova")

    assert spoken == ["Hello from Nova"]


def test_nova_speak_does_not_use_fallback_when_renderer_succeeds(monkeypatch):
    spoken: list[str] = []

    monkeypatch.setattr(tts_engine, "run_speech_task", lambda fn: fn())
    monkeypatch.setattr(tts_engine.SpeechRenderer, "render", lambda self, text: True)
    monkeypatch.setattr(
        tts_engine,
        "LedgerWriter",
        lambda: types.SimpleNamespace(log_event=lambda *args, **kwargs: None),
    )
    monkeypatch.setattr(
        tts_engine.importlib,
        "import_module",
        lambda _name: types.SimpleNamespace(TTSEngine=types.SimpleNamespace(speak=lambda text: spoken.append(text))),
    )

    tts_engine.nova_speak("Hello from Nova")

    assert spoken == []


def test_inspect_voice_runtime_reports_engine_availability(monkeypatch):
    monkeypatch.setattr(tts_engine, "_voice_preferred_engine_status", lambda: ("ready", "Preferred engine ready."))
    monkeypatch.setattr(tts_engine, "_voice_fallback_engine_status", lambda: ("ready", "Fallback engine ready."))
    monkeypatch.setattr(
        tts_engine.speech_state,
        "snapshot",
        lambda: {
            "last_engine": "piper",
            "last_attempt_status": "rendered",
            "last_error": "",
            "last_attempt_at": "2026-03-26T12:00:00Z",
            "last_spoken_text": "Nova voice check complete.",
        },
    )

    snapshot = tts_engine.inspect_voice_runtime()

    assert snapshot["preferred_status"] == "ready"
    assert snapshot["fallback_status"] == "ready"
    assert snapshot["last_engine"] == "piper"
    assert snapshot["last_attempt_status"] == "rendered"
    assert "Last attempt rendered via piper" in snapshot["summary"]
