from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COGNITION_ROOT = PROJECT_ROOT / "src" / "cognition"


FORBIDDEN_MODULE_IMPORTS = {
    "subprocess",
    "requests",
    "urllib",
    "socket",
}

FORBIDDEN_FROM_IMPORT_PREFIXES = (
    "src.executors",
    "src.governor.governor",
    "src.governor.capability_registry",
)

FORBIDDEN_CALL_NAMES = {"eval", "exec"}
FORBIDDEN_ATTRIBUTE_CALLS = {("os", "system"), ("subprocess", "run"), ("subprocess", "Popen")}


def test_cognition_modules_are_analysis_only_and_non_authorizing():
    offenders: list[str] = []

    for py_file in COGNITION_ROOT.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".", 1)[0]
                    if root_name in FORBIDDEN_MODULE_IMPORTS:
                        offenders.append(f"{py_file}: forbidden import '{alias.name}'")

            if isinstance(node, ast.ImportFrom):
                module = (node.module or "").strip()
                if module.startswith(FORBIDDEN_FROM_IMPORT_PREFIXES):
                    offenders.append(f"{py_file}: forbidden from-import '{module}'")
                if module.split(".", 1)[0] in FORBIDDEN_MODULE_IMPORTS:
                    offenders.append(f"{py_file}: forbidden from-import '{module}'")

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALL_NAMES:
                    offenders.append(f"{py_file}: forbidden call '{node.func.id}'")
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    pair = (node.func.value.id, node.func.attr)
                    if pair in FORBIDDEN_ATTRIBUTE_CALLS:
                        offenders.append(f"{py_file}: forbidden call '{pair[0]}.{pair[1]}'")

    assert not offenders, "\n".join(offenders)
