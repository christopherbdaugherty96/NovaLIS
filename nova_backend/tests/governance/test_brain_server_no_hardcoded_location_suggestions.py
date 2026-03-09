from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRAIN_SERVER_PATH = PROJECT_ROOT / "src" / "brain_server.py"


def test_clarification_suggestions_do_not_hardcode_city():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8", errors="replace")
    assert "search weather in Ann Arbor" not in source
