"""Reminder suggestion framework for the Chief of Staff personality layer.

Produces plain reminder dicts. Does not persist, call capabilities,
or access governed stores. Only governed callers (session handler)
can persist reminders through Cap 61.

Governance boundaries:
  - No imports from src.governor, src.executors, src.ledger,
    src.memory, src.connectors
  - No calendar event creation
  - No persistence methods (save, write, store, commit)
  - Pattern-derived reminders always include opt-out
  - Enforced by import boundary test
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(text: str, source: str) -> str:
    raw = f"{source}::{text.strip().lower()[:80]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Reminder:
    """Immutable reminder suggestion. No authority flags."""

    id: str
    text: str
    source: str
    created_at: str
    dismissed: bool
    opt_out: bool


class ReminderFramework:
    """Produces reminder suggestions as plain dicts.

    Does not persist data. Does not call capabilities.
    Does not access governed stores or clients.
    """

    def create_reminder(
        self,
        text: str,
        *,
        source: str = "user_created",
    ) -> Reminder:
        cleaned = str(text or "").strip()
        return Reminder(
            id=_make_id(cleaned, source),
            text=cleaned,
            source=source,
            created_at=_utc_now_iso(),
            dismissed=False,
            opt_out=False,
        )

    def derive_from_pattern(
        self,
        pattern_description: str,
        *,
        source_label: str,
    ) -> Reminder | None:
        desc = str(pattern_description or "").strip()
        if not desc:
            return None
        return Reminder(
            id=_make_id(desc, "pattern_derived"),
            text=desc,
            source="pattern_derived",
            created_at=_utc_now_iso(),
            dismissed=False,
            opt_out=False,
        )

    def list_active(self) -> list[Reminder]:
        return []

    def dismiss(self, reminder_id: str) -> None:
        pass

    def opt_out(self, reminder_id: str) -> None:
        pass

    def to_notice(self, reminder: Reminder) -> dict[str, Any] | None:
        if not reminder or not reminder.text:
            return None

        is_pattern = reminder.source == "pattern_derived"

        if is_pattern:
            summary = (
                f"{reminder.text} — want me to track this, "
                f"or stop mentioning it?"
            )
        else:
            summary = (
                f"{reminder.text} — want me to look into this?"
            )

        actions = [
            {"label": "Set reminder", "command": f"remember {reminder.text.lower()[:60]}"},
            {"label": "Dismiss", "command": "dismiss assistive notice"},
        ]
        if is_pattern:
            actions.append(
                {"label": "Stop mentioning this", "command": f"opt out reminder {reminder.id}"}
            )

        return {
            "id": f"reminder::{reminder.id}",
            "type": "tier3_recommend",
            "title": f"Reminder: {reminder.text[:60]}",
            "summary": summary,
            "why_now": f"Source: {reminder.source.replace('_', ' ')}.",
            "risk_level": "low",
            "requires_permission": True,
            "suggested_actions": actions,
        }
