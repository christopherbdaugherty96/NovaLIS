"""
NovaLIS ActionRequest (Phase-2)

Purpose:
- Canonical, immutable description of a user-requested action
- Carries intent ONLY (never execution)
- Passed through confirmation and execution boundaries

LOCKED RULES:
- No execution logic
- No confirmation logic
- No LLM usage
- No side effects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4
import time

from .action_types import ActionType


@dataclass(frozen=True)
class ActionRequest:
    """
    Immutable action request object.
    """

    action_type: ActionType
    title: str
    payload: Dict[str, Any] = field(default_factory=dict)

    # Metadata (system-owned)
    action_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: float = field(default_factory=time.time)

    # Phase-2 rule: all actions require confirmation
    requires_confirmation: bool = True

    # Optional executor targeting (used later in Phase-2)
    target_executor_id: Optional[str] = None
