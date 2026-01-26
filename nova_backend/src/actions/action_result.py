"""
NovaLIS ActionResult (Phase-2)

Purpose:
- Canonical result of an executed action
- Returned from execute_action boundary
- Sent to UI or speech layer as-is

LOCKED RULES:
- No follow-up actions
- No chaining
- No retries
- No side effects
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    """
    Result of a single executed action.
    """

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
