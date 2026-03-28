from src.actions.action_request import ActionRequest
from src.executors.tts_executor import execute_tts, TTSEngine


def test_execute_tts_fails_on_empty_text():
    req = ActionRequest(request_id="r1", capability_id=18, params={"text": "   "})
    result = execute_tts(req)
    assert result.success is False


def test_execute_tts_success_with_mocked_engine(monkeypatch):
    calls = []

    def fake_speak(text):
        calls.append(text)

    monkeypatch.setattr("src.executors.tts_executor.try_render_tts", lambda _text: False)
    monkeypatch.setattr(TTSEngine, "speak", fake_speak)

    req = ActionRequest(request_id="r2", capability_id=18, params={"text": "Hello"})
    result = execute_tts(req)

    assert result.success is True
    assert calls == ["Hello"]
    assert result.message == "I read that aloud."
    assert result.data["spoken_text"] == "Hello"
    assert result.data["character_count"] == 5


def test_execute_tts_prefers_piper_renderer_when_available(monkeypatch):
    fallback_calls = []

    monkeypatch.setattr("src.executors.tts_executor.try_render_tts", lambda text: text == "Hello")
    monkeypatch.setattr(TTSEngine, "speak", lambda text: fallback_calls.append(text))

    req = ActionRequest(request_id="r-piper", capability_id=18, params={"text": "Hello"})
    result = execute_tts(req)

    assert result.success is True
    assert fallback_calls == []
    assert result.message == "I read that aloud."
    assert result.data["spoken_text"] == "Hello"


def test_execute_tts_returns_failure_when_engine_raises(monkeypatch):
    events = []

    def broken_speak(_text):
        raise RuntimeError("engine failed")

    monkeypatch.setattr("src.executors.tts_executor.try_render_tts", lambda _text: False)
    monkeypatch.setattr(TTSEngine, "speak", broken_speak)
    monkeypatch.setattr(
        "src.executors.tts_executor.LedgerWriter",
        lambda: type("LedgerStub", (), {"log_event": staticmethod(lambda event, meta: events.append((event, dict(meta))))})(),
    )

    req = ActionRequest(request_id="r3", capability_id=18, params={"text": "Hello"})
    result = execute_tts(req)

    assert result.success is False
    assert "couldn't speak" in result.message.lower()
    assert events
    assert events[-1][0] == "SPEECH_RENDER_FAILED"
