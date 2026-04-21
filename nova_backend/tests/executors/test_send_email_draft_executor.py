# tests/executors/test_send_email_draft_executor.py
"""
Unit tests for SendEmailDraftExecutor (capability 64 — send_email_draft).

All tests are fully isolated: LLM calls and OS mailto: launch are monkey-patched
so the suite runs offline without opening any mail client.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.actions.action_result import ActionResult
from src.executors.send_email_draft_executor import SendEmailDraftExecutor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _req(params: dict, request_id: str = "req-email-1"):
    return SimpleNamespace(params=params, request_id=request_id)


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


def _make_executor(ledger=None):
    return SendEmailDraftExecutor(ledger=ledger or _FakeLedger())


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

def test_empty_params_returns_failure():
    ex = _make_executor()
    result = ex.execute(_req({}))
    assert result.success is False
    assert "email" in result.message.lower()


def test_empty_strings_returns_failure():
    ex = _make_executor()
    result = ex.execute(_req({"to": "", "subject": "", "body_intent": ""}))
    assert result.success is False


# ---------------------------------------------------------------------------
# Body generation tests (LLM mocked)
# ---------------------------------------------------------------------------

def test_generate_body_uses_llm_when_available():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Dear Team,\n\nPlease join the call.") as mock_llm,
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "team@example.com", "subject": "Standup call", "body_intent": "remind about standup"}))

    assert result.success is True
    mock_llm.assert_called_once()
    assert result.data["body"] == "Dear Team,\n\nPlease join the call."


def test_generate_body_falls_back_when_llm_raises():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", side_effect=RuntimeError("LLM offline")),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "alice@example.com", "subject": "Hello", "body_intent": "greet"}))

    assert result.success is True
    assert "Nova could not generate" in result.data["body"]


def test_generate_body_falls_back_when_llm_returns_empty():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="   "),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "alice@example.com", "subject": "Hello", "body_intent": "greet"}))

    assert result.success is True
    assert "Nova could not generate" in result.data["body"]


# ---------------------------------------------------------------------------
# mailto: URI construction
# ---------------------------------------------------------------------------

def test_build_mailto_with_all_fields():
    ex = _make_executor()
    uri = ex._build_mailto(to="bob@example.com", subject="Test", body="Hello Bob")
    # RFC 6068: '@' is safe in the mailto recipient — must not be percent-encoded.
    assert uri.startswith("mailto:bob@example.com")
    assert "subject=Test" in uri
    assert "body=Hello+Bob" in uri or "body=Hello%20Bob" in uri


def test_build_mailto_recipient_only():
    ex = _make_executor()
    uri = ex._build_mailto(to="carol@example.com", subject="", body="")
    assert uri == "mailto:carol@example.com"


def test_build_mailto_no_recipient():
    ex = _make_executor()
    uri = ex._build_mailto(to="", subject="Meeting", body="See you there")
    assert uri.startswith("mailto:?")
    assert "subject=Meeting" in uri


# ---------------------------------------------------------------------------
# Success path — mail client opens
# ---------------------------------------------------------------------------

def test_success_includes_to_and_subject_in_message():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body text"),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "dave@example.com", "subject": "Project update"}))

    assert result.success is True
    assert "dave@example.com" in result.message
    assert "Project update" in result.message
    assert result.data["mailto_opened"] is True


def test_success_result_has_correct_governance_fields():
    ex = _make_executor()

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body"),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "eve@example.com", "subject": "Hi"}))

    assert result.risk_level == "confirm"
    assert result.authority_class == "persistent_change"
    assert result.external_effect is True
    assert result.reversible is False


# ---------------------------------------------------------------------------
# Failure path — mail client won't open
# ---------------------------------------------------------------------------

def test_mailto_open_failure_returns_draft_inline():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body text"),
        patch.object(ex, "_open_mailto", return_value=False),
    ):
        result = ex.execute(_req({"to": "frank@example.com", "subject": "Invoice"}))

    assert result.success is False
    assert "frank@example.com" in result.message
    assert "Invoice" in result.message
    assert "Body text" in result.message
    assert result.data["mailto_opened"] is False


# ---------------------------------------------------------------------------
# Ledger events
# ---------------------------------------------------------------------------

def test_ledger_records_email_draft_created_on_success():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body"),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        ex.execute(_req({"to": "gina@example.com", "subject": "Hello"}))

    event_names = [name for name, _ in ledger.events]
    assert "EMAIL_DRAFT_CREATED" in event_names


def test_ledger_records_email_draft_failed_when_open_fails():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body"),
        patch.object(ex, "_open_mailto", return_value=False),
    ):
        ex.execute(_req({"to": "henry@example.com", "subject": "Hello"}))

    event_names = [name for name, _ in ledger.events]
    assert "EMAIL_DRAFT_FAILED" in event_names


def test_ledger_event_includes_to_and_subject():
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body"),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        ex.execute(_req({"to": "iris@example.com", "subject": "Test subject", "session_id": "s123"}))

    events = {name: payload for name, payload in ledger.events}
    assert "EMAIL_DRAFT_CREATED" in events
    payload = events["EMAIL_DRAFT_CREATED"]
    assert payload["to"] == "iris@example.com"
    assert payload["subject"] == "Test subject"
    assert payload["capability_id"] == 64


def test_ledger_failure_does_not_block_response():
    """LedgerWriter raising must not surface to the user."""
    bad_ledger = MagicMock()
    bad_ledger.log_event.side_effect = RuntimeError("disk full")
    ex = _make_executor(bad_ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body"),
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "joe@example.com", "subject": "Hi"}))

    assert result.success is True  # must still succeed despite ledger failure


# ---------------------------------------------------------------------------
# body_intent alias test
# ---------------------------------------------------------------------------

def test_body_intent_alias_body_is_accepted():
    """Executor accepts 'body' param as fallback for body_intent."""
    ledger = _FakeLedger()
    ex = _make_executor(ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Body from alias") as mock_llm,
        patch.object(ex, "_open_mailto", return_value=True),
    ):
        result = ex.execute(_req({"to": "kate@example.com", "body": "discuss Q3 results"}))

    assert result.success is True
    # generate_chat should have been called with the body intent in the prompt
    call_args = mock_llm.call_args[0][0]
    assert any("discuss Q3 results" in str(msg) for msg in call_args)
