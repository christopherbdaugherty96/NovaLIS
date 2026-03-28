from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src import brain_server


def test_websocket_rejects_non_local_host_and_origin():
    client = TestClient(brain_server.app)

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            "/ws",
            headers={"Host": "evil.example", "Origin": "https://evil.example"},
        ) as websocket:
            websocket.receive_json()
