# src/connectors/email_connector.py
"""
Email Connector — interface stub for inbox_check (Phase 8+).

This module defines the protocol that an email integration must implement
to enable the `inbox_check` home-agent template in OpenClaw.

Status: STUB — not yet connected.
The `inbox_check` template in the agent runner is currently blocked until a
compliant implementation of this interface is provided and wired into
`openclaw/agent_runner.py`.

Implementation requirements for a real connector:
  1. Implement `EmailConnector` (subclass or duck-type).
  2. Register the instance via `set_email_connector(instance)` at startup.
  3. The connector must NOT store credentials in plain text in the repo.
     Use environment variables or a secrets manager.
  4. All network I/O must go through the governor's NetworkMediator when
     invoked from a governed capability path.
  5. The returned `EmailInboxSummary` must be serialisable to JSON.

Environment variables expected by a future implementation:
  NOVA_EMAIL_PROVIDER  — e.g. "imap", "gmail_api", "outlook_api"
  NOVA_EMAIL_HOST      — IMAP host (if IMAP provider)
  NOVA_EMAIL_PORT      — IMAP port (default 993)
  NOVA_EMAIL_USER      — mailbox address
  NOVA_EMAIL_SECRET    — app-password or OAuth token (injected at runtime)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EmailMessage:
    """Minimal representation of a single inbox message for the agent layer."""

    message_id: str
    subject: str
    sender: str
    received_at: str          # ISO 8601 UTC
    snippet: str              # First ~200 chars of body
    is_unread: bool = True
    labels: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "subject": self.subject,
            "sender": self.sender,
            "received_at": self.received_at,
            "snippet": self.snippet,
            "is_unread": self.is_unread,
            "labels": list(self.labels),
        }


@dataclass(frozen=True)
class EmailInboxSummary:
    """Summary returned by `fetch_inbox_summary`."""

    unread_count: int
    total_count: int
    messages: tuple[EmailMessage, ...]    # Most recent N messages
    provider_label: str                   # e.g. "Gmail", "IMAP"
    fetched_at: str                       # ISO 8601 UTC
    error: str = ""                       # Non-empty if partial failure

    def as_dict(self) -> dict[str, Any]:
        return {
            "unread_count": self.unread_count,
            "total_count": self.total_count,
            "messages": [m.as_dict() for m in self.messages],
            "provider_label": self.provider_label,
            "fetched_at": self.fetched_at,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

class EmailConnector:
    """
    Abstract base for email provider integrations.

    Implementations must be async-safe. All network I/O should be awaitable.
    Raise `EmailConnectorError` for recoverable failures (auth, timeout, rate
    limit). Raise `NotImplementedError` for unimplemented optional methods.
    """

    @property
    def provider_label(self) -> str:
        """Human-readable provider name shown in the agent inbox card."""
        raise NotImplementedError

    @property
    def is_configured(self) -> bool:
        """Return True if all required env vars / credentials are present."""
        raise NotImplementedError

    async def fetch_inbox_summary(
        self,
        *,
        max_messages: int = 10,
        unread_only: bool = False,
    ) -> EmailInboxSummary:
        """
        Fetch a summary of recent inbox messages.

        Args:
            max_messages: Maximum number of messages to return.
            unread_only: If True, only return unread messages.

        Returns:
            EmailInboxSummary with the fetched messages and metadata.

        Raises:
            EmailConnectorError: On recoverable failure (auth, network, etc.).
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement fetch_inbox_summary. "
            "Provide a concrete EmailConnector implementation."
        )

    async def health_check(self) -> dict[str, Any]:
        """
        Return a dict with at minimum: {'ok': bool, 'label': str}.
        Used by the status dashboard to show connector readiness.
        """
        raise NotImplementedError


class EmailConnectorError(Exception):
    """Raised by EmailConnector on recoverable failures."""


# ---------------------------------------------------------------------------
# Singleton registry
# ---------------------------------------------------------------------------

_email_connector: EmailConnector | None = None


def get_email_connector() -> EmailConnector | None:
    """Return the registered email connector, or None if not yet configured."""
    return _email_connector


def set_email_connector(connector: EmailConnector) -> None:
    """Register the active email connector at startup."""
    global _email_connector
    if not isinstance(connector, EmailConnector):
        raise TypeError(
            f"set_email_connector requires an EmailConnector instance, got {type(connector)}"
        )
    _email_connector = connector


def is_email_connected() -> bool:
    """True if an email connector is registered and reports itself as configured."""
    connector = _email_connector
    if connector is None:
        return False
    try:
        return bool(connector.is_configured)
    except Exception:
        return False
