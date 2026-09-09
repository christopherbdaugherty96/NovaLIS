from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

VALIDATED_BASELINE_SHA = "ec20a7146f7d6d55b8983cb7d6d3918d5fad9915"


def _load_checker():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_operational_truth_consistency.py"
    spec = importlib.util.spec_from_file_location("post_wave_c_truth_checker", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _governance_fixture(root: Path) -> None:
    _write(
        root,
        "docs/CANONICAL/03_GOVERNANCE_TRUTH.md",
        "Governed capability plane\n"
        "Local operator / administrative plane\n"
        "Bounded agent / routine plane\n"
        "nova_backend/src/api/connections_api.py\n",
    )


def _post_wave_c_active_fixture(root: Path) -> None:
    _write(root, "README.md", "Historical active closeout fixture.\n")
    _write(root, "START_HERE.md", "Historical active closeout fixture.\n")
    _write(
        root,
        "AGENTS.md",
        "## Post-Wave-C Current Development State — 2026-08-25\n"
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package "
        "PR #366. #335 remains NEXT / NOT AUTHORIZED.\n",
    )
    _write(
        root,
        ".agent_context/current_priority.md",
        "## Post-Wave-C Documentation Closeout — PR #366 Truth-Hygiene Contract — 2026-08-25\n"
        "#335 OPEN / DRAFT / UNMERGED\n"
        "#335 reconstruction: NEXT / NOT AUTHORIZED\n",
    )
    _write(
        root,
        "docs/status/CURRENT_WORK_STATUS.md",
        "## Current Development Lane\n```text\nPOST-WAVE-C DOCUMENTATION CLOSEOUT\n"
        "TRUTH-HYGIENE CONTRACT: PR #366\n```\n",
    )
    _write(
        root,
        "docs/status/DAILY_COMMAND_CENTER.md",
        "CURRENT PLANNING LANE:\n"
        "  Post-Wave-C documentation closeout — truth-hygiene contract PR #366.\n",
    )
    _write(
        root,
        "docs/todo/ACTIVE_TODO.md",
        "## Active Now\n### Post-Wave-C documentation closeout\n"
        "Current state:\n```text\ntruth-hygiene contract package: PR #366\n```\n",
    )
    _write(
        root,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n"
        "**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        "Current gate: **post-Wave-C documentation closeout — truth-hygiene contract "
        "package PR #366**. PR #335 remains NEXT / NOT AUTHORIZED.\n",
    )
    _governance_fixture(root)
    _write(
        root,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package PR #366.\n"
        "#335 OPEN / DRAFT / UNMERGED\n"
        "#335 reconstruction: NEXT / NOT AUTHORIZED\n",
    )


def _completed_state_text(*, include_unmerged: bool = False) -> str:
    lines = [
        "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE",
        "truth-hygiene provenance: PR #366 MERGED",
        "narration/front-door package: PR #378 MERGED",
        f"validated_baseline_sha: {VALIDATED_BASELINE_SHA}",
    ]
    if include_unmerged:
        lines.append("#335 OPEN / DRAFT / UNMERGED")
    lines.extend(
        [
            "#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED",
            "#368: NEXT BOUNDED TECHNICAL LANE",
            "#387: AFTER #368 / DOCS-ONLY",
            "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED",
        ]
    )
    return "\n".join(lines) + "\n"


def _post_wave_c_complete_fixture(root: Path) -> None:
    _write(root, "README.md", _completed_state_text())
    _write(root, "START_HERE.md", _completed_state_text())
    _write(root, "AGENTS.md", _completed_state_text())
    _write(
        root,
        ".agent_context/current_priority.md",
        _completed_state_text(include_unmerged=True),
    )
    _write(root, "docs/status/CURRENT_WORK_STATUS.md", _completed_state_text())
    _write(root, "docs/status/DAILY_COMMAND_CENTER.md", _completed_state_text())
    _write(root, "docs/todo/ACTIVE_TODO.md", _completed_state_text())
    _write(
        root,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n"
        "**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        + _completed_state_text(),
    )
    _governance_fixture(root)
    _write(
        root,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        _completed_state_text(include_unmerged=True),
    )


def test_checker_accepts_active_merge_safe_documentation_closeout_gate(tmp_path):
    checker = _load_checker()
    _post_wave_c_active_fixture(tmp_path)

    assert checker.check_operational_truth(tmp_path) == []
    assert checker.POST_WAVE_C_ACTIVE_LANE == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_ACTIVE"
    )


def test_checker_accepts_completed_documentation_closeout(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)

    assert checker.check_operational_truth(tmp_path) == []
    assert checker.POST_WAVE_C_COMPLETE_LANE == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE"
    )
    assert checker.VALIDATED_BASELINE_SHA == VALIDATED_BASELINE_SHA


def test_agents_binds_active_truth_hygiene_contract_pr():
    checker = _load_checker()
    text = (
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package PR #366. "
        "PR #335 reconstruction remains NEXT / NOT AUTHORIZED.\n"
    )

    assert checker._extract_lane("agents", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_ACTIVE:PR#366"
    )


def test_completed_state_binds_truth_hygiene_provenance_not_ui_state():
    checker = _load_checker()
    text = (
        "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE\n"
        "truth-hygiene provenance: PR #366 OPEN / DRAFT / READY / ACTIVE / MERGED\n"
        "narration/front-door package: PR #378 MERGED\n"
        f"validated_baseline_sha: {VALIDATED_BASELINE_SHA}\n"
        "#335 OPEN / DRAFT / UNMERGED\n"
        "#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED\n"
        "#368: NEXT BOUNDED TECHNICAL LANE\n"
        "#387: AFTER #368 / DOCS-ONLY\n"
        "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n"
    )

    assert checker._extract_lane("priority", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE"
    )


