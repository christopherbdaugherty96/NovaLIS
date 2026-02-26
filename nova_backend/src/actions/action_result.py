# src/actions/action_result.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    """
    Result of a single governed action execution.

    Core Fields (unchanged):
        success:      True if execution succeeded, False otherwise.
        message:      User‑friendly message (success or error).
        data:         Optional structured payload (machine‑readable).
        request_id:   Links back to the originating ActionRequest.

    Governance Metadata (new):
        risk_level:   "low" | "moderate" | "high"
                      Intended risk classification of the action.
        authority_class: "read_only" | "local_effect" | "network_outbound" | "persistent_change"
                      Category of authority required.
        external_effect: True if action affected an external system (network, device, service).
        reversible:   True if the action can be undone (e.g., toggle vs. delete).
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

    # Governance metadata – safe defaults provided
    risk_level: str = "low"
    authority_class: str = "read_only"
    external_effect: bool = False
    reversible: bool = True

    # --- Factory methods (updated) ---

    @classmethod
    def ok(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        risk_level: str = "low",
        authority_class: str = "read_only",
        external_effect: bool = False,
        reversible: bool = True,
    ) -> ActionResult:
        """Factory for successful execution results."""
        return cls(
            success=True,
            message=message,
            data=data,
            request_id=request_id,
            risk_level=risk_level,
            authority_class=authority_class,
            external_effect=external_effect,
            reversible=reversible,
        )

    @classmethod
    def failure(
        cls,
        message: str,
        request_id: Optional[str] = None,
        risk_level: str = "low",
        authority_class: str = "read_only",
        external_effect: bool = False,
        reversible: bool = True,
    ) -> ActionResult:
        """Factory for execution failures (network errors, timeouts, etc.)."""
        return cls(
            success=False,
            message=message,
            request_id=request_id,
            risk_level=risk_level,
            authority_class=authority_class,
            external_effect=external_effect,
            reversible=reversible,
        )

    @classmethod
    def refusal(
        cls,
        message: str,
        request_id: Optional[str] = None,
        risk_level: str = "low",
        authority_class: str = "read_only",
        external_effect: bool = False,
        reversible: bool = True,
    ) -> ActionResult:
        """
        Factory for constitutionally denied actions.
        Refusal means the action was valid but blocked by policy (phase gate, confirmation, etc.).
        """
        return cls(
            success=False,
            message=message,
            request_id=request_id,
            risk_level=risk_level,
            authority_class=authority_class,
            external_effect=external_effect,
            reversible=reversible,
        )

    @property
    def user_message(self) -> str:
        """Alias for `.message` – for backward compatibility."""
        return self.message