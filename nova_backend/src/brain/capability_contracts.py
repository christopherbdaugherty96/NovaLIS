"""Static Brain capability contract catalog.

Contracts describe what a capability can and cannot do. They are vocabulary for
planning and review only: looking up a contract does not authorize, route, or
execute anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.brain.environment_request import AuthorityTier, CapabilityContract, EnvironmentType


@dataclass(frozen=True)
class StaticCapabilityContract:
    """A stable catalog entry around the shared Brain CapabilityContract shape."""

    key: str
    contract: CapabilityContract
    current_state: str = "static_catalog_only"

    @property
    def capability_id(self) -> int | None:
        return self.contract.capability_id

    @property
    def name(self) -> str:
        return self.contract.name


class CapabilityContractNotFound(KeyError):
    """Raised when a required static capability contract is unavailable."""


CAP16_GOVERNED_WEB_SEARCH = StaticCapabilityContract(
    key="cap16_governed_web_search",
    current_state="active_runtime_capability_static_contract",
    contract=CapabilityContract(
        capability_id=16,
        name="governed_web_search",
        environment=EnvironmentType.WEB_SEARCH,
        authority_tier=AuthorityTier.NETWORK_READ,
        can=[
            "perform governed web/network read search",
            "return source-backed answers",
            "preserve visible source URLs",
            "report weak/no evidence",
            "use fallback when synthesis/source reads are limited",
        ],
        cannot=[
            "bypass NetworkMediator",
            "browse uncontrolled sites outside the governed path",
            "perform account actions",
            "treat stale memory as current proof",
            "guarantee current truth without sources",
        ],
        required_setup=[
            "search provider credentials if needed",
            "NetworkMediator path",
        ],
        confirmation_required=False,
        expected_receipts=[
            "search/action result data",
            "source URLs",
            "confidence/known/unclear fields where available",
        ],
        fallbacks=[
            "return partial source-backed answer",
            "state weak/no evidence honestly",
            "ask user to narrow or retry when budget/provider limits block synthesis",
        ],
        known_failure_modes=[
            "provider credentials missing",
            "NetworkMediator refusal",
            "source read timeout",
            "synthesis budget/CPU timeout",
            "weak or mismatched search results",
        ],
    ),
)

CAP64_SEND_EMAIL_DRAFT = StaticCapabilityContract(
    key="cap64_send_email_draft",
    current_state="active_runtime_capability_static_contract",
    contract=CapabilityContract(
        capability_id=64,
        name="send_email_draft",
        environment=EnvironmentType.EMAIL_DRAFT,
        authority_tier=AuthorityTier.EXTERNAL_EFFECT_DRAFT,
        can=[
            "open a local mail client draft through mailto after confirmation",
            "prefill recipient, subject, and body",
            "let user manually review/send",
        ],
        cannot=[
            "send email",
            "access inbox",
            "read Gmail",
            "use SMTP",
            "transmit autonomously",
            "mark email as sent",
            "forward email",
            "archive/delete/label email",
        ],
        required_setup=[
            "local mail client/mailto handler",
        ],
        confirmation_required=True,
        expected_receipts=[
            "EMAIL_DRAFT_CREATED",
            "EMAIL_DRAFT_FAILED",
            "confirmation/boundary receipt if existing system supports it",
        ],
        fallbacks=[
            "show draft text in chat",
            "user copy/pastes manually",
            "explain local mail client setup",
        ],
        known_failure_modes=[
            "missing recipient/subject/body context",
            "local mail client unavailable",
            "mailto handler failed to open",
            "local LLM draft generation unavailable",
        ],
    ),
)

CAP65_SHOPIFY_INTELLIGENCE_REPORT = StaticCapabilityContract(
    key="cap65_shopify_intelligence_report",
    current_state="active_runtime_capability_static_contract",
    contract=CapabilityContract(
        capability_id=65,
        name="shopify_intelligence_report",
        environment=EnvironmentType.SHOPIFY_READ_ONLY,
        authority_tier=AuthorityTier.ACCOUNT_READ,
        can=[
            "read configured Shopify data for intelligence/reporting if credentials exist",
            "produce read-only store/business report",
            "use NetworkMediator",
        ],
        cannot=[
            "write Shopify",
            "change product price",
            "update products",
            "fulfill orders",
            "refund orders",
            "create/delete products",
            "mutate store state",
        ],
        required_setup=[
            "NOVA_SHOPIFY_SHOP_DOMAIN",
            "NOVA_SHOPIFY_ACCESS_TOKEN",
        ],
        confirmation_required=False,
        expected_receipts=[
            "report generated / failed receipt if existing system supports it",
            "visible credential/setup missing response when not configured",
        ],
        fallbacks=[
            "explain required env vars",
            "produce manual checklist",
            "skip Shopify section in brief",
        ],
        known_failure_modes=[
            "Shopify environment variables missing",
            "invalid Shopify access token",
            "Shopify GraphQL error",
            "NetworkMediator refusal",
            "partial store snapshot",
        ],
    ),
)

CAP63_OPENCLAW_EXECUTE = StaticCapabilityContract(
    key="cap63_openclaw_execute",
    current_state="active_runtime_capability_static_contract",
    contract=CapabilityContract(
        capability_id=63,
        name="openclaw_execute",
        environment=EnvironmentType.OPENCLAW_ISOLATED_BROWSER,
        authority_tier=AuthorityTier.BROWSER_INTERACTION,
        can=[
            "route OpenClaw actions through governed capability path when enabled",
            "represent isolated browser/computer-use execution as a high-authority environment",
            "run approved bounded templates through the governed OpenClaw path",
        ],
        cannot=[
            "run as the Brain itself",
            "bypass Governor",
            "silently use personal browser sessions",
            "execute outside approved envelope/path",
            "perform broad autonomy by default",
        ],
        required_setup=[
            "enabled OpenClaw capability/runtime path",
            "approved template or governed execution envelope",
        ],
        confirmation_required=True,
        expected_receipts=[
            "governed OpenClaw action result",
            "template/run status where available",
            "screenshots before/after if a future approved browser execution path captures them",
        ],
        fallbacks=[
            "dry-run plan only",
            "manual step outline",
            "blocked explanation",
        ],
        known_failure_modes=[
            "unknown or unavailable template",
            "OpenClaw runtime unavailable",
            "execution envelope missing",
            "Governor or ExecuteBoundary refusal",
        ],
    ),
)

_CONTRACTS: tuple[StaticCapabilityContract, ...] = (
    CAP16_GOVERNED_WEB_SEARCH,
    CAP64_SEND_EMAIL_DRAFT,
    CAP65_SHOPIFY_INTELLIGENCE_REPORT,
    CAP63_OPENCLAW_EXECUTE,
)

_BY_KEY: dict[str, StaticCapabilityContract] = {
    entry.key.lower(): entry for entry in _CONTRACTS
}
_BY_NAME: dict[str, StaticCapabilityContract] = {
    entry.name.lower(): entry for entry in _CONTRACTS
}
_BY_ID: dict[int, StaticCapabilityContract] = {
    int(entry.capability_id): entry for entry in _CONTRACTS if entry.capability_id is not None
}


def list_capability_contracts() -> tuple[StaticCapabilityContract, ...]:
    """Return the static contract catalog in stable order."""
    return _CONTRACTS


def get_capability_contract(key_or_id: str | int) -> StaticCapabilityContract | None:
    """Return a known static contract, or None for unknown input."""
    if isinstance(key_or_id, int):
        return _BY_ID.get(key_or_id)
    normalized = str(key_or_id or "").strip().lower()
    if not normalized:
        return None
    if normalized.isdigit():
        return _BY_ID.get(int(normalized))
    return _BY_KEY.get(normalized) or _BY_NAME.get(normalized)


def require_capability_contract(key_or_id: str | int) -> StaticCapabilityContract:
    """Return a contract or fail closed with a clear unavailable error."""
    contract = get_capability_contract(key_or_id)
    if contract is None:
        raise CapabilityContractNotFound(f"Static capability contract unavailable: {key_or_id!r}")
    return contract


def capability_contract_summary(key_or_id: str | int) -> dict[str, object]:
    """Return a non-authorizing summary for UI, dry-run, or docs consumers."""
    entry = require_capability_contract(key_or_id)
    contract = entry.contract
    return {
        "key": entry.key,
        "capability_id": contract.capability_id,
        "name": contract.name,
        "environment": contract.environment.value,
        "authority_tier": contract.authority_tier.value,
        "confirmation_required": contract.confirmation_required,
        "current_state": entry.current_state,
        "can": list(contract.can),
        "cannot": list(contract.cannot),
        "required_setup": list(contract.required_setup),
        "expected_receipts": list(contract.expected_receipts),
        "fallbacks": list(contract.fallbacks),
        "known_failure_modes": list(contract.known_failure_modes),
        "non_authorizing": True,
    }


def contract_keys(entries: Iterable[StaticCapabilityContract] | None = None) -> tuple[str, ...]:
    """Return stable keys for tests and lightweight callers."""
    selected = _CONTRACTS if entries is None else tuple(entries)
    return tuple(entry.key for entry in selected)
