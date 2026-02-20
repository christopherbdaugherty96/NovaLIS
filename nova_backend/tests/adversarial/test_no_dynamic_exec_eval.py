# tests/adversarial/test_no_dynamic_exec_eval.py
from __future__ import annotations

import ast
from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, find_py_files, read_text

"""
Goal:
- Ban `eval`, `exec` and dynamic code execution in authority paths.
- You can scope this to src/governor, src/executors, src/gates.
"""

SCOPED_DIRS = [SRC_ROOT / "governor", SRC_ROOT / "executors", SRC_ROOT / "gates"]
BANNED_CALLS = {"eval", "exec"}


def _calls_banned(tree: ast.AST) -> list[str]:
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id in BANNED_CALLS:
                hits.append(fn.id)
    return hits


def test_no_exec_eval_in_authority_paths():
    offenders = []
    for d in SCOPED_DIRS:
        if not d.exists():
            continue
        for py in find_py_files(d):
            tree = ast.parse(read_text(py), filename=str(py))
            hits = _calls_banned(tree)
            if hits:
                offenders.append((py, hits))

    assert not offenders, "Found banned dynamic execution in authority paths:\n" + "\n".join(
        f"- {p}: {hits}" for p, hits in offenders
    )