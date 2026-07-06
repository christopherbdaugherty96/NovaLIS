from __future__ import annotations

import inspect

import pytest

from src.conversation.awareness_brief_handler import is_awareness_brief_request


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
    awareness_line = source.index("is_awareness_brief_request(lowered)")
    daily_line = source.index("is_daily_brief_request(lowered)")
    assert awareness_line < daily_line
