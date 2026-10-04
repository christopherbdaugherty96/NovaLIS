from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from src import brain_server
from src.utils.local_request_guard import (
    describe_http_rebinding_violation,
    describe_websocket_rebinding_violation,
)


def _request(peer: str | None, *, host: str = "localhost:8000", origin: str = "http://localhost:8000"):
    return SimpleNamespace(
        url=SimpleNamespace(path="/api/memory/export"),
        client=SimpleNamespace(host=peer) if peer is not None else None,
        headers={"host": host, "origin": origin},
    )


def test_non_loopback_peer_cannot_spoof_local_headers():
    violation = describe_http_rebinding_violation(_request("192.0.2.10"))
    assert violation and "socket peer" in violation


def test_loopback_peer_with_local_headers_is_allowed():
    assert describe_http_rebinding_violation(_request("127.0.0.1")) is None


def test_supported_nondefault_loopback_bind_is_allowed_by_host_guard():
    assert describe_http_rebinding_violation(
        _request(
            "127.0.0.2",
            host="127.0.0.2:8000",
            origin="http://127.0.0.2:8000",
        )
    ) is None


def test_missing_http_peer_fails_closed():
    violation = describe_http_rebinding_violation(_request(None))
    assert violation and "socket peer" in violation


def test_websocket_non_loopback_peer_cannot_spoof_local_headers():
    ws = SimpleNamespace(
        client=SimpleNamespace(host="198.51.100.7"),
        headers={"host": "localhost:8000", "origin": "http://localhost:8000"},
    )
    violation = describe_websocket_rebinding_violation(ws)
    assert violation and "socket peer" in violation


def test_missing_websocket_peer_fails_closed():
    ws = SimpleNamespace(
        client=None,
        headers={"host": "localhost:8000", "origin": "http://localhost:8000"},
    )
    violation = describe_websocket_rebinding_violation(ws)
    assert violation and "socket peer" in violation


def test_rejected_remote_http_request_creates_no_ledger_receipt(monkeypatch):
    ledger_events: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        brain_server,
        "_log_ledger_event",
        lambda *args, **kwargs: ledger_events.append((*args, kwargs)),
    )

    response = TestClient(
        brain_server.app,
        base_url="http://localhost",
        client=("192.0.2.10", 50000),
    ).get(
        "/api/memory/export",
        headers={"Host": "localhost", "Origin": "http://localhost"},
    )

    assert response.status_code == 403
    assert ledger_events == []


def test_rejected_remote_websocket_creates_no_session_or_ledger_receipt(monkeypatch):
    ledger_events: list[tuple[object, ...]] = []
    session_started = False

    class _RemoteWebSocket:
        client = SimpleNamespace(host="198.51.100.7", port=50000)
        headers = {"host": "localhost", "origin": "http://localhost"}
        accepted = False
        closed: tuple[int, str] | None = None

        async def accept(self):
            self.accepted = True

        async def close(self, *, code: int, reason: str):
            self.closed = (code, reason)

    def _unexpected_session_start(*_args, **_kwargs):
        nonlocal session_started
        session_started = True
        raise AssertionError("rejected websocket must not initialize a governed session")

    monkeypatch.setattr(
        brain_server,
        "_log_ledger_event",
        lambda *args, **kwargs: ledger_events.append((*args, kwargs)),
    )
    monkeypatch.setattr(brain_server, "build_general_chat_skill", _unexpected_session_start)
    websocket = _RemoteWebSocket()

    asyncio.run(brain_server.websocket_endpoint(websocket))

    assert websocket.accepted is False
    assert websocket.closed == (1008, "Local Nova websocket access requires loopback Host/Origin.")
    assert session_started is False
    assert ledger_events == []


def test_main_rejects_non_loopback_bind(monkeypatch):
    monkeypatch.setenv("NOVA_HOST", "0.0.0.0")
    with pytest.raises(RuntimeError, match="loopback"):
        brain_server.main()


def test_main_passes_loopback_bind_to_uvicorn(monkeypatch):
    monkeypatch.setenv("NOVA_HOST", "127.0.0.1")
    monkeypatch.setenv("NOVA_PORT", "8765")
    called = {}
    monkeypatch.setattr(
        "uvicorn.run",
        lambda target, **kwargs: called.update(target=target, **kwargs),
    )
    brain_server.main()
    assert called == {"target": "src.brain_server:app", "host": "127.0.0.1", "port": 8765}


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_api_documentation_routes_are_disabled(path):
    response = TestClient(brain_server.app).get(path)
    assert response.status_code == 404
