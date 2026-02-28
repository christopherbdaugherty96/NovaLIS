from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRAIN_SERVER_PATH = PROJECT_ROOT / "src" / "brain_server.py"
TTS_EXECUTOR_PATH = PROJECT_ROOT / "src" / "executors" / "tts_executor.py"


def test_voice_auto_response_does_not_call_governor_tts_capability():
    text = BRAIN_SERVER_PATH.read_text(encoding="utf-8", errors="replace")

    voice_guard = 'last_input_channel") == "voice"'
    assert voice_guard in text, "Voice auto-response branch missing"

    assert 'governor.handle_governed_invocation(18, {"text": action_result.message})' not in text
    assert 'governor.handle_governed_invocation(18, {"text": message})' not in text
    assert 'governor.handle_governed_invocation(18, {"text": fallback_message})' not in text


def test_no_tts_execution_outside_governor_surface():
    text = TTS_EXECUTOR_PATH.read_text(encoding="utf-8", errors="replace")
    assert "def execute_tts(" in text, "Missing governed TTS execution entrypoint"

    src_root = PROJECT_ROOT / "src"
    offenders: list[str] = []
    for py in src_root.rglob("*.py"):
        if py == TTS_EXECUTOR_PATH:
            continue
        body = py.read_text(encoding="utf-8", errors="replace")
        if "execute_tts(" in body:
            offenders.append(str(py))

    allowed = {str(src_root / "governor" / "governor.py")}
    extra = [p for p in offenders if p not in allowed]
    assert not extra, f"execute_tts invoked outside Governor: {extra}"
