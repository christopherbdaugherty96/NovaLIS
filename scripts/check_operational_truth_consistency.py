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
- merged PR #366 truth-hygiene provenance and merged PR #378 narration provenance
  for completed closeout state;
- the known ``connections_api.py`` requests-based network exception and
  three-control-plane boundary in canonical governance;
- current-HEAD vs validated-baseline and implementation-vs-evidence boundaries;
- exact Wave C validated-baseline preservation for completed closeout state;
- the post-#394 completion boundary on active operational surfaces;
- the post-#405 beta-readiness order through #406 and the durability/install gates;
- PR #335 remaining explicitly historical and UNMERGED while its implementation
  path is marked SUPERSEDED BY MERGED PR #394;
- Google/provider expansion and the other frozen feature categories remaining
  paused during the #406-first beta-readiness sequence.

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
    "README.md",
    "START_HERE.md",
    "AGENTS.md",
    ".agent_context/current_priority.md",
    "docs/status/CURRENT_WORK_STATUS.md",
    "docs/status/DAILY_COMMAND_CENTER.md",
    "docs/todo/ACTIVE_TODO.md",
    "docs/CANONICAL/00_INDEX.md",
    "docs/CANONICAL/03_GOVERNANCE_TRUTH.md",
    "docs/CANONICAL/07_ROADMAP_TRUTH.md",
)
CURRENT_CHECKED_SURFACES = CHECKED_SURFACES + (
    "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md",
)

NON_GOALS = (
    "semantic correctness",
    "generated runtime truth/runtime behavior",
    "future/archive material other than the explicitly validated master roadmap",
    "test/capability/authority certification",
)

POST_WAVE_C_LANE = "POST_WAVE_C_DOCUMENTATION_CLOSEOUT"
POST_WAVE_C_ACTIVE_LANE = f"{POST_WAVE_C_LANE}_ACTIVE"
POST_WAVE_C_COMPLETE_LANE = f"{POST_WAVE_C_LANE}_COMPLETE"
VALIDATED_BASELINE_SHA = "ec20a7146f7d6d55b8983cb7d6d3918d5fad9915"
POST_405_LIFECYCLE_MARKER = "BETA_READINESS_SEQUENCE_V1: ACTIVE"
CURRENT_LIFECYCLE_GENERATION = "POST_405_BETA_READINESS_V1"
HISTORICAL_LIFECYCLE_GENERATION = "HISTORICAL_AUTO"
POST_405_DIRECTIVE_SEQUENCE = (
    "NEXT: #406 GOVERNED-MEMORY ID COLLISION CORRECTNESS",
    "THEN: #408 DURABILITY/STATE-OWNERSHIP DECISION",
    "THEN: EVIDENCE-AUTHORIZED DURABILITY IMPLEMENTATION",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)

POST_394_ORDERING_SURFACES = (
    "priority",
    "work_status",
    "command_center",
    "canonical_index",
    "roadmap",
    "master_roadmap",
)

POST_405_ORDERING_SURFACES = (
    "readme",
    "start_here",
    "agents",
    "priority",
    "work_status",
    "command_center",
    "active_todo",
    "canonical_index",
    "roadmap",
    "master_roadmap",
)

CURRENT_ORDERING_SURFACES = (
    "readme",
    "start_here",
    "agents",
    "priority",
    "work_status",
    "command_center",
    "active_todo",
    "canonical_index",
    "roadmap",
)

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

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_lane(name: str, text: str) -> str | None:
    scoped = text[:12000]

    if POST_WAVE_C_COMPLETE_MARKER.search(scoped):
        return POST_WAVE_C_COMPLETE_LANE

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
    standalone_state = re.compile(
        r"^(?:OPEN|DRAFT|UNMERGED|MERGED|CLOSED)"
        r"(?:\s*/\s*(?:OPEN|DRAFT|UNMERGED|MERGED|CLOSED))*$",
        re.IGNORECASE,
    )

    for index, line in enumerate(lines):
        if not pr_ref.search(line):
            continue
        upper = line.upper()
        if "UNMERGED" in upper and not re.search(r"\bMERGED\b", upper):
            return True
        if block_header.search(line):
            in_fence = False
            for status_line in lines[index + 1 : index + 12]:
                stripped = status_line.strip()
                if not stripped:
                    continue
                if stripped.startswith("```"):
                    if in_fence:
                        break
                    in_fence = True
                    continue

                status_upper = stripped.upper()
                if "UNMERGED" in status_upper and not re.search(
                    r"\bMERGED\b", status_upper
                ):
                    return True
                if re.search(r"\bMERGED\b", status_upper):
                    return False

                if in_fence:
                    continue
                if standalone_state.fullmatch(stripped):
                    continue
                break
            return False
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


def _preserves_merged_pr_role(
    text: str, pr_number: int, required_terms: tuple[str, ...]
) -> bool:
    """Require MERGED and the expected provenance role on the target PR line."""

    for line in _lines_for_pr(text, pr_number):
        upper = line.upper()
        if "NOT MERGED" in upper or "UNMERGED" in upper:
            continue
        if not re.search(r"\bMERGED\b", upper):
            continue
        if all(term.upper() in upper for term in required_terms):
            return True
    return False