def test_completed_state_ignores_nearby_365_provenance_collision():
    checker = _load_checker()
    text = (
        "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE\n"
        "PR #365 merge / PR #366 branch base: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c\n"
        "PR #366 truth-hygiene package: MERGED\n"
        "PR #378 narration/front-door package: MERGED / VERIFIED\n"
        f"validated_baseline_sha: {VALIDATED_BASELINE_SHA}\n"
        "#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED\n"
        "#368: NEXT BOUNDED TECHNICAL LANE\n"
        "#387: AFTER #368 / DOCS-ONLY\n"
        "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n"
    )

    assert checker._preserves_merged_pr_role(text, 366, ("TRUTH-HYGIENE",))
    assert checker._preserves_merged_pr_role(
        text, 378, ("NARRATION", "FRONT-DOOR")
    )
    assert checker._extract_lane("active_todo", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE"
    )


def test_canonical_index_accepts_completion_without_current_gate_wording():
    checker = _load_checker()
    text = (
        "**Implementation:** code\n"
        "**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        + _completed_state_text()
    )

    assert "Current gate:" not in text
    assert checker._extract_lane("canonical_index", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE"
    )


def test_roadmap_binds_active_truth_hygiene_contract_pr():
    checker = _load_checker()
    text = (
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package PR #366. "
        "PR #335 reconstruction remains NEXT / NOT AUTHORIZED.\n"
    )

    assert checker._extract_lane("roadmap", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_ACTIVE:PR#366"
    )


def test_checker_detects_active_to_complete_state_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/status/DAILY_COMMAND_CENTER.md",
        "CURRENT PLANNING LANE:\n"
        "  Post-Wave-C documentation closeout — truth-hygiene contract PR #366.\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("gate mismatch" in error for error in errors)
    assert any(
        "command_center=POST_WAVE_C_DOCUMENTATION_CLOSEOUT_ACTIVE:PR#366" in error
        for error in errors
    )


def test_checker_detects_post_wave_c_to_legacy_lane_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_active_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "Current active stabilization lane: C\n"
        "#335 OPEN / DRAFT / UNMERGED\n"
        "#335 reconstruction: NEXT / NOT AUTHORIZED\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("gate mismatch" in error for error in errors)
    assert any("roadmap=C" in error for error in errors)


def test_checker_preserves_legacy_b1_lane_parsing():
    checker = _load_checker()

    assert checker._extract_lane(
        "priority", "## Wave B1 — Runtime Truth Instrumentation\n"
    ) == "B1"


def test_checker_detects_completed_truth_hygiene_pr_identity_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n"
        "**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE\n"
        "truth-hygiene provenance: PR #999 MERGED\n"
        "narration/front-door package: PR #378 MERGED\n"
        f"validated_baseline_sha: {VALIDATED_BASELINE_SHA}\n"
        "#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED\n"
        "#368: NEXT BOUNDED TECHNICAL LANE\n"
        "#387: AFTER #368 / DOCS-ONLY\n"
        "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any(
        "PR #366 as MERGED truth-hygiene provenance" in error
        for error in errors
    )


