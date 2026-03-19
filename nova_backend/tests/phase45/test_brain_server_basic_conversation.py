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

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        if self._messages:
            return json.dumps({"type": "chat", "text": self._messages.pop(0)})
        raise WebSocketDisconnect()


def _chat_messages(ws: _ScriptedWebSocket) -> list[str]:
    return [msg.get("message", "") for msg in ws.sent_messages if msg.get("type") == "chat"]


def test_hello_uses_deterministic_local_response(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["hello"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Hello. What do you want to work on?" in msg for msg in chat_messages)


def test_what_can_you_do_with_question_mark_stays_on_capability_path(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["what can you do?"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Nova Capabilities" in msg for msg in chat_messages)


def test_project_status_this_without_active_thread_is_actionable(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["project status this"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("I do not have an active project thread yet." in msg for msg in chat_messages)


def test_followup_chat_uses_recent_conversation_context(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["What is a GPU?", "Why does that matter?"])
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        if len(prompts) == 1:
            return "A GPU is a processor designed for parallel workloads like graphics and machine learning."
        return "It matters because those parallel workloads are common in local AI and graphics."

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) >= 2
    assert "Current user message:\nWhy does that matter?" in prompts[-1]
    assert "Recent conversation" in prompts[-1]
    assert "User: What is a GPU?" in prompts[-1]
    assert "Nova: A GPU is a processor designed for parallel workloads" in prompts[-1]
