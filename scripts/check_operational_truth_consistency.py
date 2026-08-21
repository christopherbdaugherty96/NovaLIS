from __future__ import annotations

"""Narrow consistency check for Nova's active operational truth surfaces.

This is intentionally separate from ``check_runtime_doc_drift.py``. The runtime
checker prevents broad runtime facts from leaking into navigation docs; this
script checks that the hand-maintained *operational* entry points agree on the
same active stabilization lane and preserve a few permanent truth boundaries.

Checked here:
- required presence of the active operational entry points;
- active stabilization-lane agreement across AGENTS, canonical index,
  priority/status/todo, and the canonical roadmap marker;
- the known ``connections_api.py`` requests-based network exception and
  three-control-plane boundary in canonical governance;
- current-HEAD vs validated-baseline and implementation-vs-evidence boundaries;
- PR #335 remaining explicitly UNMERGED near its reference in priority/roadmap.

Not checked here:
- semantic correctness of the documents;
- generated runtime truth or runtime behavior;
- future/archive material;
- test execution, capability behavior, or authority correctness.

A green result is therefore a bounded consistency signal, not a repository or
runtime certification.
"""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECKED_SURFACES = (
    "AGENTS.md",
    ".agent_context/current_priority.md",
    "docs/status/CURRENT_WORK_STATUS.md",
    "docs/status/DAILY_COMMAND_CENTER.md",
    "docs/todo/ACTIVE_TODO.md",
    "docs/CANONICAL/00_INDEX.md",
    "docs/CANONICAL/03_GOVERNANCE_TRUTH.md",
    "docs/CANONICAL/07_ROADMAP_TRUTH.md",
)

NON_GOALS = (
    "semantic correctness",
    "generated runtime truth/runtime behavior",
    "future/archive material",
    "test/capability/authority certification",
)

LANE_PATTERNS = {
    "agents": re.compile(
        r"^## Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b.*Current Development State",
        re.MULTILINE,
    ),
    "priority": re.compile(
        r"^## Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b", re.MULTILINE
    ),
    "work_status": re.compile(
        r"^WAVE (?P<lane>A1|A2|B1|B2|B3|B4|C)\s+[—-]", re.MULTILINE
    ),
    "command_center": re.compile(
        r"^\s*Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\s+[—-]", re.MULTILINE
    ),
    "active_todo": re.compile(
        r"^### Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b", re.MULTILINE
    ),
    "canonical_index": re.compile(
        r"^Current active stabilization lane:\s*(?P<lane>A1|A2|B1|B2|B3|B4|C)\b",
        re.MULTILINE,
    ),
    "roadmap": re.compile(
        r"^Current active stabilization lane:\s*(?P<lane>A1|A2|B1|B2|B3|B4|C)\b",
        re.MULTILINE,
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_lane(name: str, text: str) -> str | None:
    match = LANE_PATTERNS[name].search(text[:8000])
    return match.group("lane") if match else None


def _preserves_pr_335_unmerged(text: str) -> bool:
    for match in re.finditer(r"#335\b", text, re.IGNORECASE):
        nearby = text[match.start() : match.start() + 500].upper()
        if "UNMERGED" in nearby:
            return True
    return False


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
        rendered = ", ".join(
            f"{name}={lane}" for name, lane in sorted(lanes.items())
        )
        errors.append(f"active stabilization lane mismatch: {rendered}")

    governance = texts.get("governance", "")
    if "nova_backend/src/api/connections_api.py" not in governance:
        errors.append(
            "canonical governance does not name the known connections_api.py requests-based network exception"
        )
    for marker in (
        "Governed capability plane",
        "Local operator / administrative plane",
        "Bounded agent / routine plane",
    ):
        if marker not in governance:
            errors.append(f"canonical governance missing control-plane marker: {marker}")

    canonical_index = texts.get("canonical_index", "")
    if "current HEAD != immutable validated baseline" not in canonical_index:
        errors.append(
            "canonical index no longer distinguishes current HEAD from immutable validated baseline"
        )
    if (
        "**Implementation:**" not in canonical_index
        or "**Automated/recorded evidence:**" not in canonical_index
    ):
        errors.append(
            "canonical index no longer separates implementation from evidence"
        )

    priority = texts.get("priority", "")
    roadmap = texts.get("roadmap", "")
    for name, text in (("current priority", priority), ("canonical roadmap", roadmap)):
        if not _preserves_pr_335_unmerged(text):
            errors.append(
                f"{name} does not preserve PR #335 as explicitly UNMERGED near its reference"
            )

    return errors


def main() -> int:
    errors = check_operational_truth()
    if errors:
        print("Operational truth consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Operational truth consistency check passed (bounded scope).")
    print("Checked surfaces:")
    for surface in CHECKED_SURFACES:
        print(f"- {surface}")
    print("Not proven by this check:")
    for non_goal in NON_GOALS:
        print(f"- {non_goal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
