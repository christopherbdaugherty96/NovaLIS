from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_governed_invocation_branch_increments_turn_count():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"if isinstance\(inv_result, Invocation\):(?P<body>.*?)elif isinstance\(inv_result, Clarification\):",
        source,
        flags=re.DOTALL,
    )
    assert match is not None
    assert 'session_state["turn_count"] += 1' in match.group("body")


def test_clarification_branch_increments_turn_count():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"elif isinstance\(inv_result, Clarification\):(?P<body>.*?)# --- inv_result is None",
        source,
        flags=re.DOTALL,
    )
    assert match is not None
    assert 'session_state["turn_count"] += 1' in match.group("body")