def _preserves_validated_baseline(text: str) -> bool:
    return VALIDATED_BASELINE_SHA in text


def _preserves_pr_335_pending_not_authorized(text: str) -> bool:
    """Bind pending/not-authorized state to the #335 reconstruction line."""

    for line in _lines_for_pr(text, 335):
        upper = line.upper()
        if (
            "RECONSTRUCTION" in upper
            and "PENDING" in upper
            and "SEPARATE OWNER DECISION" in upper
            and "NOT AUTHORIZED" in upper
            and not re.search(r"\bNEXT\b", upper)
        ):
            return True
    return False


def _preserves_separate_335_authorization_decision(text: str) -> bool:
    """Require the separate owner decision on the #335 reconstruction line."""

    for line in _lines_for_pr(text, 335):
        upper = line.upper()
        if "RECONSTRUCTION" in upper and "SEPARATE OWNER DECISION" in upper:
            return True
    return False


def _ordering_line_index(
    text: str, issue_number: int, required_terms: tuple[str, ...]
) -> int | None:
    issue_ref = re.compile(rf"(?<!\d)#{issue_number}(?!\d)")
    ordered_issue_ref = re.compile(r"(?<!\d)#(?:388|368|387)(?!\d)")
    for index, line in enumerate(text.splitlines()):
        upper = line.upper()
        target = issue_ref.search(line)
        if target is None:
            continue
        first_ordered_issue = ordered_issue_ref.search(line)
        if first_ordered_issue is None or first_ordered_issue.start() != target.start():
            continue
        if all(term.upper() in upper for term in required_terms):
            return index
        return None
    return None


def _preserves_post_394_boundary(text: str) -> bool:
    """Require completed prerequisites, merged #394, and the proof-first next input."""

    upper = text.upper().split("HISTORICAL PRE-#394", 1)[0]
    required = (
        "GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED",
        "691A397D14E93C1E0607A73DE2AB54B9BBFC3CC2",
        "SUPERSEDED BY MERGED PR #394",
        "GOOGLE IDENTITY-ONLY LIVE PROOF",
        "GOOGLE TASKS READ",
    )
    completed = all(
        re.search(rf"(?m)^\s*#{issue}\s*(?::|—|-)?\s*COMPLETE\b", upper)
        for issue in (388, 368, 387, 393)
    )
    tasks_gated = any(
        marker in upper
        for marker in (
            "SEPARATELY AUTHORIZED: GOOGLE TASKS READ",
            "NOT YET AUTHORIZED: GOOGLE TASKS READ",
            "SEPARATE AUTHORIZATION REQUIRED: GOOGLE TASKS READ",
            "ONLY WITH SEPARATE REVIEWED AUTHORIZATION — GOOGLE TASKS READ",
        )
    )
    return completed and tasks_gated and all(marker in upper for marker in required)


def _extract_post_405_active_block(text: str) -> str | None:
    """Extract the one current lifecycle block, excluding later historical sections."""

    upper = text.upper()
    marker = re.search(
        rf"(?m)^\s*{re.escape(POST_405_LIFECYCLE_MARKER)}\s*$",
        upper,
    )
    if marker is None:
        return None
    preceding_headings = tuple(
        re.finditer(r"(?m)^#{1,6}\s+\S.*$", upper[: marker.start()])
    )
    section_start = preceding_headings[-1].start() if preceding_headings else 0
    remainder = upper[marker.end() :]
    boundary = re.search(r"(?m)^(?:#{1,6}\s+\S|-{3,}\s*$)", remainder)
    if boundary is None:
        return upper[section_start:]
    return upper[section_start : marker.end() + boundary.start()]


def _preserves_post_405_boundary(text: str) -> bool:
    """Require the current #406-first beta-readiness order and feature freeze."""

    active = _extract_post_405_active_block(text)
    if active is None:
        return False
    directives = tuple(
        line.strip()
        for line in active.splitlines()
        if re.match(r"^\s*(?:NEXT|THEN):", line)
    )
    if directives != POST_405_DIRECTIVE_SEQUENCE:
        return False
    normalized = " ".join(active.split())
    required = (
        POST_405_LIFECYCLE_MARKER,
        "#397 THROUGH #405: COMPLETE / MERGED",
    )
    if not all(marker in normalized for marker in required):
        return False
    if re.search(r"VERIFIED MAIN AT SYNC START:\s+[0-9A-F]{40}\b", normalized) is None:
        return False
    frozen_categories = (
        "GOOGLE/PROVIDER EXPANSION",
        "OPERATIONAL CONTINUITY IMPLEMENTATION",
        "NEW CAPABILITIES",
        "VOICE EXPANSION",
        "BROADER UI WORK",
        "OTHER FEATURE EXPANSION",
    )
    if not all(
        re.search(rf"{re.escape(category)}\s+REMAINS? PAUSED", normalized)
        for category in frozen_categories
    ):
        return False
    contradictory_states = (
        r"(?:IS\s+)?(?:ACTIVE|AUTHORIZED|ENABLED|RESUMED|UNPAUSED)",
        r"IS\s+(?:NO\s+LONGER|NOT)\s+PAUSED",
        r"WILL\s+(?:RESUME|BE\s+RESUMED|BECOME\s+ACTIVE|BE\s+ACTIVATED)",
        r"IS\s+(?:NOW\s+ACTIVE|AUTHORIZED\s+NOW)",
    )
    if any(
        re.search(
            rf"{re.escape(category)}\s+{state}",
            normalized,
        )
        for category in frozen_categories
        for state in contradictory_states
    ):
        return False
    return True


