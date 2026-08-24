from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.governor.governor_mediator import (
    Clarification,
    GovernorMediator,
    Invocation,
    is_private_google_calendar_search,
)
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


def test_private_google_drive_search_is_a_non_executing_source_boundary():
    result = GovernorMediator.parse_governed_invocation("search my Google Drive")

    assert isinstance(result, Clarification)
    assert not isinstance(result, Invocation)
    assert "isn't enabled" in result.message
    assert "didn't search the public web" in result.message
    assert "no Drive data was accessed" in result.message


def test_private_drive_search_is_rejected_without_public_search_or_general_chat(monkeypatch):
    monkeypatch.setattr(
        "src.trust.session_activity.get_session_action_receipts",
        lambda session_id: [],
    )
    ws = _ScriptedWebSocket(
        [
            "search my Google Drive",
            "what did you actually do?",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("GeneralChat must not run for private Drive search"),
    ), patch.object(
        brain_server,
        "invoke_governed_capability",
        side_effect=AssertionError("No governed capability may run for private Drive search"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    messages = _chat_messages(ws)
    assert "Google Drive access isn't enabled" in messages[-2]
    assert "didn't search the public web" in messages[-2]
    assert "no Drive data was accessed" in messages[-2]
    assert "Google Drive search: rejected or unsupported; no action was attempted" in messages[-1]
    assert "completed" not in messages[-1].lower()


@pytest.mark.parametrize(
    "prompt",
    [
        "search Google Calendar for tomorrow",
        "search Google Calendar for my appointments",
        "look up Google Calendar events today",
    ],
)
def test_private_google_calendar_search_is_a_non_executing_source_boundary(prompt):
    assert is_private_google_calendar_search(prompt) is True

    result = GovernorMediator.parse_governed_invocation(prompt)

    assert isinstance(result, Clarification)
    assert not isinstance(result, Invocation)
    assert "isn't enabled" in result.message
    assert "didn't search the public web" in result.message
    assert "no private Calendar data was accessed" in result.message


@pytest.mark.parametrize(
    "prompt",
    [
        "search Google Calendar pricing",
        "search Google Calendar API documentation",
        "search Google Calendar software features",
    ],
)
def test_public_google_calendar_information_can_still_use_public_search(prompt):
    assert is_private_google_calendar_search(prompt) is False

    result = GovernorMediator.parse_governed_invocation(prompt)

    assert isinstance(result, Invocation)
    assert result.capability_id == 16


def test_private_calendar_search_is_rejected_without_public_search_or_general_chat(monkeypatch):
    monkeypatch.setattr(
        "src.trust.session_activity.get_session_action_receipts",
        lambda session_id: [],
    )
    ws = _ScriptedWebSocket(
        [
            "search Google Calendar for tomorrow",
            "what did you actually do?",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("GeneralChat must not run for private Calendar search"),
    ), patch.object(
        brain_server,
        "invoke_governed_capability",
        side_effect=AssertionError("No governed capability may run for private Calendar search"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    messages = _chat_messages(ws)
    assert "Google Calendar access isn't enabled" in messages[-2]
    assert "didn't search the public web" in messages[-2]
    assert "no private Calendar data was accessed" in messages[-2]
    assert "Google Calendar search: rejected or unsupported; no action was attempted" in messages[-1]
    assert "completed" not in messages[-1].lower()
