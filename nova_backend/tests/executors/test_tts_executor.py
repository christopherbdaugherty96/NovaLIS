from src.actions.action_request import ActionRequest
from src.executors.tts_executor import execute_tts, TTSEngine


def test_execute_tts_fails_on_empty_text():
    req = ActionRequest(request_id="r1", capability_id=18, params={"text": "   "})
    result = execute_tts(req)
    assert result.success is False


def test_execute_tts_success_with_mocked_engine(monkeypatch):
    from src.executors import tts_executor as mod

    calls = []

    def fake_speak(text):
        calls.append(text)

    monkeypatch.setattr(mod, "run_speech_task", lambda task: task())
    monkeypatch.setattr(TTSEngine, "speak", fake_speak)

    req = ActionRequest(request_id="r2", capability_id=18, params={"text": "Hello"})
    result = execute_tts(req)

    assert result.success is True
    assert calls == ["Hello"]


def test_execute_tts_schedules_speech_without_inline_blocking(monkeypatch):
    from src.executors import tts_executor as mod

    scheduled = {"count": 0}
    called = {"speak": 0}

    def fake_run(task):
        scheduled["count"] += 1
        # Intentionally do not execute task here.
        return None

    def fake_speak(text):
        del text
        called["speak"] += 1

    monkeypatch.setattr(mod, "run_speech_task", fake_run)
    monkeypatch.setattr(TTSEngine, "speak", fake_speak)

    req = ActionRequest(request_id="r3", capability_id=18, params={"text": "Hello"})
    result = execute_tts(req)

    assert result.success is True
    assert scheduled["count"] == 1
    assert called["speak"] == 0