def test_checker_detects_missing_merged_378_provenance(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/status/CURRENT_WORK_STATUS.md",
        _completed_state_text().replace(
            "narration/front-door package: PR #378 MERGED\n", ""
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("PR #378 as MERGED" in error for error in errors)


def test_checker_does_not_borrow_366_merged_state_for_378(tmp_path):
    checker = _load_checker()
    negative = (
        "PR #366 truth-hygiene package: MERGED\n"
        "PR #378 narration/front-door package: OPEN / DRAFT\n"
    )
    positive = (
        "PR #366 truth-hygiene package: MERGED\n"
        "PR #378 narration/front-door package: MERGED / VERIFIED\n"
    )

    assert checker._preserves_merged_pr(negative, 378) is False
    assert checker._preserves_merged_pr(positive, 378) is True

    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/status/CURRENT_WORK_STATUS.md",
        _completed_state_text().replace(
            "truth-hygiene provenance: PR #366 MERGED\n"
            "narration/front-door package: PR #378 MERGED\n",
            "PR #366 truth-hygiene package: MERGED\n"
            "PR #378 narration/front-door package: OPEN / DRAFT\n",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("PR #378 as MERGED" in error for error in errors)


def test_checker_rejects_explicit_negative_378_merge_state(tmp_path):
    checker = _load_checker()

    assert checker._preserves_merged_pr("PR #378 NOT MERGED\n", 378) is False
    assert checker._preserves_merged_pr("PR #378 UNMERGED\n", 378) is False
    assert checker._preserves_merged_pr("PR #378 MERGED / VERIFIED\n", 378) is True

    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/status/CURRENT_WORK_STATUS.md",
        _completed_state_text().replace(
            "narration/front-door package: PR #378 MERGED\n",
            "narration/front-door package: PR #378 NOT MERGED\n",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("PR #378 as MERGED" in error for error in errors)


def test_checker_does_not_borrow_unmerged_for_335_from_other_line(tmp_path):
    checker = _load_checker()
    text = (
        "PR #335 remains: OPEN / DRAFT / MERGED\n"
        "unrelated historical branch: UNMERGED\n"
        "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n"
    )

    assert checker._preserves_pr_335_unmerged(text) is False
    assert checker._preserves_pr_335_unmerged("PR #335 remains: OPEN / DRAFT / UNMERGED\n") is True

    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        ".agent_context/current_priority.md",
        _completed_state_text(include_unmerged=True).replace(
            "#335 OPEN / DRAFT / UNMERGED\n",
            "#335 OPEN / DRAFT / MERGED\nunrelated historical branch: UNMERGED\n",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("current priority does not preserve PR #335 as explicitly UNMERGED" in error for error in errors)


def test_checker_accepts_structured_multiline_335_unmerged_status():
    checker = _load_checker()
    positive = (
        "PR #335 remains:\n\n"
        "```text\n"
        "OPEN\n"
        "DRAFT\n"
        "UNMERGED\n"
        "head: befb69ef\n"
        "```\n"
    )
    negative = (
        "PR #335 remains:\n\n"
        "```text\n"
        "OPEN\n"
        "DRAFT\n"
        "MERGED\n"
        "```\n"
        "unrelated historical branch: UNMERGED\n"
    )

    assert checker._preserves_pr_335_unmerged(positive) is True
    assert checker._preserves_pr_335_unmerged(negative) is False


def test_checker_does_not_borrow_pending_not_authorized_for_335_from_other_line(
    tmp_path,
):
    checker = _load_checker()
    text = (
        "#335 reconstruction: AUTHORIZED\n"
        "unrelated lane: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n"
    )

    assert checker._preserves_pr_335_pending_not_authorized(text) is False
    assert checker._preserves_pr_335_pending_not_authorized(
        "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n"
    ) is True

    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        _completed_state_text(include_unmerged=True).replace(
            "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n",
            "PR #335 reconstruction: AUTHORIZED\n"
            "unrelated lane: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED" in error for error in errors)


def test_checker_detects_validated_baseline_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/status/DAILY_COMMAND_CENTER.md",
        _completed_state_text().replace(VALIDATED_BASELINE_SHA, "deadbeef"),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("exact validated_baseline_sha" in error for error in errors)


def test_checker_detects_missing_335_unmerged_in_priority(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        ".agent_context/current_priority.md",
        _completed_state_text(include_unmerged=False),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("current priority does not preserve PR #335 as explicitly UNMERGED" in error for error in errors)


def test_checker_detects_missing_335_pending_not_authorized(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        _completed_state_text(include_unmerged=True).replace(
            "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n",
            "",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED" in error for error in errors)


def test_checker_detects_unrelated_separate_owner_decision(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/todo/ACTIVE_TODO.md",
        _completed_state_text().replace(
            "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED\n",
            "PR #335 reconstruction: PENDING / NOT AUTHORIZED\n"
            "#368: SEPARATE OWNER DECISION\n",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("separate owner decision to #335 reconstruction" in error for error in errors)


def test_checker_still_requires_current_head_vs_validated_baseline_boundary(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    index_path = tmp_path / "docs/CANONICAL/00_INDEX.md"
    index_path.write_text(
        index_path.read_text(encoding="utf-8").replace(
            "current HEAD != immutable validated baseline\n", ""
        ),
        encoding="utf-8",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("current HEAD from immutable validated baseline" in error for error in errors)


def _copy_current_checked_surfaces(checker, destination: Path) -> None:
    for relative in checker.CHECKED_SURFACES:
        source = checker.ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _copy_post_405_ordering_surfaces(checker, destination: Path) -> None:
    for relative in checker.CURRENT_CHECKED_SURFACES:
        source = checker.ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def test_current_repository_operational_truth_is_consistent():
    checker = _load_checker()

    assert checker.check_operational_truth(checker.ROOT) == []


def test_current_cli_reports_master_roadmap_validation_truthfully(capsys):
    checker = _load_checker()

    assert checker.main() == 0
    output = capsys.readouterr().out

    assert "- docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md" in output
    assert (
        "future/archive material other than the explicitly validated master roadmap"
        in output
    )


def test_checker_rejects_pre_merge_388_lifecycle_after_closeout(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace(
            "#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED",
            "#388: IMMEDIATE / P1 PREREQUISITE",
            1,
        ),
        encoding="utf-8",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any(
        "AGENTS.md: current ordering does not preserve #388 COMPLETE -> #368 NEXT -> #387 AFTER #368"
        in error
        for error in errors
    )


@pytest.mark.parametrize(
    "target_relative",
    (
        ".agent_context/current_priority.md",
        "README.md",
        "START_HERE.md",
        "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md",
    ),
)
def test_current_repository_shape_rejects_corrupted_post_405_order(
    tmp_path, target_relative
):
    checker = _load_checker()
    _copy_current_checked_surfaces(checker, tmp_path)
    master = checker.ROOT / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master = tmp_path / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, copied_master)
    target = tmp_path / target_relative
    original = target.read_text(encoding="utf-8")
    corrupted = original.replace(
        "NEXT: canonical user-data root + logical store registry/migration detection",
        "NEXT: Google identity-only live proof",
        1,
    )
    assert corrupted != original
    target.write_text(corrupted, encoding="utf-8")

    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )

    assert any(
        str(target) in error
        and "current ordering does not preserve the active beta-readiness boundary"
        in error
        for error in errors
    )


def test_current_repository_shape_records_408_complete_and_lane_1_next():
    checker = _load_checker()

    for relative in (
        "README.md",
        "START_HERE.md",
        "AGENTS.md",
        ".agent_context/current_priority.md",
        "docs/status/CURRENT_WORK_STATUS.md",
        "docs/status/DAILY_COMMAND_CENTER.md",
        "docs/todo/ACTIVE_TODO.md",
        "docs/CANONICAL/00_INDEX.md",
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md",
    ):
        text = (checker.ROOT / relative).read_text(encoding="utf-8")
        active = checker._extract_post_405_active_block(text)
        assert active is not None
        normalized = " ".join(active.upper().split())
        assert checker.POST_406_COMPLETE_MARKER in normalized
        assert checker.POST_408_COMPLETE_MARKER in normalized
        assert "PR #412" in normalized
        assert "2592AD91" in normalized
        assert checker.LANE_1_AUTHORIZATION_MARKER in normalized
        assert (
            "NEXT: CANONICAL USER-DATA ROOT + LOGICAL STORE REGISTRY/MIGRATION DETECTION"
            in normalized
        )


def test_pre_406_sequence_is_historical_only():
    checker = _load_checker()
    current = (checker.ROOT / "README.md").read_text(encoding="utf-8")
    pre_406 = current.replace(
        "COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)\n"
        "COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)\n"
        "AUTHORIZED: durability implementation lane 1 only\n"
        "NEXT: canonical user-data root + logical store registry/migration detection\n"
        "THEN: separate exact-head review and merge decision\n"
        "THEN: separately authorized corruption-safe readers",
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation",
        1,
    )

    assert pre_406 != current
    assert checker._preserves_post_405_boundary(pre_406) is True
    assert (
        checker._preserves_post_405_boundary(
            pre_406,
            allow_pre_406_sequence=False,
            require_lane_1_sequence=True,
        )
        is False
    )


@pytest.mark.parametrize("retain_master_marker", (True, False))
def test_post_405_marker_prevents_coordinated_fallback_to_historical_order(
    tmp_path, retain_master_marker
):
    checker = _load_checker()
    _copy_current_checked_surfaces(checker, tmp_path)
    master = checker.ROOT / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master = tmp_path / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, copied_master)

    for relative in (
        "README.md",
        "START_HERE.md",
        "AGENTS.md",
        ".agent_context/current_priority.md",
        "docs/status/CURRENT_WORK_STATUS.md",
        "docs/status/DAILY_COMMAND_CENTER.md",
        "docs/todo/ACTIVE_TODO.md",
        "docs/CANONICAL/00_INDEX.md",
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md",
    ):
        target = tmp_path / relative
        original = target.read_text(encoding="utf-8")
        corrupted = original.replace(
            "NEXT: #408 durability/state-ownership decision",
            "NEXT: Google identity-only live proof",
            1,
        )
        corrupted = corrupted.replace(
            "df2df490083511f480b653c0960fbe7a6e6abfe8",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            1,
        )
        if (
            not retain_master_marker
            or relative != "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
        ):
            corrupted = corrupted.replace(
                "BETA_READINESS_SEQUENCE_V1: ACTIVE\n", "", 1
            )
        assert corrupted != original
        target.write_text(corrupted, encoding="utf-8")

    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )

    assert any(
        "current ordering does not preserve the active beta-readiness boundary"
        in error
        for error in errors
    )


def test_post_405_mode_survives_normal_sync_start_sha_update(tmp_path):
    checker = _load_checker()
    _copy_current_checked_surfaces(checker, tmp_path)
    master = checker.ROOT / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master = tmp_path / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, copied_master)

    for relative in (
        "README.md",
        "START_HERE.md",
        "AGENTS.md",
        ".agent_context/current_priority.md",
        "docs/status/CURRENT_WORK_STATUS.md",
        "docs/status/DAILY_COMMAND_CENTER.md",
        "docs/todo/ACTIVE_TODO.md",
        "docs/CANONICAL/00_INDEX.md",
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md",
    ):
        target = tmp_path / relative
        updated = target.read_text(encoding="utf-8").replace(
            "df2df490083511f480b653c0960fbe7a6e6abfe8",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            1,
        )
        target.write_text(updated, encoding="utf-8")

    assert (
        checker.check_operational_truth(
            tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
        )
        == []
    )


def test_post_405_mode_rejects_one_current_surface_with_different_sync_sha(tmp_path):
    checker = _load_checker()
    _copy_post_405_ordering_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    target.write_text(
        target.read_text(encoding="utf-8").replace(
            "df2df490083511f480b653c0960fbe7a6e6abfe8",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            1,
        ),
        encoding="utf-8",
    )

    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )

    assert any("post-#405 sync-start SHA mismatch" in error for error in errors)


def test_post_405_mode_rejects_two_groups_of_current_sync_shas(tmp_path):
    checker = _load_checker()
    _copy_post_405_ordering_surfaces(checker, tmp_path)
    for relative in checker.CURRENT_CHECKED_SURFACES[:5]:
        target = tmp_path / relative
        target.write_text(
            target.read_text(encoding="utf-8").replace(
                "df2df490083511f480b653c0960fbe7a6e6abfe8",
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                1,
            ),
            encoding="utf-8",
        )

    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )

    assert any("post-#405 sync-start SHA mismatch" in error for error in errors)


def test_post_405_mode_ignores_historical_different_sync_sha(tmp_path):
    checker = _load_checker()
    _copy_post_405_ordering_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    with target.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n## Historical reconciliation\n"
            "verified main at sync start: cccccccccccccccccccccccccccccccccccccccc\n"
        )

    assert (
        checker.check_operational_truth(
            tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
        )
        == []
    )


_ACTIVE_CLOSEOUT_SNIPPETS = {
    "agents": (
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package "
        "PR #366.\n"
    ),
    "priority": (
        "## Post-Wave-C Documentation Closeout — PR #366 Truth-Hygiene Contract\n"
    ),
    "work_status": (
        "POST-WAVE-C DOCUMENTATION CLOSEOUT\n"
        "TRUTH-HYGIENE CONTRACT: PR #366\n"
    ),
    "command_center": (
        "Post-Wave-C documentation closeout — truth-hygiene contract PR #366.\n"
    ),
    "active_todo": (
        "### Post-Wave-C documentation closeout\n"
        "truth-hygiene contract package: PR #366\n"
    ),
    "canonical_index": (
        "Current gate: post-Wave-C documentation closeout — truth-hygiene contract "
        "package PR #366.\n"
    ),
    "roadmap": (
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package "
        "PR #366.\n"
    ),
}


def _replace_completed_closeout_with_active(checker, root, names):
    relative_by_name = {
        "agents": "AGENTS.md",
        "priority": ".agent_context/current_priority.md",
        "work_status": "docs/status/CURRENT_WORK_STATUS.md",
        "command_center": "docs/status/DAILY_COMMAND_CENTER.md",
        "active_todo": "docs/todo/ACTIVE_TODO.md",
        "canonical_index": "docs/CANONICAL/00_INDEX.md",
        "roadmap": "docs/CANONICAL/07_ROADMAP_TRUTH.md",
    }
    for name in names:
        target = root / relative_by_name[name]
        text = checker.POST_WAVE_C_COMPLETE_MARKER.sub(
            "", target.read_text(encoding="utf-8")
        )
        target.write_text(_ACTIVE_CLOSEOUT_SNIPPETS[name] + text, encoding="utf-8")


def test_post_405_mode_requires_all_completed_closeout_surfaces(tmp_path):
    checker = _load_checker()
    _copy_current_checked_surfaces(checker, tmp_path)
    master = checker.ROOT / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master = tmp_path / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, copied_master)

    assert (
        checker.check_operational_truth(
            tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
        )
        == []
    )

    _replace_completed_closeout_with_active(checker, tmp_path, checker.LANE_PATTERNS)
    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )

    assert sum("requires completed PR #366 closeout state" in error for error in errors) == 7


def test_post_405_mode_rejects_one_active_or_missing_completed_surface(tmp_path):
    checker = _load_checker()
    _copy_current_checked_surfaces(checker, tmp_path)
    master = checker.ROOT / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master = tmp_path / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, copied_master)

    _replace_completed_closeout_with_active(checker, tmp_path, ("agents",))
    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )
    assert any(
        "AGENTS.md: current post-#405 lifecycle requires completed PR #366 closeout state"
        in error
        for error in errors
    )

    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace(
            _ACTIVE_CLOSEOUT_SNIPPETS["agents"], "", 1
        ),
        encoding="utf-8",
    )
    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )
    assert any(
        "AGENTS.md: current post-#405 lifecycle requires completed PR #366 closeout state"
        in error
        for error in errors
    )


