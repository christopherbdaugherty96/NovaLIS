from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from fastapi import WebSocketDisconnect

from src import brain_server
from src.conversation.session_router import GateResult


class _ScriptedWebSocket:
    def __init__(self, messages: list[str]) -> None:
        self._messages = list(messages)
        self.sent_messages: list[dict] = []
        self.headers = {"host": "testserver", "origin": "http://testserver"}

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        if self._messages:
            return json.dumps({"type": "chat", "text": self._messages.pop(0)})
        raise WebSocketDisconnect()


def test_parse_tone_set_body_accepts_normalized_trailing_punctuation():
    assert brain_server._parse_tone_set_body("concise.") == ("global", "concise", True)
    assert brain_server._parse_tone_set_body("research detailed.") == ("research", "detailed", True)


def test_tone_commands_accept_normalized_punctuation(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server.interface_personality_agent,
        "set_global_tone",
        lambda profile: {
            "global_profile": profile,
            "override_count": 0,
            "summary": f"Global tone: {profile}. No domain overrides.",
        },
    )
    monkeypatch.setattr(
        brain_server.interface_personality_agent,
        "reset_all_tone",
        lambda: {
            "global_profile": "balanced",
            "override_count": 0,
            "summary": "Global tone: balanced. No domain overrides.",
        },
    )

    ws = _ScriptedWebSocket(["tone set concise", "tone reset all"])
    asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = [msg for msg in ws.sent_messages if msg.get("type") == "chat"]
    assert any("Global tone set to concise." in msg.get("message", "") for msg in chat_messages)
    assert any("Tone settings reset to the default profile." in msg.get("message", "") for msg in chat_messages)


def test_detailed_tone_general_chat_is_not_double_formatted(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["tone set detailed", "What is a GPU?", "tone reset all"])
    original_reset = brain_server.interface_personality_agent.reset_all_tone

    try:
        with patch(
            "src.skills.general_chat.generate_chat",
            return_value=(
                "First sentence has useful context. "
                "Second sentence adds details. "
                "Third sentence keeps important nuance. "
                "Fourth sentence rounds it out."
            ),
        ):
            asyncio.run(brain_server.websocket_endpoint(ws))
    finally:
        original_reset()

    chat_messages = [msg.get("message", "") for msg in ws.sent_messages if msg.get("type") == "chat"]
    detailed_reply = next(
        (
            message
            for message in chat_messages
            if "First sentence has useful context." in message and "Third sentence keeps important nuance." in message
        ),
        "",
    )
    assert "Global tone set to detailed." in "\n".join(chat_messages)
    assert detailed_reply
    assert detailed_reply.count("Summary:") <= 1
