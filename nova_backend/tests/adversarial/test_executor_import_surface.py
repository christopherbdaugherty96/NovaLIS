# tests/adversarial/test_executor_import_surface.py
from __future__ import annotations

from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, assert_no_imports, find_py_files

"""
Goal:
- Executors must be "dumb and bounded".
- They must NOT import governor, gates, or ActionRequest creation surfaces.
- They must NOT be able to recursively create/dispatch ActionRequests.
"""

EXECUTORS_DIR = SRC_ROOT / "executors"
ACTIONS_DIR = SRC_ROOT / "actions"

FORBIDDEN = [
    # authority surfaces
    "src.governor",                 # governor.*, execute_boundary.*, network_mediator
    "src.gates",                    # confirmation gate, etc.
    "src.actions.action_request",   # never create/shape ActionRequest from executor
    "src.actions.action_types",     # optional: forbid if you want pure data-free executors
    # dangerous runtime exec surfaces
    "subprocess",
    "os.system",
    "eval",
    "exec",
]


def test_executors_do_not_import_authority_surfaces():
    assert EXECUTORS_DIR.exists(), f"Missing {EXECUTORS_DIR}"
    for py in find_py_files(EXECUTORS_DIR):
        assert_no_imports(py, FORBIDDEN)


def test_actions_do_not_import_governor_directly():
    """
    Optional, stricter:
    - actions/* should not import src.governor.* either.
    """
    if not ACTIONS_DIR.exists():
        return
    for py in find_py_files(ACTIONS_DIR):
        assert_no_imports(py, ["src.governor", "src.gates"])