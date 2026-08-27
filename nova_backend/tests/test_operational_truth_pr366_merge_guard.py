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
            "#388: IMMEDIATE / P1 PREREQUISITE",
            "#368: NEXT BOUNDED TECHNICAL LANE AFTER #388",
            "#387: AFTER #368 / DOCS-ONLY",
            "PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED",
        ]
    )
    return "\n".join(lines) + "\n"


def _complete_fixture(root: Path) -> None:
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
        _completed_state_text(include_unmerged=True),
    )


def test_pr366_merged_state_is_target_bound_and_rejects_negation():
    checker = _load_checker()

    assert checker._preserves_merged_pr(
        "truth-hygiene provenance: PR #366 MERGED\n", 366
    ) is True
    assert checker._preserves_merged_pr(
        "truth-hygiene provenance: PR #366 NOT MERGED\n", 366
    ) is False
    assert checker._preserves_merged_pr(
        "truth-hygiene provenance: PR #366 UNMERGED\n", 366
    ) is False
    assert checker._preserves_merged_pr(
        "PR #365 MERGED\ntruth-hygiene provenance: PR #366 OPEN / DRAFT\n", 366
    ) is False


def test_completed_closeout_requires_pr366_merged_provenance(tmp_path):
    checker = _load_checker()
    _complete_fixture(tmp_path)
    _write(
        tmp_path,
        "docs/status/CURRENT_WORK_STATUS.md",
        _completed_state_text().replace(
            "truth-hygiene provenance: PR #366 MERGED\n",
            "truth-hygiene provenance: PR #366 UNMERGED\n",
        ),
    )

    errors = checker.check_operational_truth(tmp_path)

    assert any(
        "PR #366 as MERGED truth-hygiene provenance" in error for error in errors
    )
