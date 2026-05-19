"""Regression tests for deterministic routing of everyday utility prompts.

These prompts timed out in the live-user simulation (2026-05-19) because
they fell through to advisory LLM fallback instead of being routed
deterministically. Each test verifies the exact simulation phrase now
resolves without Ollama.

Covers:
- Simple arithmetic ("what is 247 times 38?")
- News headline phrasing ("give me the latest news headlines")
- Weather-in-city phrasing ("weather in Boston")
- Weather-like phrasing ("what's the weather like today in Pittsburgh?")
"""

from __future__ import annotations

import re

import pytest


# ---------------------------------------------------------------------------
# Arithmetic — _try_arithmetic deterministic handler
# ---------------------------------------------------------------------------

class TestDeterministicArithmetic:
    """Verify exact simulation prompts hit the fast arithmetic path."""

    def test_exact_simulation_phrase(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("what is 247 times 38?")
        assert result is not None
        assert "9,386" in result

    def test_multiplication_with_x(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("12 x 5")
        assert result is not None
        assert "60" in result

    def test_addition(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("100 plus 200")
        assert result is not None
        assert "300" in result

    def test_subtraction(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("500 minus 123")
        assert result is not None
        assert "377" in result

    def test_division(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("100 divided by 4")
        assert result is not None
        assert "25" in result

    def test_division_by_zero(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("10 divided by 0")
        assert result is not None
        assert "zero" in result.lower()

    def test_decimal_result(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("7 divided by 3")
        assert result is not None
        assert "2.33" in result

    def test_comma_formatted_numbers(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("1,000 times 50")
        assert result is not None
        assert "50,000" in result

    def test_non_arithmetic_returns_none(self):
        from src.websocket.session_handler import _try_arithmetic

        assert _try_arithmetic("tell me about neural networks") is None
        assert _try_arithmetic("what is machine learning?") is None
        assert _try_arithmetic("") is None

    def test_whats_prefix(self):
        from src.websocket.session_handler import _try_arithmetic

        result = _try_arithmetic("what's 15 + 27")
        assert result is not None
        assert "42" in result


# ---------------------------------------------------------------------------
# News headline normalization
# ---------------------------------------------------------------------------

class TestNewsHeadlineNormalization:
    """Verify news headline phrasing normalizes to a routable form."""

    def test_exact_simulation_phrase(self):
        from src.conversation.response_style_router import InputNormalizer

        result = InputNormalizer.normalize("give me the latest news headlines")
        lowered = result.lower().rstrip(".?!")
        # Should normalize to "news" which the session_handler can route
        assert lowered in {"news", "today's news", "headlines", "latest news"}

    def test_show_me_latest_headlines(self):
        from src.conversation.response_style_router import InputNormalizer

        result = InputNormalizer.normalize("show me the latest headlines")
        lowered = result.lower().rstrip(".?!")
        assert lowered in {"news", "today's news", "headlines", "latest news"}

    def test_what_are_the_top_headlines(self):
        from src.conversation.response_style_router import InputNormalizer

        result = InputNormalizer.normalize("what are the top headlines")
        lowered = result.lower().rstrip(".?!")
        assert lowered in {"news", "today's news", "headlines", "latest news"}

    def test_latest_news_headlines(self):
        from src.conversation.response_style_router import InputNormalizer

        result = InputNormalizer.normalize("latest news headlines")
        lowered = result.lower().rstrip(".?!")
        assert lowered in {"news", "today's news", "headlines", "latest news"}

    def test_existing_give_me_news_still_works(self):
        from src.conversation.response_style_router import InputNormalizer

        result = InputNormalizer.normalize("give me today's news")
        lowered = result.lower().rstrip(".?!")
        assert lowered == "today's news"

    def test_news_routes_to_governor(self):
        """Verify 'news' matches the GovernorMediator NEWS_RE."""
        from src.governor.governor_mediator import NEWS_RE

        assert NEWS_RE.match("news")
        assert NEWS_RE.match("headlines")
        assert NEWS_RE.match("latest news")


# ---------------------------------------------------------------------------
# Weather-in-city routing
# ---------------------------------------------------------------------------

class TestWeatherInCityRouting:
    """Verify weather-in-city phrasing hits the weather capability."""

    def test_weather_in_city_matches_governor(self):
        from src.governor.governor_mediator import WEATHER_RE

        assert WEATHER_RE.match("weather in Boston")
        assert WEATHER_RE.match("weather in Pittsburgh")
        assert WEATHER_RE.match("weather in New York")
        assert WEATHER_RE.match("weather in San Francisco")

    def test_weather_like_today_normalizes(self):
        from src.conversation.response_style_router import InputNormalizer

        result = InputNormalizer.normalize(
            "what's the weather like today in Pittsburgh?"
        )
        lowered = result.lower().rstrip(".?!")
        assert "weather" in lowered

    def test_existing_weather_phrases_still_match(self):
        from src.governor.governor_mediator import WEATHER_RE

        assert WEATHER_RE.match("weather")
        assert WEATHER_RE.match("current weather")
        assert WEATHER_RE.match("weather forecast")
        assert WEATHER_RE.match("what's the weather")
        assert WEATHER_RE.match("how's the weather")
        assert WEATHER_RE.match("what's the weather in Boston")

    def test_weather_in_city_session_handler_route(self):
        """Verify 'weather in boston' matches the session_handler regex."""
        pattern = re.compile(r"^weather\s+in\s+[a-z0-9 ,.\-]+$")
        assert pattern.match("weather in boston")
        assert pattern.match("weather in new york")
        assert pattern.match("weather in san francisco")
        assert not pattern.match("weather")
        assert not pattern.match("weather today")


# ---------------------------------------------------------------------------
# Handler ordering — deterministic commands before ambient clarification
# ---------------------------------------------------------------------------

class TestHandlerOrdering:
    """Verify deterministic commands are handled before ambient clarification.

    After PR #213, the session_handler routes time, arithmetic, news, and
    weather commands BEFORE the ambient clarification block.  This means
    first-turn inputs like "news" or "weather in Boston" (no prior context)
    cannot be intercepted by context-free follow-up heuristics.
    """

    def _handler_line(self, marker: str) -> int:
        """Return the first line number where *marker* appears in session_handler."""
        import inspect
        from src.websocket import session_handler as mod

        source = inspect.getsource(mod)
        for i, line in enumerate(source.splitlines(), start=1):
            if marker in line:
                return i
        raise AssertionError(f"marker {marker!r} not found in session_handler")

    def test_time_query_before_ambient_clarification(self):
        time_line = self._handler_line("TIME_QUERY_RE.match(command_text)")
        ambient_line = self._handler_line("AMBIENT_CLARIFICATION_PATTERNS if pat.match")
        assert time_line < ambient_line, (
            f"TIME_QUERY_RE ({time_line}) must fire before "
            f"AMBIENT_CLARIFICATION_PATTERNS ({ambient_line})"
        )

    def test_arithmetic_before_ambient_clarification(self):
        arith_line = self._handler_line("_try_arithmetic(command_text)")
        ambient_line = self._handler_line("AMBIENT_CLARIFICATION_PATTERNS if pat.match")
        assert arith_line < ambient_line, (
            f"_try_arithmetic ({arith_line}) must fire before "
            f"AMBIENT_CLARIFICATION_PATTERNS ({ambient_line})"
        )

    def test_news_handler_before_ambient_clarification(self):
        news_line = self._handler_line(
            'lowered in {"news", "headlines", "latest news", "top news"}'
        )
        ambient_line = self._handler_line("AMBIENT_CLARIFICATION_PATTERNS if pat.match")
        assert news_line < ambient_line, (
            f"News handler ({news_line}) must fire before "
            f"AMBIENT_CLARIFICATION_PATTERNS ({ambient_line})"
        )

    def test_weather_handler_before_ambient_clarification(self):
        weather_line = self._handler_line(
            'lowered in {"weather", "weather update", "current weather"}'
        )
        ambient_line = self._handler_line("AMBIENT_CLARIFICATION_PATTERNS if pat.match")
        assert weather_line < ambient_line, (
            f"Weather handler ({weather_line}) must fire before "
            f"AMBIENT_CLARIFICATION_PATTERNS ({ambient_line})"
        )

    def test_headline_summary_before_ambient_clarification(self):
        headline_line = self._handler_line("is_headline_summary_request(command_text)")
        ambient_line = self._handler_line("AMBIENT_CLARIFICATION_PATTERNS if pat.match")
        assert headline_line < ambient_line, (
            f"Headline summary ({headline_line}) must fire before "
            f"AMBIENT_CLARIFICATION_PATTERNS ({ambient_line})"
        )

    def test_news_not_in_ambient_clarification_patterns(self):
        """Verify 'news' doesn't match any ambient clarification pattern."""
        from src.websocket.intent_patterns import AMBIENT_CLARIFICATION_PATTERNS

        for pat, _ in AMBIENT_CLARIFICATION_PATTERNS:
            assert not pat.match("news"), (
                f"'news' must not match ambient pattern {pat.pattern}"
            )
            assert not pat.match("News"), (
                f"'News' must not match ambient pattern {pat.pattern}"
            )

    def test_weather_not_in_ambient_clarification_patterns(self):
        """Verify weather commands don't match any ambient clarification pattern."""
        from src.websocket.intent_patterns import AMBIENT_CLARIFICATION_PATTERNS

        for phrase in ["weather", "weather in Boston", "current weather"]:
            for pat, _ in AMBIENT_CLARIFICATION_PATTERNS:
                assert not pat.match(phrase), (
                    f"{phrase!r} must not match ambient pattern {pat.pattern}"
                )

    def test_arithmetic_not_in_ambient_clarification_patterns(self):
        """Verify arithmetic doesn't match any ambient clarification pattern."""
        from src.websocket.intent_patterns import AMBIENT_CLARIFICATION_PATTERNS

        for phrase in ["247 times 38", "what is 10 plus 5"]:
            for pat, _ in AMBIENT_CLARIFICATION_PATTERNS:
                assert not pat.match(phrase), (
                    f"{phrase!r} must not match ambient pattern {pat.pattern}"
                )

    def test_ambiguous_followup_still_matches_ambient_clarification(self):
        """Ambient clarification must still fire for genuinely ambiguous phrases."""
        from src.websocket.intent_patterns import AMBIENT_CLARIFICATION_PATTERNS

        ambiguous_phrases = [
            "tell me more",
            "go deeper",
            "what went wrong",
            "i'm lost",
        ]
        for phrase in ambiguous_phrases:
            matched = any(pat.match(phrase) for pat, _ in AMBIENT_CLARIFICATION_PATTERNS)
            assert matched, (
                f"Ambiguous phrase {phrase!r} should still match "
                f"ambient clarification"
            )
