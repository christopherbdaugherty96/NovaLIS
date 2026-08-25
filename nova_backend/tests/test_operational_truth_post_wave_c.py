from __future__ import annotations

import importlib.util
from pathlib import Path


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
            "#335 reconstruction: NEXT / NOT AUTHORIZED",
            "next decision: separate owner authorization for #335 reconstruction/reconciliation",
        ]
    )
    return "\n".join(lines) + "\n"


def _post_wave_c_complete_fixture(root: Path) -> None:
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
        "#335 reconstruction: NEXT / NOT AUTHORIZED\n"
        "next decision: separate owner authorization for #335 reconstruction/reconciliation\n"
    )

    assert checker._extract_lane("priority", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE:PR#366"
    )


def test_completed_state_ignores_nearby_365_provenance_collision():
    checker = _load_checker()
    text = (
        "POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE\n"
        "PR #365 merge / PR #366 branch base: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c\n"
        "PR #366 truth-hygiene package: MERGED\n"
        "PR #378 narration/front-door package: MERGED / VERIFIED\n"
        f"validated_baseline_sha: {VALIDATED_BASELINE_SHA}\n"
        "#335 reconstruction: NEXT / NOT AUTHORIZED\n"
        "next decision: separate owner authorization for #335 reconstruction/reconciliation\n"
    )

    assert checker._extract_truth_hygiene_pr(text) == "366"
    assert checker._extract_lane("active_todo", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE:PR#366"
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
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE:PR#366"
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
        "#335 reconstruction: NEXT / NOT AUTHORIZED\n"
        "next decision: separate owner authorization for #335 reconstruction/reconciliation\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("gate mismatch" in error for error in errors)
    assert any(
        "canonical_index=POST_WAVE_C_DOCUMENTATION_CLOSEOUT_COMPLETE:PR#999"
        in error
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


def test_checker_detects_missing_335_next_not_authorized(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        _completed_state_text(include_unmerged=True).replace(
            "#335 reconstruction: NEXT / NOT AUTHORIZED\n", ""
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("NEXT / NOT AUTHORIZED" in error for error in errors)


def test_checker_detects_missing_separate_owner_authorization_decision(tmp_path):
    checker = _load_checker()
    _post_wave_c_complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/todo/ACTIVE_TODO.md",
        _completed_state_text().replace(
            "next decision: separate owner authorization for #335 reconstruction/reconciliation\n",
            "",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("separate owner authorization decision" in error for error in errors)


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
