from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SESSION_HANDLER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "websocket" / "session_handler.py"


def test_websocket_ping_is_noop_keepalive_before_command_dispatch():
    source = SESSION_HANDLER_PATH.read_text(encoding="utf-8")

    assert 'if msg_type == "ping":' in source
    assert "Do not process or respond." in source
    assert "continue" in source

    ping_index = source.index('if msg_type == "ping":')
    get_thought_index = source.index('if msg_type == "get_thought":')
    assert ping_index < get_thought_index
