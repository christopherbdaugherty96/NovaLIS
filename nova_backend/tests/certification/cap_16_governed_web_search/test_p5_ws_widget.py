# tests/certification/cap_16_governed_web_search/test_p5_ws_widget.py
"""
Phase 5 — WebSocket widget-emission certification for capability 16 (governed_web_search).

Verifies the fix for #141: the search widget produced by WebSearchExecutor must be
transmitted to the WebSocket client as a {type: "search", data: {...}} message, not
silently discarded.

Tests:
  1. send_widget_message("search", ...) emits {type: "search", data: inner_data}
     and NOT {type: "search", message: text} with no data field.
  2. send_widget_message("search", ...) attaches turn_id when one is active.
  3. A WebSocket session driven by a Cap 16 success emits at least one message
     with type == "search" containing a non-empty data dict.
  4. The search widget data contains a results list.
"""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Unit tests — send_widget_message search case
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_widget_message_search_emits_type_search_with_data():
    """send_widget_message("search", ...) must emit {type: "search", data: ...}."""
    from src.brain_server import send_widget_message

    sent: list[dict] = []

    async def fake_ws_send(ws, payload):
        sent.append(payload)

    widget = {
        "type": "search",
        "data": {
            "query": "electric vehicles 2026",
            "results": [{"title": "EV boom", "url": "https://example.com"}],
            "summary": "EV adoption climbed sharply.",
            "result_count": 1,
        },
    }

    ws = MagicMock()
    with patch("src.brain_server.ws_send", side_effect=fake_ws_send):
        await send_widget_message(ws, "search", "Here are your results.", widget)

    assert len(sent) == 1
    msg = sent[0]
    assert msg["type"] == "search", f"Expected type 'search', got {msg.get('type')!r}"
    assert "data" in msg, "Search widget message must include a 'data' field"
    assert "message" not in msg or "data" in msg, (
        "Search widget must not be sent as bare text message"
    )
    inner = msg["data"]
    assert isinstance(inner, dict), "data field must be a dict"
    assert inner.get("query") == "electric vehicles 2026"
    assert isinstance(inner.get("results"), list)
    assert len(inner["results"]) == 1


@pytest.mark.asyncio
async def test_send_widget_message_search_does_not_send_bare_message():
    """The pre-fix fallthrough sent {type: "search", message: text} with no data.
    Verify that regression cannot occur.
    """
    from src.brain_server import send_widget_message

    sent: list[dict] = []

    async def fake_ws_send(ws, payload):
        sent.append(payload)

    widget = {"type": "search", "data": {"query": "test", "results": []}}
    ws = MagicMock()

    with patch("src.brain_server.ws_send", side_effect=fake_ws_send):
        await send_widget_message(ws, "search", "Some message text.", widget)

    assert len(sent) == 1
    msg = sent[0]
    # Must NOT be the pre-fix bare-message shape
    assert not (msg.get("type") == "search" and "message" in msg and "data" not in msg), (
        "Regression: search widget is being sent as bare text with no data field"
    )


@pytest.mark.asyncio
async def test_send_widget_message_search_attaches_turn_id():
    """turn_id is attached when a WS turn is active."""
    from src.brain_server import send_widget_message, _current_ws_turn_id

    sent: list[dict] = []

    async def fake_ws_send(ws, payload):
        sent.append(payload)

    widget = {"type": "search", "data": {"query": "q", "results": []}}
    ws = MagicMock()
    token = _current_ws_turn_id.set("test-turn-abc")
    try:
        with patch("src.brain_server.ws_send", side_effect=fake_ws_send):
            await send_widget_message(ws, "search", "msg", widget)
    finally:
        _current_ws_turn_id.reset(token)

    assert len(sent) == 1
    assert sent[0].get("turn_id") == "test-turn-abc"


# ---------------------------------------------------------------------------
# Integration test — WebSocket session emits search widget
# ---------------------------------------------------------------------------

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

_BRAVE_RESPONSE = {
    "status_code": 200,
    "data": {
        "web": {
            "results": [
                {
                    "title": "EV sales surge in 2026",
                    "url": "https://example.com/ev-2026",
                    "description": "Global EV sales rose 40% in early 2026.",
                },
            ]
        }
    },
}


@pytest.fixture(scope="module")
def search_client():
    with (
        patch("src.executors.web_search_executor.generate_chat",
              return_value="EV sales climbed sharply in 2026."),
        patch(
            "src.governor.network_mediator.NetworkMediator.request",
            return_value=_BRAVE_RESPONSE,
        ),
    ):
        from src.brain_server import app
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


def test_websocket_search_emits_search_widget_type(search_client):
    """After a search intent, at least one WebSocket message must have type == 'search'
    and a non-empty data dict.
    """
    found_search_widget = False
    with search_client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "type": "chat",
            "text": "search for latest electric vehicle sales data",
        }))
        # Drain up to 20 messages looking for the search widget
        for _ in range(20):
            try:
                raw = ws.receive_text(timeout=3)
                msg = json.loads(raw)
                if isinstance(msg, dict) and msg.get("type") == "search":
                    data = msg.get("data")
                    if isinstance(data, dict):
                        found_search_widget = True
                        break
            except Exception:
                break

    assert found_search_widget, (
        "No WebSocket message with type='search' and a data dict was received. "
        "The search widget is not being emitted to the client (regression of #141)."
    )


def test_websocket_search_widget_data_has_results(search_client):
    """The search widget data must contain a results list."""
    widget_data = None
    with search_client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "type": "chat",
            "text": "search for electric vehicle sales trends",
        }))
        for _ in range(20):
            try:
                raw = ws.receive_text(timeout=3)
                msg = json.loads(raw)
                if isinstance(msg, dict) and msg.get("type") == "search":
                    widget_data = msg.get("data")
                    break
            except Exception:
                break

    assert widget_data is not None, "No search widget message received"
    assert isinstance(widget_data, dict), "data field must be a dict"
    assert "results" in widget_data, "Search widget data must contain 'results'"
    assert isinstance(widget_data["results"], list)
