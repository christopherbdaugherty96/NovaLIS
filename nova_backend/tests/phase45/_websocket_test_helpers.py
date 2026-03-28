from __future__ import annotations

import json

from fastapi import WebSocketDisconnect


class _ScriptedWebSocket:
    def __init__(self, messages: list[object]) -> None:
        self._messages = list(messages)
        self.sent_messages: list[dict] = []

    async def accept(self) -> None:
        return None

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
