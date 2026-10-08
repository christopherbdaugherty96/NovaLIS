"""Issue #457: the owner operating sequence is the single current lifecycle.

These tests bind the operational-truth checker to OWNER_OPERATING_SEQUENCE_2026_10_08
and prove that the superseded post-#405 / Alpha-0 / day-30 Guard ordering cannot
silently return as current truth. Historical provenance stays allowed under
explicitly historical headings.
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

OWNER_MARKER = "OWNER_OPERATING_SEQUENCE_2026_10_08: ACTIVE"
MASTER_ROADMAP = "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
EXPECTED_DIRECTIVES = (
    "NEXT: EGRESS INVENTORY",
    "THEN: PROVIDER-NEUTRAL DATA-OUT ENFORCEMENT AT THE COMMON OUTBOUND BOUNDARY",
    "THEN: ZERO-ATTEMPT DENIAL PROOF (DENY -> ZERO TRANSMISSION, ZERO ATTEMPTED EXTERNAL "
    "CONNECTION, EXPLICIT LOCAL RESULT, DURABLE DECISION/DISCLOSURE EVIDENCE)",
    "THEN: CLEAN ATTRIBUTABLE ALPHA-0 WINDOWS ARTIFACT (EXACT-SHA CLEAN EXPORT + "
    "FORBIDDEN-CONTENT SCAN)",
    "THEN: ONE DEFINED EXTERNAL TECHNICAL-OPERATOR WORKFLOW AGAINST THAT EXACT ARTIFACT",
    "THEN: EVIDENCE-DRIVEN BLOCKER-ONLY FIXES",
    "THEN: FROZEN PRIVATE-BETA CANDIDATE",
    "THEN: THREE REAL USERS",
    "THEN: MINIMAL CONTINUITY ONLY IF PRODUCT EVIDENCE EARNS IT",
)
ORDERING_SURFACES = (
    "README.md",
    "START_HERE.md",
    "AGENTS.md",
    ".agent_context/current_priority.md",
    "docs/status/CURRENT_WORK_STATUS.md",
    "docs/status/DAILY_COMMAND_CENTER.md",
    "docs/todo/ACTIVE_TODO.md",
    "docs/CANONICAL/00_INDEX.md",
    "docs/CANONICAL/07_ROADMAP_TRUTH.md",
)


def _load_checker():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_operational_truth_consistency.py"
    spec = importlib.util.spec_from_file_location("owner_sequence_truth_checker", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_live_surfaces(checker, destination: Path) -> None:
    for relative in checker.CURRENT_CHECKED_SURFACES:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checker.ROOT / relative, target)


def _owner_errors(checker, root: Path) -> list[str]:
    return checker.check_operational_truth(
        root, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )


def _mutate(root: Path, relative: str, old: str, new: str) -> Path:
    target = root / relative
    original = target.read_text(encoding="utf-8")
    assert old in original, f"{old!r} not found in {relative}"
    target.write_text(original.replace(old, new, 1), encoding="utf-8")
    return target


def _assert_rejected(errors: list[str], target: Path, fragment: str) -> None:
    assert any(str(target) in error and fragment in error for error in errors), errors


def test_current_lifecycle_generation_is_the_owner_sequence():
    checker = _load_checker()

    assert checker.CURRENT_LIFECYCLE_GENERATION == "OWNER_OPERATING_SEQUENCE_2026_10_08"
    assert checker.POST_405_LIFECYCLE_GENERATION == "POST_405_BETA_READINESS_V1"
    assert checker.OWNER_SEQUENCE_DIRECTIVES == EXPECTED_DIRECTIVES


def test_live_repository_passes_owner_sequence_lifecycle():
    checker = _load_checker()

    assert _owner_errors(checker, checker.ROOT) == []
    assert checker.check_operational_truth(checker.ROOT) == []


@pytest.mark.parametrize("relative", ORDERING_SURFACES)
def test_each_ordering_surface_has_one_owner_block_with_exact_sequence(relative):
    checker = _load_checker()
    text = (checker.ROOT / relative).read_text(encoding="utf-8")

    block = checker._extract_owner_sequence_block(text)

    assert block is not None
    directives = tuple(
        line
        for raw in block.splitlines()
        if (line := checker._normalize_post_405_structured_line(raw).rstrip()).startswith(
            ("NEXT", "THEN:")
        )
    )
    assert directives == EXPECTED_DIRECTIVES


@pytest.mark.parametrize("relative", ORDERING_SURFACES)
def test_missing_owner_marker_is_rejected(tmp_path, relative):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path, relative, OWNER_MARKER, "OWNER_OPERATING_SEQUENCE_2026_10_08: PROPOSED"
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


def test_second_active_owner_marker_is_rejected(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    target.write_text(
        target.read_text(encoding="utf-8") + f"\n## Another current block\n\n{OWNER_MARKER}\n",
        encoding="utf-8",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


def test_reordered_data_out_and_inventory_are_rejected(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "AGENTS.md"
    text = target.read_text(encoding="utf-8")
    swapped = text.replace("NEXT: egress inventory", "@@", 1).replace(
        "THEN: provider-neutral Data-Out enforcement at the common outbound boundary",
        "THEN: egress inventory",
        1,
    ).replace("@@", "NEXT: provider-neutral Data-Out enforcement at the common outbound boundary", 1)
    assert swapped != text
    target.write_text(swapped, encoding="utf-8")

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


def test_recovery_before_private_beta_is_rejected(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "THEN: frozen private-beta candidate",
        "THEN: recovery adoption with restrictive restore semantics\n"
        "THEN: frozen private-beta candidate",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


@pytest.mark.parametrize("relative", ORDERING_SURFACES)
def test_missing_no_authority_boundary_is_rejected(tmp_path, relative):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path,
        relative,
        "This sequence grants no new capability or authority.",
        "This sequence expands Data-Out authority.",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


def test_missing_recovery_reconciliation_is_rejected(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path,
        "docs/status/CURRENT_WORK_STATUS.md",
        "not a prerequisite for the private-beta candidate",
        "required before the private-beta candidate",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


def test_guard_gating_return_is_rejected(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path,
        "START_HERE.md",
        "Guard adoption and 30-day metrics do not gate Nova",
        "Guard adoption and 30-day metrics gate Nova",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


@pytest.mark.parametrize(
    "stale_line",
    (
        "FROZEN 2026-10-05 at main 1dfd6862: no new work. Resume only per the day-30 "
        "nova-guard decision.",
        "NEXT REQUIRED ENGINEERING: bounded local-boundary P1 repair (no remote mode or "
        "authority expansion)",
        "Canonical ordering authority for all future work:",
        "- the July master roadmap remains the long-lived ordering authority.",
        "Ordering authority: [Nova Master Roadmap 2026-07-05](docs/future/x.md).",
        "Status: canonical ordering document — the single source of truth for what comes next",
        "1. This document ORDERS work. It does not re-scope work.",
        "This roadmap still determines ordering; lane locks still determine scope.",
        "This document supersedes, as ordering authority only:",
    ),
)
@pytest.mark.parametrize(
    "relative", (".agent_context/current_priority.md", "README.md", MASTER_ROADMAP)
)
def test_stale_current_ordering_language_is_rejected_outside_history(
    tmp_path, stale_line, relative
):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / relative
    lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
    # Insert directly after the H1 title, i.e. in the current (non-historical) part.
    lines.insert(1, f"\n{stale_line}\n")
    target.write_text("".join(lines), encoding="utf-8")

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "superseded ordering language outside history"
    )


@pytest.mark.parametrize(
    "revived", ("BETA_READINESS_SEQUENCE_V1: ACTIVE", "ALPHA_0_SEQUENCE: ACTIVE")
)
@pytest.mark.parametrize("relative", ("docs/todo/ACTIVE_TODO.md", MASTER_ROADMAP))
def test_revived_superseded_lifecycle_marker_is_rejected_even_in_history(
    tmp_path, revived, relative
):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / relative
    target.write_text(
        target.read_text(encoding="utf-8")
        + f"\n## Historical revived block\n\n```text\n{revived}\n```\n",
        encoding="utf-8",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "superseded lifecycle marker declared ACTIVE"
    )


def test_stale_language_is_allowed_as_historical_provenance(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "docs/status/DAILY_COMMAND_CENTER.md"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\n## Historical extra provenance (superseded 2026-10-08)\n\n"
        "NEXT REQUIRED ENGINEERING: bounded local-boundary P1 repair (no remote mode or "
        "authority expansion)\n"
        "Resume only per the day-30 nova-guard decision.\n",
        encoding="utf-8",
    )

    assert _owner_errors(checker, tmp_path) == []


def test_master_roadmap_must_record_supersession_as_ordering_authority(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path,
        MASTER_ROADMAP,
        "superseded as current ordering authority by OWNER_OPERATING_SEQUENCE_2026_10_08",
        "retained",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path),
        target,
        "master roadmap does not record supersession by the owner operating sequence",
    )


@pytest.mark.parametrize(
    "claim",
    (
        "Guard expansion is now active.",
        "Recovery wiring will resume.",
        "New capabilities resumed.",
    ),
)
def test_paused_categories_cannot_be_resumed_inside_owner_block(tmp_path, claim):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = _mutate(
        tmp_path,
        "docs/CANONICAL/00_INDEX.md",
        "Other feature expansion remains paused.",
        f"Other feature expansion remains paused. {claim}",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "does not preserve the owner operating sequence"
    )


@pytest.mark.parametrize("relative", ("README.md", "docs/status/CURRENT_WORK_STATUS.md"))
@pytest.mark.parametrize(
    "claim",
    (
        "Recovery wiring is now active.",
        "Guard expansion resumed.",
        "Recovery wiring has resumed.",
        "New capabilities have been reactivated.",
        "Recovery wiring was restarted.",
        "Guard expansion is now underway.",
        "Recovery wiring can now begin.",
        "Voice expansion is no longer paused.",
    ),
)
def test_paused_categories_cannot_be_resumed_in_any_current_section(tmp_path, relative, claim):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / relative
    target.write_text(
        target.read_text(encoding="utf-8") + f"\n## Current recovery work\n\n{claim}\n",
        encoding="utf-8",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "paused category contradicted outside history"
    )


@pytest.mark.parametrize(
    "statement",
    (
        "Recovery wiring will not resume without a later explicit owner decision.",
        "Recovery wiring is not active.",
        "Guard expansion has not resumed.",
    ),
)
def test_negated_paused_category_statements_are_allowed(tmp_path, statement):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    target.write_text(
        target.read_text(encoding="utf-8") + f"\n## Current recovery note\n\n{statement}\n",
        encoding="utf-8",
    )

    assert _owner_errors(checker, tmp_path) == []


def test_paused_category_wording_is_allowed_as_historical_provenance(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\n## Historical recovery lane (superseded)\n\nRecovery wiring is now active.\n",
        encoding="utf-8",
    )

    assert _owner_errors(checker, tmp_path) == []


@pytest.mark.parametrize("relative", ("README.md", ".agent_context/current_priority.md"))
def test_stale_ordering_wrapped_across_lines_is_rejected(tmp_path, relative):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / relative
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\n## Current engineering\n\nNEXT REQUIRED ENGINEERING:\n"
        "bounded local-boundary P1 repair (no remote mode or authority expansion)\n",
        encoding="utf-8",
    )

    _assert_rejected(
        _owner_errors(checker, tmp_path), target, "superseded ordering language outside history"
    )


@pytest.mark.parametrize(
    ("tail", "fragment"),
    (
        ("Recovery wiring has resumed.\n", "paused category contradicted outside history"),
        (
            "Resume only per the day-30 nova-guard decision.\n",
            "superseded ordering language outside history",
        ),
    ),
)
def test_fenced_historical_heading_does_not_hide_current_text(tmp_path, tail, fragment):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\n## Current notes\n\n```text\n## Historical example\n```\n\n"
        + tail,
        encoding="utf-8",
    )

    _assert_rejected(_owner_errors(checker, tmp_path), target, fragment)


def test_fenced_heading_cannot_open_a_second_owner_section(tmp_path):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    text = target.read_text(encoding="utf-8")
    # A fenced fake heading inside the owner section must not truncate the owner block.
    patched = text.replace(
        "NEXT: egress inventory",
        "NEXT: egress inventory\n```\n\n```text\n## Historical fake\n",
        1,
    )
    assert patched != text
    target.write_text(patched, encoding="utf-8")

    assert _owner_errors(checker, tmp_path) == []


@pytest.mark.parametrize(
    ("tail", "fragment"),
    (
        ("Recovery wiring **has resumed**.", "paused category contradicted outside history"),
        ("*Recovery wiring* has resumed.", "paused category contradicted outside history"),
        ("`Guard expansion` is __now active__.", "paused category contradicted outside history"),
        (
            "**NEXT REQUIRED ENGINEERING:** bounded local-boundary P1 repair",
            "superseded ordering language outside history",
        ),
    ),
)
def test_inline_markdown_emphasis_does_not_hide_current_text(tmp_path, tail, fragment):
    checker = _load_checker()
    _copy_live_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    target.write_text(
        target.read_text(encoding="utf-8") + f"\n## Current notes\n\n{tail}\n",
        encoding="utf-8",
    )

    _assert_rejected(_owner_errors(checker, tmp_path), target, fragment)


def test_post_405_contract_remains_available_as_historical_generation():
    checker = _load_checker()
    snapshot = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "operational_truth"
        / "post_405_main_210c0085"
    )

    assert (
        checker.check_operational_truth(
            snapshot, lifecycle_generation=checker.POST_405_LIFECYCLE_GENERATION
        )
        == []
    )
    # The historical snapshot is not current truth: under the owner lifecycle it fails.
    assert checker.check_operational_truth(
        snapshot, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )
