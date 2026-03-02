# src/ledger/writer.py

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from src.governor.exceptions import LedgerWriteFailed
from src.ledger.event_types import EVENT_TYPES

LEDGER_PATH = Path(__file__).resolve().parents[1] / "data" / "ledger.jsonl"


class LedgerWriter:
    """Append‑only ledger with atomic write guarantees."""

    def __init__(self, path: Path = LEDGER_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, metadata: Dict[str, Any]) -> None:
        """Append a single event. Raises LedgerWriteFailed if write fails."""
        if event_type not in EVENT_TYPES:
            raise LedgerWriteFailed(f"Unknown ledger event type: {event_type}")

        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            **metadata
        }
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            raise LedgerWriteFailed(f"Ledger write failed: {e}") from e