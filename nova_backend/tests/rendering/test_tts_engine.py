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
