from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from src.governor.exceptions import LedgerWriteFailed
from src.ledger.reader import LedgerAnalyzer
from src.ledger.writer import LedgerWriter
from src.trust import receipt_store


def test_distinct_writers_preserve_every_concurrent_record(tmp_path, monkeypatch):
    path = tmp_path / "ledger.jsonl"
    barrier = Barrier(8)

    def append(worker):
        writer = LedgerWriter(path)
        barrier.wait(timeout=10)
        for sequence in range(15):
            writer.log_event("ACTION_COMPLETED", {
                "worker": worker,
                "sequence": sequence,
                "payload": "x" * (worker * 71),
            })

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(append, range(8)))

    records = LedgerAnalyzer(path).last_n(120)
    assert len(path.read_text(encoding="utf-8").splitlines()) == 120
    assert len(records) == 120
    assert {(row["worker"], row["sequence"]) for row in records} == {
        (worker, sequence) for worker in range(8) for sequence in range(15)
    }
    assert all(row["payload"] == "x" * (row["worker"] * 71) for row in records)
    monkeypatch.setattr(receipt_store, "_LEDGER_PATH", path)
    receipts = receipt_store.read_recent_receipts(limit=120)
    assert receipts.available
    assert len(receipts.receipts) == 120
    assert {(row["worker"], row["sequence"]) for row in receipts.receipts} == {
        (worker, sequence) for worker in range(8) for sequence in range(15)
    }


def test_distinct_writers_refuse_existing_corruption_without_overwrite(tmp_path):
    path = tmp_path / "ledger.jsonl"
    original = b'{"event_type":'
    path.write_bytes(original)

    def append(_):
        with pytest.raises(LedgerWriteFailed):
            LedgerWriter(path).log_event("ACTION_COMPLETED", {})

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(append, range(8)))
    assert path.read_bytes() == original


def test_writer_revalidates_when_ledger_changes_outside_writer(tmp_path):
    path = tmp_path / "ledger.jsonl"
    writer = LedgerWriter(path)
    writer.log_event("ACTION_COMPLETED", {"sequence": 1})
    original = path.read_bytes() + b'{"event_type":'
    path.write_bytes(original)

    with pytest.raises(LedgerWriteFailed):
        writer.log_event("ACTION_COMPLETED", {"sequence": 2})

    assert path.read_bytes() == original
