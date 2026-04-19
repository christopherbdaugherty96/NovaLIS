"""Tests for quick_corrections.py — record, load, and mark consumed."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.memory.quick_corrections import (
    load_unconsumed,
    mark_all_consumed,
    record_correction,
)


def _patched_path(tmp_path: Path) -> Path:
    return tmp_path / "quick_corrections.jsonl"


# ---------------------------------------------------------------------------
# record_correction
# ---------------------------------------------------------------------------

class TestRecordCorrection:
    def test_creates_file_and_returns_entry(self, tmp_path):
        p = _patched_path(tmp_path)
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            entry = record_correction("Berlin is the capital of Germany")
        assert p.exists()
        assert entry["content"] == "Berlin is the capital of Germany"
        assert entry["consumed"] is False
        assert entry["type"] == "user_correction"

    def test_appends_multiple_entries(self, tmp_path):
        p = _patched_path(tmp_path)
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            record_correction("Correction one")
            record_correction("Correction two")
        lines = [l for l in p.read_text().splitlines() if l.strip()]
        assert len(lines) == 2

    def test_strips_whitespace(self, tmp_path):
        p = _patched_path(tmp_path)
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            entry = record_correction("   spaced content   ")
        assert entry["content"] == "spaced content"


# ---------------------------------------------------------------------------
# load_unconsumed
# ---------------------------------------------------------------------------

class TestLoadUnconsumed:
    def test_returns_empty_when_no_file(self, tmp_path):
        p = tmp_path / "missing.jsonl"
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            result = load_unconsumed()
        assert result == []

    def test_returns_unconsumed_content(self, tmp_path):
        p = _patched_path(tmp_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({"content": "fix one", "consumed": False}) + "\n" +
            json.dumps({"content": "fix two", "consumed": False}) + "\n"
        )
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            result = load_unconsumed()
        assert result == ["fix one", "fix two"]

    def test_skips_consumed_entries(self, tmp_path):
        p = _patched_path(tmp_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({"content": "already consumed", "consumed": True}) + "\n" +
            json.dumps({"content": "fresh correction", "consumed": False}) + "\n"
        )
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            result = load_unconsumed()
        assert result == ["fresh correction"]

    def test_respects_limit(self, tmp_path):
        p = _patched_path(tmp_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        lines = "\n".join(
            json.dumps({"content": f"fix {i}", "consumed": False}) for i in range(10)
        ) + "\n"
        p.write_text(lines)
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            result = load_unconsumed(limit=3)
        assert len(result) == 3

    def test_skips_malformed_lines(self, tmp_path):
        p = _patched_path(tmp_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            "not valid json\n" +
            json.dumps({"content": "valid entry", "consumed": False}) + "\n"
        )
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            result = load_unconsumed()
        assert result == ["valid entry"]


# ---------------------------------------------------------------------------
# mark_all_consumed
# ---------------------------------------------------------------------------

class TestMarkAllConsumed:
    def test_noop_when_no_file(self, tmp_path):
        p = tmp_path / "missing.jsonl"
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            mark_all_consumed()  # should not raise
        assert not p.exists()

    def test_marks_unconsumed_entries(self, tmp_path):
        p = _patched_path(tmp_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({"content": "fix one", "consumed": False}) + "\n" +
            json.dumps({"content": "fix two", "consumed": False}) + "\n"
        )
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            mark_all_consumed()
        lines = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        assert all(entry["consumed"] is True for entry in lines)

    def test_does_not_change_already_consumed(self, tmp_path):
        p = _patched_path(tmp_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({"content": "already done", "consumed": True}) + "\n"
        )
        original = p.stat().st_mtime
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            mark_all_consumed()
        # File should not be rewritten since nothing changed
        lines = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        assert lines[0]["consumed"] is True

    def test_round_trip_record_load_mark(self, tmp_path):
        p = _patched_path(tmp_path)
        with patch("src.memory.quick_corrections._CORRECTIONS_PATH", p):
            record_correction("The capital is Berlin")
            record_correction("The river is the Spree")
            corrections = load_unconsumed()
            assert len(corrections) == 2
            mark_all_consumed()
            after = load_unconsumed()
        assert after == []