def _preserves_current_order(text: str) -> bool:
    prerequisite = _ordering_line_index(
        text, 388, ("COMPLETE", "TRUTH-CHECKER", "PREREQUISITE", "SATISFIED")
    )
    technical = _ordering_line_index(text, 368, ("NEXT", "BOUNDED", "TECHNICAL", "LANE"))
    roadmap = _ordering_line_index(text, 387, ("AFTER #368", "DOCS-ONLY"))
    return (
        prerequisite is not None
        and technical is not None
        and roadmap is not None
        and prerequisite < technical < roadmap
    )


def check_operational_truth(
    root: Path = ROOT, *, lifecycle_generation: str | None = None
) -> list[str]:
    paths = {
        "readme": root / "README.md",
        "start_here": root / "START_HERE.md",
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

    master_path = root / "docs" / "future" / "NOVA_MASTER_ROADMAP_2026-07-05.md"
    if master_path.exists():
        texts["master_roadmap"] = _read(master_path)
        paths["master_roadmap"] = master_path

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
        if lane == POST_WAVE_C_COMPLETE_LANE
    }
    if lifecycle_generation is None:
        lifecycle_generation = (
            CURRENT_LIFECYCLE_GENERATION
            if root.resolve() == ROOT.resolve()
            else HISTORICAL_LIFECYCLE_GENERATION
        )

    post_394_mode = any(
        "GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED" in text.upper()
        for text in texts.values()
    )
    post_405_mode = lifecycle_generation == CURRENT_LIFECYCLE_GENERATION
    for name in sorted(completed_surfaces):
        text = texts[name]
        if not _preserves_merged_pr_role(text, 366, ("TRUTH-HYGIENE",)):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve PR #366 as MERGED truth-hygiene provenance"
            )
        if not _preserves_merged_pr_role(text, 378, ("NARRATION", "FRONT-DOOR")):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve PR #378 as MERGED narration/front-door provenance"
            )
        if not _preserves_validated_baseline(text):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve exact validated_baseline_sha {VALIDATED_BASELINE_SHA}"
            )
        if post_394_mode:
            continue
        if not _preserves_pr_335_pending_not_authorized(text):
            errors.append(
                f"{paths[name]}: completed closeout does not preserve #335 reconstruction as PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED"
            )
        if not _preserves_separate_335_authorization_decision(text):
            errors.append(
                f"{paths[name]}: completed closeout does not bind the separate owner decision to #335 reconstruction"
            )

    if post_405_mode:
        if "master_roadmap" not in texts:
            errors.append(f"{master_path}: required post-#405 ordering surface missing")
        for name in POST_405_ORDERING_SURFACES:
            text = texts.get(name)
            if text is None:
                continue
            if not _preserves_post_405_boundary(text):
                errors.append(
                    f"{paths[name]}: current ordering does not preserve the post-#405 #406-first beta-readiness boundary"
                )
    elif completed_surfaces and post_394_mode:
        if "master_roadmap" not in texts:
            errors.append(f"{master_path}: required post-#394 ordering surface missing")
        for name in POST_394_ORDERING_SURFACES:
            text = texts.get(name)
            if text is None:
                continue
            if not _preserves_post_394_boundary(text):
                errors.append(
                    f"{paths[name]}: current ordering does not preserve the post-#394 completion and proof-first boundary"
                )
    elif completed_surfaces:
        for name in CURRENT_ORDERING_SURFACES:
            text = texts.get(name)
            if text is None:
                continue
            if not _preserves_current_order(text):
                errors.append(
                    f"{paths[name]}: current ordering does not preserve #388 COMPLETE -> #368 NEXT -> #387 AFTER #368"
                )
            if not _preserves_pr_335_pending_not_authorized(text):
                errors.append(
                    f"{paths[name]}: current ordering does not bind #335 reconstruction to PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED"
                )
            if not _preserves_separate_335_authorization_decision(text):
                errors.append(
                    f"{paths[name]}: current ordering does not bind the separate owner decision to #335 reconstruction"
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
    for surface in CURRENT_CHECKED_SURFACES:
        print(f"- {surface}")
    print("Not proven by this check:")
    for non_goal in NON_GOALS:
        print(f"- {non_goal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
