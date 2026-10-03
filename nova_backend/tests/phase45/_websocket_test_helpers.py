from __future__ import annotations

import json
from types import SimpleNamespace

from fastapi import WebSocketDisconnect


class _ScriptedWebSocket:
    def __init__(self, messages: list[object], *, headers: dict[str, str] | None = None) -> None:
        self._messages = list(messages)
        self.sent_messages: list[dict] = []
        self.client = SimpleNamespace(host="127.0.0.1", port=50000)
        self.closed: tuple[int, str] | None = None
        self.headers = {
            "host": "localhost",
            "origin": "http://localhost",
        }
        if headers:
            self.headers.update({str(key): str(value) for key, value in headers.items()})

    async def accept(self) -> None:
        return None

    async def close(self, *, code: int, reason: str) -> None:
        self.closed = (code, reason)

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        if self._messages:
            next_message = self._messages.pop(0)
            if isinstance(next_message, dict):
                return json.dumps(next_message)
            return json.dumps({"type": "chat", "text": next_message})
        raise WebSocketDisconnect()


def _chat_messages(ws: _ScriptedWebSocket) -> list[str]:
    return [msg.get("message", "") for msg in ws.sent_messages if msg.get("type") == "chat"]
