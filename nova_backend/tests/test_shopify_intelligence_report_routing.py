"""
Tests for GovernorMediator routing of capability 65 (shopify_intelligence_report).

Verifies that Shopify-intent phrases resolve to Invocation(capability_id=65, ...)
and non-Shopify phrases do not.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch

from src.governor.governor_mediator import GovernorMediator, Invocation

_ENABLED = frozenset({16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51,
                      52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65})


def _parse(text: str, session_id: str = "s1") -> object:
    with patch(
        "src.governor.governor_mediator._load_enabled_capability_ids",
        return_value=_ENABLED,
    ):
        return GovernorMediator.parse_governed_invocation(text, session_id=session_id)


# ---------------------------------------------------------------------------
# Positive routing — should yield Invocation(capability_id=65, ...)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "shopify report",
    "shopify stats",
    "shopify status",
    "shopify intelligence",
    "shopify summary",
    "shopify snapshot",
    "shopify brief",
    "shopify overview",
    "shopify store",
    "store report",
    "store stats",
    "store summary",
    "show my shopify data",
    "get shopify metrics",
    "fetch shopify orders",
    "show shopify products",
    "how's my store doing",
    "how is my store doing",
    "how's my shopify store doing",
])
def test_shopify_phrases_route_to_cap_65(phrase: str):
    result = _parse(phrase)
    assert isinstance(result, Invocation), f"Expected Invocation for: {phrase!r}"
    assert result.capability_id == 65


# ---------------------------------------------------------------------------
# Period extraction
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase,expected_period", [
    ("shopify report last 30 days", "last_30_days"),
    ("shopify stats for the past month", "last_30_days"),
    ("shopify report today", "today"),
    ("shopify stats today", "today"),
    ("shopify report last 90 days", "last_90_days"),
    ("shopify report quarter", "last_90_days"),
    ("shopify report", "last_7_days"),
    ("store stats", "last_7_days"),
])
def test_shopify_routing_extracts_period(phrase: str, expected_period: str):
    result = _parse(phrase)
    assert isinstance(result, Invocation), f"Expected Invocation for: {phrase!r}"
    assert result.capability_id == 65
    assert result.params.get("period") == expected_period


# ---------------------------------------------------------------------------
# Negative routing — should NOT route to cap 65
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "what's the weather today",
    "show me today's news",
    "morning brief",
    "draft an email to boss about shopify",
    "search for shopify",
    "what is shopify",
])
def test_non_shopify_phrases_do_not_route_to_cap_65(phrase: str):
    result = _parse(phrase)
    if isinstance(result, Invocation):
        assert result.capability_id != 65, f"Should not route to 65 for: {phrase!r}"
