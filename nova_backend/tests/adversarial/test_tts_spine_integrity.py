from __future__ import annotations

from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, read_text


TTS_EXECUTOR = SRC_ROOT / "executors" / "tts_executor.py"
BRAIN_SERVER = SRC_ROOT / "brain_server.py"
GOVERNOR_FILE = SRC_ROOT / "governor" / "governor.py"


def test_tts_engine_speak_only_called_in_tts_executor():
    offenders: list[Path] = []
    for py in SRC_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = read_text(py)
        if "TTSEngine.speak(" in text and py != TTS_EXECUTOR:
            offenders.append(py)

    assert not offenders, "TTSEngine.speak() used outside tts_executor:\n" + "\n".join(str(p) for p in offenders)


def test_brain_server_uses_renderer_for_voice_auto_tts():
    text = read_text(BRAIN_SERVER)
    assert "nova_speak(" in text
    assert "governor.handle_governed_invocation(18" not in text
    assert "execute_tts(" not in text
    assert "TTSEngine.speak(" not in text


def test_governor_routes_capability_18_to_tts_executor():
    text = read_text(GOVERNOR_FILE)
    assert "elif req.capability_id == 18" in text
    assert "from src.executors.tts_executor import execute_tts" in text
