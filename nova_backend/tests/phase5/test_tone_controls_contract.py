from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"
SESSION_HANDLER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "websocket" / "session_handler.py"


def test_brain_server_exposes_manual_tone_controls_and_widget_updates():
    source = (
        BRAIN_SERVER_PATH.read_text(encoding="utf-8")
        + "\n"
        + SESSION_HANDLER_PATH.read_text(encoding="utf-8")
    )

    assert "TONE_STATUS_COMMANDS" in source
    assert "TONE_PROFILE_VIEWED" in source
    assert "TONE_PROFILE_UPDATED" in source
    assert "TONE_PROFILE_RESET" in source
    assert "send_tone_profile_widget" in source
    assert "tone set concise" in source
    assert "tone reset all" in source
