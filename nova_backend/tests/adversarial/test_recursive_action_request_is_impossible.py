# tests/adversarial/test_recursive_action_request_is_impossible.py
from __future__ import annotations

from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, read_text

"""
Goal:
- No module outside governor.py may instantiate ActionRequest.
- Easiest mechanical check: ActionRequest( ... ) only appears in governor.py.
- Stronger check: ActionRequest constructor is private / not importable.
"""

ACTION_REQUEST_CTOR = "ActionRequest("

GOVERNOR_FILE = SRC_ROOT / "governor" / "governor.py"


def test_action_request_constructed_only_in_governor_py():
    assert GOVERNOR_FILE.exists(), f"Missing {GOVERNOR_FILE}"
    all_py = [
        p for p in SRC_ROOT.rglob("*.py")
        if "__pycache__" not in p.parts and "archive_quarantine" not in p.parts
    ]

    offenders = []
    for py in all_py:
        text = read_text(py)
        if ACTION_REQUEST_CTOR in text and py != GOVERNOR_FILE:
            offenders.append(py)

    assert not offenders, "ActionRequest constructor used outside governor.py:\n" + "\n".join(
        f"- {p}" for p in offenders
    )