from __future__ import annotations

"""Narrow consistency check for Nova's active operational truth surfaces.

This is intentionally separate from ``check_runtime_doc_drift.py``. The runtime
checker prevents broad runtime facts from leaking into navigation docs; this
script checks that the hand-maintained *operational* entry points agree on the
same active stabilization lane and preserve a few permanent truth boundaries.

It does not prove semantic correctness of the documents and it does not inspect
future/archive material.
"""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LANE_PATTERNS = {
    "agents": re.compile(r"^## Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b.*Current Development State", re.MULTILINE),
    "priority": re.compile(r"^## Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b", re.MULTILINE),
    "work_status": re.compile(r"^WAVE (?P<lane>A1|A2|B1|B2|B3|B4|C)\s+[—-]", re.MULTILINE),
    "command_center": re.compile(r"^\s*Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\s+[—-]", re.MULTILINE),
    "active_todo": re.compile(r"^### Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b", re.MULTILINE),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_lane(name: str, text: str) -> str | None:
    match = LANE_PATTERNS[name].search(text[:5000])
    return match.group("lane") if match else None


def check_operational_truth(root: Path = ROOT) -> list[str]:
    paths = {
        "agents": root / "AGENTS.md",
        "priority": root / ".agent_context" / "current_priority.md",
        "work_status": root / "docs" / "status" / "CURRENT_WORK_STATUS.md",
        "command_center": root / "docs" / "status" / "DAILY_COMMAND_CENTER.md",
        "active_todo": root / "docs" / "todo" / "ACTIVE_TODO.md",
        "canonical_index": root / "docs" / "CANONICAL" / "00_INDEX.md",
        "governance": root / "docs" / "CANONICAL" / "03_GOVERNANCE_TRUTH.md",
        "roadmap": root / "docs" / "CANONICAL" / "07_ROADMAP_TRUTH.md",
    }
    errors: list[str] = []
    texts: dict[str, str] = {}

    for name, path in paths.items():
        if not path.exists():
            errors.append(f"{path}: required operational truth surface missing")
            continue
        texts[name] = _read(path)

    lanes: dict[str, str] = {}
    for name in LANE_PATTERNS:
        text = texts.get(name)
        if text is None:
            continue
        lane = _extract_lane(name, text)
        if lane is None:
            errors.append(f"{paths[name]}: active stabilization lane marker not found")
        else:
            lanes[name] = lane

    if lanes and len(set(lanes.values())) != 1:
        rendered = ", ".join(f"{name}={lane}" for name, lane in sorted(lanes.items()))
        errors.append(f"active stabilization lane mismatch: {rendered}")

    governance = texts.get("governance", "")
    if "nova_backend/src/api/connections_api.py" not in governance:
        errors.append("canonical governance does not name the known connections_api.py direct-network exception")
    for marker in (
        "Governed capability plane",
        "Local operator / administrative plane",
        "Bounded agent / routine plane",
    ):
        if marker not in governance:
            errors.append(f"canonical governance missing control-plane marker: {marker}")

    canonical_index = texts.get("canonical_index", "")
    if "current HEAD != immutable validated baseline" not in canonical_index:
        errors.append("canonical index no longer distinguishes current HEAD from immutable validated baseline")
    if "**Implementation:**" not in canonical_index or "**Automated/recorded evidence:**" not in canonical_index:
        errors.append("canonical index no longer separates implementation from evidence")

    priority = texts.get("priority", "")
    roadmap = texts.get("roadmap", "")
    for name, text in (("current priority", priority), ("canonical roadmap", roadmap)):
        if "#335" not in text or "UNMERGED" not in text.upper():
            errors.append(f"{name} does not preserve PR #335 as unmerged")

    return errors


def main() -> int:
    errors = check_operational_truth()
    if errors:
        print("Operational truth consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Operational truth consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
