# src/memory/quick_corrections.py
"""
Phase-3.5 Staged Governed Memory — Quick Corrections

Properties:
- Explicit invocation only ("Correction:")
- Append-only
- No reads
- No inference
- No automatic behavior changes
- Auditable and reversible
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict


# Location is explicit and inspectable
_CORRECTIONS_PATH = Path("memory/quick_corrections.jsonl")


def record_correction(content: str) -> Dict[str, str]:
    """
    Record a user-issued correction verbatim.

    This function performs no interpretation and no validation
    beyond trimming whitespace.
    """

    entry = {
        "type": "user_correction",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "content": content.strip(),
        "source": "explicit_user_correction",
        "consumed": False,
    }

    _CORRECTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _CORRECTIONS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
