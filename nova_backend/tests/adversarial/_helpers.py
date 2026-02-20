# tests/adversarial/_helpers.py
from __future__ import annotations

import ast
import importlib
import inspect
import os
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def ast_imports(py_file: Path) -> set[str]:
    """
    Returns top-level imported module names (best-effort) from a .py file.
    e.g. "requests", "httpx", "src.governor.governor"
    """
    tree = ast.parse(read_text(py_file), filename=str(py_file))
    mods: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module)
    return mods


def assert_no_imports(py_file: Path, forbidden_prefixes: Iterable[str]) -> None:
    imports = ast_imports(py_file)
    hits: list[str] = []
    for imp in imports:
        for pref in forbidden_prefixes:
            if imp == pref or imp.startswith(pref + "."):
                hits.append(imp)
    assert not hits, f"{py_file} has forbidden imports: {sorted(set(hits))}"


def find_py_files(root: Path, *, exclude_dirs: set[str] | None = None) -> list[Path]:
    exclude_dirs = exclude_dirs or set()
    out: list[Path] = []
    for p in root.rglob("*.py"):
        if any(part in exclude_dirs for part in p.parts):
            continue
        out.append(p)
    return out


def import_obj(dotted: str):
    """
    Import `module:attr` or `module.attr` target.
    Examples:
      - "src.governor.governor:Governor"
      - "src.governor.governor_mediator:mediate"
    """
    if ":" in dotted:
        mod, attr = dotted.split(":", 1)
    else:
        *mod_parts, attr = dotted.split(".")
        mod = ".".join(mod_parts)

    m = importlib.import_module(mod)
    return getattr(m, attr)


def try_find_callable(module_name: str, candidates: list[str]):
    """
    Utility for tests when you're not sure of exact API:
    it tries a list of names and returns the first callable found.
    """
    m = importlib.import_module(module_name)
    for name in candidates:
        obj = getattr(m, name, None)
        if callable(obj):
            return obj
    raise AssertionError(f"No callable found in {module_name}. Tried: {candidates}")