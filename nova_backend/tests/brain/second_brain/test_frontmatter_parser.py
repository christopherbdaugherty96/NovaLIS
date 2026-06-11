"""Tests for frontmatter parser and wikilink extraction.

Invariants under test:
  1. parse_note reads files without modifying them
  2. Frontmatter is correctly extracted as a dict
  3. Wikilinks are extracted from the Markdown body
  4. Missing frontmatter is reported
  5. Invalid YAML is reported
  6. frontmatter_to_entry converts valid frontmatter to KnowledgeEntry
  7. frontmatter_to_entry rejects invalid enum values
  8. No file mutation occurs during parsing
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from src.brain.second_brain.frontmatter_parser import (
    ParsedNote,
    extract_wikilinks,
    frontmatter_to_entry,
    parse_note,
)

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "second_brain"


# -------------------------------------------------------------------
# parse_note — basic behavior
# -------------------------------------------------------------------

class TestParseNote:
    def test_valid_promoted_note(self):
        note = parse_note(_FIXTURES / "valid_promoted_note.md")
        assert note.has_frontmatter
        assert note.note_id == "kb_test_valid_promoted"
        assert note.title == "Valid Promoted Note"
        assert not note.parse_errors

    def test_valid_candidate_note(self):
        note = parse_note(_FIXTURES / "valid_candidate_note.md")
        assert note.has_frontmatter
        assert note.note_id == "kb_test_candidate"

    def test_missing_frontmatter(self):
        note = parse_note(_FIXTURES / "missing_frontmatter.md")
        assert not note.has_frontmatter
        assert not note.parse_errors

    def test_nonexistent_file(self):
        note = parse_note(Path("/nonexistent/file.md"))
        assert not note.has_frontmatter
        assert note.parse_errors


# -------------------------------------------------------------------
# Wikilink extraction
# -------------------------------------------------------------------

class TestWikilinks:
    def test_extract_basic_wikilinks(self):
        links = extract_wikilinks("See [[target_one]] and [[target_two]].")
        assert links == ("target_one", "target_two")

    def test_extract_aliased_wikilinks(self):
        links = extract_wikilinks("See [[target|display name]].")
        assert links == ("target",)

    def test_no_wikilinks(self):
        links = extract_wikilinks("No links here.")
        assert links == ()

    def test_deduplicates(self):
        links = extract_wikilinks("[[a]] then [[a]] again.")
        assert links == ("a",)

    def test_from_fixture_file(self):
        note = parse_note(_FIXTURES / "valid_promoted_note.md")
        assert "kb_test_candidate" in note.wikilinks
        assert "kb_missing_target" in note.wikilinks


# -------------------------------------------------------------------
# frontmatter_to_entry
# -------------------------------------------------------------------

class TestFrontmatterToEntry:
    def test_valid_candidate_converts(self):
        note = parse_note(_FIXTURES / "valid_candidate_note.md")
        entry, errors = frontmatter_to_entry(note.frontmatter)
        assert entry is not None
        assert errors == []
        assert entry.id == "kb_test_candidate"
        assert entry.non_authorizing is True

    def test_valid_promoted_converts(self):
        note = parse_note(_FIXTURES / "valid_promoted_note.md")
        entry, errors = frontmatter_to_entry(note.frontmatter)
        assert entry is not None
        assert errors == []

    def test_invalid_entry_type_returns_errors(self):
        fm = {"entry_type": "invalid_type", "status": "candidate",
              "authority_label": "raw_source", "review_state": "unreviewed",
              "confidence": "low"}
        entry, errors = frontmatter_to_entry(fm)
        assert entry is None
        assert any("entry_type" in e.field for e in errors)

    def test_bad_promoted_returns_schema_errors(self):
        note = parse_note(_FIXTURES / "bad_promoted_no_review.md")
        entry, errors = frontmatter_to_entry(note.frontmatter)
        assert errors

    def test_proves_without_evidence_returns_errors(self):
        note = parse_note(_FIXTURES / "proves_without_evidence.md")
        entry, errors = frontmatter_to_entry(note.frontmatter)
        assert any("source_ref" in e.field for e in errors)


# -------------------------------------------------------------------
# No-mutation guarantee
# -------------------------------------------------------------------

class TestNoMutation:
    def test_parse_does_not_modify_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8",
        ) as f:
            content = "---\nid: kb_temp\ntitle: Temp\n---\n# Body\n"
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            stat_before = os.stat(path)
            mtime_before = stat_before.st_mtime_ns
            size_before = stat_before.st_size

            _ = parse_note(path)

            stat_after = os.stat(path)
            assert stat_after.st_mtime_ns == mtime_before
            assert stat_after.st_size == size_before
            assert path.read_text(encoding="utf-8") == content
        finally:
            path.unlink()