def test_post_405_mode_preserves_historical_active_closeout_wording(tmp_path):
    checker = _load_checker()
    _copy_current_checked_surfaces(checker, tmp_path)
    master = checker.ROOT / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master = tmp_path / "docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md"
    copied_master.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master, copied_master)
    agents = tmp_path / "AGENTS.md"
    with agents.open("a", encoding="utf-8") as stream:
        stream.write("\n## Historical closeout\n" + _ACTIVE_CLOSEOUT_SNIPPETS["agents"])

    assert (
        checker.check_operational_truth(
            tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
        )
        == []
    )


def test_post_394_boundary_accepts_new_state_and_rejects_obsolete_directives():
    checker = _load_checker()
    current = (
        "#388 COMPLETE\n"
        "#368 COMPLETE\n"
        "#387 COMPLETE / DOCS-ONLY\n"
        "#393 COMPLETE / EXACT-HEAD PROOF POLICY\n"
        "#394 GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED\n"
        "691a397d14e93c1e0607a73de2ab54b9bbfc3cc2\n"
        "PR #335 OPEN / DRAFT / UNMERGED / UNTOUCHED\n"
        "PR #335 implementation path: SUPERSEDED BY MERGED PR #394\n"
        "NEXT: Google identity-only live proof\n"
        "NOT YET AUTHORIZED: Google Tasks READ\n"
    )

    assert checker._preserves_post_394_boundary(current) is True

    obsolete_variants = (
        current.replace("#368 COMPLETE", "#368 NEXT BOUNDED TECHNICAL LANE"),
        current.replace("#387 COMPLETE / DOCS-ONLY", "#387 AFTER #368 / DOCS-ONLY"),
        current.replace(
            "PR #335 implementation path: SUPERSEDED BY MERGED PR #394",
            "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED",
        ),
    )
    assert all(
        checker._preserves_post_394_boundary(candidate) is False
        for candidate in obsolete_variants
    )


