"""Non-executing OpenClaw delegation mediator skeleton.

This module is the first explicit boundary between Nova planning envelopes and
future OpenClaw work. It evaluates whether a request is safe enough for a
read-only delegated preview. It does not execute OpenClaw, call capabilities,
call the Governor, touch files, open browsers, or make network requests.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


_AUTHORITY_EFFECT_NONE = "none"
_PREVIEW_ALLOWED = "preview_allowed"
_BLOCKED = "blocked"

_BLOCKED_ACTIONS = (
    "browser_use",
    "computer_use",
    "filesystem_write",
    "external_write",
    "email_action",
    "calendar_action",
    "shopify_action",
    "account_action",
    "direct_cap63_shortcut",
)

_ACTION_TERMS = {
    "browser_use": ("browser", "webpage", "tab", "click", "navigate", "computer-use", "computer use"),
    "computer_use": ("mouse", "keyboard", "desktop", "screen control", "computer-use", "computer use"),
    "filesystem_write": ("write file", "edit file", "delete file", "move file", "rename file", "save file"),
    "external_write": ("submit", "publish", "purchase", "post", "send", "change setting", "update account"),
    "email_action": ("email", "inbox", "mailto", "send draft", "send message"),
    "calendar_action": ("calendar", "schedule", "meeting", "invite", "event"),
    "shopify_action": ("shopify", "product price", "inventory", "order", "store admin"),
    "account_action": ("login", "log in", "account", "password", "profile setting"),
    "direct_cap63_shortcut": ("cap 63", "cap63", "openclaw_execute", "direct cap 63"),
}


@dataclass(frozen=True)
class OpenClawDelegationEnvelope:
    request_text: str
    requested_actions: tuple[str, ...] = ()
    allowed_input_scope: tuple[str, ...] = ()
    read_only: bool = True
    browser_use: bool = False
    computer_use: bool = False
    filesystem_write: bool = False
    external_write: bool = False
    email_action: bool = False
    calendar_action: bool = False
    shopify_action: bool = False
    account_action: bool = False
    direct_cap63_shortcut: bool = False
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_text", str(self.request_text or "").strip())
        object.__setattr__(self, "requested_actions", _clean_tuple(self.requested_actions))
        object.__setattr__(self, "allowed_input_scope", _clean_tuple(self.allowed_input_scope))
        object.__setattr__(self, "metadata", _copy_public_mapping(self.metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class OpenClawMediatorDecision:
    decision: str
    preview_allowed: bool
    reason: str
    blocked_reasons: tuple[str, ...] = ()
    allowed_preview_actions: tuple[str, ...] = ()
    blocked_actions: tuple[str, ...] = ()
    required_boundaries: tuple[str, ...] = ()
    authority_effect: str = _AUTHORITY_EFFECT_NONE
    execution_performed: bool = False
    authorization_granted: bool = False
    openclaw_called: bool = False
    governor_called: bool = False
    capabilities_called: bool = False
    filesystem_touched: bool = False
    browser_opened: bool = False
    network_called: bool = False

    def __post_init__(self) -> None:
        if self.decision not in {_PREVIEW_ALLOWED, _BLOCKED}:
            raise ValueError("OpenClawMediatorDecision must be preview_allowed or blocked.")
        if self.authority_effect != _AUTHORITY_EFFECT_NONE:
            raise ValueError("OpenClawMediatorDecision must remain non-authorizing.")
        if self.execution_performed:
            raise ValueError("OpenClawMediatorDecision must not record execution.")
        if self.authorization_granted:
            raise ValueError("OpenClawMediatorDecision must not grant authorization.")
        if self.openclaw_called:
            raise ValueError("OpenClawMediatorDecision must not call OpenClaw.")
        if self.governor_called:
            raise ValueError("OpenClawMediatorDecision must not call the Governor.")
        if self.capabilities_called:
            raise ValueError("OpenClawMediatorDecision must not call capabilities.")
        if self.filesystem_touched:
            raise ValueError("OpenClawMediatorDecision must not touch files.")
        if self.browser_opened:
            raise ValueError("OpenClawMediatorDecision must not open browsers.")
        if self.network_called:
            raise ValueError("OpenClawMediatorDecision must not make network calls.")
        if self.preview_allowed and self.decision != _PREVIEW_ALLOWED:
            raise ValueError("Preview allowance must use the preview_allowed decision.")
        if self.preview_allowed and not self.allowed_preview_actions:
            raise ValueError("Preview allowance requires explicit preview actions.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class OpenClawMediatorReceipt:
    receipt_type: str
    request_text: str
    decision: str
    summary: str
    non_action_statement: str
    did_happen: tuple[str, ...]
    did_not_happen: tuple[str, ...]
    blocked_reasons: tuple[str, ...] = ()
    authority_effect: str = _AUTHORITY_EFFECT_NONE
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if self.receipt_type != "openclaw_mediator_preview":
            raise ValueError("OpenClawMediatorReceipt has an invalid receipt type.")
        if self.authority_effect != _AUTHORITY_EFFECT_NONE:
            raise ValueError("OpenClawMediatorReceipt must remain non-authorizing.")
        if self.execution_performed:
            raise ValueError("OpenClawMediatorReceipt must not record execution.")
        if self.authorization_granted:
            raise ValueError("OpenClawMediatorReceipt must not grant authorization.")
        if "OpenClaw was not executed." not in self.did_not_happen:
            raise ValueError("OpenClawMediatorReceipt must state that OpenClaw was not executed.")

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


class OpenClawMediator:
    """Evaluate future OpenClaw delegation envelopes without execution."""

    def evaluate(self, envelope: OpenClawDelegationEnvelope) -> OpenClawMediatorDecision:
        blocked_reasons: list[str] = []
        blocked_actions: list[str] = []

        if not envelope.request_text:
            blocked_reasons.append("missing_request_text")
        if not envelope.read_only:
            blocked_reasons.append("read_only_required")
            blocked_actions.append("non_read_only_delegation")
        if not envelope.allowed_input_scope:
            blocked_reasons.append("missing_allowed_input_scope")

        requested_text = " ".join((envelope.request_text, *envelope.requested_actions)).lower()
        for action in _BLOCKED_ACTIONS:
            if bool(getattr(envelope, action)) or _mentions_blocked_action(requested_text, action):
                blocked_reasons.append(f"{action}_blocked")
                blocked_actions.append(action)

        if blocked_reasons:
            clean_reasons = tuple(dict.fromkeys(blocked_reasons))
            clean_actions = tuple(dict.fromkeys(blocked_actions))
            return OpenClawMediatorDecision(
                decision=_BLOCKED,
                preview_allowed=False,
                reason="OpenClaw delegation preview is blocked by the mediator skeleton policy.",
                blocked_reasons=clean_reasons,
                allowed_preview_actions=(),
                blocked_actions=clean_actions,
                required_boundaries=_required_boundaries(),
            )

        return OpenClawMediatorDecision(
            decision=_PREVIEW_ALLOWED,
            preview_allowed=True,
            reason="Read-only delegated preview is allowed; execution remains blocked.",
            blocked_reasons=(),
            allowed_preview_actions=(
                "inspect caller-provided scope labels",
                "prepare a read-only delegation preview",
                "emit a non-action receipt",
            ),
            blocked_actions=_BLOCKED_ACTIONS,
            required_boundaries=_required_boundaries(),
        )

    def receipt_for(
        self,
        *,
        envelope: OpenClawDelegationEnvelope,
        decision: OpenClawMediatorDecision,
    ) -> OpenClawMediatorReceipt:
        did_happen = (
            "OpenClawMediator evaluated the delegation envelope.",
            "OpenClawMediator returned a policy decision.",
            "OpenClawMediator constructed this non-action receipt.",
        )
        did_not_happen = (
            "OpenClaw was not executed.",
            "No capability was called.",
            "The Governor was not called.",
            "No browser or computer-use action was performed.",
            "No filesystem write was performed.",
            "No email, calendar, Shopify, account, or external write action was performed.",
            "No network request was made.",
            "Cap 63 was not used as a shortcut.",
        )
        return OpenClawMediatorReceipt(
            receipt_type="openclaw_mediator_preview",
            request_text=envelope.request_text,
            decision=decision.decision,
            summary=(
                "Read-only OpenClaw preview was allowed without execution."
                if decision.preview_allowed
                else "OpenClaw preview was blocked without execution."
            ),
            non_action_statement="This receipt records a mediator policy decision only, not OpenClaw execution.",
            did_happen=did_happen,
            did_not_happen=did_not_happen,
            blocked_reasons=decision.blocked_reasons,
        )

    def evaluate_with_receipt(
        self,
        envelope: OpenClawDelegationEnvelope,
    ) -> tuple[OpenClawMediatorDecision, OpenClawMediatorReceipt]:
        decision = self.evaluate(envelope)
        return decision, self.receipt_for(envelope=envelope, decision=decision)


def _mentions_blocked_action(text: str, action: str) -> bool:
    terms = _ACTION_TERMS.get(action, ())
    normalized = " ".join(str(text or "").lower().split())
    return any(_contains_term(normalized, term) for term in terms)


def _contains_term(text: str, term: str) -> bool:
    normalized_term = " ".join(str(term or "").lower().split())
    if not normalized_term:
        return False
    if " " in normalized_term or "-" in normalized_term or "_" in normalized_term:
        return normalized_term in text
    return re.search(rf"\b{re.escape(normalized_term)}\b", text) is not None


def _required_boundaries() -> tuple[str, ...]:
    return (
        "explicit allowed input scope",
        "read-only delegation only",
        "no browser/computer-use",
        "no filesystem writes",
        "no external writes",
        "no direct Cap 63 shortcut",
        "receipt/non-action statement",
    )


def _clean_tuple(values: tuple[str, ...] | list[str] | Any) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        values = (values,)
    try:
        iterable = tuple(values)
    except TypeError:
        iterable = (values,)
    return tuple(str(item or "").strip() for item in iterable if str(item or "").strip())


def _copy_public_mapping(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _to_primitive(item) for key, item in value.items()}


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    return value


__all__ = [
    "OpenClawDelegationEnvelope",
    "OpenClawMediator",
    "OpenClawMediatorDecision",
    "OpenClawMediatorReceipt",
]
