"""Tests for the deterministic brief-phrasing intent resolver.

Lane: docs/future/NOVA_BRIEF_PHRASING_INTENT_LANE_PLAN.md

The resolver widens recognition of common morning phrasing for already-supported
brief capabilities (weather / news / calendar). It is pure and non-authorizing:
it returns an intent tag only — it never calls a capability, mutates text, or
performs I/O. High confidence routes to an existing governed path; medium asks a
clarification; low leaves the existing advisory path untouched.
"""

from __future__ import annotations

import pytest
from src.conversation.brief_intent_resolver import (
    BRIEF_CLARIFICATION,
    BriefIntent,
    resolve_brief_intent,
)


def _resolve(text: str, *, news_loaded: bool = False) -> BriefIntent:
    return resolve_brief_intent(text, news_context_loaded=news_loaded)


# --- Positive: HIGH confidence → existing capability ------------------------

@pytest.mark.parametrize(
    "text,capability,canonical",
    [
        ("is it hot out?", "weather", "weather"),
        ("do I need a jacket?", "weather", "weather"),
        ("theres heat alerts for outside, how should i stay cool?", "weather", "weather"),
        ("will it rain later?", "weather", "weather"),
        ("anyhting on my schedule?", "calendar", "agenda for today"),
        ("tomorrow's schedule", "calendar", "agenda for tomorrow"),
        ("what do I have scheduled tomorrow?", "calendar", "agenda for tomorrow"),
        ("what is my upcoming schedule?", "calendar", "upcoming events"),
        ("am I free after that?", "calendar", "agenda for today"),
        ("what are my plans?", "calendar", "agenda for today"),
        ("anything happening?", "news", "news"),
        ("what should I know today?", "news", "news"),
        ("what matters today?", "news", "news"),
    ],
)
def test_high_confidence_routes_to_capability(text, capability, canonical):
    intent = _resolve(text)
    assert intent.confidence == "high"
    assert intent.capability == capability
    assert intent.canonical == canonical
    assert intent.clarification == ""


# --- Medium: ambiguous preparation phrase → clarification -------------------

@pytest.mark.parametrize(
    "text",
    [
        "do I need to prepare?",
        "what should I do about today?",
    ],
)
def test_ambiguous_preparation_asks_clarification(text):
    intent = _resolve(text)
    assert intent.confidence == "medium"
    assert intent.capability is None
    assert intent.clarification == BRIEF_CLARIFICATION


def test_cross_domain_collision_asks_clarification():
    # umbrella (weather) + free (calendar) → do not silently pick one.
    intent = _resolve("should I bring an umbrella, and am I free?")
    assert intent.confidence == "medium"
    assert intent.capability is None
    assert intent.clarification == BRIEF_CLARIFICATION


# --- Theft-guard: authoring / search intents must NOT be stolen -------------

@pytest.mark.parametrize(
    "text",
    [
        "build a weather page",
        "make a jacket recommendation widget",       # 'jacket' would match weather absent the guard
        "design a busy-day planner app",             # 'busy' would match calendar absent the guard
        "create a component for my plans",           # 'plans' would match calendar absent the guard
        "write a blog post about the heat wave",
        "look up how to stay cool",                  # 'stay cool' would match weather absent the guard
        "search for umbrella deals",                 # 'umbrella' would match weather absent the guard
        "google the best jacket brands",
    ],
)
def test_authoring_and_search_intents_are_not_stolen(text):
    intent = _resolve(text)
    assert intent.confidence == "low"
    assert intent.capability is None


@pytest.mark.parametrize(
    "text",
    [
        "is there anything on the local server today?",
        "is there any note on my desk today?",
        "is there anything written on this document today?",
    ],
)
def test_local_or_document_queries_are_not_stolen_by_calendar(text):
    intent = _resolve(text)
    assert intent.confidence == "low"
    assert intent.capability is None


# --- Regression: exact existing commands are left to their own branches -----

@pytest.mark.parametrize(
    "text",
    ["weather", "weather update", "news", "headlines", "agenda for today", "system status", "open documents"],
)
def test_exact_or_unrelated_commands_are_untouched(text):
    # These already have dedicated handlers (or are unrelated). The resolver must
    # not shadow them — it only fires on natural phrasing.
    intent = _resolve(text)
    # 'headlines' is an owner-listed news term and legitimately resolves to news;
    # everything else here must stay low so the existing path handles it.
    if text == "headlines":
        assert intent.capability == "news"
    else:
        assert intent.confidence == "low"
        assert intent.capability is None


@pytest.mark.parametrize(
    "text",
    [
        "take a screenshot",
        "screen snapshot",
        "capture my screen",
        "show me the hotkey settings",
    ],
)
def test_weather_terms_require_token_boundaries(text):
    intent = _resolve(text)

    assert intent.capability != "weather"


# --- Purity / contract ------------------------------------------------------

def test_confidence_is_always_valid():
    for text in ["", "   ", "is it hot out?", "do I need to prepare?", "build a weather page", "xyzzy"]:
        intent = _resolve(text)
        assert intent.confidence in {"high", "medium", "low"}
        if intent.confidence == "high":
            assert intent.canonical
        if intent.confidence == "medium":
            assert intent.clarification


def test_empty_input_is_low():
    assert _resolve("").confidence == "low"
    assert _resolve("   ").confidence == "low"


def test_news_capability_is_independent_of_context_flag():
    # The resolver classifies intent; whether to render from cache vs fetch fresh
    # is the caller's decision. Classification must be stable regardless.
    assert _resolve("anything happening?", news_loaded=True).capability == "news"
    assert _resolve("anything happening?", news_loaded=False).capability == "news"