def test_post_405_boundary_accepts_406_first_order_and_rejects_google_reactivation():
    checker = _load_checker()
    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: df2df490083511f480b653c0960fbe7a6e6abfe8\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "df2df490083511f480b653c0960fbe7a6e6abfe8",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            )
        )
        is True
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "verified main at sync start: "
                "df2df490083511f480b653c0960fbe7a6e6abfe8\n",
                "",
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "verified main at sync start: "
                "df2df490083511f480b653c0960fbe7a6e6abfe8\n",
                "verified main at sync start: "
                "df2df490083511f480b653c0960fbe7a6e6abfe8\n"
                "verified main at sync start: "
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "THEN: #408 durability/state-ownership decision\n"
                "THEN: evidence-authorized durability implementation\n",
                "THEN: evidence-authorized durability implementation\n",
            )
        )
        is False
    )


def test_post_405_boundary_requires_one_canonical_active_next_directive():
    checker = _load_checker()
    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )
    canonical_next = "NEXT: #406 governed-memory ID collision correctness\n"

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                canonical_next,
                "NEXT: #408 durability/state-ownership decision\n" + canonical_next,
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                canonical_next, "NEXT: Google identity-only live proof\n" + canonical_next
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(canonical_next, canonical_next + canonical_next)
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(current.replace(canonical_next, ""))
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current + "\n## Historical ordering\nNEXT: Google identity-only live proof\n"
        )
        is True
    )


@pytest.mark.parametrize(
    "competing_directive",
    (
        "NEXT: Google identity-only live proof",
        "NEXT: #408 durability/state-ownership decision",
        "THEN: Google identity-only live proof",
    ),
)
def test_post_405_boundary_rejects_directives_before_lifecycle_marker(
    competing_directive,
):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )
    corrupted = current.replace(
        "BETA_READINESS_SEQUENCE_V1: ACTIVE",
        f"{competing_directive}\nBETA_READINESS_SEQUENCE_V1: ACTIVE",
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert checker._preserves_post_405_boundary(corrupted) is False


def test_post_405_boundary_checks_pre_marker_contradiction_but_excludes_history():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )
    contradiction = current.replace(
        "BETA_READINESS_SEQUENCE_V1: ACTIVE",
        "Google/provider expansion will resume.\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE",
    )
    historical_before = (
        "## Historical prior order\n"
        "NEXT: Google identity-only live proof\n"
        "Google/provider expansion is active.\n"
        + current
    )
    historical_after = (
        current
        + "\n## Historical later order\n"
        "THEN: Google identity-only live proof\n"
        "Google/provider expansion is active.\n"
    )

    assert checker._preserves_post_405_boundary(contradiction) is False
    assert checker._preserves_post_405_boundary(historical_before) is True
    assert checker._preserves_post_405_boundary(historical_after) is True


