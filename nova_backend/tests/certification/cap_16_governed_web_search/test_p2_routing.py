# tests/certification/cap_16_governed_web_search/test_p2_routing.py
"""
Phase 2 — Routing certification for capability 16 (governed_web_search).

Verifies GovernorMediator routes correctly to cap 16 for current/search/
freshness phrasing, does NOT force cap 16 for broader research intents
that belong to cap 48/50, and handles "search" bare clarification.
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(text: str, session_id: str | None = None):
    from src.governor.governor_mediator import GovernorMediator
    return GovernorMediator.parse_governed_invocation(text, session_id=session_id)


def _invocation(text: str):
    from src.governor.governor_mediator import Invocation
    result = _parse(text)
    assert isinstance(result, Invocation), f"Expected Invocation for {text!r}, got {type(result).__name__}"
    return result


def _not_cap16(text: str):
    from src.governor.governor_mediator import Invocation
    result = _parse(text)
    if isinstance(result, Invocation):
        assert result.capability_id != 16, (
            f"Expected cap 16 NOT to be chosen for {text!r}, but got cap 16"
        )


# ---------------------------------------------------------------------------
# Bare "search" → Clarification
# ---------------------------------------------------------------------------

def test_bare_search_returns_clarification():
    # Clarification requires a session_id so the mediator can track the pending state.
    from src.governor.governor_mediator import Clarification, GovernorMediator
    session_id = "cert-16-p2-bare-no-ctx"
    GovernorMediator.clear_session(session_id)
    result = _parse("search", session_id=session_id)
    assert isinstance(result, Clarification)
    assert "what would you like to search for" in result.message.lower()


def test_bare_search_clarification_then_cap16():
    from src.governor.governor_mediator import Clarification, GovernorMediator, Invocation
    session_id = "cert-16-p2-bare-search"
    GovernorMediator.clear_session(session_id)

    first = _parse("search", session_id=session_id)
    assert isinstance(first, Clarification)

    second = _parse("latest AI news", session_id=session_id)
    assert isinstance(second, Invocation)
    assert second.capability_id == 16
    assert second.params["query"]


# ---------------------------------------------------------------------------
# Explicit search phrasings → cap 16
# ---------------------------------------------------------------------------

def test_search_for_latest_ai_news_routes_to_cap16():
    inv = _invocation("search for latest AI news")
    assert inv.capability_id == 16
    assert "ai news" in inv.params["query"].lower() or "latest" in inv.params["query"].lower()


def test_look_up_electric_vehicles_routes_to_cap16():
    inv = _invocation("look up what is happening with electric vehicles")
    assert inv.capability_id == 16
    assert "electric vehicle" in inv.params["query"].lower()


def test_search_web_cite_sources_routes_to_cap16():
    inv = _invocation(
        "Search the web and tell me what happened with electric vehicle sales recently. Cite your sources."
    )
    assert inv.capability_id == 16
    # "search the web" prefix should be stripped from query
    assert "search the web" not in inv.params["query"].lower()
    assert "electric vehicle" in inv.params["query"].lower()


# ---------------------------------------------------------------------------
# Freshness / current / latest phrasing → cap 16
# ---------------------------------------------------------------------------

def test_what_is_happening_now_routes_to_cap16():
    inv = _invocation("what is happening with the EU AI Act right now")
    assert inv.capability_id == 16


def test_current_status_phrasing_routes_to_cap16():
    inv = _invocation("show me current updates about semiconductor exports")
    assert inv.capability_id == 16


def test_latest_keyword_routes_to_cap16():
    inv = _invocation("what are the latest updates on AI regulation")
    assert inv.capability_id == 16
    assert "latest updates" in inv.params["query"].lower() or "regulation" in inv.params["query"].lower()


def test_today_freshness_routes_to_cap16():
    inv = _invocation("how is Tesla stock doing today")
    assert inv.capability_id == 16
    assert "tesla" in inv.params["query"].lower()


def test_right_now_routes_to_cap16():
    inv = _invocation("what is the price of Bitcoin right now")
    assert inv.capability_id == 16
    assert "bitcoin" in inv.params["query"].lower()


@pytest.mark.parametrize(
    "text",
    [
        "is there any sports on live today?",
        "are there any games on today?",
        "is there any live transit coverage tonight?",
        "are there any current service outages right now?",
        "what sports are live right now?",
        "is there anything happening in Congress today?",
        "are there any live events happening today?",
        "is there anything new with OpenAI today?",
        "are there any policy updates today?",
    ],
)
def test_natural_current_availability_questions_route_to_cap16(text: str):
    inv = _invocation(text)
    assert inv.capability_id == 16
    assert inv.params["query"]


# ---------------------------------------------------------------------------
# Claim-check / fact-check phrasing → cap 16
# ---------------------------------------------------------------------------

def test_claim_check_routes_to_cap16():
    inv = _invocation("Is this claim true: drinking coffee prevents Alzheimer's")
    assert inv.capability_id == 16
    assert "coffee prevents" in inv.params["query"].lower()


def test_find_current_info_routes_to_cap16():
    inv = _invocation("find current information about Zorblax Quantum Sandwich Labs")
    assert inv.capability_id == 16
    assert "Zorblax Quantum Sandwich Labs" in inv.params["query"]


# ---------------------------------------------------------------------------
# Broader research / intelligence → must NOT be forced to cap 16
# ---------------------------------------------------------------------------

def test_broad_research_does_not_force_cap16():
    """'research AI regulation trends' belongs to cap 48 — must not be overridden."""
    _not_cap16("tell me about AI regulation")


def test_intelligence_brief_does_not_route_to_cap16():
    """Intel brief requests belong to cap 50 — must not map to cap 16."""
    _not_cap16("create an intelligence brief on the semiconductor shortage")


def test_analyze_source_reliability_does_not_route_to_cap16():
    """Source reliability analysis belongs to cap 48/50 — must not map to cap 16."""
    _not_cap16("analyze source reliability for climate change coverage")


# ---------------------------------------------------------------------------
# Non-search intents → no invocation
# ---------------------------------------------------------------------------

def test_explain_factual_returns_none():
    from src.governor.governor_mediator import GovernorMediator
    result = GovernorMediator.parse_governed_invocation("Explain what Shopify is")
    assert result is None


def test_generic_factual_question_returns_none():
    from src.governor.governor_mediator import GovernorMediator
    result = GovernorMediator.parse_governed_invocation("is the sky blue")
    assert result is None


@pytest.mark.parametrize(
    "text",
    [
        "explain how live sports broadcasting works",
        "write a live sports schedule parser",
        "I watched sports today",
        "tell me the history of the Super Bowl",
        "is there a difference between live and recorded sports?",
        "is there any difference between today and tomorrow?",
        "are there any reminders today?",
        "is there anything in my files today?",
        "are there any updates in my inbox today?",
        "what reminders do I have today?",
        "what's in my inbox today?",
        "what happened with my project today?",
    ],
)
def test_non_current_or_local_requests_do_not_route_to_cap16(text: str):
    _not_cap16(text)


@pytest.mark.parametrize(
    ("text", "capability_id"),
    [
        ("what's the weather today?", 55),
        ("today's news", 50),
        ("show my calendar", 57),
        ("what's my schedule today?", 57),
        ("is there anything on my calendar today?", 57),
        ("are there any appointments on my schedule today?", 57),
        ("is there any news today?", 56),
    ],
)
def test_specific_current_information_domains_keep_precedence(
    text: str,
    capability_id: int,
):
    inv = _invocation(text)
    assert inv.capability_id == capability_id
