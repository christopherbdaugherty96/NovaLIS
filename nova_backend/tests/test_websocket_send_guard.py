import asyncio

import pytest
from src import brain_server


class _ClosedWebSocket:
    async def send_text(self, payload: str) -> None:
        raise RuntimeError('Cannot call "send" once a close message has been sent.')


class _BrokenWebSocket:
    async def send_text(self, payload: str) -> None:
        raise RuntimeError("unexpected websocket failure")


def test_ws_send_ignores_already_closed_connection():
    asyncio.run(brain_server.ws_send(_ClosedWebSocket(), {"type": "chat_done"}))


def test_ws_send_reraises_unrelated_runtime_error():
    with pytest.raises(RuntimeError, match="unexpected websocket failure"):
        asyncio.run(brain_server.ws_send(_BrokenWebSocket(), {"type": "chat_done"}))
