from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.durability.corruption import read_jsonl_state, require_state


class LedgerAnalyzer:
    def __init__(self, path: Path):
        self.path = path

    def _read_entries(self) -> List[Dict]:
        if not self.path.exists():
            return []
        entries = read_jsonl_state(self.path, "ledger")
        for entry in entries:
            require_state(isinstance(entry, dict), "ledger", self.path, "expected object record")
        return entries

    def last_n(self, n: int) -> List[Dict]:
        n = max(0, int(n))
        if n == 0:
            return []
        entries = self._read_entries()
        return entries[-n:]

    def summarize_recent_activity(self) -> Dict:
        entries = self.last_n(50)
        summary: Dict[str, int] = {}
        for entry in entries:
            et = entry.get("event_type", "UNKNOWN")
            summary[et] = summary.get(et, 0) + 1
        return {
            "count": len(entries),
            "event_counts": summary,
        }
