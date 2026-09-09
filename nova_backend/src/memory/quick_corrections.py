# src/memory/quick_corrections.py
"""
Phase-3.5 Staged Governed Memory — Quick Corrections

Properties:
- Explicit invocation only ("Correction:")
- Append-only writes via record_correction()
- load_unconsumed() reads corrections not yet injected into a session
- mark_all_consumed() rewrites the log marking all entries consumed
- No inference
- No automatic behavior changes
- Auditable and reversible
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, List

from src.durability.corruption import read_jsonl_state, require_state
from src.utils.persistent_state import runtime_path

# Absolute path anchored to this file — consistent regardless of CWD.
# Matches the pattern used by all other Nova memory stores.
_CORRECTIONS_PATH = runtime_path(__file__, "data", "nova_state", "memory", "quick_corrections.jsonl")


def record_correction(content: str) -> Dict[str, str]:
    """
    Record a user-issued correction verbatim.

    This function performs no interpretation and no validation
    beyond trimming whitespace.
    """

    entry = {
        "type": "user_correction",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content.strip(),
        "source": "explicit_user_correction",
        "consumed": False,
    }

    if _CORRECTIONS_PATH.exists():
        _validated_entries()
    _CORRECTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _CORRECTIONS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def load_unconsumed(limit: int = 10) -> List[str]:
    """
    Return the content strings of unconsumed corrections (oldest-first).

    Corrections are unconsumed when ``consumed`` is False. Call
    ``mark_all_consumed()`` after loading to prevent re-injection on
    the next session.

    Returns an empty list only when the file does not exist.
    """
    if not _CORRECTIONS_PATH.exists():
        return []
    results: List[str] = []
    for entry in _validated_entries():
        if not entry.get("consumed", True):
            content = str(entry.get("content") or "").strip()
            if content:
                results.append(content)
            if len(results) >= limit:
                break
    return results


def mark_all_consumed() -> None:
    """
    Rewrite the corrections log marking every entry as consumed.

    Safe to call even if the file does not exist or is empty.
    """
    if not _CORRECTIONS_PATH.exists():
        return
    entries = _validated_entries()
    updated: List[str] = []
    changed = False
    for entry in entries:
        if not entry.get("consumed", True):
            entry["consumed"] = True
            changed = True
        updated.append(json.dumps(entry, ensure_ascii=False))
    if changed:
        _CORRECTIONS_PATH.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _validated_entries() -> List[dict]:
    records = read_jsonl_state(_CORRECTIONS_PATH, "quick_corrections")
    for entry in records:
        require_state(isinstance(entry, dict), "quick_corrections", _CORRECTIONS_PATH, "expected object record")
        require_state(isinstance(entry.get("consumed"), bool), "quick_corrections", _CORRECTIONS_PATH, "consumed must be boolean")
    return records
