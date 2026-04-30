"""Deterministic Brain task clarification and boundary wording.

This module is intentionally read-only. It does not route, authorize, invoke
tools, call the Governor, or execute capabilities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TaskClarification:
    matched: bool
    response: str
    reason: str = ""
    missing_fields: list[str] = field(default_factory=list)
    environment_hint: str = ""
    authority_hint: str = ""
    severity: str = "info"


PERSONAL_ACCOUNT_BOUNDARY = (
    "That would require a personal account/browser/account-write environment. "
    "I can outline the steps or prepare a dry-run plan, but I cannot change account settings "
    "without an explicit governed capability, confirmation, and proof. No execution has started."
)

BROWSER_AMBIGUITY_BOUNDARY = (
    "Which two public websites should I compare? If this only needs public information, "
    "I can use governed search/open-website style paths. If you want browser automation, "
    "that would be an OpenClaw isolated-browser environment and would require a governed "
    "plan/confirmation."
)

BROWSER_AUTOMATION_BOUNDARY = (
    "Browser automation would be an OpenClaw isolated-browser environment and would require "
    "a governed plan/confirmation. Tell me the public websites or URLs to compare, and I can "
    "keep the next step bounded. No browser automation has started."
)

SHOPIFY_READ_ONLY_BOUNDARY = (
    "Current Shopify support is read-only reporting/intelligence. I cannot change products, "
    "orders, customers, refunds, or fulfillment through the current Cap 65 path."
)

SHOPIFY_REPORT_BOUNDARY = (
    "Nova can produce a read-only Shopify intelligence report if Cap 65 is configured with "
    "the required Shopify environment variables. This path is read-only: it does not change "
    "products, orders, customers, refunds, or fulfillment."
)

SHOPIFY_WRITE_BOUNDARY = (
    "Current Shopify support is read-only reporting/intelligence. I cannot change product "
    "prices with the current Cap 65 path. I can help draft manual steps or prepare a future "
    "dry-run plan, but I will not write to Shopify."
)

EMAIL_DRAFT_BOUNDARY = (
    "I can prepare a local draft, but Nova does not send email. Opening a draft requires "
    "confirmation, and you manually review/send or close it."
)

MEMORY_BOUNDARY = (
    "Memory can help Nova understand context, preferences, and project continuity. Memory "
    "cannot authorize actions. Governed actions still require capability checks, confirmation "
    "when needed, and receipts."
)

LOCAL_SELF_DESCRIPTION = (
    "Nova is a governed local AI system. It can explain, converse, search with sources, manage "
    "memory/context, show receipts/proof, and use governed capabilities.\n\n"
    "Actions stay bounded by capability checks. Email is local draft-only and manual-send. "
    "Shopify is read-only if configured. OpenClaw is an environment/future governed execution "
    "lane, not the Brain. Full Brain runtime routing is not live yet."
)

_CONTRACTOR_SERVICE_RE = re.compile(
    r"\b(?:contractors?|hvac|plumbers?|electricians?|roofers?|barbers?|companies|local\s+services?)\b",
    re.IGNORECASE,
)
_OUTREACH_RE = re.compile(r"\b(?:draft|email|message|outreach|write)\b", re.IGNORECASE)
_LOCATION_RE = re.compile(
    r"\b(?:in|near|around|serving|service\s+area|within)\s+[a-z][a-z0-9 .'-]{2,}\b",
    re.IGNORECASE,
)
_PERSONAL_ACCOUNT_RE = re.compile(
    r"\b(?:log\s*in|login|sign\s*in|go\s+into|open\s+my\s+account|my\s+account|my\s+profile)\b"
    r".{0,80}\b(?:change|update|edit|delete|submit|settings?|billing|password|profile)\b"
    r"|\b(?:change|update|edit|delete)\s+my\s+(?:password|billing|account|settings?|profile)\b"
    r"|\b(?:submit\s+this\s+form\s+for\s+me|buy\s+this|purchase\s+this|delete\s+my\s+account)\b",
    re.IGNORECASE,
)
_CREDENTIALS_RE = re.compile(r"\b(?:password|credentials?|login details?)\b", re.IGNORECASE)
_BROWSER_COMPARE_RE = re.compile(
    r"\b(?:(?:use|open|launch)\s+(?:the\s+)?browser|openclaw|go\s+to)\b.{0,80}\b(?:compare|review|analy[sz]e)\b"
    r"|\b(?:compare|review|analy[sz]e)\b.{0,80}\b(?:websites?|sites?|urls?)\b",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"\bhttps?://[^\s,]+|\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b", re.IGNORECASE)
_OPENCLAW_RE = re.compile(r"\bopenclaw|browser\s+automation|automate\s+(?:the\s+)?browser\b", re.IGNORECASE)
_SHOPIFY_RE = re.compile(r"\bshopify\b", re.IGNORECASE)
_SHOPIFY_REPORT_RE = re.compile(r"\b(?:create|make|generate|produce|build)?\s*(?:a\s+)?shopify\s+(?:report|intelligence|summary)\b", re.IGNORECASE)
_SHOPIFY_WRITE_RE = re.compile(
    r"\b(?:change|update|edit|refund|fulfill|delete|create|write|mutate)\b.{0,80}\b(?:shopify|product|price|inventory|order|customer|discount|fulfillment|refund)\b"
    r"|\b(?:shopify\b.{0,80})?(?:change|update|edit)\b.{0,80}\b(?:product\s+price|price|inventory)\b"
    r"|\b(?:refund\s+an?\s+order|fulfill\s+an?\s+order|delete\s+a\s+customer|create\s+a\s+discount\s+code)\b",
    re.IGNORECASE,
)
_MEMORY_ALLOWED_RE = re.compile(
    r"^\s*(?:what\s+is\s+)?memory\s+(?:allowed\s+to\s+do|allowed\s+for|allowed)\s*[.?!]*\s*$"
    r"|^\s*what\s+is\s+memory\s+allowed\s+to\s+do\s*[.?!]*\s*$",
    re.IGNORECASE,
)
_LOCAL_SELF_DESCRIPTION_RE = re.compile(
    r"^\s*(?:explain|tell\s+me)\s+what\s+nova\s+can\s+do\s*[.?!]*\s*$",
    re.IGNORECASE,
)
_EMAIL_DRAFT_COMPLETE_RE = re.compile(
    r"\bdraft\s+an?\s+email\s+to\s+[\w.+-]+@[\w.-]+\.[a-z]{2,}\b.{0,120}\b(?:about|regarding|for)\b",
    re.IGNORECASE,
)
_EMAIL_DRAFT_REQUEST_RE = re.compile(
    r"\b(?:draft|write|compose)\s+an?\s+email\b|\bemail\s+them\b|\bwrite\s+(?:an?\s+)?outreach\b",
    re.IGNORECASE,
)
_EMAIL_RECIPIENT_RE = re.compile(r"\b(?:to\s+[\w.+-]+@[\w.-]+\.[a-z]{2,}|to\s+[^.?!,]{2,60})\b", re.IGNORECASE)
_EMAIL_TOPIC_RE = re.compile(r"\b(?:about|regarding|re:|for)\s+[^.?!]{3,}\b", re.IGNORECASE)


_QUICK_SKIP_RE = re.compile(
    r"^\s*(?:what|how|why|when|where|who|tell\s+me|show\s+me|what's|what\s+is)\b",
    re.IGNORECASE,
)
_QUICK_SKIP_KEYWORDS = frozenset(
    ("shopify", "browser", "login", "log in", "account", "email", "openclaw", "credentials", "memory")
)


def clarify_task(message: str) -> TaskClarification:
    """Return a deterministic clarification/boundary response when needed."""
    text = (message or "").strip()
    if not text:
        return TaskClarification(matched=False, response="")
    if _QUICK_SKIP_RE.match(text) and not any(kw in text.lower() for kw in _QUICK_SKIP_KEYWORDS):
        return TaskClarification(matched=False, response="")

    if _EMAIL_DRAFT_COMPLETE_RE.search(text):
        return TaskClarification(matched=False, response="")

    if _MEMORY_ALLOWED_RE.search(text):
        return TaskClarification(
            matched=True,
            response=MEMORY_BOUNDARY,
            reason="memory_boundary",
            environment_hint="local_memory",
            authority_hint="none",
            severity="info",
        )

    if _LOCAL_SELF_DESCRIPTION_RE.search(text):
        return TaskClarification(
            matched=True,
            response=LOCAL_SELF_DESCRIPTION,
            reason="local_self_description",
            environment_hint="local_conversation",
            authority_hint="none",
            severity="info",
        )

    if _PERSONAL_ACCOUNT_RE.search(text):
        return TaskClarification(
            matched=True,
            response=PERSONAL_ACCOUNT_BOUNDARY,
            reason="personal_account_write_boundary",
            missing_fields=[],
            environment_hint="personal_browser_session",
            authority_hint="account_write",
            severity="p1",
        )

    if _SHOPIFY_REPORT_RE.search(text):
        return TaskClarification(
            matched=True,
            response=SHOPIFY_REPORT_BOUNDARY,
            reason="shopify_read_only_report_boundary",
            environment_hint="shopify_read_only",
            authority_hint="account_read",
            severity="info",
        )

    _SHOPIFY_WRITE_VERB_RE = re.compile(
        r"\b(?:write|change|update|edit|delete|refund|fulfill|create|mutate)\b", re.IGNORECASE
    )
    if _SHOPIFY_RE.search(text) and (
        _SHOPIFY_WRITE_RE.search(text) or _SHOPIFY_WRITE_VERB_RE.search(text) or "product price" in text.lower()
    ):
        return TaskClarification(
            matched=True,
            response=SHOPIFY_WRITE_BOUNDARY,
            reason="shopify_write_blocked",
            environment_hint="shopify_write_future",
            authority_hint="blocked_future",
            severity="p1",
        )

    if _BROWSER_COMPARE_RE.search(text):
        urls = _URL_RE.findall(text)
        if _OPENCLAW_RE.search(text):
            return TaskClarification(
                matched=True,
                response=BROWSER_AUTOMATION_BOUNDARY,
                missing_fields=[] if len(urls) >= 2 else ["websites"],
                reason="browser_automation_boundary",
                environment_hint="openclaw_isolated_browser",
                authority_hint="browser_interaction",
                severity="p1",
            )
        if len(urls) < 2:
            return TaskClarification(
                matched=True,
                response=BROWSER_AMBIGUITY_BOUNDARY,
                missing_fields=["websites"],
                reason="browser_compare_missing_websites",
                environment_hint="website_open",
                authority_hint="network_read",
                severity="p1",
            )

    if _CONTRACTOR_SERVICE_RE.search(text) and _OUTREACH_RE.search(text) and not _LOCATION_RE.search(text):
        return TaskClarification(
            matched=True,
            response=(
                "What city or service area should I search in?\n\n"
                "After that, I can search for candidates and prepare a draft plan, "
                "but I will not open an email draft without confirmation."
            ),
            reason="contractor_outreach_missing_location",
            missing_fields=["city_or_service_area"],
            environment_hint="web_search_then_email_draft",
            authority_hint="network_read_then_external_effect_draft",
            severity="p1",
        )
    if _CONTRACTOR_SERVICE_RE.search(text) and _OUTREACH_RE.search(text) and _LOCATION_RE.search(text):
        return TaskClarification(matched=False, response="")

    if _EMAIL_DRAFT_REQUEST_RE.search(text):
        missing: list[str] = []
        if not _EMAIL_RECIPIENT_RE.search(text):
            missing.append("recipient")
        if not _EMAIL_TOPIC_RE.search(text):
            missing.append("topic_or_context")
        if missing:
            if missing == ["recipient"]:
                question = "Who should the email draft be addressed to?"
            elif missing == ["topic_or_context"]:
                question = "What should the email draft be about?"
            else:
                question = "Who should the email draft be addressed to, and what should it be about?"
            return TaskClarification(
                matched=True,
                response=f"{question}\n\n{EMAIL_DRAFT_BOUNDARY}",
                reason="email_draft_missing_required_field",
                missing_fields=missing,
                environment_hint="email_draft",
                authority_hint="external_effect_draft",
                severity="info",
            )

    if _CREDENTIALS_RE.search(text) and re.search(r"\b(?:give|send|share|enter|use|ask)\b", text, re.IGNORECASE):
        return TaskClarification(
            matched=True,
            response=(
                f"{PERSONAL_ACCOUNT_BOUNDARY} I will not ask for passwords or credentials."
            ),
            reason="credential_boundary",
            environment_hint="personal_browser_session",
            authority_hint="account_write",
            severity="p1",
        )

    return TaskClarification(matched=False, response="")
