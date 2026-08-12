from __future__ import annotations

import asyncio

import pytest
from src import brain_server
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket

pytestmark = pytest.mark.slow


def test_governed_helper_uses_only_trusted_session_and_origin_arguments():
    calls: list[dict] = []

    class _Governor:
        def handle_governed_invocation(self, capability_id, params, **authority):
            calls.append(
                {
                    "capability_id": capability_id,
                    "params": dict(params),
                    "authority": dict(authority),
                }
            )
            from src.actions.action_result import ActionResult

            return ActionResult.ok("ok")

    asyncio.run(
        brain_server.invoke_governed_capability(
            _Governor(),
            19,
            {
                "action": "up",
                "session_id": "client-spoofed",
                "_nova_trusted_activity_origin": "client-spoofed",
            },
        )
    )
    asyncio.run(
        brain_server.invoke_governed_capability(
            _Governor(),
            19,
            {
                "action": "up",
                "session_id": "client-spoofed",
                "_nova_trusted_activity_origin": "background_read",
            },
            session_id="server-session",
        )
    )

    assert "session_id" not in calls[0]["params"]
    assert calls[0]["authority"]["session_id"] == ""
    assert calls[0]["authority"]["activity_origin"] == "user_action"
    assert calls[1]["params"]["session_id"] == "server-session"
    assert calls[1]["authority"]["session_id"] == "server-session"
    assert calls[1]["authority"]["activity_origin"] == "background_read"
    assert "_nova_trusted_activity_origin" not in calls[1]["params"]


def test_recap_bypasses_general_chat_and_uses_only_current_session_evidence(monkeypatch):
    async def _must_not_run(*args, **kwargs):
        raise AssertionError("GeneralChat must not run for deterministic session recap.")

    monkeypatch.setattr(brain_server, "run_general_chat_fallback", _must_not_run)
    def _session_receipts(session_id):
        common = {
            "timestamp_utc": "2026-08-12T12:00:00+00:00",
            "session_id": session_id,
            "request_id": "background-news",
            "activity_origin": "background_read",
            "capability_id": 56,
            "capability_name": "news_snapshot",
        }
        return [
            {"event_type": "ACTION_COMPLETED", "success": True, "status": "completed", **common},
            {"event_type": "ACTION_ATTEMPTED", **common},
        ]

    monkeypatch.setattr(
        "src.trust.session_activity.get_session_action_receipts",
        _session_receipts,
    )
    ws = _ScriptedWebSocket(
        [
            "what did you actually do?",
            "what actions did you perform?",
            "what happened during this session?",
            "what can you verify happened?",
        ]
    )

    asyncio.run(brain_server.websocket_endpoint(ws))

    chats = _chat_messages(ws)
    recaps = chats[-4:]
    assert len(set(recaps)) == 1
    assert "News snapshot (Cap 56): background read completed" in recaps[0]
    assert "did not infer actions from the conversation transcript" in recaps[0]


def test_unsupported_calendar_write_is_recalled_without_fake_action_receipt(monkeypatch):
    async def _must_not_run(*args, **kwargs):
        raise AssertionError("GeneralChat must not run for calendar boundary or recap.")

    monkeypatch.setattr(brain_server, "run_general_chat_fallback", _must_not_run)
    monkeypatch.setattr(
        "src.trust.session_activity.get_session_action_receipts",
        lambda session_id: [],
    )
    ws = _ScriptedWebSocket(
        [
            "add a dentist appointment tomorrow at 3 PM",
            "what can you verify happened?",
        ]
    )

    asyncio.run(brain_server.websocket_endpoint(ws))

    chats = _chat_messages(ws)
    assert "No calendar event was created" in chats[-2]
    assert "Calendar write: rejected or unsupported; no action was attempted" in chats[-1]
    assert "completed" not in chats[-1].lower()


def test_client_cannot_set_background_origin_without_silent_refresh(monkeypatch):
    calls: list[dict] = []

    async def _fake_invoke(_governor, capability_id, params, **authority):
        calls.append({"capability_id": capability_id, "params": dict(params), "authority": authority})
        from src.actions.action_result import ActionResult

        return ActionResult.ok("Weather loaded.", request_id="weather-request")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)
    ws = _ScriptedWebSocket(
        [
            {
                "type": "chat",
                "text": "weather",
                "activity_origin": "background_read",
                "session_id": "client-spoofed-session",
            }
        ]
    )

    asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls
    assert calls[0]["params"]["_nova_trusted_activity_origin"] == "user_action"
    assert calls[0]["params"]["session_id"]
    assert calls[0]["params"]["session_id"] != "client-spoofed-session"


def test_silent_widget_refresh_is_classified_server_side_as_background_read(monkeypatch):
    calls: list[dict] = []

    async def _fake_invoke(_governor, capability_id, params, **authority):
        calls.append({"capability_id": capability_id, "params": dict(params), "authority": authority})
        from src.actions.action_result import ActionResult

        return ActionResult.ok("Weather loaded.", request_id="weather-request")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)
    ws = _ScriptedWebSocket(
        [
            {
                "type": "chat",
                "text": "weather",
                "silent_widget_refresh": True,
            }
        ]
    )

    asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls
    assert calls[0]["params"]["_nova_trusted_activity_origin"] == "background_read"


def test_silent_flag_cannot_relabel_action_command_as_background(monkeypatch):
    calls: list[dict] = []

    async def _fake_invoke(_governor, capability_id, params, **authority):
        calls.append({"capability_id": capability_id, "params": dict(params)})
        from src.actions.action_result import ActionResult

        return ActionResult.ok("Volume adjusted.", request_id="volume-request")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)
    ws = _ScriptedWebSocket(
        [
            {
                "type": "chat",
                "text": "volume up",
                "silent_widget_refresh": True,
            }
        ]
    )

    asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls
    assert calls[0]["params"]["_nova_trusted_activity_origin"] == "user_action"


@pytest.mark.parametrize(
    "raw",
    [
        "what happened with OpenAI today?",
        "what happened with the election?",
        "what happened with my project?",
    ],
)
def test_generic_happened_questions_do_not_use_activity_recap(monkeypatch, raw):
    sentinel = "normal route handled this question"

    async def _general_chat(*args, **kwargs):
        from src.base_skill import SkillResult

        return SkillResult(success=True, message=sentinel, skill="general_chat")

    monkeypatch.setattr(brain_server, "run_general_chat_fallback", _general_chat)
    monkeypatch.setattr(
        brain_server.GovernorMediator,
        "parse_governed_invocation",
        staticmethod(lambda *args, **kwargs: None),
    )
    ws = _ScriptedWebSocket([raw])

    asyncio.run(brain_server.websocket_endpoint(ws))

    assert sentinel in _chat_messages(ws)[-1]
