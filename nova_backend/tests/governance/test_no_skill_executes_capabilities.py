from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = PROJECT_ROOT / "src" / "skills"

FORBIDDEN_PATTERNS = [
    "handle_governed_invocation",
    "governor.",
    "ActionRequest(",
    "executor",
    "capability_id",
]


def test_skills_do_not_execute_or_reference_capability_execution_surface():
    offenders: list[str] = []

    for py_file in SKILLS_ROOT.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="replace")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                offenders.append(f"{py_file}: found forbidden pattern '{pattern}'")

    assert not offenders, "\n".join(offenders)
