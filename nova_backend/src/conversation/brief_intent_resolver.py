"""Deterministic brief-phrasing intent resolver.

Lane: docs/future/NOVA_BRIEF_PHRASING_INTENT_LANE_PLAN.md

Purpose
-------
Widen recognition of common *morning* phrasing for already-supported brief
capabilities — weather, news, calendar — so natural questions like "is it hot
out?" or "anything on my schedule?" reach the existing governed capability path
instead of falling through to the slow advisory LLM.

Boundaries (Phase-3 aligned)
----------------------------
This module is pure and NON-AUTHORIZING. It:
  * performs no I/O and holds no state,
  * never calls a capability, governor, or network,
  * never mutates the user's text,
  * only returns an intent tag the caller may act on.

It uses simple deterministic substring matching over an owner-supplied lexicon.
There is no model, no embedding, and no stemming. New terms are added only with
a corresponding test.

Confidence contract
-------------------
  high   -> exactly one brief domain matched, no authoring/search intent.
            Caller routes to the existing governed branch via `canonical`.
  medium -> ambiguous: a preparation phrase with no clear domain, or two or more
            domains at once. Caller asks `clarification` and does nothing else.
  low    -> no brief signal (or an authoring/search intent). Caller leaves the
            existing path untouched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

BRIEF_CLARIFICATION = "Do you mean your calendar, the weather, or the news?"


@dataclass(frozen=True)
class BriefIntent:
    capability: str | None            # "weather" | "news" | "calendar" | None
    confidence: str                   # "high" | "medium" | "low"
    canonical: str = ""               # canonical command for high-confidence routing
    clarification: str = ""           # populated for medium
    matched_terms: tuple[str, ...] = ()


# --- Owner-supplied v1 lexicon (the entire matcher; extend only with a test) ---
_WEATHER_TERMS = ("hot", "cold", "rain", "jacket", "stay cool", "outside", "heat alert", "umbrella")
_CALENDAR_TERMS = ("what am i doing", "plans", "free", "busy", "schedule", "after that")
_NEWS_TERMS = ("anything happening", "headlines", "what should i know", "what matters today")

_CANONICAL = {"weather": "weather", "news": "news", "calendar": "agenda for today"}
_UPCOMING_CALENDAR_MARKERS = ("upcoming", "this week", "next 7 days", "coming up")

# --- Ambiguous preparation phrases that plausibly span >=2 brief domains -------
_MEDIUM_PREPARE_PHRASES = (
    "do i need to prepare",
    "what should i do about today",
    "what do i need to do today",
    "do i need to get ready",
)

# --- Theft-guard: creation/authoring intents must never be stolen -------------
# Strong verbs imply creation on their own; weak verbs only when paired with an
# artifact noun (so "write down" or "make sure" are not over-suppressed).
_STRONG_AUTHORING_VERBS = frozenset(
    {"build", "create", "design", "implement", "develop", "generate", "code",
     "program", "scaffold", "prototype", "refactor"}
)
_WEAK_AUTHORING_VERBS = frozenset({"make", "write", "add", "draft", "mock"})
_ARTIFACT_NOUNS = frozenset(
    {"page", "app", "site", "website", "widget", "component", "feature", "screen",
     "mockup", "dashboard", "ui", "interface", "prototype", "post", "blog", "article",
     "report", "email", "newsletter", "story", "copy", "form", "button", "layout", "template"}
)

# --- Theft-guard: explicit search/lookup intents (search broadening is out of scope) ---
_SEARCH_START_PREFIXES = ("look up", "search for", "search ", "google ", "find online", "web search")
_SEARCH_CONTAINS = ("look up", "search for", "find online", "web search", "google for")


def _normalize(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _has_authoring_intent(q: str) -> bool:
    words = set(re.findall(r"[a-z]+", q))
    if words & _STRONG_AUTHORING_VERBS:
        return True
    if (words & _WEAK_AUTHORING_VERBS) and (words & _ARTIFACT_NOUNS):
        return True
    return False


def _has_search_intent(q: str) -> bool:
    if q.startswith(_SEARCH_START_PREFIXES):
        return True
    return any(phrase in q for phrase in _SEARCH_CONTAINS)


def _domain_hits(q: str) -> dict[str, tuple[str, ...]]:
    hits: dict[str, tuple[str, ...]] = {}
    for domain, terms in (("weather", _WEATHER_TERMS), ("calendar", _CALENDAR_TERMS), ("news", _NEWS_TERMS)):
        matched = tuple(term for term in terms if term in q)
        if matched:
            hits[domain] = matched
    return hits


def _canonical_for_domain(domain: str, q: str) -> str:
    if domain != "calendar":
        return _CANONICAL[domain]
    if "tomorrow" in q:
        return "agenda for tomorrow"
    if any(marker in q for marker in _UPCOMING_CALENDAR_MARKERS):
        return "upcoming events"
    return _CANONICAL[domain]


def resolve_brief_intent(text: str, *, news_context_loaded: bool = False) -> BriefIntent:
    """Classify a natural utterance against the brief lexicon.

    `news_context_loaded` is accepted for caller convenience (it may prefer a
    grounded cache render over a fresh fetch) but does not change classification.
    """
    q = _normalize(text)
    if not q:
        return BriefIntent(capability=None, confidence="low")

    # 1. Creation / search intents are never stolen by brief routing.
    if _has_authoring_intent(q) or _has_search_intent(q):
        return BriefIntent(capability=None, confidence="low")

    # 2. Single-domain match → high confidence.
    hits = _domain_hits(q)
    if len(hits) == 1:
        domain, matched = next(iter(hits.items()))
        return BriefIntent(
            capability=domain,
            confidence="high",
            canonical=_canonical_for_domain(domain, q),
            matched_terms=matched,
        )

    # 3. Two or more domains at once → ask which one.
    if len(hits) >= 2:
        return BriefIntent(capability=None, confidence="medium", clarification=BRIEF_CLARIFICATION)

    # 4. No domain, but an ambiguous "prepare for today" phrase → ask which one.
    if any(phrase in q for phrase in _MEDIUM_PREPARE_PHRASES):
        return BriefIntent(capability=None, confidence="medium", clarification=BRIEF_CLARIFICATION)

    # 5. Nothing recognized → leave the existing path alone.
    return BriefIntent(capability=None, confidence="low")
