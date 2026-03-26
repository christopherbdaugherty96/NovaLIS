from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from fastapi import WebSocketDisconnect

from src import brain_server
from src.conversation.session_router import GateResult


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


def _message_types(ws: _ScriptedWebSocket) -> list[str]:
    return [str(msg.get("type") or "") for msg in ws.sent_messages]


def test_silent_policy_overview_refresh_updates_widget_without_chat_noise(monkeypatch, tmp_path):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    store = brain_server.AtomicPolicyStore(path=tmp_path / "atomic_policies.json")
    monkeypatch.setattr(brain_server, "AtomicPolicyStore", lambda *args, **kwargs: store)

    ws = _ScriptedWebSocket([{"type": "chat", "text": "policy overview", "silent_widget_refresh": True}])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert not any("Policy Drafts" in msg for msg in _chat_messages(ws))
    assert "policy_overview" in _message_types(ws)


def test_policy_create_simulate_and_run_once_emit_policy_widgets(monkeypatch, tmp_path):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    store = brain_server.AtomicPolicyStore(path=tmp_path / "atomic_policies.json")
    monkeypatch.setattr(brain_server, "AtomicPolicyStore", lambda *args, **kwargs: store)

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        create_ws = _ScriptedWebSocket(["policy create weekday system status at 8:00 am"])
        asyncio.run(brain_server.websocket_endpoint(create_ws))

        overview = store.overview()
        policy_id = str(overview["items"][0]["policy_id"])

        simulate_ws = _ScriptedWebSocket([f"policy simulate {policy_id}"])
        asyncio.run(brain_server.websocket_endpoint(simulate_ws))

        run_ws = _ScriptedWebSocket([f"policy run {policy_id} once"])
        asyncio.run(brain_server.websocket_endpoint(run_ws))

    assert "policy_overview" in _message_types(create_ws)
    assert "policy_item" in _message_types(create_ws)
    assert any("Policy draft created" in msg for msg in _chat_messages(create_ws))

    assert "policy_item" in _message_types(simulate_ws)
    assert "policy_simulation" in _message_types(simulate_ws)
    assert any("Policy Simulation" in msg for msg in _chat_messages(simulate_ws))

    assert "policy_item" in _message_types(run_ws)
    assert "policy_run" in _message_types(run_ws)
    assert any("Policy Manual Run" in msg for msg in _chat_messages(run_ws))

    refreshed = store.get_policy(policy_id)
    assert refreshed is not None
    assert int(refreshed.get("simulation_count") or 0) >= 1
    assert int(refreshed.get("manual_run_count") or 0) >= 1