def test_post_405_boundary_includes_subordinate_headings():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(
            current + "\n### Current implementation update\nNo ordering change.\n"
        )
        is True
    )
    assert (
        checker._preserves_post_405_boundary(
            current
            + "\n### Current implementation update\n"
            "Google/provider expansion is active.\n"
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current
            + "\n### Current implementation update\n"
            "NEXT: Google identity-only live proof\n"
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current
            + "\n### Current implementation update\n"
            "THEN: Google identity-only live proof\n"
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current
            + "\n## Historical ordering\n"
            "Google/provider expansion is active.\n"
            "NEXT: Google identity-only live proof\n"
        )
        is True
    )


def test_post_405_boundary_requires_exactly_one_active_lifecycle_declaration():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "BETA_READINESS_SEQUENCE_V1: ACTIVE\n",
                "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
                "BETA_READINESS_SEQUENCE_V1: INACTIVE\n",
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "BETA_READINESS_SEQUENCE_V1: ACTIVE\n",
                "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
                "BETA_READINESS_SEQUENCE_V1: ACTIVE\n",
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                "BETA_READINESS_SEQUENCE_V1: ACTIVE",
                "BETA_READINESS_SEQUENCE_V1: INACTIVE",
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current
            + "\n## Historical ordering\n"
            "BETA_READINESS_SEQUENCE_V1: INACTIVE\n"
        )
        is True
    )


def test_post_405_boundary_rejects_duplicate_non_historical_lifecycle_blocks():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )
    identical = current + "\n" + current
    conflicting_prefix = (
        "\n## Current emergency override\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert checker._preserves_post_405_boundary(identical) is False
    assert (
        checker._preserves_post_405_boundary(
            current
            + conflicting_prefix
            + "Google/provider expansion is active.\n"
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current + conflicting_prefix + "NEXT: Google identity-only live proof\n"
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current + conflicting_prefix + "THEN: Google identity-only live proof\n"
        )
        is False
    )


@pytest.mark.parametrize(
    "prefix, state",
    (
        ("- ", "INACTIVE"),
        ("* ", "INACTIVE"),
        ("+ ", "INACTIVE"),
        ("> ", "INACTIVE"),
        ("> - ", "INACTIVE"),
        ("> 1. ", "INACTIVE"),
        ("1. ", "INACTIVE"),
        ("> * ", "ACTIVE"),
    ),
)
def test_post_405_boundary_rejects_prefixed_conflicting_lifecycle_declarations(
    prefix, state
):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(
            current + f"{prefix}BETA_READINESS_SEQUENCE_V1: {state}\n"
        )
        is False
    )


@pytest.mark.parametrize("prefix", ("- ", "> ", "> - ", "1. ", "> 1. "))
def test_post_405_boundary_accepts_one_prefixed_active_lifecycle(prefix):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        f"{prefix}BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "- Harmless current note.\n"
        "> Harmless current explanation.\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True


def test_post_405_boundary_rejects_only_prefixed_inactive_lifecycle():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "> - BETA_READINESS_SEQUENCE_V1: INACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is False


def test_post_405_boundary_excludes_historical_prefixed_lifecycle_declarations():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
        "## Historical ordering\n"
        "- BETA_READINESS_SEQUENCE_V1: INACTIVE\n"
        "> BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "### Historical nested ordering\n"
        "> 1. BETA_READINESS_SEQUENCE_V1: RETIRED\n"
    )

    assert checker._preserves_post_405_boundary(current) is True


def test_post_405_boundary_excludes_explicitly_historical_lifecycle_blocks():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )
    historical = (
        "\n## Historical ordering\n"
        "BETA_READINESS_SEQUENCE_V1: INACTIVE\n"
        "Google/provider expansion is active.\n"
        "NEXT: Google identity-only live proof\n"
    )
    nested_historical = (
        "\n### Historical emergency override\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "#### Preserved details\n"
        "BETA_READINESS_SEQUENCE_V1: INACTIVE\n"
        "THEN: Google identity-only live proof\n"
    )

    assert checker._preserves_post_405_boundary(current + historical) is True
    assert (
        checker._preserves_post_405_boundary(
            current + historical + nested_historical
        )
        is True
    )


def test_post_405_boundary_requires_exact_active_directive_sequence():
    checker = _load_checker()
    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )
    durability = "THEN: evidence-authorized durability implementation\n"
    translation = "THEN: bounded product-translation/readiness pass\n"

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                durability,
                durability + "THEN: Google identity-only live proof\n",
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(durability, durability + "THEN: #409 repo integrity\n")
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(durability, durability + durability)
        )
        is False
    )
    assert checker._preserves_post_405_boundary(current.replace(durability, "")) is False
    assert (
        checker._preserves_post_405_boundary(
            current.replace(durability + translation, translation + durability)
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current + "\n## Historical ordering\nTHEN: Google identity-only live proof\n"
        )
        is True
    )


