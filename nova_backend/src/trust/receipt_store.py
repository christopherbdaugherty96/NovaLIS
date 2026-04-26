# src/trust/receipt_store.py
"""
Minimum viable action receipt store.

Reads the ledger in reverse and returns the last N receipt-worthy events
so the dashboard (and users) can see what Nova actually did.

Receipt-worthy = any event that represents a completed or attempted governed
action, or a significant state change that a user would want to know about.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.utils.persistent_state import runtime_path

_log = logging.getLogger(__name__)

_LEDGER_PATH: Path = runtime_path(__file__, "data", "ledger.jsonl")

_RECEIPT_WORTHY: frozenset[str] = frozenset(
    {
        "ACTION_ATTEMPTED",
        "ACTION_COMPLETED",
        "EMAIL_DRAFT_CREATED",
        "EMAIL_DRAFT_FAILED",
        "EMAIL_DRAFT_OPENED",
        "OPENCLAW_ACTION_APPROVED",
        "OPENCLAW_ACTION_DENIED",
        "OPENCLAW_ACTION_PENDING",
        "OPENCLAW_AGENT_RUN_COMPLETED",
        "SCREEN_CAPTURE_COMPLETED",
        "MEMORY_ITEM_SAVED",
        "MEMORY_ITEM_DELETED",
        "POLICY_EXECUTION_COMPLETED",
        "POLICY_EXECUTION_BLOCKED",
    }
)

_DEFAULT_LIMIT = 20
_READ_TAIL = 500  # max ledger lines to scan for receipts


def get_recent_receipts(limit: int = _DEFAULT_LIMIT) -> list[dict[str, Any]]:
    """
    Return up to `limit` recent action receipts from the ledger, newest first.

    Each receipt is a dict with at minimum:
      - timestamp_utc (str)
      - event_type (str)
    Plus any additional metadata the governor logged with the event.

    Returns [] on missing ledger, empty ledger, or any read/parse error so
    callers (API layer, dashboard) stay functional on a fresh install.
    """
    try:
        return _collect_receipts(limit)
    except Exception:
        _log.exception("receipt_store: unexpected error reading ledger")
        return []


def _collect_receipts(limit: int) -> list[dict[str, Any]]:
    if not _LEDGER_PATH.exists():
        return []

    try:
        raw_lines = _read_tail_lines(_LEDGER_PATH, _READ_TAIL)
    except OSError:
        return []

    receipts: list[dict[str, Any]] = []
    for line in reversed(raw_lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("event_type") in _RECEIPT_WORTHY:
            receipts.append(entry)
        if len(receipts) >= limit:
            break

    return receipts


def get_receipt_summary() -> dict[str, Any]:
    """Return a brief summary: total receipt-worthy events seen and the last one."""
    receipts = get_recent_receipts(limit=1)
    return {
        "last_receipt": receipts[0] if receipts else None,
        "has_receipts": bool(receipts),
    }


def _read_tail_lines(path: Path, n: int) -> list[str]:
    """Read the last n lines of a file without loading the whole file."""
    chunk = 1024 * 8
    lines: list[str] = []
    with open(path, "rb") as f:
        f.seek(0, 2)
        remaining = f.tell()
        buf = b""
        while remaining > 0 and len(lines) < n:
            read_size = min(chunk, remaining)
            remaining -= read_size
            f.seek(remaining)
            buf = f.read(read_size) + buf
            lines = buf.decode("utf-8", errors="replace").splitlines()
    return lines[-n:] if len(lines) > n else lines
