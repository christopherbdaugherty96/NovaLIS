from __future__ import annotations

import asyncio
import json

from fastapi import WebSocketDisconnect

from src import brain_server
from src.governor.governor_mediator import GovernorMediator


class _DisconnectingWebSocket:
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        raise WebSocketDisconnect()


def test_websocket_disconnect_clears_governor_mediator_session(monkeypatch):
    called: list[str] = []

    def _fake_clear_session(session_id: str) -> None:
        called.append(session_id)

    monkeypatch.setattr(GovernorMediator, "clear_session", staticmethod(_fake_clear_session))

    ws = _DisconnectingWebSocket()
    asyncio.run(brain_server.websocket_endpoint(ws))

    assert called, "GovernorMediator.clear_session should be called on websocket disconnect."