@pytest.mark.parametrize(
    "prefix, directive",
    (
        ("- ", "NEXT: Google identity-only live proof"),
        ("* ", "NEXT: Google identity-only live proof"),
        ("+ ", "THEN: Google identity-only live proof"),
        ("> ", "NEXT: Google identity-only live proof"),
        ("> - ", "NEXT: Google identity-only live proof"),
        ("> * ", "THEN: Google identity-only live proof"),
        ("1. ", "NEXT: Google identity-only live proof"),
    ),
)
def test_post_405_boundary_rejects_markdown_prefixed_competing_directives(
    prefix, directive
):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert (
        checker._preserves_post_405_boundary(current + f"{prefix}{directive}\n")
        is False
    )


@pytest.mark.parametrize(
    "directive",
    (
        "- **NEXT:** Google identity-only live proof",
        "> **THEN:** Google identity-only live proof",
        "> - **NEXT:** Google identity-only live proof",
    ),
)
def test_post_405_boundary_rejects_bold_markdown_competing_directives(directive):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert checker._preserves_post_405_boundary(current + directive + "\n") is False


@pytest.mark.parametrize(
    "directive",
    (
        "***NEXT: Google identity-only live proof***",
        "> - **_NEXT: Google identity-only live proof_**",
        "**NEXT: Google identity-only live proof**",
        "__THEN: Google identity-only live proof__",
        "`NEXT: Google identity-only live proof`",
        "- **NEXT: Google identity-only live proof**",
    ),
)
def test_post_405_boundary_rejects_whole_line_formatted_competing_directives(
    directive,
):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    assert checker._preserves_post_405_boundary(current + directive + "\n") is False


@pytest.mark.parametrize("delimiter", ("**", "__", "`", "***", "___"))
def test_post_405_boundary_accepts_consistently_formatted_directive_sequence(delimiter):
    checker = _load_checker()

    def formatted(value):
        return f"{delimiter}{value}{delimiter}\n"

    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        + formatted("NEXT: #406 governed-memory ID collision correctness")
        + formatted("THEN: #408 durability/state-ownership decision")
        + formatted("THEN: evidence-authorized durability implementation")
        + formatted("THEN: bounded product-translation/readiness pass")
        + formatted("THEN: clean Windows operator proof")
        + formatted("THEN: frozen-SHA full beta acceptance")
        + formatted("THEN: private-beta candidacy/distribution decision")
        + "**Harmless emphasized prose.**\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
        "## Historical ordering\n"
        "**NEXT: Google identity-only live proof**\n"
    )

    assert checker._preserves_post_405_boundary(current) is True


def test_post_405_boundary_accepts_consistently_bold_markdown_directive_sequence():
    checker = _load_checker()
    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "- **NEXT:** #406 governed-memory ID collision correctness\n"
        "- **THEN:** #408 durability/state-ownership decision\n"
        "- **THEN:** evidence-authorized durability implementation\n"
        "- **THEN:** bounded product-translation/readiness pass\n"
        "- **THEN:** clean Windows operator proof\n"
        "- **THEN:** frozen-SHA full beta acceptance\n"
        "- **THEN:** private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True


@pytest.mark.parametrize("prefix", ("- ", "> ", "> - ", "1. "))
def test_post_405_boundary_accepts_consistently_markdown_prefixed_sequence(prefix):
    checker = _load_checker()
    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        f"{prefix}NEXT: #406 governed-memory ID collision correctness\n"
        f"{prefix}THEN: #408 durability/state-ownership decision\n"
        f"{prefix}THEN: evidence-authorized durability implementation\n"
        f"{prefix}THEN: bounded product-translation/readiness pass\n"
        f"{prefix}THEN: clean Windows operator proof\n"
        f"{prefix}THEN: frozen-SHA full beta acceptance\n"
        f"{prefix}THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True


def test_post_405_boundary_ignores_historical_markdown_directives_and_harmless_markup():
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "### Current sequence details\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "- Harmless current note.\n"
        "> Harmless current explanation.\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
        "## Historical ordering\n"
        "- NEXT: Google identity-only live proof\n"
        "> THEN: resume provider expansion\n"
    )

    assert checker._preserves_post_405_boundary(current) is True


@pytest.mark.parametrize(
    "content",
    (
        "---\nHarmless current explanation.\n",
        "---\nGoogle/provider expansion is active.\n",
        "---\nNEXT: Google identity-only live proof\n",
        "---\nBETA_READINESS_SEQUENCE_V1: INACTIVE\n",
    ),
)
def test_post_405_boundary_keeps_thematic_break_content_in_active_section(content):
    checker = _load_checker()
    current = (
        "## Current post-#405 beta-readiness order\n"
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    expected = content == "---\nHarmless current explanation.\n"
    assert checker._preserves_post_405_boundary(current + content) is expected
    assert (
        checker._preserves_post_405_boundary(
            current
            + content
            + "## Historical ordering\n"
            + "Google/provider expansion is active.\n"
        )
        is expected
    )


def test_current_lifecycle_rejects_coordinated_legacy_active_lane(tmp_path):
    checker = _load_checker()
    _post_wave_c_active_fixture(tmp_path)

    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )

    assert errors
    assert any("active beta-readiness boundary" in error for error in errors)


