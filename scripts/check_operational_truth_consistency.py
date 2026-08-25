"""Narrow consistency check for Nova's active operational truth surfaces.

This is intentionally separate from ``check_runtime_doc_drift.py``. The runtime
checker prevents broad runtime facts from leaking into navigation docs; this
script checks that the hand-maintained *operational* entry points agree on the
same stabilization/current-truth gate and preserve a few permanent truth
boundaries.

Checked here:
- required presence of the active operational entry points;
- stabilization/current-truth gate agreement across AGENTS, canonical index,
  priority/status/todo, and the canonical roadmap marker;
- active-vs-complete post-Wave-C documentation-closeout lifecycle agreement;
- durable PR #366 truth-hygiene provenance and merged PR #378 narration provenance
  for completed closeout state;
- the known ``connections_api.py`` requests-based network exception and
  three-control-plane boundary in canonical governance;
- current-HEAD vs validated-baseline and implementation-vs-evidence boundaries;
- exact Wave C validated-baseline preservation for completed closeout state;
- PR #335 remaining explicitly UNMERGED / NEXT / NOT AUTHORIZED on its
  priority/roadmap status representation;
- completed closeout preserving a separate owner-authorization decision before
  #335 reconstruction/reconciliation.

The checker supports historical Wave A1-C representations, the active
post-Wave-C documentation-closeout representation, and the completed
post-Wave-C documentation-closeout representation. PR #366 remains durable
truth-hygiene provenance; temporary GitHub workflow states such as OPEN, DRAFT,
READY, or ACTIVE are intentionally not part of the normalized PR identity.

Not checked here:
- semantic correctness of the documents;
- generated runtime truth or runtime behavior;
- future/archive material;
- test execution, capability behavior, or authority correctness.

A green result is therefore a bounded consistency signal, not a repository or
runtime certification.
"""

from __future__ import annotations

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

POST_WAVE_C_LANE = "POST_WAVE_C_DOCUMENTATION_CLOSEOUT"
POST_WAVE_C_ACTIVE_LANE = f"{POST_WAVE_C_LANE}_ACTIVE"
POST_WAVE_C_COMPLETE_LANE = f"{POST_WAVE_C_LANE}_COMPLETE"
VALIDATED_BASELINE_SHA = "ec20a7146f7d6d55b8983cb7d6d3918d5fad9915"

# Historical stabilization-lane markers. Keep these for compatibility with the
# already-proven A1-C operational fixtures and historical checked revisions.
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

