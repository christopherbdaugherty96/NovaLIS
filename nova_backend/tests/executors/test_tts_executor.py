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

    monkeypatch.setattr(TTSEngine, "speak", fake_speak)

    req = ActionRequest(request_id="r2", capability_id=18, params={"text": "Hello"})
    result = execute_tts(req)

    assert result.success is True
    assert calls == ["Hello"]
