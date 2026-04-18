# tests/certification/cap_64_send_email_draft/test_p3_integration.py
"""
Phase 3 — Integration certification for capability 64 (send_email_draft).

Tests the FULL Governor spine:
  GovernorMediator → CapabilityRegistry → ExecuteBoundary
  → LedgerWriter → SendEmailDraftExecutor → ActionResult

The executor's OS side-effects (mailto: open, LLM call) are mocked so the
test runs offline without opening a mail client.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src.governor.governor import Governor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CONFIRMED_PARAMS = {
    "to": "integration-test@example.com",
    "subject": "Integration test subject",
    "body_intent": "explain the integration test",
    "confirmed": True,
}

_UNCONFIRMED_PARAMS = {
    "to": "integration-test@example.com",
    "subject": "Should be blocked",
}


def _make_governor() -> Governor:
    return Governor()


# ---------------------------------------------------------------------------
# Registry / capability checks
# ---------------------------------------------------------------------------

def test_cap_64_is_registered():
    gov = _make_governor()
    cap = gov.registry.get(64)
    assert cap is not None
    assert cap.name == "send_email_draft"


def test_cap_64_is_enabled():
    gov = _make_governor()
    assert gov.registry.is_enabled(64) is True


def test_cap_64_has_correct_authority_class():
    gov = _make_governor()
    cap = gov.registry.get(64)
    assert str(cap.authority_class) == "persistent_change"


def test_cap_64_requires_confirmation():
    gov = _make_governor()
    cap = gov.registry.get(64)
    assert cap.requires_confirmation is True


# ---------------------------------------------------------------------------
# Confirmation gate
# ---------------------------------------------------------------------------

def test_unconfirmed_call_is_refused_by_governor():
    """The governor must refuse cap 64 when confirmed=True is absent."""
    gov = _make_governor()
    result = gov.handle_governed_invocation(64, _UNCONFIRMED_PARAMS)
    assert result.success is False
    assert "confirm" in result.message.lower()


def test_confirmed_false_is_refused_by_governor():
    gov = _make_governor()
    params = {**_UNCONFIRMED_PARAMS, "confirmed": False}
    result = gov.handle_governed_invocation(64, params)
    assert result.success is False
    assert "confirm" in result.message.lower()


# ---------------------------------------------------------------------------
# Confirmed happy-path — full spine
# ---------------------------------------------------------------------------

def test_confirmed_call_passes_through_full_spine():
    """With confirmed=True and mocked executor side-effects, governor succeeds."""
    gov = _make_governor()

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Integration body text"),
        patch("src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto", return_value=True),
    ):
        result = gov.handle_governed_invocation(64, _CONFIRMED_PARAMS)

    assert result.success is True
    assert result.authority_class == "persistent_change"
    assert result.external_effect is True
    assert result.reversible is False


def test_full_spine_ledger_receives_action_attempted():
    """The governor must log ACTION_ATTEMPTED before dispatch."""
    gov = _make_governor()
    logged_types: list[str] = []

    original_log = gov.ledger.log_event

    def _capture(event_type, payload):
        logged_types.append(event_type)
        return original_log(event_type, payload)

    gov.ledger.log_event = _capture

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="body"),
        patch("src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto", return_value=True),
    ):
        gov.handle_governed_invocation(64, _CONFIRMED_PARAMS)

    assert "ACTION_ATTEMPTED" in logged_types
    assert "ACTION_COMPLETED" in logged_types


def test_full_spine_result_has_request_id():
    gov = _make_governor()
    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="body"),
        patch("src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto", return_value=True),
    ):
        result = gov.handle_governed_invocation(64, _CONFIRMED_PARAMS)
    assert result.request_id is not None
    assert len(result.request_id) > 0


# ---------------------------------------------------------------------------
# Governance fields enforced by the governor spine
# ---------------------------------------------------------------------------

def test_governor_normalizes_risk_level_on_result():
    gov = _make_governor()
    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="body"),
        patch("src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto", return_value=True),
    ):
        result = gov.handle_governed_invocation(64, _CONFIRMED_PARAMS)
    assert result.risk_level == "confirm"


def test_governor_normalizes_external_effect_true():
    gov = _make_governor()
    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="body"),
        patch("src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto", return_value=True),
    ):
        result = gov.handle_governed_invocation(64, _CONFIRMED_PARAMS)
    assert result.external_effect is True


# ---------------------------------------------------------------------------
# Failure path through governor
# ---------------------------------------------------------------------------

def test_mailto_open_failure_propagates_gracefully_through_governor():
    """Even if the OS call fails, the governor must return a handled result."""
    gov = _make_governor()
    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="body"),
        patch("src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto", return_value=False),
    ):
        result = gov.handle_governed_invocation(64, _CONFIRMED_PARAMS)
    # success=False is fine; what matters is no unhandled exception
    assert isinstance(result.success, bool)
    assert result.message


def test_unknown_capability_still_refused_with_cap_64_present():
    """Presence of cap 64 must not affect refusal of unknown caps."""
    gov = _make_governor()
    result = gov.handle_governed_invocation(9999, {})
    assert result.success is False
