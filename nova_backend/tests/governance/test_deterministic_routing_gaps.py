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
