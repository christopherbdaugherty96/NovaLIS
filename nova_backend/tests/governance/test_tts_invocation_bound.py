from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRAIN_SERVER_PATH = PROJECT_ROOT / "src" / "brain_server.py"
TTS_EXECUTOR_PATH = PROJECT_ROOT / "src" / "executors" / "tts_executor.py"


def test_brain_server_does_not_auto_invoke_capability_18():
    text = BRAIN_SERVER_PATH.read_text(encoding="utf-8", errors="replace")

    forbidden_snippets = [
        'last_input_channel") == "voice"',
        "handle_governed_invocation(18",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in text, f"Auto-TTS trigger snippet found in brain_server: {snippet}"


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

    # only governor should invoke execute_tts
    allowed = {str(src_root / "governor" / "governor.py")}
    extra = [p for p in offenders if p not in allowed]
    assert not extra, f"execute_tts invoked outside Governor: {extra}"
