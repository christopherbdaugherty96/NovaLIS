from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from src import brain_server
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


def test_daily_briefing_phrase_uses_governed_websocket_routine(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    commands: list[tuple[str, str | None]] = []
    ledger_events: list[tuple[str, dict]] = []

    async def _unavailable_read(governor, command, session_id, **kwargs):
        trusted_params = kwargs.get("extra_params") or {}
        commands.append((command, trusted_params.get("_nova_trusted_activity_origin")))
        return None, None

    def _record_event(governor, event_type, payload):
        ledger_events.append((event_type, payload))

    monkeypatch.setattr(brain_server, "invoke_governed_text_command", _unavailable_read)
    monkeypatch.setattr(brain_server, "_log_ledger_event", _record_event)

    run = SimpleNamespace(run_id="run_daily_briefing", outputs={})
    receipt = SimpleNamespace(
        receipt_id="receipt_daily_briefing",
        graph_name="daily_brief",
        sources_consulted=frozenset({"session_state"}),
    )
    result = SimpleNamespace(
        text=(
            "Weather unavailable.\n"
            "No headline summary available right now.\n"
            "Calendar unavailable."
        ),
        run=run,
        receipt=receipt,
        has_content=False,
    )
    ws = _ScriptedWebSocket(["Give me my daily briefing."])

    with (
        patch(
            "src.conversation.morning_brief_handler.compose_governed_morning_brief",
            return_value=result,
        ),
        patch(
            "src.skills.general_chat.generate_chat",
            side_effect=AssertionError("Daily Brief phrasing must not reach GeneralChat"),
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert [command for command, _ in commands] == [
        "weather",
        "news",
        "system status",
        "calendar",
    ]
    assert {origin for _, origin in commands} == {"background_read"}
    assert any("Weather unavailable" in message for message in _chat_messages(ws))
    assert len(ledger_events) == 1
    event_type, payload = ledger_events[0]
    assert event_type == "ROUTINE_BRIEF_COMPLETED"
    assert payload["session_id"]
    assert payload["run_id"] == "run_daily_briefing"
    assert payload["receipt_id"] == "receipt_daily_briefing"
    assert payload["graph_name"] == "daily_brief"
    assert payload["sources_consulted"] == ["session_state"]
    assert payload["has_content"] is False
