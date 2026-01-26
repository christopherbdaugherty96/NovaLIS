"""
Reminder Task Schema

Defines what a reminder *is* — not how or when it runs.

IMPORTANT:
- No timers
- No background execution
- No persistence
- No notifications

Phase-2:
- Objects may exist but are inert
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ReminderTask:
    """
    Immutable reminder description.
    """
    reminder_id: str
    text: str
    remind_at: datetime

    created_at: datetime
    active: bool = True

    # Optional metadata (future-safe)
    source: Optional[str] = None
