# src/ledger/writer.py

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.durability.corruption import read_jsonl_state, require_state
from src.durability.maintenance import authoritative_mutation
from src.governor.exceptions import LedgerWriteFailed
from src.ledger.event_types import EVENT_TYPES
from src.utils.persistent_state import runtime_path, shared_path_lock

LEDGER_PATH = runtime_path(__file__, "data", "ledger.jsonl")
_VALIDATED_FILE_SIGNATURES: dict[str, tuple[int, int]] = {}


def _path_key(path: Path) -> str:
    try:
        resolved = path.resolve()
    except Exception:
        resolved = path.absolute()
    text = str(resolved)
    return text.lower() if os.name == "nt" else text


def _file_signature(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def _validate_existing_ledger(path: Path) -> None:
    signature = _file_signature(path)
    key = _path_key(path)
    if _VALIDATED_FILE_SIGNATURES.get(key) == signature:
        return
    existing = read_jsonl_state(path, "ledger")
    for record in existing:
        require_state(isinstance(record, dict), "ledger", path, "expected object record")
    _VALIDATED_FILE_SIGNATURES[key] = signature


class LedgerWriter:
    """Append‑only ledger with atomic write guarantees."""

    def __init__(self, path: Path = LEDGER_PATH):
        self.path = path
        self._lock = shared_path_lock(path)

    @authoritative_mutation
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
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # Serialize separate writer instances in this process. Windows append
            # handles can otherwise overlap, corrupting acknowledged history.
            with self._lock:
                if self.path.exists():
                    _validate_existing_ledger(self.path)
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                _VALIDATED_FILE_SIGNATURES[_path_key(self.path)] = _file_signature(self.path)
        except Exception as e:
            raise LedgerWriteFailed(f"Ledger write failed: {e}") from e
