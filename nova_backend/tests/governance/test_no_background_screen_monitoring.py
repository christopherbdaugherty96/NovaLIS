from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
TARGET_ROOTS = [
    SRC_ROOT / "perception",
    SRC_ROOT / "context",
    # OpenClaw foundations remain manual-only today, so the module stays under the same
    # no-background-execution scan until a narrower scheduler carve-out is explicitly approved.
    SRC_ROOT / "openclaw",
]
TARGET_FILES = [
    SRC_ROOT / "executors" / "screen_capture_executor.py",
    SRC_ROOT / "executors" / "screen_analysis_executor.py",
]


def _iter_targets() -> list[Path]:
    files: list[Path] = []
    for root in TARGET_ROOTS:
        if root.exists():
            files.extend(sorted(root.rglob("*.py")))
    for file_path in TARGET_FILES:
        if file_path.exists():
            files.append(file_path)
    return files


def test_perception_scaffold_has_no_background_monitoring_loops_or_schedulers():
    offenders: list[str] = []

    for py_file in _iter_targets():
        source = py_file.read_text(encoding="utf-8", errors="replace")
        lowered = source.lower()
        tree = ast.parse(source, filename=str(py_file))

        if "while true" in lowered:
            offenders.append(f"{py_file}: while True loop detected")
        if "apscheduler" in lowered or "schedule.every" in lowered or "threading.timer" in lowered:
            offenders.append(f"{py_file}: scheduler marker detected")

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "create_task":
                    offenders.append(f"{py_file}:{node.lineno} create_task detected")
                if node.func.attr == "Thread":
                    base = node.func.value
                    if isinstance(base, ast.Name) and base.id == "threading":
                        offenders.append(f"{py_file}:{node.lineno} threading.Thread detected")

    assert not offenders, "\n".join(offenders)
