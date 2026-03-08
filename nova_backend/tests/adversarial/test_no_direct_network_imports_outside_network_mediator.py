# tests/adversarial/test_no_direct_network_imports_outside_network_mediator.py
from __future__ import annotations

from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, ast_imports

"""
Goal:
- Only src/governor/network_mediator.py may import network libraries.
- Scan full active source tree and only exempt archive/quarantine trees.
"""

NETWORK_LIBS = {"requests", "httpx", "urllib", "urllib3", "socket", "aiohttp"}

NETWORK_MEDIATOR_PATH = SRC_ROOT / "governor" / "network_mediator.py"
ALLOWED_NETWORK_IMPORT_FILES = {
    NETWORK_MEDIATOR_PATH,
    SRC_ROOT / "llm" / "llm_manager.py",
    SRC_ROOT / "llm" / "llm_manager_vlock.py",
    SRC_ROOT / "llm" / "model_network_mediator.py",
}


def _is_exempt(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    return any("archive" in part or "quarantine" in part for part in parts)


def test_only_network_mediator_imports_network_libs():
    assert NETWORK_MEDIATOR_PATH.exists(), f"Missing {NETWORK_MEDIATOR_PATH}"

    all_py = [p for p in SRC_ROOT.rglob("*.py") if "__pycache__" not in p.parts and not _is_exempt(p)]
    offenders: list[tuple[Path, set[str]]] = []

    for py in all_py:
        imports = ast_imports(py)
        imported_top = {imp.split(".", 1)[0] for imp in imports}
        used = imported_top.intersection(NETWORK_LIBS)
        if used and py not in ALLOWED_NETWORK_IMPORT_FILES:
            offenders.append((py, used))

    assert not offenders, "Network imports found outside NetworkMediator:\n" + "\n".join(
        f"- {p}: {sorted(list(used))}" for p, used in offenders
    )
