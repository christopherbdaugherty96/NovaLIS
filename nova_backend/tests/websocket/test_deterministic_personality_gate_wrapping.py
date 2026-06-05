from __future__ import annotations

import asyncio
from unittest.mock import patch

from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult

from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages


class _RecordingLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((str(event_type), dict(payload or {})))


def _event_types(ledger: _RecordingLedger) -> list[str]:
    return [event_type for event_type, _payload in ledger.events]


def _install_plain_gate(monkeypatch) -> None:
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )


def _assert_personality_gate(message: str, *, cap_name: str, cap_id: int) -> None:
    assert "?" in message
    assert "Would you like to proceed?" in message
    assert cap_name in message
    assert f"Cap {cap_id}" in message


def test_cap22_deterministic_prompt_uses_personality_gate_wrapper(monkeypatch, tmp_path):
    _install_plain_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket([f"open {tmp_path}"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    _assert_personality_gate(
        "\n".join(_chat_messages(ws)),
        cap_name="open_file_folder",
        cap_id=22,
    )


def test_cap64_deterministic_prompt_uses_personality_gate_wrapper(monkeypatch):
    _install_plain_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Draft opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft an email to test@example.com about quarterly report"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    _assert_personality_gate(
        "\n".join(_chat_messages(ws)),
        cap_name="send_email_draft",
        cap_id=64,
    )


def test_cap22_deterministic_yes_still_executes_same_path(monkeypatch, tmp_path):
    _install_plain_gate(monkeypatch)
    ledger = _RecordingLedger()
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened documents.", request_id="confirmed-cap22")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket([f"open {tmp_path}", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(calls) == 1
    assert calls[0][0] == 22
    assert calls[0][1]["confirmed"] is True
    assert _event_types(ledger) == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]


def test_cap64_deterministic_yes_still_executes_same_path(monkeypatch):
    _install_plain_gate(monkeypatch)
    ledger = _RecordingLedger()
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Draft opened.", request_id="confirmed-cap64")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft an email to test@example.com about quarterly report", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(calls) == 1
    assert calls[0][0] == 64
    assert calls[0][1]["confirmed"] is True
    assert _event_types(ledger) == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]


def test_cap22_deterministic_no_still_cancels(monkeypatch, tmp_path):
    _install_plain_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket([f"open {tmp_path}", "no"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert any("Cancelled pending action." in message for message in _chat_messages(ws))


def test_cap64_deterministic_no_still_cancels(monkeypatch):
    _install_plain_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Draft opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft an email to test@example.com about quarterly report", "no"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert any("Cancelled pending action." in message for message in _chat_messages(ws))


def test_recipientless_cap64_clarification_does_not_create_pending_confirm(monkeypatch):
    _install_plain_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Draft opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft an email about quarterly report"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    combined = "\n".join(_chat_messages(ws))
    assert calls == []
    assert "Who should the email draft be addressed to?" in combined
    assert "send_email_draft" not in combined
    assert "Cap 64" not in combined


def test_bare_yes_after_recipientless_clarification_does_not_execute(monkeypatch):
    _install_plain_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("Draft opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft an email about quarterly report", "yes"])
    with patch("src.skills.general_chat.generate_chat", return_value="I'm here when you're ready."):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert not any("Draft opened." in message for message in _chat_messages(ws))
