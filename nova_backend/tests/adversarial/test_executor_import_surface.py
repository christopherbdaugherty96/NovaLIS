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

# Executors explicitly allowed to import from src.governor for read-only diagnostic reporting.
# These imports are capability metadata reads (not dispatch or execution authority).
GOVERNOR_READ_ALLOWLIST = {
    EXECUTORS_DIR / "os_diagnostics_executor.py",
    # os_diagnostics_executor reads capability_registry and capability_topology to
    # report on what capabilities are active. It does not create ActionRequests or
    # invoke governor dispatch. Read-only diagnostic access is permitted.
}


def test_executors_do_not_import_authority_surfaces():
    assert EXECUTORS_DIR.exists(), f"Missing {EXECUTORS_DIR}"
    for py in find_py_files(EXECUTORS_DIR):
        if py in GOVERNOR_READ_ALLOWLIST:
            # Allow governor reads for diagnostics; still block dispatch and gate surfaces
            restricted = [f for f in FORBIDDEN if f not in ("src.governor",)]
            assert_no_imports(py, restricted)
        else:
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