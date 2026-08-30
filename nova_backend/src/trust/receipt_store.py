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
from dataclasses import dataclass
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
_READ_TAIL = 5000  # bounded scan that survives capability-registry event bursts
_SESSION_READ_TAIL = 5000
_SESSION_ACTION_EVENTS: frozenset[str] = frozenset(
    {"ACTION_ATTEMPTED", "ACTION_COMPLETED"}
)
_TRUSTED_ACTIVITY_ORIGINS: frozenset[str] = frozenset(
    {"user_action", "background_read"}
)


@dataclass(frozen=True)
class ReceiptReadResult:
    receipts: tuple[dict[str, Any], ...]
    available: bool
    error: str = ""


def read_recent_receipts(limit: int = _DEFAULT_LIMIT) -> ReceiptReadResult:
    """Read receipts while preserving empty-versus-unavailable truth."""

    try:
        return ReceiptReadResult(tuple(_collect_receipts(limit)), available=True)
    except Exception as exc:
        _log.exception("receipt_store: unexpected error reading ledger")
        return ReceiptReadResult((), available=False, error=type(exc).__name__)


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
    return list(read_recent_receipts(limit).receipts)


def _collect_receipts(limit: int) -> list[dict[str, Any]]:
    if not _LEDGER_PATH.exists():
        return []

    raw_lines = _read_tail_lines(_LEDGER_PATH, _READ_TAIL)

    receipts: list[dict[str, Any]] = []
    nonempty_lines = 0
    parseable_records = 0
    for line in reversed(raw_lines):
        line = line.strip()
        if not line:
            continue
        nonempty_lines += 1
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        parseable_records += 1
        if entry.get("event_type") in _RECEIPT_WORTHY:
            receipts.append(entry)
        if len(receipts) >= limit:
            break

    if nonempty_lines and not parseable_records:
        raise ValueError("Receipt ledger contains no parseable records")

    return receipts


def get_receipt_summary() -> dict[str, Any]:
    """Return a brief summary: total receipt-worthy events seen and the last one."""
    receipts = get_recent_receipts(limit=1)
    return {
        "last_receipt": receipts[0] if receipts else None,
        "has_receipts": bool(receipts),
    }


def get_session_action_receipts(
    session_id: str,
    *,
    limit: int = 200,
) -> list[dict[str, Any]]:
    """Return strictly correlated action receipts for one server session.

    Legacy receipts without an exact session ID, request ID, or trusted origin
    are intentionally excluded.  Current-session membership is never inferred
    from timestamp proximity.
    """
    trusted_session_id = str(session_id or "").strip()
    if not trusted_session_id or limit <= 0:
        return []
    try:
        return _collect_session_action_receipts(trusted_session_id, limit)
    except Exception:
        _log.exception("receipt_store: unexpected error reading session receipts")
        return []


def _collect_session_action_receipts(
    session_id: str,
    limit: int,
) -> list[dict[str, Any]]:
    if not _LEDGER_PATH.exists():
        return []
    try:
        raw_lines = _read_tail_lines(_LEDGER_PATH, _SESSION_READ_TAIL)
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
        if entry.get("event_type") not in _SESSION_ACTION_EVENTS:
            continue
        if str(entry.get("session_id") or "").strip() != session_id:
            continue
        if not str(entry.get("request_id") or "").strip():
            continue
        origin = str(entry.get("activity_origin") or "").strip().lower()
        if origin not in _TRUSTED_ACTIVITY_ORIGINS:
            continue
        receipts.append(entry)
        if len(receipts) >= limit:
            break
    return receipts


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
