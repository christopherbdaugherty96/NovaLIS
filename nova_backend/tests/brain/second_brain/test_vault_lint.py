"""Tests for vault health/lint report.

Invariants under test:
  1. lint_vault produces a VaultHealthReport without modifying files
  2. Duplicate IDs are detected
  3. Missing frontmatter is reported
  4. Broken wikilinks are reported
  5. Missing relationship targets are reported
  6. Schema errors in frontmatter are reported
  7. VaultHealthReport.non_authorizing is always True
  8. Report is read-only — vault files unchanged after lint
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from src.brain.second_brain.vault_lint import (
    FindingSeverity,
    VaultHealthReport,
    lint_vault,
)

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "second_brain"


def _copy_fixtures_to_tmpdir() -> Path:
    tmp = Path(tempfile.mkdtemp())
    for f in _FIXTURES.glob("*.md"):
        shutil.copy2(f, tmp / f.name)
    return tmp


def _record_file_state(directory: Path) -> dict[str, tuple[int, int]]:
    state: dict[str, tuple[int, int]] = {}
    for f in sorted(directory.rglob("*.md")):
        s = os.stat(f)
        state[str(f)] = (s.st_mtime_ns, s.st_size)
    return state


# -------------------------------------------------------------------
# Basic lint
# -------------------------------------------------------------------

class TestBasicLint:
    def test_lint_fixture_vault(self):
        tmp = _copy_fixtures_to_tmpdir()
        try:
            report = lint_vault(tmp)
            assert isinstance(report, VaultHealthReport)
            assert report.total_notes >= 4
            assert report.with_frontmatter >= 3
        finally:
            shutil.rmtree(tmp)

    def test_nonexistent_vault_root(self):
        report = lint_vault(Path("/nonexistent/vault"))
        assert report.total_notes == 0
        assert report.error_count >= 1

    def test_empty_directory(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            report = lint_vault(tmp)
            assert report.total_notes == 0
            assert report.is_healthy
        finally:
            shutil.rmtree(tmp)


# -------------------------------------------------------------------
# Finding detection
# -------------------------------------------------------------------

class TestFindings:
    def test_duplicate_id_detected(self):
        tmp = _copy_fixtures_to_tmpdir()
        try:
            report = lint_vault(tmp)
            dup_findings = [
                f for f in report.findings
                if f.rule == "duplicate_id"
            ]
            assert len(dup_findings) >= 1
            assert "kb_test_candidate" in dup_findings[0].message
        finally:
            shutil.rmtree(tmp)

    def test_missing_frontmatter_detected(self):
        tmp = _copy_fixtures_to_tmpdir()
        try:
            report = lint_vault(tmp)
            missing = [
                f for f in report.findings
                if f.rule == "missing_frontmatter"
            ]
            assert len(missing) >= 1
        finally:
            shutil.rmtree(tmp)

    def test_broken_wikilink_detected(self):
        tmp = _copy_fixtures_to_tmpdir()
        try:
            report = lint_vault(tmp)
            broken = [
                f for f in report.findings
                if f.rule == "broken_wikilink"
            ]
            assert len(broken) >= 1
            assert any("kb_missing_target" in f.message for f in broken)
        finally:
            shutil.rmtree(tmp)

    def test_schema_errors_detected(self):
        tmp = _copy_fixtures_to_tmpdir()
        try:
            report = lint_vault(tmp)
            schema_findings = [
                f for f in report.findings
                if f.rule.startswith("schema_")
            ]
            assert len(schema_findings) >= 1
        finally:
            shutil.rmtree(tmp)


# -------------------------------------------------------------------
# Non-authorizing invariant
# -------------------------------------------------------------------

class TestNonAuthorizing:
    def test_report_non_authorizing_always_true(self):
        report = lint_vault(Path(tempfile.mkdtemp()))
        assert report.non_authorizing is True

    def test_report_non_authorizing_cannot_be_overridden(self):
        report = VaultHealthReport(
            vault_root="/tmp",
            total_notes=0,
            parsed_ok=0,
            with_frontmatter=0,
            valid_entries=0,
            total_wikilinks=0,
            findings=(),
            non_authorizing=False,
        )
        assert report.non_authorizing is True

    def test_to_dict_non_authorizing_true(self):
        report = lint_vault(Path(tempfile.mkdtemp()))
        assert report.to_dict()["non_authorizing"] is True


# -------------------------------------------------------------------
# No-mutation guarantee
# -------------------------------------------------------------------

class TestNoMutation:
    def test_lint_does_not_modify_vault_files(self):
        tmp = _copy_fixtures_to_tmpdir()
        try:
            before = _record_file_state(tmp)
            _ = lint_vault(tmp)
            after = _record_file_state(tmp)
            assert before == after
        finally:
            shutil.rmtree(tmp)