# Merge-safe active post-Wave-C representation. These patterns bind PR #366
# only as truth-hygiene provenance and intentionally ignore temporary PR UI
# state such as OPEN/DRAFT/READY/ACTIVE.
POST_WAVE_C_ACTIVE_PATTERNS = {
    "agents": re.compile(
        r"^Post-Wave-C documentation closeout gate:.*?truth-hygiene contract.*?PR #(?P<pr>\d+)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
    "priority": re.compile(
        r"^## Post-Wave-C Documentation Closeout\s+[—-]\s+PR #(?P<pr>\d+) Truth-Hygiene Contract\b",
        re.MULTILINE | re.IGNORECASE,
    ),
    "work_status": re.compile(
        r"^POST-WAVE-C DOCUMENTATION CLOSEOUT[ \t]*\nTRUTH-HYGIENE CONTRACT:\s*PR #(?P<pr>\d+)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
    "command_center": re.compile(
        r"^\s*Post-Wave-C documentation closeout\s+[—-]\s+truth-hygiene contract PR #(?P<pr>\d+)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
    "active_todo": re.compile(
        r"^### Post-Wave-C documentation closeout\b[\s\S]{0,2000}?^truth-hygiene contract package:\s*PR #(?P<pr>\d+)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
    "canonical_index": re.compile(
        r"^Current gate:.*?post-Wave-C documentation closeout.*?truth-hygiene contract.*?PR #(?P<pr>\d+)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
    "roadmap": re.compile(
        r"^Post-Wave-C documentation closeout gate:.*?truth-hygiene contract.*?PR #(?P<pr>\d+)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
}

POST_WAVE_C_COMPLETE_MARKER = re.compile(
    r"POST-WAVE-C DOCUMENTATION CLOSEOUT(?:\s*:\s*|\s+[—-]\s*)COMPLETE\b",
    re.IGNORECASE,
)

TRUTH_HYGIENE_PROVENANCE_PATTERNS = (
    re.compile(
        r"\btruth-hygiene(?:\s+contract)?\s+(?:provenance|package)\s*"
        r"(?:[:—-]\s*)?(?:PR\s*)?#(?P<pr>\d+)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bPR\s*#(?P<pr>\d+)\b"
        r"(?:(?!\bPR\s*#)[^\n]){0,100}\btruth-hygiene"
        r"(?:\s+contract)?\s+(?:provenance|package)\b",
        re.IGNORECASE,
    ),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_truth_hygiene_pr(text: str) -> str | None:
    """Return the PR number structurally bound to truth-hygiene provenance."""

    for pattern in TRUTH_HYGIENE_PROVENANCE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group("pr")
    return None


def _extract_lane(name: str, text: str) -> str | None:
    scoped = text[:12000]

    if POST_WAVE_C_COMPLETE_MARKER.search(scoped):
        provenance_pr = _extract_truth_hygiene_pr(scoped)
        if provenance_pr is not None:
            return f"{POST_WAVE_C_COMPLETE_LANE}:PR#{provenance_pr}"
        return None

    active_match = POST_WAVE_C_ACTIVE_PATTERNS[name].search(scoped)
    if active_match:
        return f"{POST_WAVE_C_ACTIVE_LANE}:PR#{active_match.group('pr')}"

    legacy_match = LANE_PATTERNS[name].search(scoped)
    if legacy_match:
        return legacy_match.group("lane")

    return None


def _lines_for_pr(text: str, pr_number: int) -> tuple[str, ...]:
    """Return only lines that contain the exact target PR reference."""

    pr_ref = re.compile(rf"(?:\bPR\s*)?#{pr_number}\b", re.IGNORECASE)
    return tuple(line for line in text.splitlines() if pr_ref.search(line))


def _preserves_pr_335_unmerged(text: str) -> bool:
    lines = text.splitlines()
    pr_ref = re.compile(r"(?:\bPR\s*)?#335\b", re.IGNORECASE)
    block_header = re.compile(r"\bPR\s*#335\s+remains\s*:\s*$", re.IGNORECASE)

    for index, line in enumerate(lines):
        if not pr_ref.search(line):
            continue
        upper = line.upper()
        if "UNMERGED" in upper and not re.search(r"\bMERGED\b", upper):
            return True
        if block_header.search(line):
            for status_line in lines[index + 1 : index + 6]:
                stripped = status_line.strip()
                if not stripped or stripped.startswith("```"):
                    continue
                status_upper = stripped.upper()
                return "UNMERGED" in status_upper and not re.search(
                    r"\bMERGED\b", status_upper
                )
    return False


def _preserves_pr_335_next_not_authorized(text: str) -> bool:
    for line in _lines_for_pr(text, 335):
        upper = line.upper()
        if (
            re.search(r"\bNEXT\b", upper)
            and "NOT AUTHORIZED" in upper
            and "NOT NEXT" not in upper
        ):
            return True
    return False


def _preserves_merged_pr(text: str, pr_number: int) -> bool:
    """Require an affirmative MERGED state on the target PR's own line."""

    for line in _lines_for_pr(text, pr_number):
        upper = line.upper()
        if "NOT MERGED" in upper or "UNMERGED" in upper:
            continue
        if re.search(r"\bMERGED\b", upper):
            return True
    return False


def _preserves_validated_baseline(text: str) -> bool:
    return VALIDATED_BASELINE_SHA in text


def _preserves_separate_335_authorization_decision(text: str) -> bool:
    upper = text.upper()
    return "SEPARATE OWNER AUTHORIZATION" in upper and "#335" in upper


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
            errors.append(f"{paths[name]}: stabilization/current-truth gate marker not found")
        else:
            lanes[name] = lane

    if lanes and len(set(lanes.values())) != 1:
        rendered = ", ".join(
            f"{name}={lane}" for name, lane in sorted(lanes.items())
        )
        errors.append(
            f"active stabilization lane mismatch / stabilization/current-truth gate mismatch: {rendered}"
        )

    completed_surfaces = {
        name
        for name, lane in lanes.items()
        if lane.startswith(f"{POST_WAVE_C_COMPLETE_LANE}:")
    }
    for name in sorted(completed_surfaces):
        text = texts[name]
        if not _preserves_merged_pr(text, 378):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve PR #378 as MERGED narration/front-door provenance"
            )
        if not _preserves_validated_baseline(text):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve exact validated_baseline_sha {VALIDATED_BASELINE_SHA}"
            )
        if not _preserves_pr_335_next_not_authorized(text):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve #335 as NEXT / NOT AUTHORIZED"
            )
        if not _preserves_separate_335_authorization_decision(text):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve a separate owner authorization decision before #335 reconstruction"
            )

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
                f"{name} does not preserve PR #335 as explicitly UNMERGED in its status representation"
            )
        if not _preserves_pr_335_next_not_authorized(text):
            errors.append(
                f"{name} does not preserve PR #335 as NEXT / NOT AUTHORIZED on its status line"
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
