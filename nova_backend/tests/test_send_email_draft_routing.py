# tests/test_send_email_draft_routing.py
"""
Tests for GovernorMediator routing of capability 64 (send_email_draft).

Verifies that email-intent phrases resolve to Invocation(capability_id=64, ...)
and non-email phrases do not.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch

from src.governor.governor_mediator import GovernorMediator, Invocation

# Patch the enabled-ids loader so cap 64 is always enabled for routing tests.
_ENABLED = frozenset({16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51,
                      52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64})


def _parse(text: str, session_id: str = "s1") -> object:
    with patch(
        "src.governor.governor_mediator._load_enabled_capability_ids",
        return_value=_ENABLED,
    ):
        return GovernorMediator.parse_governed_invocation(text, session_id=session_id)


# ---------------------------------------------------------------------------
# Positive routing cases — should yield Invocation(capability_id=64, ...)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase,expected_to,expected_subject", [
    ("draft an email to john@example.com about the project update",
     "john@example.com", "the project update"),
    ("compose an email to Sarah about scheduling a meeting",
     "Sarah", "scheduling a meeting"),
    ("write an email to boss@company.com about quarterly review",
     "boss@company.com", "quarterly review"),
    ("draft email to alice@work.com about onboarding",
     "alice@work.com", "onboarding"),
    ("prepare an email to team@corp.com about the deadline",
     "team@corp.com", "the deadline"),
    # Shorthand via EMAIL_SHORTHAND_RE
    ("email bob@example.com about the invoice",
     "bob@example.com", "the invoice"),
])
def test_email_phrases_route_to_cap_64(phrase, expected_to, expected_subject):
    result = _parse(phrase)
    assert isinstance(result, Invocation), f"Expected Invocation for: {phrase!r}"
    assert result.capability_id == 64
    assert result.params.get("to") == expected_to
    assert result.params.get("subject") == expected_subject


@pytest.mark.parametrize("phrase", [
    "draft an email",
    "compose an email",
    "write an email",
    "draft an e-mail",
])
def test_email_phrases_without_recipient_still_route_to_cap_64(phrase):
    result = _parse(phrase)
    assert isinstance(result, Invocation), f"Expected Invocation for: {phrase!r}"
    assert result.capability_id == 64


# ---------------------------------------------------------------------------
# Negative cases — must NOT route to cap 64
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "search for news",
    "weather",
    "open github",
    "volume up",
    "tell me about AI regulation",
    "memory list",
    "system check",
])
def test_non_email_phrases_do_not_route_to_cap_64(phrase):
    result = _parse(phrase)
    if isinstance(result, Invocation):
        assert result.capability_id != 64, (
            f"Phrase {phrase!r} incorrectly routed to cap 64"
        )


# ---------------------------------------------------------------------------
# Params structure
# ---------------------------------------------------------------------------

def test_routing_passes_session_id_in_params():
    result = _parse("draft an email to test@example.com about hello", session_id="sess-abc")
    assert isinstance(result, Invocation)
    assert result.params.get("session_id") == "sess-abc"


def test_routing_body_intent_equals_subject_when_only_subject_captured():
    result = _parse("draft an email to test@example.com about the budget")
    assert isinstance(result, Invocation)
    assert result.params.get("body_intent") == result.params.get("subject")
