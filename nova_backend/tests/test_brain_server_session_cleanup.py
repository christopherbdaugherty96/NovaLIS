from __future__ import annotations

import asyncio
import json

from fastapi import WebSocketDisconnect

from src import brain_server
from src.governor.governor_mediator import GovernorMediator
from src.governor.governor_mediator import Invocation
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult


class _DisconnectingWebSocket:
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []
        self.headers = {"host": "testserver", "origin": "http://testserver"}

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        raise WebSocketDisconnect()


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


def test_websocket_disconnect_clears_governor_mediator_session(monkeypatch):
    called: list[str] = []

    def _fake_clear_session(session_id: str) -> None:
        called.append(session_id)

    monkeypatch.setattr(GovernorMediator, "clear_session", staticmethod(_fake_clear_session))

    ws = _DisconnectingWebSocket()
    asyncio.run(brain_server.websocket_endpoint(ws))

    assert called, "GovernorMediator.clear_session should be called on websocket disconnect."


def test_open_file_folder_requires_confirmation_before_dispatch(monkeypatch):
    calls: list[tuple[int, dict]] = []

    def _fake_parse(text: str, session_id: str | None = None):
        if "open documents" in text.strip().lower():
            return Invocation(capability_id=22, params={"target": "documents"})
        return None

    def _fake_handle(capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Opened.", request_id="req-confirm")

    monkeypatch.setattr(
        GovernorMediator,
        "parse_governed_invocation",
        staticmethod(_fake_parse),
    )
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server.RUNTIME_GOVERNOR,
        "handle_governed_invocation",
        _fake_handle,
    )

    ws = _ScriptedWebSocket(["open documents", "yes"])
    asyncio.run(brain_server.websocket_endpoint(ws))

    assert any(
        msg.get("type") == "chat" and "This action needs confirmation." in msg.get("message", "")
        for msg in ws.sent_messages
    )
    assert calls, "Expected confirmed capability dispatch."
    cap_id, params = calls[0]
    assert cap_id == 22
    assert params.get("confirmed") is True


def test_response_verification_chat_surface_prefers_accuracy_label(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server.RUNTIME_GOVERNOR,
        "handle_governed_invocation",
        lambda capability_id, params: ActionResult.ok(
            "Verification Report\nClaim Reliability: Low (0.40)\nReport Confidence: High (0.90)",
            data={
                "verification_accuracy_label": "Low",
                "verification_confidence_label": "High",
                "verification_recommended": True,
            },
            request_id="verify-runtime",
        ),
    )

    ws = _ScriptedWebSocket(["fact check The moon has a thick atmosphere like Earth."])
    asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = [msg for msg in ws.sent_messages if msg.get("type") == "chat"]
    assert any(msg.get("confidence") == "Claim reliability Low" for msg in chat_messages)
    assert any(
        any(action.get("label") == "Re-check with sources" for action in (msg.get("suggested_actions") or []))
        for msg in chat_messages
    )
