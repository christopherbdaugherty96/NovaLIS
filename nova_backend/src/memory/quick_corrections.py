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
from pathlib import Path
from typing import Dict, List


# Absolute path anchored to this file — consistent regardless of CWD.
# Matches the pattern used by all other Nova memory stores.
_CORRECTIONS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "nova_state"
    / "memory"
    / "quick_corrections.jsonl"
)


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

    Returns an empty list if the file does not exist or cannot be read.
    """
    if not _CORRECTIONS_PATH.exists():
        return []
    results: List[str] = []
    try:
        lines = _CORRECTIONS_PATH.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not entry.get("consumed", True):
                content = str(entry.get("content") or "").strip()
                if content:
                    results.append(content)
                if len(results) >= limit:
                    break
    except Exception:
        return []
    return results


def mark_all_consumed() -> None:
    """
    Rewrite the corrections log marking every entry as consumed.

    Safe to call even if the file does not exist or is empty.
    """
    if not _CORRECTIONS_PATH.exists():
        return
    try:
        lines = _CORRECTIONS_PATH.read_text(encoding="utf-8").splitlines()
        updated: List[str] = []
        changed = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if not entry.get("consumed", True):
                    entry["consumed"] = True
                    changed = True
                updated.append(json.dumps(entry, ensure_ascii=False))
            except json.JSONDecodeError:
                updated.append(line)  # preserve malformed lines as-is
        if changed:
            _CORRECTIONS_PATH.write_text(
                "\n".join(updated) + "\n", encoding="utf-8"
            )
    except Exception:
        pass
