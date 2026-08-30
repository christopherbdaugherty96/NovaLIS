"""
Unit tests for src/trust/receipt_store.py.

These tests exercise the store directly — no HTTP layer, no FastAPI app.
They use tmp_path to write synthetic ledger files and monkeypatch
_LEDGER_PATH so the store reads the test file instead of the real ledger.
"""
from __future__ import annotations

import json
from pathlib import Path

import src.trust.receipt_store as store_mod
from src.trust.receipt_store import (
    _RECEIPT_WORTHY,
    get_receipt_summary,
    get_recent_receipts,
    get_session_action_receipts,
    read_recent_receipts,
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


class TestReceiptAvailabilityTruth:
    def test_missing_ledger_is_available_and_empty(self, monkeypatch, tmp_path):
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", tmp_path / "missing.jsonl")

        result = read_recent_receipts()

        assert result.available is True
        assert result.receipts == ()

    def test_read_failure_is_unavailable_not_empty_success(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text("{}\n", encoding="utf-8")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        def fail_read(*args, **kwargs):
            raise OSError("synthetic read failure")

        monkeypatch.setattr(store_mod, "_read_tail_lines", fail_read)
        result = read_recent_receipts()

        assert result.available is False
        assert result.receipts == ()
        assert result.error == "OSError"

    def test_nonempty_fully_corrupt_ledger_is_unavailable(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text("}{bad}{json\n@@@@\n", encoding="utf-8")
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        result = read_recent_receipts()

        assert result.available is False
        assert result.receipts == ()
        assert result.error == "ValueError"


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

    def test_registry_event_burst_does_not_hide_recent_action_receipt(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        entries = [
            _entry("ACTION_COMPLETED", request_id="req-visible", capability_id=19),
            *[
                _entry("CAPABILITY_INSTALLED", capability_id=index)
                for index in range(700)
            ],
        ]
        _write_ledger(ledger, entries)
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        result = get_recent_receipts(limit=1)

        assert result[0]["event_type"] == "ACTION_COMPLETED"
        assert result[0]["request_id"] == "req-visible"


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


class TestSessionActionReceipts:
    def test_requires_exact_session_request_and_trusted_origin(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(
            ledger,
            [
                _entry(
                    "ACTION_ATTEMPTED",
                    session_id="current",
                    request_id="req-1",
                    activity_origin="user_action",
                ),
                _entry(
                    "ACTION_COMPLETED",
                    session_id="current",
                    request_id="req-1",
                    activity_origin="user_action",
                    success=True,
                    status="completed",
                ),
                _entry(
                    "ACTION_COMPLETED",
                    session_id="other",
                    request_id="req-other",
                    activity_origin="user_action",
                ),
                _entry(
                    "ACTION_COMPLETED",
                    session_id="current",
                    request_id="",
                    activity_origin="user_action",
                ),
                _entry(
                    "ACTION_COMPLETED",
                    session_id="current",
                    request_id="legacy-no-origin",
                ),
                _entry(
                    "ACTION_COMPLETED",
                    session_id="current",
                    request_id="free-form-origin",
                    activity_origin="dashboard_guess",
                ),
            ],
        )
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        receipts = get_session_action_receipts("current")

        assert [item["request_id"] for item in receipts] == ["req-1", "req-1"]
        assert {item["event_type"] for item in receipts} == {
            "ACTION_ATTEMPTED",
            "ACTION_COMPLETED",
        }

    def test_does_not_infer_legacy_session_from_timestamp(self, monkeypatch, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        _write_ledger(
            ledger,
            [
                _entry(
                    "ACTION_COMPLETED",
                    ts="2026-08-12T12:00:00Z",
                    request_id="recent-but-legacy",
                    activity_origin="user_action",
                )
            ],
        )
        monkeypatch.setattr(store_mod, "_LEDGER_PATH", ledger)

        assert get_session_action_receipts("current") == []
