# src/actions/action_result.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    """
    Result of a single governed action execution.

    Canonical contract fields:
        success
        status
        user_message
        speakable_text
        structured_data
        risk_level
        authority_class
        external_effect
        reversible
        request_id
        capability_id
        ledger_ref
        outcome_reason

    Backward compatibility:
        - `message` remains the stored user-facing text field.
        - `data` remains the legacy payload container, but it is normalized
          to always carry `speakable_text` and `structured_data`.
    """

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

    # Governance metadata
    risk_level: str = "low"
    authority_class: str = "read_only"
    external_effect: bool = False
    reversible: bool = True

    # Canonical contract metadata
    status: str = ""
    capability_id: Optional[int] = None
    ledger_ref: Optional[str] = None
    outcome_reason: str = ""

    def __post_init__(self) -> None:
        self.status = self._normalized_status(self.status, success=self.success)
        if not self.outcome_reason and not self.success:
            self.outcome_reason = str(self.message or "").strip()
        self.data = self._build_data_payload(
            self.data,
            speakable_text="",
            structured_data=None,
            default_message=self.message,
        )

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
        speakable_text: str = "",
        structured_data: Optional[Dict[str, Any]] = None,
        status: str = "completed",
        capability_id: Optional[int] = None,
        ledger_ref: Optional[str] = None,
        outcome_reason: str = "",
    ) -> ActionResult:
        return cls(
            success=True,
            message=message,
            data=cls._build_data_payload(
                data,
                speakable_text=speakable_text,
                structured_data=structured_data,
                default_message=message,
            ),
            request_id=request_id,
            risk_level=risk_level,
            authority_class=authority_class,
            external_effect=external_effect,
            reversible=reversible,
            status=status,
            capability_id=capability_id,
            ledger_ref=ledger_ref,
            outcome_reason=outcome_reason,
        )

    @classmethod
    def failure(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        risk_level: str = "low",
        authority_class: str = "read_only",
        external_effect: bool = False,
        reversible: bool = True,
        speakable_text: str = "",
        structured_data: Optional[Dict[str, Any]] = None,
        status: str = "failed",
        capability_id: Optional[int] = None,
        ledger_ref: Optional[str] = None,
        outcome_reason: str = "",
    ) -> ActionResult:
        return cls(
            success=False,
            message=message,
            data=cls._build_data_payload(
                data,
                speakable_text=speakable_text,
                structured_data=structured_data,
                default_message=message,
            ),
            request_id=request_id,
            risk_level=risk_level,
            authority_class=authority_class,
            external_effect=external_effect,
            reversible=reversible,
            status=status,
            capability_id=capability_id,
            ledger_ref=ledger_ref,
            outcome_reason=outcome_reason or message,
        )

    @classmethod
    def refusal(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        risk_level: str = "low",
        authority_class: str = "read_only",
        external_effect: bool = False,
        reversible: bool = True,
        speakable_text: str = "",
        structured_data: Optional[Dict[str, Any]] = None,
        status: str = "refused",
        capability_id: Optional[int] = None,
        ledger_ref: Optional[str] = None,
        outcome_reason: str = "",
    ) -> ActionResult:
        return cls(
            success=False,
            message=message,
            data=cls._build_data_payload(
                data,
                speakable_text=speakable_text,
                structured_data=structured_data,
                default_message=message,
            ),
            request_id=request_id,
            risk_level=risk_level,
            authority_class=authority_class,
            external_effect=external_effect,
            reversible=reversible,
            status=status,
            capability_id=capability_id,
            ledger_ref=ledger_ref,
            outcome_reason=outcome_reason or message,
        )

    @property
    def user_message(self) -> str:
        return self.message

    @property
    def speakable_text(self) -> str:
        payload = self._coerce_data_dict(self.data)
        value = str(payload.get("speakable_text") or "").strip()
        return value or self.message

    @property
    def structured_data(self) -> Dict[str, Any]:
        payload = self._coerce_data_dict(self.data)
        nested = payload.get("structured_data")
        if isinstance(nested, dict):
            return dict(nested)
        return self._extract_structured_data(payload)

    def normalize(
        self,
        *,
        request_id: Optional[str] = None,
        capability_id: Optional[int] = None,
        authority_class: Optional[str] = None,
        ledger_ref: Optional[str] = None,
        status: Optional[str] = None,
        outcome_reason: Optional[str] = None,
    ) -> ActionResult:
        self.request_id = str(request_id or self.request_id or "").strip() or None
        if capability_id is not None:
            self.capability_id = int(capability_id)
        elif self.capability_id is not None:
            self.capability_id = int(self.capability_id)
        if authority_class:
            self.authority_class = str(authority_class).strip() or self.authority_class
        self.ledger_ref = str(ledger_ref or self.ledger_ref or "").strip() or None
        self.status = self._normalized_status(status or self.status, success=self.success)
        if outcome_reason is not None:
            self.outcome_reason = str(outcome_reason or "").strip()
        elif not self.outcome_reason and not self.success:
            self.outcome_reason = str(self.message or "").strip()
        self.data = self._build_data_payload(
            self.data,
            speakable_text=self.speakable_text,
            structured_data=self.structured_data,
            default_message=self.message,
        )
        return self

    def to_contract_dict(self) -> Dict[str, Any]:
        return {
            "success": bool(self.success),
            "status": self.status,
            "user_message": str(self.user_message or ""),
            "speakable_text": str(self.speakable_text or ""),
            "structured_data": dict(self.structured_data or {}),
            "risk_level": str(self.risk_level or "low"),
            "authority_class": str(self.authority_class or "read_only"),
            "external_effect": bool(self.external_effect),
            "reversible": bool(self.reversible),
            "request_id": str(self.request_id or ""),
            "capability_id": self.capability_id,
            "ledger_ref": str(self.ledger_ref or ""),
            "outcome_reason": str(self.outcome_reason or ""),
        }

    @staticmethod
    def _normalized_status(raw_status: str, *, success: bool) -> str:
        value = str(raw_status or "").strip().lower()
        if value in {"completed", "failed", "refused"}:
            return value
        return "completed" if success else "failed"

    @classmethod
    def _build_data_payload(
        cls,
        data: Optional[Dict[str, Any]],
        *,
        speakable_text: str,
        structured_data: Optional[Dict[str, Any]],
        default_message: str,
    ) -> Dict[str, Any]:
        payload = cls._coerce_data_dict(data)
        resolved_structured = (
            dict(structured_data)
            if isinstance(structured_data, dict)
            else cls._extract_structured_data(payload)
        )
        payload["structured_data"] = resolved_structured
        resolved_speakable = str(speakable_text or payload.get("speakable_text") or default_message or "").strip()
        payload["speakable_text"] = resolved_speakable
        return payload

    @staticmethod
    def _coerce_data_dict(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(data, dict):
            return dict(data)
        return {}

    @staticmethod
    def _extract_structured_data(payload: Dict[str, Any]) -> Dict[str, Any]:
        nested = payload.get("structured_data")
        if isinstance(nested, dict):
            return dict(nested)
        return {
            key: value
            for key, value in payload.items()
            if key not in {"structured_data", "speakable_text"}
        }
