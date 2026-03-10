from src.conversation.response_style_router import ResponseStyle, ResponseStyleRouter
from src.conversation.response_style_router import InputNormalizer


def test_response_style_defaults_to_direct():
    assert ResponseStyleRouter.route("Give me status") == ResponseStyle.DIRECT


def test_response_style_detects_brainstorm_keywords():
    assert ResponseStyleRouter.route("brainstorm ideas for launch") == ResponseStyle.BRAINSTORM


def test_response_style_detects_deep_input():
    assert ResponseStyleRouter.route("deep analysis of this architecture") == ResponseStyle.DEEP


def test_response_style_detects_casual_opener():
    assert ResponseStyleRouter.route("hello") == ResponseStyle.CASUAL


def test_input_normalizer_aliases_non_technical_phrase():
    normalized = InputNormalizer.normalize("turn the volume up")
    assert normalized.lower() == "volume up."


def test_input_normalizer_maps_mute_phrase():
    normalized = InputNormalizer.normalize("mute the sound")
    assert normalized.lower() == "mute."


def test_input_normalizer_maps_brightness_phrase():
    normalized = InputNormalizer.normalize("make the screen brighter")
    assert normalized.lower() == "brightness up."


def test_input_normalizer_collapses_spaced_acronyms():
    normalized = InputNormalizer.normalize("open A B C news")
    assert normalized.lower() == "open abc news."


def test_input_normalizer_strips_polite_prefixes():
    normalized = InputNormalizer.normalize("Hey Nova, can you open my documents please")
    assert normalized.lower() == "open documents."


def test_input_normalizer_maps_natural_research_phrase():
    normalized = InputNormalizer.normalize("I want to know about AI chip competition")
    assert normalized.lower() == "research ai chip competition."


def test_input_normalizer_maps_todays_news_phrase():
    normalized = InputNormalizer.normalize("what is today's news")
    assert normalized.lower() == "today's news."


def test_input_normalizer_maps_weather_phrase():
    normalized = InputNormalizer.normalize("what is the weather tomorrow")
    assert normalized.lower() == "weather forecast."