@pytest.mark.parametrize(
    "category",
    (
        "Google/provider expansion",
        "Operational Continuity implementation",
        "New capabilities",
        "Voice expansion",
        "Broader UI work",
        "Other feature expansion",
    ),
)
def test_post_405_boundary_rejects_each_reactivated_feature_category(category):
    checker = _load_checker()
    current = (
        "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
        "verified main at sync start: df2df490083511f480b653c0960fbe7a6e6abfe8\n"
        "#397 through #405: COMPLETE / MERGED\n"
        "NEXT: #406 governed-memory ID collision correctness\n"
        "THEN: #408 durability/state-ownership decision\n"
        "THEN: evidence-authorized durability implementation\n"
        "THEN: bounded product-translation/readiness pass\n"
        "THEN: clean Windows operator proof\n"
        "THEN: frozen-SHA full beta acceptance\n"
        "THEN: private-beta candidacy/distribution decision\n"
        "Google/provider expansion remains paused.\n"
        "Operational Continuity implementation remains paused.\n"
        "New capabilities remain paused.\n"
        "Voice expansion remains paused.\n"
        "Broader UI work remains paused.\n"
        "Other feature expansion remains paused.\n"
    )

    assert checker._preserves_post_405_boundary(current) is True
    paused_phrase = (
        f"{category} remain paused."
        if category == "New capabilities"
        else f"{category} remains paused."
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                paused_phrase, f"{category} is active.\n{paused_phrase}"
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                paused_phrase, f"{category} is authorized.\n{paused_phrase}"
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                paused_phrase, f"{paused_phrase}\n{category} is no longer paused."
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                paused_phrase, f"{paused_phrase}\n{category} does not remain paused."
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                paused_phrase, f"{paused_phrase}\n{category} do not remain paused."
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(
                paused_phrase, f"{paused_phrase}\n{category} will resume."
            )
        )
        is False
    )
    assert (
        checker._preserves_post_405_boundary(current + f"{category} is active.\n")
        is False
    )
    assert (
        checker._preserves_post_405_boundary(
            current + f"\n## Historical feature state\n{category} is active.\n"
        )
        is True
    )
    assert (
        checker._preserves_post_405_boundary(
            current.replace(paused_phrase, f"{category} is active.")
        )
        is False
    )


@pytest.mark.parametrize("position", ("before", "after", "nested"))
def test_current_closeout_cannot_be_satisfied_by_historical_markers(tmp_path, position):
    checker = _load_checker()
    _copy_post_405_ordering_surfaces(checker, tmp_path)
    _replace_completed_closeout_with_active(checker, tmp_path, checker.LANE_PATTERNS)
    for relative in checker.CHECKED_SURFACES:
        target = tmp_path / relative
        text = target.read_text(encoding="utf-8")
        historical = (
            "\n## Historical closeout evidence\n"
            "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE\n"
        )
        if position == "before":
            text = historical + "\n## Current guidance\n" + text
        elif position == "nested":
            text += "\n## Historical evidence\n### Closeout\n" + historical.split("\n", 2)[2]
        else:
            text += historical
        target.write_text(text, encoding="utf-8")
    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )
    assert sum("requires completed PR #366 closeout state" in error for error in errors) == 7


@pytest.mark.parametrize("opening, closing", (("***", "***"), ("**_", "_**"), ("___", "___"), ("`**", "**`")))
@pytest.mark.parametrize("competing", (False, True))
def test_full_checker_validates_nested_directive_labels(tmp_path, opening, closing, competing):
    checker = _load_checker()
    _copy_post_405_ordering_surfaces(checker, tmp_path)
    target = tmp_path / "README.md"
    text = target.read_text(encoding="utf-8")
    if competing:
        text = text.replace(
            "BETA_READINESS_SEQUENCE_V1: ACTIVE\n",
            "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
            + f"> - {opening}NEXT:{closing} Google identity-only live proof\n",
            1,
        )
    else:
        for label in ("NEXT:", "THEN:"):
            text = text.replace(label, f"{opening}{label}{closing}")
    target.write_text(text, encoding="utf-8")
    errors = checker.check_operational_truth(
        tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION
    )
    if competing:
        assert any("README.md: current ordering does not preserve" in error for error in errors)
    else:
        assert errors == []


@pytest.mark.parametrize("case", ("containers", "historical_heading", "adjacent", "parent_section"))
@pytest.mark.parametrize("conflict", (True, False))
def test_full_checker_structure_corrections(tmp_path, case, conflict):
    checker = _load_checker()
    _copy_post_405_ordering_surfaces(checker, tmp_path)
    target = tmp_path / "AGENTS.md"
    text = target.read_text(encoding="utf-8")
    marker = "BETA_READINESS_SEQUENCE_V1: ACTIVE\n"
    bad = "NEXT: Google identity-only live proof\n"
    if case == "containers":
        if conflict:
            text = text.replace(marker, marker + "- > ***NEXT:*** Google identity-only live proof\n", 1)
        else:
            for label in ("NEXT:", "THEN:"):
                text = text.replace(label, f"- > 1. > ***{label}***")
    elif case == "adjacent":
        if conflict:
            text = text.replace(marker, marker + "**NEXT:**Google identity-only live proof\n", 1)
        else:
            for label in ("NEXT:", "THEN:"):
                text = text.replace(label + " ", f"**{label}**")
    elif case == "parent_section":
        prefix = bad if conflict else "Harmless parent guidance.\n"
        text = text.replace(marker, prefix + "### Current sequence details\n" + marker, 1)
    else:
        if conflict:
            text = text.replace("POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE", "POST-WAVE-C DOCUMENTATION CLOSEOUT: ACTIVE", 1)
        end = text.index("## Post-Wave-C Current Development State")
        text = text[:end] + (
            "### **Historical closeout evidence**\n"
            "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE\n"
            + ("" if conflict else "BETA_READINESS_SEQUENCE_V1: INACTIVE\n") + bad
        ) + text[end:]
    target.write_text(text, encoding="utf-8")
    errors = checker.check_operational_truth(tmp_path, lifecycle_generation=checker.CURRENT_LIFECYCLE_GENERATION)
    if conflict:
        expected = "requires completed PR #366 closeout state" if case == "historical_heading" else "current ordering does not preserve"
        assert any(expected in error for error in errors)
    else:
        assert errors == []


@pytest.mark.parametrize("prefix", ("> - ", "- > ", "> 1. > - "))
def test_nested_containers_preserve_plain_payload_markdown(prefix):
    checker = _load_checker()
    assert checker._normalize_post_405_structured_line(prefix + "NEXT:**payload**") == "NEXT: **payload**"
    assert checker._normalize_post_405_structured_line(prefix + "**NEXT:* payload") == "**NEXT:* payload"
