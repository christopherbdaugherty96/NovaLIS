# src/actions/action_result.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    """
    Result of a single governed action execution.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None

    @classmethod
    def ok(cls, data: Dict[str, Any], request_id: Optional[str] = None) -> ActionResult:
        return cls(success=True, data=data, request_id=request_id)

    @classmethod
    def failure(cls, error: str, request_id: Optional[str] = None) -> ActionResult:
        return cls(success=False, error=error, request_id=request_id)

    @classmethod
    def refusal(cls, reason: str, request_id: Optional[str] = None) -> ActionResult:
        return cls(success=False, error=reason, request_id=request_id)

    @property
    def message(self) -> str:
        """User‑friendly message for display."""
        if self.success:
            return "Done."
        else:
            return self.error or "I can’t do that right now."