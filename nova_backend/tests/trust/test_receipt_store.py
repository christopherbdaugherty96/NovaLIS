"""
Unit tests for src/trust/receipt_store.py.

These tests exercise the store directly — no HTTP layer, no FastAPI app.
They use tmp_path to write synthetic ledger files and monkeypatch
_LEDGER_PATH so the store reads the test file instead of the real ledger.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import src.trust.receipt_store as store_mod
from src.trust.receipt_store import (
    _RECEIPT_WORTHY,
    get_receipt_summary,
    get_recent_receipts,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RECEIPT_TYPE = next(iter(_RECEIPT_WORTHY))  # any one valid receipt event type
_NON_RECEIPT_TYPE = "SOME_INTERNAL_DIAGNOSTIC_EVENT"


def _write_ledger(path: Path, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def _entry(event_type: str, ts: str = "2026-04-25T12:00:00Z", **kwargs) -> dict:
    return {"event_type": event_type, "timestamp_utc": ts, **kwargs}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMissingLedger:
    def test_returns_empty_list(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        assert get_recent_receipts() == []

    def test_summary_has_no_receipts(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        summary = get_receipt_summary()
        assert summary["has_receipts"] is False
        assert summary["last_receipt"] is None


class TestEmptyLedger:
    def test_returns_empty_list(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text("", encoding="utf-8")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        assert get_recent_receipts() == []


class TestNonReceiptWorthy:
    def test_non_worthy_events_excluded(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [
            _entry(_NON_RECEIPT_TYPE),
            _entry(_NON_RECEIPT_TYPE),
        ])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        assert get_recent_receipts() == []


class TestReceiptWorthy:
    def test_worthy_events_returned(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [_entry(_RECEIPT_TYPE)])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts()
        assert len(result) == 1
        assert result[0]["event_type"] == _RECEIPT_TYPE

    def test_mixed_events_only_worthy_returned(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [
            _entry(_NON_RECEIPT_TYPE, ts="2026-04-25T10:00:00Z"),
            _entry(_RECEIPT_TYPE, ts="2026-04-25T11:00:00Z"),
            _entry(_NON_RECEIPT_TYPE, ts="2026-04-25T12:00:00Z"),
            _entry(_RECEIPT_TYPE, ts="2026-04-25T13:00:00Z"),
        ])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts()
        assert len(result) == 2
        assert all(r["event_type"] == _RECEIPT_TYPE for r in result)

    def test_newest_first_ordering(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [
            _entry(_RECEIPT_TYPE, ts="2026-04-25T10:00:00Z"),
            _entry(_RECEIPT_TYPE, ts="2026-04-25T11:00:00Z"),
            _entry(_RECEIPT_TYPE, ts="2026-04-25T12:00:00Z"),
        ])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts()
        timestamps = [r["timestamp_utc"] for r in result]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_limit_respected(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [_entry(_RECEIPT_TYPE, ts=f"2026-04-25T{h:02d}:00:00Z") for h in range(10)])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        assert len(get_recent_receipts(limit=3)) == 3

    def test_limit_1_returns_one(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [_entry(_RECEIPT_TYPE), _entry(_RECEIPT_TYPE)])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        assert len(get_recent_receipts(limit=1)) == 1


class TestMalformedLines:
    def test_invalid_json_line_skipped(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        with open(ledger, "w", encoding="utf-8") as f:
            f.write("not json at all\n")
            f.write(json.dumps(_entry(_RECEIPT_TYPE)) + "\n")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts()
        assert len(result) == 1

    def test_non_dict_json_line_skipped(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        with open(ledger, "w", encoding="utf-8") as f:
            f.write(json.dumps([1, 2, 3]) + "\n")          # list — valid JSON, not dict
            f.write(json.dumps("a string") + "\n")          # string — valid JSON, not dict
            f.write(json.dumps(_entry(_RECEIPT_TYPE)) + "\n")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts()
        assert len(result) == 1

    def test_blank_lines_skipped(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        with open(ledger, "w", encoding="utf-8") as f:
            f.write("\n\n")
            f.write(json.dumps(_entry(_RECEIPT_TYPE)) + "\n")
            f.write("\n")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts()
        assert len(result) == 1

    def test_fully_corrupt_ledger_returns_empty(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text("}{bad}{json\n@@@@\n", encoding="utf-8")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        assert get_recent_receipts() == []


class TestReadError:
    def test_os_error_returns_empty(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text(json.dumps(_entry(_RECEIPT_TYPE)) + "\n", encoding="utf-8")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        def _bad_read(path, n):
            raise OSError("simulated read failure")

        monkeypatch.setattr(store_mod, "_read_tail_lines", _bad_read)
        assert get_recent_receipts() == []

    def test_unexpected_exception_returns_empty(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text(json.dumps(_entry(_RECEIPT_TYPE)) + "\n", encoding="utf-8")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        def _explode(path, n):
            raise RuntimeError("unexpected internal error")

        monkeypatch.setattr(store_mod, "_read_tail_lines", _explode)
        assert get_recent_receipts() == []


class TestSummary:
    def test_summary_with_receipts(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [_entry(_RECEIPT_TYPE)])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        summary = get_receipt_summary()
        assert summary["has_receipts"] is True
        assert summary["last_receipt"] is not None
        assert summary["last_receipt"]["event_type"] == _RECEIPT_TYPE

    def test_summary_without_receipts(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [_entry(_NON_RECEIPT_TYPE)])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        summary = get_receipt_summary()
        assert summary["has_receipts"] is False
        assert summary["last_receipt"] is None


class TestAllReceiptEventTypes:
    def test_all_receipt_worthy_types_accepted(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(ledger, [_entry(t) for t in sorted(_RECEIPT_WORTHY)])
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)
        result = get_recent_receipts(limit=100)
        returned_types = {r["event_type"] for r in result}
        assert returned_types == _RECEIPT_WORTHY
