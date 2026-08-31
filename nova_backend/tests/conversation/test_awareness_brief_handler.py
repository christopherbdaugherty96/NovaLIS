from __future__ import annotations

import inspect

import pytest
from src.conversation.awareness_brief_handler import (
    SURFACE_AMBIGUOUS,
    SURFACE_AURALIS_TODAY,
    SURFACE_AWARENESS_BRIEF,
    classify_governed_surface_request,
    governed_surface_request_guard_response,
    is_awareness_brief_request,
)


@pytest.mark.parametrize(
    "phrase",
    [
        "awareness brief",
        "daily awareness",
        "awareness",
        "what should I do today?",
        "whats my brief",
        "what's my brief",
        "read me my brief",
        "give me the rundown",
        "give me rundown",
        "what should I do for Auralis today?",
        "what matters for Auralis today",
        "what is my Auralis move today",
        "Give me my Daily Awareness Brief.",
        "Show me Auralis Today",
    ],
)
def test_awareness_brief_dogfood_phrasings_route_to_current_surface(phrase: str):
    assert is_awareness_brief_request(phrase) is True


@pytest.mark.parametrize(
    "phrase",
    [
        "",
        "daily brief",
        "brief me",
        "give me a brief summary of this article",
        "what is Auralis",
        "what should I do about this Python error",
    ],
)
def test_awareness_brief_handler_does_not_capture_unrelated_brief_or_task_phrases(phrase: str):
    assert is_awareness_brief_request(phrase) is False


def test_session_handler_uses_awareness_brief_helper_before_daily_brief():
    from src.websocket import session_handler

    source = inspect.getsource(session_handler)
    awareness_line = source.index("classify_governed_surface_request(lowered)")
    daily_line = source.index("if governed_daily_brief_request:")
    assert awareness_line < daily_line


def test_exact_smoke_requests_resolve_to_the_intended_awareness_surface():
    assert (
        classify_governed_surface_request("Give me my Daily Awareness Brief.")
        == SURFACE_AWARENESS_BRIEF
    )
    assert (
        classify_governed_surface_request("Show me Auralis Today")
        == SURFACE_AURALIS_TODAY
    )


@pytest.mark.parametrize(
    "phrase",
    [
        "I hate this rainy weather",
        "Auralis's been busy",
        "I mentioned Auralis Today in the meeting",
        "Let's discuss the awareness brief design",
    ],
)
def test_surface_mentions_remain_normal_conversation(phrase: str):
    assert classify_governed_surface_request(phrase) == ""
    assert governed_surface_request_guard_response(phrase) == ""


def test_ambiguous_request_shaped_surface_reference_fails_safe():
    phrase = "Open the Auralis Today report"
    assert classify_governed_surface_request(phrase) == SURFACE_AMBIGUOUS
    response = governed_surface_request_guard_response(phrase)
    assert "Which one did you mean?" in response
