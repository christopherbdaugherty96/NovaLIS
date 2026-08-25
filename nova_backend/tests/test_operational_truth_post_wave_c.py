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
        "Wave C is COMPLETE / MERGED / VALIDATED. The current active lane is "
        "**PR #366 post-Wave-C truth hygiene — documentation/current-truth only**.\n",
    )
    _write(
        root,
        ".agent_context/current_priority.md",
        "## Post-Wave-C Truth Hygiene — PR #366 Active — 2026-08-25\n"
        "#335 OPEN / DRAFT / UNMERGED\n",
    )
    _write(
        root,
        "docs/status/CURRENT_WORK_STATUS.md",
        "## Current Development Lane\n```text\nPOST-WAVE-C TRUTH HYGIENE\n"
        "STATUS: ACTIVE / DRAFT PR #366\n```\n",
    )
    _write(
        root,
        "docs/status/DAILY_COMMAND_CENTER.md",
        "CURRENT PLANNING LANE:\n"
        "  Post-Wave-C truth hygiene — ACTIVE / DRAFT PR #366.\n",
    )
    _write(
        root,
        "docs/todo/ACTIVE_TODO.md",
        "## Active Now\n### Post-Wave-C truth hygiene — active\n",
    )
    _write(
        root,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n"
        "**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        "Current active lane: **PR #366 post-Wave-C truth hygiene — OPEN / DRAFT / "
        "documentation-current-truth only**.\n",
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
        "Wave C is COMPLETE / MERGED / VALIDATED. The current active lane is the "
        "documentation-only post-Wave-C truth-hygiene pass in draft PR #366.\n"
        "#335 OPEN / DRAFT / UNMERGED\n",
    )


def test_checker_accepts_post_wave_c_truth_hygiene_lane(tmp_path):
    checker = _load_checker()
    _post_wave_c_fixture(tmp_path)

    assert checker.check_operational_truth(tmp_path) == []
    assert checker.POST_WAVE_C_LANE == "POST_WAVE_C_TRUTH_HYGIENE"


def test_checker_detects_post_wave_c_to_legacy_lane_drift(tmp_path):
    checker = _load_checker()
    _post_wave_c_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "Current active stabilization lane: C\n#335 OPEN / DRAFT / UNMERGED\n",
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any("lane mismatch" in error for error in errors)
    assert any("roadmap=C" in error for error in errors)
