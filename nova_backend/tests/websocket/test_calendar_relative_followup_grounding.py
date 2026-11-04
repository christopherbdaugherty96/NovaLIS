from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


def _result(message: str, widget: dict, *, success: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        success=success,
        message=message,
        data={"widget": widget},
    )


def _disable_unrelated_gate(monkeypatch) -> None:
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )


def test_calendar_tomorrow_followup_reuses_governed_calendar_read(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    commands: list[str] = []

    async def _invoke(governor, command, session_id, **kwargs):
        commands.append(command)
        if command == "calendar":
            return None, _result(
                "Today's schedule: 2:00 PM Planning.",
                {
                    "type": "calendar",
                    "status": "ok",
                    "connected": True,
                    "scope": "today",
                    "summary": "2:00 PM Planning",
                    "events": [
                        {
                            "title": "Planning",
                            "date": "2026-11-04",
                            "time": "2:00 PM",
                            "day_label": "Wednesday",
                        }
                    ],
                },
            )
        if command == "what do i have tomorrow":
            return None, _result(
                "Tomorrow looks like this: 10:00 AM Review.",
                {
                    "type": "calendar",
                    "status": "ok",
                    "connected": True,
                    "scope": "tomorrow",
                    "summary": "10:00 AM Review",
                    "events": [
                        {
                            "title": "Review",
                            "date": "2026-11-05",
                            "time": "10:00 AM",
                            "day_label": "Thursday",
                        }
                    ],
                },
            )
        raise AssertionError(f"Unexpected governed command: {command}")

    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _invoke)
    ws = _ScriptedWebSocket(["calendar", "What about tomorrow?"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Calendar follow-up must not reach GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert commands == ["calendar", "what do i have tomorrow"]
    chat = _chat_messages(ws)
    assert any("Today's schedule" in message for message in chat)
    assert any("Tomorrow looks like this: 10:00 AM Review" in message for message in chat)
    assert not any("dentist" in message.lower() for message in chat)


def test_calendar_tomorrow_followup_fails_closed_when_source_unavailable(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    commands: list[str] = []

    async def _invoke(governor, command, session_id, **kwargs):
        commands.append(command)
        return None, _result(
            "Calendar data is currently unavailable.",
            {
                "type": "calendar",
                "status": "unavailable",
                "connected": True,
                "scope": "today",
                "summary": "Unavailable.",
                "events": [],
            },
            success=False,
        )

    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _invoke)
    ws = _ScriptedWebSocket(["calendar", "What about tomorrow?"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Unavailable calendar follow-up must not reach GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert commands == ["calendar"]
    assert any(
        "calendar" in message.lower() and "unavailable" in message.lower()
        for message in _chat_messages(ws)
    )


def test_tomorrow_followup_without_active_domain_requests_clarification(monkeypatch):
    _disable_unrelated_gate(monkeypatch)
    ws = _ScriptedWebSocket(["What about tomorrow?"])

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("Ambiguous tomorrow follow-up must not reach GeneralChat"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert any(
        "tomorrow" in message.lower()
        and "calendar" in message.lower()
        and "weather" in message.lower()
        for message in _chat_messages(ws)
    )


@pytest.mark.parametrize("active_domain", ["weather", "news", "awareness_brief"])
def test_calendar_followup_binding_does_not_capture_other_active_domains(active_domain):
    from src.websocket.session_handler import calendar_relative_followup_action

    state = {
        "active_brief_item": active_domain,
        "brief_calendar": {
            "type": "calendar",
            "status": "ok",
            "connected": True,
        },
    }

    assert calendar_relative_followup_action("What about tomorrow?", state) == ""
