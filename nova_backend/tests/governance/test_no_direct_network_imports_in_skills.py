from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = PROJECT_ROOT / "src" / "skills"

FORBIDDEN_IMPORT_TOPLEVEL = {"requests", "httpx", "socket", "urllib", "subprocess"}
FORBIDDEN_CALL_NAMES = {"system", "popen"}
FORBIDDEN_OPEN_WRITE_MODES = {"w", "a", "x", "wb", "ab", "xb", "w+", "a+", "x+"}


def _parse(py_file: Path) -> ast.AST:
    return ast.parse(py_file.read_text(encoding="utf-8", errors="replace"), filename=str(py_file))


def _imports(tree: ast.AST) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".", 1)[0])
    return out


def _attribute_chain(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def test_no_direct_network_or_exec_imports_in_skills():
    assert SKILLS_ROOT.exists(), f"Missing skills directory: {SKILLS_ROOT}"
    offenders: list[str] = []

    for py_file in SKILLS_ROOT.rglob("*.py"):
        tree = _parse(py_file)
        imports = _imports(tree)
        hit = imports.intersection(FORBIDDEN_IMPORT_TOPLEVEL)
        if hit:
            offenders.append(f"{py_file}: forbidden imports {sorted(hit)}")

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Direct Session(...) construction
                if isinstance(node.func, ast.Name) and node.func.id == "Session":
                    offenders.append(f"{py_file}:{node.lineno} direct Session(...) usage")

                # os.system / subprocess.* usage
                chain = _attribute_chain(node.func)
                if chain == "os.system" or chain.startswith("subprocess."):
                    offenders.append(f"{py_file}:{node.lineno} forbidden call {chain}")

                # open(..., mode='w'/'a'/...) write-like usage
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    mode_val = None
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                        mode_val = node.args[1].value
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            mode_val = kw.value.value
                    if mode_val and any(flag in mode_val for flag in FORBIDDEN_OPEN_WRITE_MODES):
                        offenders.append(f"{py_file}:{node.lineno} file write mode '{mode_val}'")

    assert not offenders, "\n".join(offenders)
