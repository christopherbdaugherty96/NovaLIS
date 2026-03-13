from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_brain_server_exposes_opt_in_pattern_review_controls():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")

    assert "PATTERN_STATUS_COMMANDS" in source
    assert "PATTERN_OPT_IN_RE" in source
    assert "PATTERN_REVIEW_RE" in source
    assert "send_pattern_review_widget" in source
    assert "PATTERN_REVIEW_GENERATED" in source
    assert "pattern opt in" in source
    assert "review patterns" in source
