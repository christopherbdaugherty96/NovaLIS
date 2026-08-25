from __future__ import annotations

import importlib.util
from pathlib import Path


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


def _post_wave_c_fixture(root: Path) -> None:
    _write(
        root,
        "AGENTS.md",
        "## Post-Wave-C Current Development State — 2026-08-25\n"
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package "
        "PR #366. #335 remains next/not authorized until closeout is reviewed and merged.\n",
    )
    _write(
        root,
        ".agent_context/current_priority.md",
        "## Post-Wave-C Documentation Closeout — PR #366 Truth-Hygiene Contract — 2026-08-25\n"
        "#335 OPEN / DRAFT / UNMERGED\n",
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
        "package PR #366**.\n",
    )
    _write(
        root,
        "docs/CANONICAL/03_GOVERNANCE_TRUTH.md",
        "Governed capability plane\n"
        "Local operator / administrative plane\n"
        "Bounded agent / routine plane\n"
        "nova_backend/src/api/connections_api.py\n",
    )
    _write(
        root,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package PR #366. "
        "PR #335 reconstruction remains next but not authorized until documentation "
        "closeout is reviewed and merged.\n"
        "#335 OPEN / DRAFT / UNMERGED\n",
    )


def test_checker_accepts_merge_safe_documentation_closeout_gate(tmp_path):
    checker = _load_checker()
    _post_wave_c_fixture(tmp_path)

    assert checker.check_operational_truth(tmp_path) == []
    assert checker.POST_WAVE_C_LANE == "POST_WAVE_C_DOCUMENTATION_CLOSEOUT"


def test_roadmap_binds_truth_hygiene_contract_pr():
    checker = _load_checker()
    text = (
        "Post-Wave-C documentation closeout gate: truth-hygiene contract package PR #366. "
        "PR #335 reconstruction remains next but not authorized until closeout is merged.\n"
    )

    assert checker._extract_lane("roadmap", text) == (
        "POST_WAVE_C_DOCUMENTATION_CLOSEOUT:PR#366"
    )


def test_checker_detects_post_wave_c_to_legacy_lane_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "Current active stabilization lane: C\n#335 OPEN / DRAFT / UNMERGED\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("gate mismatch" in error for error in errors)
    assert any("roadmap=C" in error for error in errors)


def test_checker_detects_post_wave_c_pr_identity_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n"
        "**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        "Current gate: **post-Wave-C documentation closeout — truth-hygiene contract "
        "package PR #999**.\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("gate mismatch" in error for error in errors)
    assert any(
        "canonical_index=POST_WAVE_C_DOCUMENTATION_CLOSEOUT:PR#999" in error
        for error in errors
    )
