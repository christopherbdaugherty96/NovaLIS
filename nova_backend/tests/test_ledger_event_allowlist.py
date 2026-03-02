import pytest


def test_ledger_rejects_unknown_event_type(tmp_path):
    from src.ledger.writer import LedgerWriter
    from src.governor.exceptions import LedgerWriteFailed

    writer = LedgerWriter(path=tmp_path / "ledger.jsonl")

    with pytest.raises(LedgerWriteFailed):
        writer.log_event("UNKNOWN_EVENT", {"x": 1})
