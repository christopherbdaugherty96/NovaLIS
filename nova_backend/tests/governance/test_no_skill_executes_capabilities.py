from __future__ import annotations

from pathlib import Path
import ast


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = PROJECT_ROOT / "src" / "skills"


def test_skills_do_not_execute_or_reference_capability_execution_surface():
    offenders: list[str] = []

    for py_file in SKILLS_ROOT.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            # Detect direct calls like execute_xxx()
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id.startswith("execute_"):
                    offenders.append(f"{py_file}: direct call to {node.func.id}")
                if isinstance(node.func, ast.Attribute) and node.func.attr.startswith("execute_"):
                    offenders.append(f"{py_file}: direct call to {node.func.attr}")

            # Detect importing the actual Governor class (execution authority)
            if isinstance(node, ast.ImportFrom):
                if node.module == "src.governor.governor":
                    offenders.append(f"{py_file}: importing Governor class (execution surface)")

    assert not offenders, "\n".join(offenders)