"""Trust presentation for the Chief of Staff personality layer.

Provides natural-language descriptions of governance state for
Trust Panel surfaces. Personality framing enhances — never
replaces — the underlying receipt data.

Governance boundaries:
  - No imports from src.governor, src.executors, src.ledger
  - Receipts are never modified
  - Governance identity always visible
  - No trust-escalation language
  - Enforced by import boundary test
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


_TRUST_ESCALATION_PHRASES = (
    "just trust me",
    "if you let me",
    "if you trusted me",
    "i could do more",
    "unlock",
)

_NEGATIVE_WITHOUT_BY_DESIGN = re.compile(
    r"\b(can't|cannot|limited|restricted)\b(?!.*\bby design\b)",
    re.IGNORECASE,
)


class TrustPresenter:
    """Describes governance state in natural language.

    Presentation-only. Does not modify receipts, call
    capabilities, or access governed stores.
    """

    def describe_capability(
        self,
        cap_name: str,
        cap_id: int,
        authority_class: str,
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> dict[str, str]:
        friendly_name = cap_name.replace("_", " ")
        summary = f"{friendly_name} (Cap {cap_id})"
        detail = (
            f"This capability ({cap_name}, Cap {cap_id}) operates "
            f"under {authority_class} authority. "
            f"This is by design — Nova's governance ensures "
            f"actions are transparent and auditable."
        )
        return {"summary": summary, "detail": detail}

    def describe_receipt(
        self,
        receipt: dict[str, Any],
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> dict[str, str]:
        cap_name = str(receipt.get("capability_name", "")).strip()
        cap_id = receipt.get("capability_id", "")
        event_type = str(receipt.get("event_type", "")).strip()
        success = receipt.get("success", False)

        friendly_name = cap_name.replace("_", " ") if cap_name else "action"
        status = "completed successfully" if success else "did not complete"

        summary = f"{friendly_name} {status}"
        detail = (
            f"Event: {event_type}. "
            f"Capability: {cap_name} (Cap {cap_id}). "
            f"Outcome: {'success' if success else 'incomplete'}."
        )
        return {"summary": summary, "detail": detail}

    def explain_boundary(
        self,
        action_description: str,
        reason: str,
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> str:
        action = str(action_description or "").strip()
        why = str(reason or "").strip()
        return (
            f"Nova can see and analyze the relevant data, but "
            f"{action.lower()} is outside Nova's current authority — "
            f"this is by design. {why} "
            f"I can prepare the details so you can act on them quickly."
        )
