from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
GOVERNOR_ROOT = SRC_ROOT / "governor"
AUDIO_MANAGER_PATH = SRC_ROOT / "audio_manager.py"


ALLOWED_CREATE_TASK_FILE = AUDIO_MANAGER_PATH


def _is_archive_or_quarantine(path: Path) -> bool:
    low = {part.lower() for part in path.parts}
    return any("archive" in part or "quarantine" in part for part in low)


def test_no_background_execution_outside_governor_or_allowed_audio_worker():
    offenders: list[str] = []

    for py in SRC_ROOT.rglob("*.py"):
        if _is_archive_or_quarantine(py):
            continue

        tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"), filename=str(py))

        for node in ast.walk(tree):
            # asyncio.create_task(...) or loop.create_task(...)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "create_task":
                if py != ALLOWED_CREATE_TASK_FILE and GOVERNOR_ROOT not in py.parents:
                    offenders.append(f"{py}:{node.lineno} create_task outside Governor")

            # threading.Thread(...)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                base = node.func.value
                if isinstance(base, ast.Name) and base.id == "threading" and node.func.attr == "Thread":
                    if GOVERNOR_ROOT not in py.parents:
                        offenders.append(f"{py}:{node.lineno} threading.Thread outside Governor")

        # coarse background worker string detection
        text = py.read_text(encoding="utf-8", errors="replace")
        if "background" in text.lower() and py != AUDIO_MANAGER_PATH and GOVERNOR_ROOT not in py.parents:
            if "background" in text.lower() and "worker" in text.lower():
                offenders.append(f"{py}: background worker marker found")

    assert not offenders, "\n".join(offenders)
