# src/actions/action_result.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    """
    Result of a single governed action execution.

    Fields:
        success:     True if execution succeeded, False otherwise.
        message:     User‑friendly message (success or error).
        data:        Optional structured payload (machine‑readable, may contain widget info).
        request_id:  Links back to the originating ActionRequest.

    Note: All UI‑relevant structured data should be placed inside the `data` dict,
          using a key like "widget" or "type" to allow the presentation layer
          to dispatch appropriately. There is no separate `widget_data` field.
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

    @classmethod
    def ok(cls, message: str, data: Optional[Dict[str, Any]] = None,
           request_id: Optional[str] = None) -> ActionResult:
        """Factory for successful execution results."""
        return cls(success=True, message=message, data=data, request_id=request_id)

    @classmethod
    def failure(cls, message: str, request_id: Optional[str] = None) -> ActionResult:
        """Factory for execution failures (network errors, timeouts, etc.)."""
        return cls(success=False, message=message, request_id=request_id)

    @classmethod
    def refusal(cls, message: str, request_id: Optional[str] = None) -> ActionResult:
        """
        Factory for constitutionally denied actions.
        Refusal means the action was valid but blocked by policy (phase gate, confirmation, etc.).
        """
        return cls(success=False, message=message, request_id=request_id)

    @property
    def user_message(self) -> str:
        """Alias for `.message` – used for backward compatibility."""
        return self.message