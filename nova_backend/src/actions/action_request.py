# src/actions/action_request.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import uuid4
from datetime import datetime, timezone


@dataclass(frozen=True)
class ActionRequest:
    """
    Immutable description of a user‑requested governed action.
    Created only in governor.py.
    """
    capability_id: int
    params: Dict[str, Any] = field(default_factory=dict)

    # System metadata
    request_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )