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
CURRENT_CHECKED_SURFACES = CHECKED_SURFACES + ("docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md",)

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
POST_406_DIRECTIVE_SEQUENCE = (
    "NEXT: #408 DURABILITY/STATE-OWNERSHIP DECISION",
    "THEN: EVIDENCE-AUTHORIZED DURABILITY IMPLEMENTATION",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
POST_406_COMPLETE_MARKER = "COMPLETE: #406 GOVERNED-MEMORY ID COLLISION CORRECTNESS"
POST_406_COMPLETE_PROVENANCE = (
    "COMPLETE: #406 GOVERNED-MEMORY ID COLLISION CORRECTNESS (PR #411; MAIN `CA66A06D`)"
)
POST_413_DIRECTIVE_SEQUENCE = (
    "NEXT: CORRUPTION-SAFE READER INVENTORY + FAIL-CLOSED IMPLEMENTATION",
    "THEN: SEPARATE EXACT-HEAD REVIEW AND MERGE DECISION",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
POST_416_DIRECTIVE_SEQUENCE = (
    "NEXT: SEPARATE OWNER AUTHORIZATION DECISION FOR MAINTENANCE LOCKING + MUTATION QUIESCENCE",
    "THEN: SEPARATELY AUTHORIZED SNAPSHOT/MANIFEST + SAFE MIGRATION",
    "THEN: SEPARATELY AUTHORIZED ENCRYPTED BACKUP/RESTORE/ROLLBACK",
    "THEN: DURABILITY TORTURE PROOF",
    "THEN: #409 RELEASE HYGIENE",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
LANE_3_ACTIVE_DIRECTIVE_SEQUENCE = (
    "NEXT: IMPLEMENT AND REVIEW ONLY THE AUTHORIZED LANE 3 CONTRACT",
    "THEN: SEPARATELY AUTHORIZED SNAPSHOT/MANIFEST + SAFE MIGRATION",
    "THEN: SEPARATELY AUTHORIZED ENCRYPTED BACKUP/RESTORE/ROLLBACK",
    "THEN: DURABILITY TORTURE PROOF",
    "THEN: #409 RELEASE HYGIENE",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
POST_419_DIRECTIVE_SEQUENCE = (
    "NEXT: SEPARATE OWNER AUTHORIZATION DECISION FOR VERSIONED SNAPSHOT + MANIFEST",
    "THEN: SEPARATELY AUTHORIZED SAFE MIGRATION + GENERATION ACTIVATION",
    "THEN: SEPARATELY AUTHORIZED ENCRYPTED BACKUP/RESTORE/ROLLBACK",
    "THEN: DURABILITY TORTURE PROOF",
    "THEN: #409 RELEASE HYGIENE",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
LANE_4_ACTIVE_DIRECTIVE_SEQUENCE = (
    "NEXT: IMPLEMENT AND REVIEW ONLY THE AUTHORIZED LANE 4 CONTRACT",
    "THEN: SEPARATELY AUTHORIZED SAFE MIGRATION + GENERATION ACTIVATION",
    "THEN: SEPARATELY AUTHORIZED ENCRYPTED BACKUP/RESTORE/ROLLBACK",
    "THEN: DURABILITY TORTURE PROOF",
    "THEN: #409 RELEASE HYGIENE",
    "THEN: BOUNDED PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
LANE_4_COMPLETE_DIRECTIVE_SEQUENCE = (
    "NEXT: #409 RELEASE INTEGRITY / REPOSITORY CONTROL (SEPARATELY SCOPED)",
    "THEN: REBASE AND EXACT-HEAD REVIEW #410 PRIVATE-BETA FREEZE CRITERIA",
    "THEN: SEPARATE OWNER AUTHORIZATION DECISION FOR RECOVERY CONSTRUCTION (LANE 5A)",
    "THEN: SEPARATELY AUTHORIZED RECOVERY PROOF: INACTIVE CANDIDATE MIGRATION -> CANDIDATE VALIDATION -> ACTIVATION -> ROLLBACK/RESTORE SEMANTICS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
LANE_5A_RECOVERY_FOUNDATION_DIRECTIVE_SEQUENCE = (
    "NEXT: ROLLBACK/RESTORE PROOF",
    "THEN: BOUNDED BETA PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
LANE_5A_RECOVERY_COMPLETE_DIRECTIVE_SEQUENCE = (
    "NEXT: BOUNDED BETA PRODUCT-TRANSLATION/READINESS PASS",
    "THEN: CLEAN WINDOWS OPERATOR PROOF",
    "THEN: FROZEN-SHA FULL BETA ACCEPTANCE",
    "THEN: PRIVATE-BETA CANDIDACY/DISTRIBUTION DECISION",
)
POST_408_COMPLETE_MARKER = "COMPLETE: #408 DURABILITY/STATE-OWNERSHIP DECISION"
POST_408_COMPLETE_PROVENANCE = (
    "COMPLETE: #408 DURABILITY/STATE-OWNERSHIP DECISION (PR #412; MAIN `2592AD91`)"
)
LANE_1_AUTHORIZATION_MARKER = "AUTHORIZED: DURABILITY IMPLEMENTATION LANE 1 ONLY"
LANE_2_AUTHORIZATION_MARKER = "AUTHORIZED: DURABILITY IMPLEMENTATION LANE 2 ONLY"
LANE_3_AUTHORIZATION_MARKER = (
    "AUTHORIZED / ACTIVE: DURABILITY IMPLEMENTATION LANE 3 - "
    "MAINTENANCE LOCKING + MUTATION QUIESCENCE "
    "(OWNER AUTHORIZATION; BASE MAIN `1BE759A5`)"
)
LANE_4_AUTHORIZATION_MARKER = (
    "AUTHORIZED / ACTIVE: DURABILITY IMPLEMENTATION LANE 4 - "
    "VERSIONED SNAPSHOT + MANIFEST "
    "(OWNER AUTHORIZATION; BASE MAIN `38DD95FD`)"
)
LANE_1_COMPLETE_MARKER = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 1 - CANONICAL STATE REGISTRY/MIGRATION DETECTION"
)
LANE_1_COMPLETE_PROVENANCE = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 1 - "
    "CANONICAL STATE REGISTRY/MIGRATION DETECTION (PR #413; MAIN `E74FDCA0`)"
)
LANE_2_COMPLETE_MARKER = "COMPLETE: DURABILITY IMPLEMENTATION LANE 2 - CORRUPTION-SAFE READERS"
LANE_2_COMPLETE_PROVENANCE = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 2 - CORRUPTION-SAFE READERS "
    "(PR #416; MAIN `80E1C86F`)"
)
LANE_3_COMPLETE_MARKER = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 3 - MAINTENANCE LOCKING + MUTATION QUIESCENCE"
)
LANE_3_COMPLETE_PROVENANCE = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 3 - "
    "MAINTENANCE LOCKING + MUTATION QUIESCENCE (PR #419; MAIN `2BFE202E`)"
)
LANE_4_COMPLETE_MARKER = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 4 - VERSIONED SNAPSHOT + MANIFEST"
)
LANE_4_COMPLETE_PROVENANCE = (
    "COMPLETE: DURABILITY IMPLEMENTATION LANE 4 - VERSIONED SNAPSHOT + MANIFEST "
    "(PR #421; MAIN `4E32B501`)"
)
LANE_4_FRESH_MAIN_CLOSEOUT = (
    "FRESH-MAIN CLOSEOUT: PASS (314 FOCUSED DURABILITY/OPERATIONAL-TRUTH TESTS "
    "PASSED; 1 EXPECTED WINDOWS POSIX-FIFO SKIP; RUNTIME STRUCTURAL SMOKE PASS)"
)
POST_423_COMPLETE_PROVENANCE = (
    "COMPLETE: #409 RELEASE INTEGRITY / REPOSITORY CONTROL (PR #423; MAIN `AA39515F`)"
)
POST_410_COMPLETE_PROVENANCE = (
    "COMPLETE: #410 PRIVATE-BETA FREEZE CRITERIA (PR #410; MAIN `3AD3F544`)"
)
LANE_5A_AUTHORIZATION_MARKER = (
    "AUTHORIZED / ACTIVE: LANE 5A RECOVERY CONSTRUCTION (OWNER AUTHORIZATION; BASE MAIN `3AD3F544`)"
)
LANE_5A_MIGRATION_COMPLETE_PROVENANCE = (
    "COMPLETE: LANE 5A STEP 1 - INACTIVE RECOVERY CANDIDATE MIGRATION (PR #424; MAIN `298B7731`)"
)
LANE_5A_MIGRATION_PROOF = (
    "MIGRATION PROOF: PASS (173 DURABILITY TESTS PASSED; 1 EXPECTED WINDOWS POSIX-FIFO SKIP)"
)
LANE_5A_VALIDATION_COMPLETE_PROVENANCE = (
    "COMPLETE: LANE 5A STEP 2 - RECOVERY CANDIDATE VALIDATION (PR #426; MAIN `9DE640CD`)"
)
LANE_5A_VALIDATION_PROOF = (
    "VALIDATION PROOF: PASS (184 DURABILITY TESTS PASSED; 1 EXPECTED WINDOWS POSIX-FIFO SKIP)"
)
LANE_5A_ACTIVATION_COMPLETE_PROVENANCE = (
    "COMPLETE: LANE 5A STEP 3 - CONTROLLED RECOVERY ACTIVATION (PR #427; MAIN `678DDA6C`)"
)
LANE_5A_ACTIVATION_PROOF = (
    "ACTIVATION PROOF: PASS (192 DURABILITY TESTS PASSED; 1 EXPECTED WINDOWS POSIX-FIFO SKIP)"
)
LANE_5A_AUTHORITY_FOUNDATION_COMPLETE_PROVENANCE = (
    "COMPLETE: LANE 5A AUTHORITY-FOUNDATION CORRECTION (PR #428; MAIN `3A3E9D33`)"
)
LANE_5A_AUTHORITY_FOUNDATION_PROOF = (
    "AUTHORITY FOUNDATION PROOF: PASS (201 DURABILITY TESTS PASSED; 1 EXPECTED WINDOWS POSIX-FIFO SKIP)"
)
LANE_5A_AUTHORITY_MODEL = "RECOVERY AUTHORITY MODEL: DUAL-SLOT HIGHEST-VALID-GENERATION SELECTION"
LANE_5A_AUTHORITY_FOUNDATION_MAIN_SHA = "3A3E9D332C6B744DCEA0FEF9D3532E5FCDE60E51"
LANE_5A_ROLLBACK_RESTORE_COMPLETE_PROVENANCE = (
    "COMPLETE: LANE 5A STEP 4 - ROLLBACK/RESTORE PROOF (PR #430; MAIN `868DE9D9`)"
)
LANE_5A_ROLLBACK_RESTORE_PROOF = (
    "ROLLBACK/RESTORE PROOF: PASS (208 DURABILITY TESTS PASSED; "
    "1 EXPECTED WINDOWS POSIX-FIFO SKIP; RUNTIME STRUCTURAL SMOKE PASS)"
)
LANE_5A_ROLLBACK_RESTORE_MAIN_SHA = "868DE9D92C701834F1C4FBA422AB9C47A01EA33F"
ROLLBACK_RESTORE_CLOSEOUT_STATE_MARKER = "ROLLBACK_RESTORE_CLOSEOUT_STATE: COMPLETE"
ROLLBACK_RESTORE_CLOSEOUT_COMPLETE = "COMPLETE"
ROLLBACK_RESTORE_INCOMPLETE_PROSE = re.compile(
    r"\b(?:STARTED|IN\s+PROGRESS|NOT\s+STARTED|NOT\s+BEGUN|UNSTARTED|PENDING|"
    r"INCOMPLETE|UNFINISHED|OUTSTANDING|"
    r"IS\s+NOT(?:\s+[A-Z0-9]+){0,3}\s+(?:COMPLETE|FINISHED)|"
    r"HAS\s+NOT(?:\s+[A-Z0-9]+){0,3}\s+COMPLETED|"
    r"WAS\s+NOT(?:\s+[A-Z0-9]+){0,3}\s+COMPLETED|"
    r"(?:STILL\s+)?NEEDS(?:\s+[A-Z0-9]+){0,3}\s+COMPLETION)\b"
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
    "priority": re.compile(r"^## Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b", re.MULTILINE),
    "work_status": re.compile(r"^WAVE (?P<lane>A1|A2|B1|B2|B3|B4|C)\s+[—-]", re.MULTILINE),
    "command_center": re.compile(r"^\s*Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\s+[—-]", re.MULTILINE),
    "active_todo": re.compile(r"^### Wave (?P<lane>A1|A2|B1|B2|B3|B4|C)\b", re.MULTILINE),
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
                if "UNMERGED" in status_upper and not re.search(r"\bMERGED\b", status_upper):
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


def _preserves_merged_pr_role(text: str, pr_number: int, required_terms: tuple[str, ...]) -> bool:
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


def _unwrap_balanced_markdown(text: str) -> str:
    """Remove balanced outer emphasis/code wrappers, including nested wrappers."""

    while True:
        for delimiter in ("**", "__", "`", "*", "_"):
            if (
                len(text) > 2 * len(delimiter)
                and text.startswith(delimiter)
                and text.endswith(delimiter)
            ):
                text = text[len(delimiter) : -len(delimiter)]
                break
        else:
            return text


def _normalize_post_405_structured_line(line: str) -> str:
    """Strip bounded Markdown containers before structured-line parsing."""

    normalized = line.lstrip()
    while True:
        container = re.match(r"^(?:>\s*|(?:[-*+]|\d+\.)\s+)", normalized)
        if container is None:
            break
        normalized = normalized[container.end() :].lstrip()
    stripped = normalized.rstrip()
    trailing = normalized[len(stripped) :]
    normalized = _unwrap_balanced_markdown(stripped) + trailing
    label = re.match(r"^(?P<opening>[*_`]*)(?P<label>NEXT:|THEN:)", normalized)
    if label:
        closing = label.group("opening")[::-1]
        end = label.end() + len(closing)
        if normalized[label.end() : end] == closing:
            wrapped_label = normalized[:end]
            if _unwrap_balanced_markdown(wrapped_label) == label.group("label"):
                payload = normalized[end:]
                separator = " " if payload and not payload[0].isspace() else ""
                normalized = label.group("label") + separator + payload
    return normalized


def _post_405_lifecycle_state(line: str) -> str | None:
    """Return a lifecycle state after bounded Markdown normalization."""

    lifecycle = re.match(
        r"^BETA_READINESS_SEQUENCE_V1:\s*(?P<state>\S+)\s*$",
        _normalize_post_405_structured_line(line).rstrip(),
    )
    return lifecycle.group("state") if lifecycle else None


def _normalized_heading(line: str) -> tuple[int, str] | None:
    """Interpret the bounded ATX heading form used by ordering documents."""

    match = re.match(r"^(?P<marks>#{1,6})\s+(?P<title>\S.*)$", line.rstrip())
    if match is None:
        return None
    title = _unwrap_balanced_markdown(match.group("title"))
    return len(match.group("marks")), title.upper()


def _markdown_structure(text: str):
    """Yield offsets, lines, heading ancestry and historical state consistently."""

    stack: list[tuple[int, str, int]] = []
    offset = 0
    for line in text.upper().splitlines(keepends=True):
        heading = _normalized_heading(line)
        if heading:
            level, title = heading
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title, offset))
        historical = any(re.match(r"HISTORICAL\b", title) for _, title, _ in stack)
        yield offset, line, heading, tuple(stack), historical
        offset += len(line)


def _non_historical_post_405_lifecycle_declarations(
    text: str,
) -> tuple[tuple[int, str], ...]:
    """Return lifecycle declarations outside explicitly historical sections."""

    declarations: list[tuple[int, str]] = []
    for offset, line, _, _, historical in _markdown_structure(text):
        lifecycle_state = _post_405_lifecycle_state(line)
        if lifecycle_state is not None and not historical:
            marker_start = line.find("BETA_READINESS_SEQUENCE_V1:")
            declarations.append((offset + marker_start, lifecycle_state))
    return tuple(declarations)


def _extract_post_405_active_block(text: str) -> str | None:
    """Validate the governing current section, not just the marker's subsection."""

    declarations = _non_historical_post_405_lifecycle_declarations(text)
    if len(declarations) != 1 or declarations[0][1] != "ACTIVE":
        return None
    marker_start = declarations[0][0]
    lines = tuple(_markdown_structure(text))
    section_start, section_level = 0, 6
    for offset, line, _, ancestors, _ in lines:
        if offset <= marker_start < offset + len(line):
            # H1 is the document title; the outermost section beneath it governs
            # the marker even when a subordinate heading immediately precedes it.
            sections = [entry for entry in ancestors if entry[0] > 1]
            governing = sections[0] if sections else (ancestors[0] if ancestors else None)
            if governing:
                section_level, _, section_start = governing
            break
    active = []
    for offset, line, heading, _, historical in lines:
        if offset < section_start:
            continue
        if offset > section_start and heading and heading[0] <= section_level:
            break
        if not historical:
            active.append(line)
    return "".join(active)


def _rollback_restore_closeout_state(text: str) -> str | None:
    """Return the canonical rollback-closeout state, never an inferred prose state."""

    active = _extract_post_405_active_block(text)
    if active is None:
        return None
    markers = tuple(
        _normalize_post_405_structured_line(line)
        for line in active.splitlines()
        if _normalize_post_405_structured_line(line).startswith(
            "ROLLBACK_RESTORE_CLOSEOUT_STATE:"
        )
    )
    if markers == (ROLLBACK_RESTORE_CLOSEOUT_STATE_MARKER,):
        return ROLLBACK_RESTORE_CLOSEOUT_COMPLETE
    return None


def _rollback_restore_prose_directly_contradicts_closeout(
    structured_lines: tuple[str, ...], canonical_lines: set[str]
) -> bool:
    """Reject ambiguous incomplete rollback prose without resolving coreference.

    The canonical marker owns the completion state. Checked operational prose may
    describe it, but a line that names rollback/restore cannot also carry an
    incomplete-state phrase. This deliberately avoids clause parsing and noun
    inference; authors must write separate, unambiguous operational lines.
    """

    prose_lines = tuple(line for line in structured_lines if line not in canonical_lines)
    for index, line in enumerate(prose_lines):
        # Markdown may wrap one direct operational sentence across two physical
        # lines. Join only an unterminated line with its immediate successor;
        # this is formatting normalization, not clause or noun inference.
        if (
            not re.search(r"[.!?;]\s*$", line)
            and index + 1 < len(prose_lines)
        ):
            line = f"{line} {prose_lines[index + 1]}"
        normalized = re.sub(r"\bISN['’]T\b", "IS NOT", line)
        normalized = re.sub(r"\bHASN['’]T\b", "HAS NOT", normalized)
        normalized = re.sub(r"\bWASN['’]T\b", "WAS NOT", normalized)
        normalized = re.sub(r"[^A-Z0-9]+", " ", normalized)
        if (
            re.search(r"\b(?:ROLLBACK|RESTORE)\b", normalized)
            and ROLLBACK_RESTORE_INCOMPLETE_PROSE.search(normalized)
        ):
            return True
    return False


def _rollback_restore_prose_directly_marks_current_or_next(
    structured_lines: tuple[str, ...], canonical_lines: set[str]
) -> bool:
    """Detect only direct current/next rollback labels, not nearby prose."""

    prose_lines = tuple(line for line in structured_lines if line not in canonical_lines)
    for index, line in enumerate(prose_lines):
        if not re.search(r"[.!?;]\s*$", line) and index + 1 < len(prose_lines):
            line = f"{line} {prose_lines[index + 1]}"
        normalized = re.sub(r"[^A-Z0-9]+", " ", line)
        if re.search(
            r"\b(?:ROLLBACK|RESTORE)(?:\s+(?:ROLLBACK|RESTORE|PROOF)){0,2}\s+"
            r"(?:(?:IS|ARE|REMAINS|STAYS)\s+)?(?:THE\s+)?"
            r"(?:NEXT|CURRENT|IMMEDIATE)(?:\s+(?:LANE|EFFORT|WORK|PROOF))?\b",
            normalized,
        ) or re.search(
            r"\b(?:THE\s+)?(?:NEXT|CURRENT|IMMEDIATE)\s+"
            r"(?:(?:LANE|EFFORT|WORK|PROOF)\s+(?:(?:IS|ARE|REMAINS|STAYS)\s+)?)?"
            r"(?:ROLLBACK|RESTORE)\b",
            normalized,
        ):
            return True
    return False


def _post_405_sync_start_shas(text: str) -> tuple[str, ...]:
    """Return sync-start SHAs from the current lifecycle section only."""

    active = _extract_post_405_active_block(text)
    if active is None:
        return ()
    return tuple(
        match.group("sha")
        for match in re.finditer(
            r"VERIFIED MAIN (?:AT SYNC START|AFTER LANE 5A MIGRATION|AFTER LANE 5A AUTHORITY FOUNDATION|"
            r"AFTER LANE 5A ROLLBACK/RESTORE PROOF):\s+"
            r"(?P<sha>[0-9A-F]{40})\b",
            active,
        )
    )


def _preserves_lane_5a_milestone_order(
    structured_lines: tuple[str, ...],
    directive_sequence: tuple[str, ...],
    completion_markers: tuple[str, ...] = (),
) -> bool:
    milestones = (
        POST_406_COMPLETE_PROVENANCE,
        POST_408_COMPLETE_PROVENANCE,
        LANE_1_COMPLETE_PROVENANCE,
        LANE_2_COMPLETE_PROVENANCE,
        LANE_3_COMPLETE_PROVENANCE,
        LANE_4_COMPLETE_PROVENANCE,
        LANE_4_FRESH_MAIN_CLOSEOUT,
        POST_423_COMPLETE_PROVENANCE,
        POST_410_COMPLETE_PROVENANCE,
        LANE_5A_AUTHORIZATION_MARKER,
        LANE_5A_MIGRATION_COMPLETE_PROVENANCE,
        LANE_5A_MIGRATION_PROOF,
        LANE_5A_VALIDATION_COMPLETE_PROVENANCE,
        LANE_5A_VALIDATION_PROOF,
        LANE_5A_ACTIVATION_COMPLETE_PROVENANCE,
        LANE_5A_ACTIVATION_PROOF,
        LANE_5A_AUTHORITY_FOUNDATION_COMPLETE_PROVENANCE,
        LANE_5A_AUTHORITY_FOUNDATION_PROOF,
        LANE_5A_AUTHORITY_MODEL,
        *completion_markers,
        *directive_sequence,
    )
    try:
        positions = tuple(structured_lines.index(marker) for marker in milestones)
    except ValueError:
        return False
    return positions == tuple(sorted(positions)) and len(set(positions)) == len(positions)


def _preserves_post_405_boundary(
    text: str,
    *,
    allow_pre_406_sequence: bool = True,
    require_lane_1_closeout: bool = False,
    require_lane_2_closeout: bool = False,
    require_lane_3_active: bool = False,
    require_lane_3_closeout: bool = False,
    require_lane_4_active: bool = False,
    require_lane_4_complete: bool = False,
    require_lane_5a_recovery_foundation: bool = False,
    require_lane_5a_rollback_restore_closeout: bool = False,
    rollback_restore_closeout_state: str | None = None,
) -> bool:
    """Require the current beta-readiness order and feature freeze."""

    active = _extract_post_405_active_block(text)
    if active is None:
        return False
    directives = tuple(
        normalized_line
        for line in active.splitlines()
        if re.match(
            r"^(?:NEXT|THEN):",
            normalized_line := _normalize_post_405_structured_line(line),
        )
    )
    structured_lines = tuple(
        _normalize_post_405_structured_line(line).rstrip() for line in active.splitlines()
    )
    completion_406_lines = tuple(
        line for line in structured_lines if line.startswith(POST_406_COMPLETE_MARKER)
    )
    completion_408_lines = tuple(
        line for line in structured_lines if line.startswith(POST_408_COMPLETE_MARKER)
    )
    lane_1_completion_lines = tuple(
        line for line in structured_lines if line.startswith(LANE_1_COMPLETE_MARKER)
    )
    lane_2_completion_lines = tuple(
        line for line in structured_lines if line.startswith(LANE_2_COMPLETE_MARKER)
    )
    lane_3_completion_lines = tuple(
        line for line in structured_lines if line.startswith(LANE_3_COMPLETE_MARKER)
    )
    lane_4_completion_lines = tuple(
        line for line in structured_lines if line.startswith(LANE_4_COMPLETE_MARKER)
    )
    post_423_completion_lines = tuple(
        line for line in structured_lines if line.startswith("COMPLETE: #409")
    )
    post_410_completion_lines = tuple(
        line for line in structured_lines if line.startswith("COMPLETE: #410")
    )
    lane_5a_migration_lines = tuple(
        line
        for line in structured_lines
        if line.startswith("COMPLETE: LANE 5A STEP 1 - INACTIVE RECOVERY CANDIDATE MIGRATION")
    )
    has_406_provenance = completion_406_lines == (POST_406_COMPLETE_PROVENANCE,)
    has_408_provenance = completion_408_lines == (POST_408_COMPLETE_PROVENANCE,)
    has_lane_1_provenance = lane_1_completion_lines == (LANE_1_COMPLETE_PROVENANCE,)
    has_lane_2_provenance = lane_2_completion_lines == (LANE_2_COMPLETE_PROVENANCE,)
    has_lane_3_provenance = lane_3_completion_lines == (LANE_3_COMPLETE_PROVENANCE,)
    has_lane_4_provenance = lane_4_completion_lines == (LANE_4_COMPLETE_PROVENANCE,)
    has_post_423_provenance = post_423_completion_lines == (POST_423_COMPLETE_PROVENANCE,)
    has_post_410_provenance = post_410_completion_lines == (POST_410_COMPLETE_PROVENANCE,)
    has_lane_5a_migration_provenance = lane_5a_migration_lines == (
        LANE_5A_MIGRATION_COMPLETE_PROVENANCE,
    )
    lane_5a_validation_lines = tuple(
        line
        for line in structured_lines
        if line.startswith("COMPLETE: LANE 5A STEP 2 - RECOVERY CANDIDATE VALIDATION")
    )
    lane_5a_activation_lines = tuple(
        line
        for line in structured_lines
        if line.startswith("COMPLETE: LANE 5A STEP 3 - CONTROLLED RECOVERY ACTIVATION")
    )
    lane_5a_authority_foundation_lines = tuple(
        line
        for line in structured_lines
        if line.startswith("COMPLETE: LANE 5A AUTHORITY-FOUNDATION CORRECTION")
    )
    lane_5a_rollback_restore_lines = tuple(
        line
        for line in structured_lines
        if line.startswith("COMPLETE: LANE 5A STEP 4 - ROLLBACK/RESTORE PROOF")
    )
    fresh_main_closeout_lines = tuple(
        line for line in structured_lines if line.startswith("FRESH-MAIN CLOSEOUT:")
    )
    has_lane_4_fresh_main_closeout = fresh_main_closeout_lines == (LANE_4_FRESH_MAIN_CLOSEOUT,)
    migration_proof_lines = tuple(
        line for line in structured_lines if line.startswith("MIGRATION PROOF:")
    )
    has_lane_5a_migration_proof = migration_proof_lines == (LANE_5A_MIGRATION_PROOF,)
    validation_proof_lines = tuple(
        line for line in structured_lines if line.startswith("VALIDATION PROOF:")
    )
    activation_proof_lines = tuple(
        line for line in structured_lines if line.startswith("ACTIVATION PROOF:")
    )
    authority_foundation_proof_lines = tuple(
        line for line in structured_lines if line.startswith("AUTHORITY FOUNDATION PROOF:")
    )
    rollback_restore_proof_lines = tuple(
        line for line in structured_lines if line.startswith("ROLLBACK/RESTORE PROOF:")
    )
    authority_model_lines = tuple(
        line for line in structured_lines if line.startswith("RECOVERY AUTHORITY MODEL:")
    )
    has_lane_5a_validation_provenance = lane_5a_validation_lines == (
        LANE_5A_VALIDATION_COMPLETE_PROVENANCE,
    )
    has_lane_5a_validation_proof = validation_proof_lines == (LANE_5A_VALIDATION_PROOF,)
    has_lane_5a_activation_provenance = lane_5a_activation_lines == (
        LANE_5A_ACTIVATION_COMPLETE_PROVENANCE,
    )
    has_lane_5a_activation_proof = activation_proof_lines == (LANE_5A_ACTIVATION_PROOF,)
    has_lane_5a_authority_foundation_provenance = lane_5a_authority_foundation_lines == (
        LANE_5A_AUTHORITY_FOUNDATION_COMPLETE_PROVENANCE,
    )
    has_lane_5a_authority_foundation_proof = authority_foundation_proof_lines == (
        LANE_5A_AUTHORITY_FOUNDATION_PROOF,
    )
    has_lane_5a_authority_model = authority_model_lines == (LANE_5A_AUTHORITY_MODEL,)
    has_lane_5a_rollback_restore_provenance = (
        lane_5a_rollback_restore_lines == (LANE_5A_ROLLBACK_RESTORE_COMPLETE_PROVENANCE,)
    )
    has_lane_5a_rollback_restore_proof = (
        rollback_restore_proof_lines == (LANE_5A_ROLLBACK_RESTORE_PROOF,)
    )
    authority_prefix_pattern = r"^(?:AUTHORIZED(?:\s*/\s*ACTIVE)?|APPROVED|ACTIVE):"
    durability_authorizations = tuple(
        line
        for line in structured_lines
        if re.match(
            authority_prefix_pattern + r"\s+DURABILITY IMPLEMENTATION LANE\b",
            line,
        )
    )
    pending_locking_authorizations = tuple(
        line
        for line in structured_lines
        if re.match(authority_prefix_pattern, line)
        and ("MAINTENANCE LOCK" in line or "MUTATION QUIESCENCE" in line)
    )
    lane_5a_authorizations = tuple(
        line
        for line in structured_lines
        if re.match(authority_prefix_pattern, line) and "LANE 5A RECOVERY CONSTRUCTION" in line
    )
    premature_later_durability_authorizations = tuple(
        line
        for line in structured_lines
        if re.match(authority_prefix_pattern, line)
        and (
            "DURABILITY" in line
            or "SNAPSHOT" in line
            or "MANIFEST" in line
            or "MIGRATION" in line
            or "CANDIDATE VALIDATION" in line
            or "CANDIDATE ACTIVATION" in line
            or "GENERATION ACTIVATION" in line
            or "BACKUP" in line
            or "RECOVERY" in line
            or "RESTORE" in line
            or "ROLLBACK" in line
        )
    )
    normalized = " ".join(active.split())
    semantic_active = re.sub(r"[^A-Z0-9]+", " ", active.upper())
    canonical_rollback_lines = {
        LANE_5A_ROLLBACK_RESTORE_COMPLETE_PROVENANCE,
        LANE_5A_ROLLBACK_RESTORE_PROOF,
        *LANE_5A_RECOVERY_FOUNDATION_DIRECTIVE_SEQUENCE,
        *LANE_5A_RECOVERY_COMPLETE_DIRECTIVE_SEQUENCE,
    }
    rollback_unfinished_claim = _rollback_restore_prose_directly_contradicts_closeout(
        structured_lines, canonical_rollback_lines
    )
    rollback_completion_claim = any(
        re.search(r"\b(?:ROLLBACK|RESTORE)\b", line)
        and re.search(r"\b(?:COMPLETE|COMPLETED)\b", line)
        for line in structured_lines
        if line not in canonical_rollback_lines
    )
    rollback_next_or_current_claim = _rollback_restore_prose_directly_marks_current_or_next(
        structured_lines, canonical_rollback_lines
    )
    obsolete_current_lane_claim = bool(
        re.search(
            r"\b(?:THE )?(?:CURRENT )?(?:IMMEDIATE )?LANE (?:CURRENTLY )?(?:IS )?(?:CURRENTLY )?"
            r"RECOVERY CANDIDATE VALIDATION\b"
            r"|\bRECOVERY CANDIDATE VALIDATION (?:IS )?"
            r"(?:THE )?(?:CURRENT )?(?:IMMEDIATE )?LANE\b",
            semantic_active,
        )
    )
    preserves_initial_order = allow_pre_406_sequence and directives == POST_405_DIRECTIVE_SEQUENCE
    preserves_post_406_order = (
        not require_lane_1_closeout
        and directives == POST_406_DIRECTIVE_SEQUENCE
        and has_406_provenance
    )
    preserves_lane_1_closeout = (
        directives == POST_413_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and durability_authorizations == (LANE_2_AUTHORIZATION_MARKER,)
    )
    preserves_lane_2_closeout = (
        directives == POST_416_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and not durability_authorizations
        and not pending_locking_authorizations
    )
    preserves_lane_3_active = (
        directives == LANE_3_ACTIVE_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and durability_authorizations == (LANE_3_AUTHORIZATION_MARKER,)
        and pending_locking_authorizations == (LANE_3_AUTHORIZATION_MARKER,)
    )
    preserves_lane_3_closeout = (
        directives == POST_419_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and has_lane_3_provenance
        and not durability_authorizations
        and not pending_locking_authorizations
        and not premature_later_durability_authorizations
    )
    preserves_lane_4_active = (
        directives == LANE_4_ACTIVE_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and has_lane_3_provenance
        and durability_authorizations == (LANE_4_AUTHORIZATION_MARKER,)
        and premature_later_durability_authorizations == (LANE_4_AUTHORIZATION_MARKER,)
    )
    preserves_lane_4_complete = (
        directives == LANE_4_COMPLETE_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and has_lane_3_provenance
        and has_lane_4_provenance
        and has_lane_4_fresh_main_closeout
        and not durability_authorizations
        and not pending_locking_authorizations
        and not premature_later_durability_authorizations
    )
    preserves_lane_5a_recovery_foundation = (
        directives == LANE_5A_RECOVERY_FOUNDATION_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and has_lane_3_provenance
        and has_lane_4_provenance
        and has_lane_4_fresh_main_closeout
        and has_post_423_provenance
        and has_post_410_provenance
        and has_lane_5a_migration_provenance
        and has_lane_5a_migration_proof
        and has_lane_5a_validation_provenance
        and has_lane_5a_validation_proof
        and has_lane_5a_activation_provenance
        and has_lane_5a_activation_proof
        and has_lane_5a_authority_foundation_provenance
        and has_lane_5a_authority_foundation_proof
        and has_lane_5a_authority_model
        and _preserves_lane_5a_milestone_order(
            structured_lines, LANE_5A_RECOVERY_FOUNDATION_DIRECTIVE_SEQUENCE
        )
        and _post_405_sync_start_shas(text) == (LANE_5A_AUTHORITY_FOUNDATION_MAIN_SHA,)
        and not durability_authorizations
        and not pending_locking_authorizations
        and lane_5a_authorizations == (LANE_5A_AUTHORIZATION_MARKER,)
        and premature_later_durability_authorizations == (LANE_5A_AUTHORIZATION_MARKER,)
        and not rollback_unfinished_claim
        and not rollback_completion_claim
        and not rollback_next_or_current_claim
        and not obsolete_current_lane_claim
    )
    preserves_lane_5a_rollback_restore_closeout = (
        directives == LANE_5A_RECOVERY_COMPLETE_DIRECTIVE_SEQUENCE
        and has_406_provenance
        and has_408_provenance
        and has_lane_1_provenance
        and has_lane_2_provenance
        and has_lane_3_provenance
        and has_lane_4_provenance
        and has_lane_4_fresh_main_closeout
        and has_post_423_provenance
        and has_post_410_provenance
        and has_lane_5a_migration_provenance
        and has_lane_5a_migration_proof
        and has_lane_5a_validation_provenance
        and has_lane_5a_validation_proof
        and has_lane_5a_activation_provenance
        and has_lane_5a_activation_proof
        and has_lane_5a_authority_foundation_provenance
        and has_lane_5a_authority_foundation_proof
        and has_lane_5a_authority_model
        and has_lane_5a_rollback_restore_provenance
        and has_lane_5a_rollback_restore_proof
        and rollback_restore_closeout_state == ROLLBACK_RESTORE_CLOSEOUT_COMPLETE
        and _preserves_lane_5a_milestone_order(
            structured_lines,
            LANE_5A_RECOVERY_COMPLETE_DIRECTIVE_SEQUENCE,
            (
                LANE_5A_ROLLBACK_RESTORE_COMPLETE_PROVENANCE,
                LANE_5A_ROLLBACK_RESTORE_PROOF,
            ),
        )
        and _post_405_sync_start_shas(text) == (LANE_5A_ROLLBACK_RESTORE_MAIN_SHA,)
        and not durability_authorizations
        and not pending_locking_authorizations
        and lane_5a_authorizations == (LANE_5A_AUTHORIZATION_MARKER,)
        and premature_later_durability_authorizations == (LANE_5A_AUTHORIZATION_MARKER,)
        and not rollback_unfinished_claim
        and not rollback_next_or_current_claim
        and not obsolete_current_lane_claim
    )
    preserves_allowed_state = (
        preserves_initial_order
        or preserves_post_406_order
        or preserves_lane_1_closeout
        or preserves_lane_2_closeout
        or preserves_lane_3_active
        or preserves_lane_3_closeout
        or preserves_lane_4_active
        or preserves_lane_4_complete
        or preserves_lane_5a_recovery_foundation
        or preserves_lane_5a_rollback_restore_closeout
    )
    if require_lane_2_closeout:
        preserves_allowed_state = (
            preserves_lane_2_closeout
            or preserves_lane_3_active
            or preserves_lane_3_closeout
            or preserves_lane_4_active
            or preserves_lane_4_complete
            or preserves_lane_5a_recovery_foundation
            or preserves_lane_5a_rollback_restore_closeout
        )
    if require_lane_3_active:
        preserves_allowed_state = preserves_lane_3_active
    if require_lane_3_closeout:
        preserves_allowed_state = (
            preserves_lane_3_closeout
            or preserves_lane_4_active
            or preserves_lane_4_complete
            or preserves_lane_5a_recovery_foundation
            or preserves_lane_5a_rollback_restore_closeout
        )
    if require_lane_4_active:
        preserves_allowed_state = preserves_lane_4_active
    if require_lane_4_complete:
        preserves_allowed_state = (
            preserves_lane_4_complete
            or preserves_lane_5a_recovery_foundation
            or preserves_lane_5a_rollback_restore_closeout
        )
    if require_lane_5a_recovery_foundation:
        preserves_allowed_state = (
            preserves_lane_5a_recovery_foundation or preserves_lane_5a_rollback_restore_closeout
        )
    if require_lane_5a_rollback_restore_closeout:
        preserves_allowed_state = preserves_lane_5a_rollback_restore_closeout
    if not preserves_allowed_state:
        return False
    required = ("#397 THROUGH #405: COMPLETE / MERGED",)
    if not all(marker in normalized for marker in required):
        return False
    lifecycle_states = tuple(
        state
        for line in active.splitlines()
        if (state := _post_405_lifecycle_state(line)) is not None
    )
    if lifecycle_states != ("ACTIVE",):
        return False
    if len(_post_405_sync_start_shas(text)) != 1:
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
        r"(?:DOES|DO)\s+NOT\s+REMAIN\s+PAUSED",
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
        rendered = ", ".join(f"{name}={lane}" for name, lane in sorted(lanes.items()))
        errors.append(
            f"active stabilization lane mismatch / stabilization/current-truth gate mismatch: {rendered}"
        )

    completed_surfaces = {name for name, lane in lanes.items() if lane == POST_WAVE_C_COMPLETE_LANE}
    if lifecycle_generation is None:
        lifecycle_generation = (
            CURRENT_LIFECYCLE_GENERATION
            if root.resolve() == ROOT.resolve()
            else HISTORICAL_LIFECYCLE_GENERATION
        )

    post_394_mode = any(
        "GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED" in text.upper() for text in texts.values()
    )
    post_405_mode = lifecycle_generation == CURRENT_LIFECYCLE_GENERATION
    if post_405_mode:
        required_completed_surfaces = set(LANE_PATTERNS)
        current_completed_surfaces = {
            name
            for name in required_completed_surfaces
            if POST_WAVE_C_COMPLETE_MARKER.search(
                _extract_post_405_active_block(texts.get(name, "")) or ""
            )
        }
        for name in sorted(required_completed_surfaces - current_completed_surfaces):
            errors.append(
                f"{paths[name]}: current post-#405 lifecycle requires completed PR #366 closeout state"
            )
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
        rollback_restore_closeout_state = _rollback_restore_closeout_state(
            texts.get("canonical_index", "")
        )
        if rollback_restore_closeout_state != ROLLBACK_RESTORE_CLOSEOUT_COMPLETE:
            errors.append(
                f"{paths['canonical_index']}: canonical rollback/restore closeout state marker must be "
                f"{ROLLBACK_RESTORE_CLOSEOUT_STATE_MARKER}"
            )
        sync_start_shas: dict[str, str] = {}
        for name in POST_405_ORDERING_SURFACES:
            text = texts.get(name)
            if text is None:
                continue
            if not _preserves_post_405_boundary(
                text,
                allow_pre_406_sequence=False,
                require_lane_1_closeout=True,
                require_lane_2_closeout=True,
                require_lane_3_closeout=True,
                require_lane_4_complete=True,
                require_lane_5a_rollback_restore_closeout=True,
                rollback_restore_closeout_state=rollback_restore_closeout_state,
            ):
                errors.append(
                    f"{paths[name]}: current ordering does not preserve the active beta-readiness boundary"
                )
                continue
            sync_start_shas[name] = _post_405_sync_start_shas(text)[0]
        if len(set(sync_start_shas.values())) > 1:
            rendered = ", ".join(f"{name}={sha}" for name, sha in sorted(sync_start_shas.items()))
            errors.append(f"post-#405 sync-start SHA mismatch: {rendered}")
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
        errors.append("canonical index no longer separates implementation from evidence")

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
