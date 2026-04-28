"""
Tests for the PAUSED_SCOPE_RE guard in the thread-continuation router.

The guard prevents "continue Shopify" / "continue Auralis" from being
intercepted by CONTINUE_THREAD_RE and swallowing the turn before
run_general_chat_fallback can inject the paused-scope boundary block.

Unit tests cover the pattern directly; integration tests verify that
build_request_understanding returns PAUSED for the same inputs.
"""
from __future__ import annotations

import pytest

from src.websocket.intent_patterns import CONTINUE_THREAD_RE, PAUSED_SCOPE_RE
from src.conversation.request_understanding import (
    CapabilityStatus,
    build_request_understanding,
)


# ---------------------------------------------------------------------------
# PAUSED_SCOPE_RE pattern tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("thread_name", [
    "Shopify",
    "shopify cap 65",
    "Cap 65 signoff",
    "Auralis",
    "auralis website merger",
    "website merger",
    "the Auralis work",
    "Shopify P5 live",
])
def test_paused_scope_re_matches_paused_names(thread_name: str) -> None:
    assert PAUSED_SCOPE_RE.search(thread_name), (
        f"PAUSED_SCOPE_RE should match paused scope name: {thread_name!r}"
    )


@pytest.mark.parametrize("thread_name", [
    "my project",
    "cap 64",
    "installer validation",
    "trust card",
    "this",
    "it",
    "the marketing plan",
    "Nova runtime stabilization",
])
def test_paused_scope_re_does_not_match_non_paused_names(thread_name: str) -> None:
    assert not PAUSED_SCOPE_RE.search(thread_name), (
        f"PAUSED_SCOPE_RE should NOT match: {thread_name!r}"
    )


# ---------------------------------------------------------------------------
# CONTINUE_THREAD_RE still matches the raw text (so the guard fires)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text,expected_name", [
    ("continue Shopify", "Shopify"),
    ("continue shopify cap 65 signoff", "shopify cap 65 signoff"),
    ("continue the Auralis website merger", "the Auralis website merger"),
    ("continue Auralis", "Auralis"),
])
def test_continue_thread_re_matches_paused_scope_phrases(
    text: str, expected_name: str
) -> None:
    m = CONTINUE_THREAD_RE.match(text)
    assert m is not None, f"CONTINUE_THREAD_RE should match: {text!r}"
    assert m.group("name") == expected_name


def test_paused_scope_re_fires_for_continue_shopify_extracted_name() -> None:
    m = CONTINUE_THREAD_RE.match("continue Shopify")
    assert m is not None
    thread_name = m.group("name").strip()
    assert PAUSED_SCOPE_RE.search(thread_name), (
        "Guard should fire for extracted name 'Shopify'"
    )


def test_paused_scope_re_does_not_fire_for_continue_my_project() -> None:
    m = CONTINUE_THREAD_RE.match("continue my project")
    assert m is not None
    thread_name = m.group("name").strip()
    assert not PAUSED_SCOPE_RE.search(thread_name), (
        "Guard must NOT fire for 'my project' — normal threads should still route"
    )


# ---------------------------------------------------------------------------
# build_request_understanding returns PAUSED for these same inputs
# (proves the fallback path would produce the right boundary block)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("query", [
    "continue Shopify",
    "continue shopify cap 65 signoff",
    "continue the Auralis website merger",
    "continue Auralis",
])
def test_paused_scope_queries_get_paused_understanding(query: str) -> None:
    understanding = build_request_understanding(query)
    assert understanding.capability_status == CapabilityStatus.PAUSED, (
        f"Expected PAUSED for {query!r}, got {understanding.capability_status!r}"
    )
    assert understanding.authority_effect == "none"
