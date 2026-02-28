from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"

ALLOWED_REQUESTS_IMPORT_FILES = {
    SRC_ROOT / "governor" / "network_mediator.py",
    SRC_ROOT / "llm" / "llm_manager.py",
    SRC_ROOT / "llm" / "llm_manager_vlock.py",
    SRC_ROOT / "llm" / "inference_wrapper.py",
    SRC_ROOT / "llm" / "ilic.py",
}


def _imports(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"), filename=str(py_file))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def _is_archive(path: Path) -> bool:
    low = {part.lower() for part in path.parts}
    return any("archive" in part or "quarantine" in part for part in low)


def test_requests_imports_restricted_to_mediator_and_ilic_modules():
    offenders: list[str] = []
    for py in SRC_ROOT.rglob("*.py"):
        if _is_archive(py):
            continue
        imports = _imports(py)
        if any(m == "requests" or m.startswith("requests.") for m in imports):
            if py not in ALLOWED_REQUESTS_IMPORT_FILES:
                offenders.append(str(py))

    assert not offenders, "Direct requests import outside approved modules:\n" + "\n".join(offenders)
