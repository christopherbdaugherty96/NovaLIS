# tests/adversarial/test_no_direct_network_imports_outside_network_mediator.py
from __future__ import annotations

from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, ast_imports, find_py_files

"""
Goal:
- Only src/governor/network_mediator.py may import network libraries.
"""

NETWORK_LIBS = {"requests", "httpx", "urllib", "urllib3", "socket", "aiohttp"}

NETWORK_MEDIATOR_PATH = SRC_ROOT / "governor" / "network_mediator.py"


def test_only_network_mediator_imports_network_libs():
    assert NETWORK_MEDIATOR_PATH.exists(), f"Missing {NETWORK_MEDIATOR_PATH}"

    all_py = find_py_files(SRC_ROOT, exclude_dirs={"__pycache__", "archive_phase4", "archive_quarantine", "llm"})
    offenders: list[tuple[Path, set[str]]] = []

    for py in all_py:
        imports = ast_imports(py)
        imported_top = {imp.split(".", 1)[0] for imp in imports}  # normalize
        used = imported_top.intersection(NETWORK_LIBS)
        if used and py != NETWORK_MEDIATOR_PATH:
            offenders.append((py, used))

    assert not offenders, "Network imports found outside NetworkMediator:\n" + "\n".join(
        f"- {p}: {sorted(list(used))}" for p, used in offenders
    )