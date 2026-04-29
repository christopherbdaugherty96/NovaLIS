"""Read-only Brain environment planning schemas.

These models make the Brain architecture testable without changing runtime
routing, Governor behavior, or execution authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class EnvironmentType(_StringEnum):
    LOCAL_CONVERSATION = "local_conversation"
    LOCAL_RUNTIME_TRUTH = "local_runtime_truth"
    LOCAL_MEMORY = "local_memory"
    LOCAL_PROJECT_DOCS = "local_project_docs"
    LOCAL_LEDGER = "local_ledger"
    LOCAL_DASHBOARD = "local_dashboard"
    LOCAL_FILESYSTEM = "local_filesystem"
    LOCAL_SCREEN = "local_screen"
    LOCAL_OS_CONTROLS = "local_os_controls"
    LOCAL_MAIL_CLIENT = "local_mail_client"
    WEB_SEARCH = "web_search"
    WEBSITE_OPEN = "website_open"
    NEWS_API = "news_api"
    WEATHER_API = "weather_api"
    CALENDAR_READ = "calendar_read"
    SHOPIFY_READ_ONLY = "shopify_read_only"
    OPENCLAW_ISOLATED_BROWSER = "openclaw_isolated_browser"
    BROWSER_USE_TEST_BROWSER = "browser_use_test_browser"
    PERSONAL_BROWSER_SESSION = "personal_browser_session"
    EMAIL_DRAFT = "email_draft"
    EMAIL_SEND_FUTURE = "email_send_future"
    SHOPIFY_WRITE_FUTURE = "shopify_write_future"
    CALENDAR_WRITE_FUTURE = "calendar_write_future"
    FORM_SUBMIT = "form_submit"
    PURCHASE_PAYMENT = "purchase_payment"
    ACCOUNT_CHANGE = "account_change"


class AuthorityTier(_StringEnum):
    NONE = "none"
    LOCAL_READ = "local_read"
    NETWORK_READ = "network_read"
    ACCOUNT_READ = "account_read"
    LOCAL_DEVICE_EFFECT = "local_device_effect"
    EXTERNAL_EFFECT_DRAFT = "external_effect_draft"
    BROWSER_INTERACTION = "browser_interaction"
    ACCOUNT_WRITE = "account_write"
    BLOCKED_FUTURE = "blocked_future"


class AllowedStatus(_StringEnum):
    ALLOWED = "allowed"
    NEEDS_CLARIFICATION = "needs_clarification"
    NEEDS_CONFIRMATION = "needs_confirmation"
    SETUP_REQUIRED = "setup_required"
    BLOCKED = "blocked"
    FUTURE_ONLY = "future_only"
    DRY_RUN_ONLY = "dry_run_only"


@dataclass(frozen=True)
class EnvironmentOption:
    environment: EnvironmentType
    confidence: float
    risk_level: str
    authority_tier: AuthorityTier
    capability_needed: str = ""
    requires_confirmation: bool = False
    reason: str = ""


@dataclass(frozen=True)
class ClarificationQuestion:
    question: str
    missing_fields: list[str] = field(default_factory=list)
    assumptions_to_avoid: list[str] = field(default_factory=list)
    safe_partial_path: str = ""


@dataclass(frozen=True)
class CapabilityContract:
    capability_id: int | None
    name: str
    environment: EnvironmentType
    authority_tier: AuthorityTier
    can: list[str] = field(default_factory=list)
    cannot: list[str] = field(default_factory=list)
    required_setup: list[str] = field(default_factory=list)
    confirmation_required: bool = False
    expected_receipts: list[str] = field(default_factory=list)
    fallbacks: list[str] = field(default_factory=list)
    known_failure_modes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    description: str
    environment: EnvironmentType
    capability_needed: str = ""
    authority_required: AuthorityTier = AuthorityTier.NONE
    confirmation_required: bool = False
    proof_required: list[str] = field(default_factory=list)
    fallback_step: str = ""


@dataclass(frozen=True)
class EnvironmentRequest:
    task_id: str
    task: str
    task_type: str
    requested_environment: EnvironmentType
    reason: str
    authority_required: AuthorityTier
    capability_needed: str = ""
    confirmation_required: bool = False
    setup_required: list[str] = field(default_factory=list)
    proof_required: list[str] = field(default_factory=list)
    confidence: float = 0.0
    risk_level: str = ""
    fallback_ladder: list[str] = field(default_factory=list)
    allowed_status: AllowedStatus = AllowedStatus.DRY_RUN_ONLY
    next_safe_step: str = ""


@dataclass(frozen=True)
class BrainDryRun:
    task: str
    clarification: ClarificationQuestion | None = None
    environment_options: list[EnvironmentOption] = field(default_factory=list)
    selected_environment: EnvironmentType | None = None
    plan_steps: list[PlanStep] = field(default_factory=list)
    capability_contracts: list[CapabilityContract] = field(default_factory=list)
    confirmation_points: list[str] = field(default_factory=list)
    proof_expected: list[str] = field(default_factory=list)
    fallback_ladder: list[str] = field(default_factory=list)
    will_not_do: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


@dataclass(frozen=True)
class BrainTraceEvent:
    event_type: str
    timestamp: str
    task_id: str
    route: str
    environment: EnvironmentType
    capability: str
    authority_tier: AuthorityTier
    status: AllowedStatus
    receipt_id: str | None = None
    note: str = ""

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        task_id: str,
        route: str,
        environment: EnvironmentType,
        capability: str,
        authority_tier: AuthorityTier,
        status: AllowedStatus,
        receipt_id: str | None = None,
        note: str = "",
    ) -> "BrainTraceEvent":
        return cls(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            route=route,
            environment=environment,
            capability=capability,
            authority_tier=authority_tier,
            status=status,
            receipt_id=receipt_id,
            note=note,
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(self)


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_to_primitive(item) for item in value)
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    return value

