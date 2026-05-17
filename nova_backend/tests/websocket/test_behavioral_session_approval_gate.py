from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult
from src.governor.governor_mediator import GovernorMediator, Invocation

from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages


class _RecordingLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((str(event_type), dict(payload or {})))


def _event_types(ledger: _RecordingLedger) -> list[str]:
    return [event_type for event_type, _payload in ledger.events]


def _install_session_gate_baseline(monkeypatch, routes: dict[str, Invocation]) -> list[str]:
    parse_calls: list[str] = []

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    def _fake_parse(text: str, session_id: str | None = None):
        normalized = str(text or "").strip().lower().rstrip(".!?")
        parse_calls.append(normalized)
        return routes.get(normalized)

    monkeypatch.setattr(
        GovernorMediator,
        "parse_governed_invocation",
        staticmethod(_fake_parse),
    )
    return parse_calls


def test_cap22_session_request_creates_pending_state_without_execution(monkeypatch):
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)
    assert any("This action needs confirmation." in message for message in _chat_messages(ws))


def test_cap64_session_request_creates_pending_state_without_execution(monkeypatch):
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {
            "draft email": Invocation(
                capability_id=64,
                params={"to": "test@example.com", "subject": "Approval gate test"},
            )
        },
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Draft opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft email"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)
    chat_messages = _chat_messages(ws)
    assert any("Reply 'yes' to proceed or 'no' to cancel." in message for message in chat_messages)
    assert any("Nova never sends email automatically" in message for message in chat_messages)


def test_session_yes_resumes_pending_cap22_only_through_governed_invocation(monkeypatch):
    ledger = _RecordingLedger()
    parse_calls = _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened documents.", request_id="confirmed-cap22")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert parse_calls == ["open documents"]
    assert len(calls) == 1
    capability_id, params = calls[0]
    assert capability_id == 22
    assert params["target"] == "documents"
    assert params["confirmed"] is True
    assert str(params.get("session_id") or "").strip()
    assert _event_types(ledger) == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]
    assert any("Opened documents." in message for message in _chat_messages(ws))


def test_session_yes_resumes_pending_cap64_only_through_governed_invocation(monkeypatch):
    ledger = _RecordingLedger()
    parse_calls = _install_session_gate_baseline(
        monkeypatch,
        {
            "draft email": Invocation(
                capability_id=64,
                params={"to": "test@example.com", "subject": "Approval gate test"},
            )
        },
    )
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Draft opened.", request_id="confirmed-cap64")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft email", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert parse_calls == ["draft email"]
    assert len(calls) == 1
    capability_id, params = calls[0]
    assert capability_id == 64
    assert params["to"] == "test@example.com"
    assert params["subject"] == "Approval gate test"
    assert params["confirmed"] is True
    assert str(params.get("session_id") or "").strip()
    assert _event_types(ledger) == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]
    assert any("Draft opened." in message for message in _chat_messages(ws))


def test_session_approved_cap22_uses_real_governor_ledger_sequence(monkeypatch):
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open repo": Invocation(capability_id=22, params={"path": str(Path.cwd())})},
    )
    monkeypatch.setattr(brain_server.RUNTIME_GOVERNOR, "_ledger", ledger)

    ws = _ScriptedWebSocket(["open repo", "yes"])
    with (
        patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")),
        patch(
            "src.system_control.system_control_executor.SystemControlExecutor.open_path",
            return_value=True,
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1
    assert any("Opened folder:" in message or "Opened path:" in message for message in _chat_messages(ws))


def test_session_approved_cap64_uses_real_governor_ledger_sequence(monkeypatch):
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {
            "draft email": Invocation(
                capability_id=64,
                params={
                    "to": "test@example.com",
                    "subject": "Approval gate test",
                    "body_intent": "write a short approval gate test draft",
                },
            )
        },
    )
    monkeypatch.setattr(brain_server.RUNTIME_GOVERNOR, "_ledger", ledger)

    ws = _ScriptedWebSocket(["draft email", "yes"])
    with (
        patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("general chat model should not run")),
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="Approval gate test body."),
        patch(
            "src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto",
            return_value=True,
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert "EMAIL_DRAFT_CREATED" in _event_types(ledger)
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1
    assert any("Email draft" in message and "opened in your mail client" in message for message in _chat_messages(ws))


def test_session_no_clears_pending_without_execution(monkeypatch):
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents", "no"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)
    assert any("Cancelled pending action." in message for message in _chat_messages(ws))


def test_session_cancel_clears_pending_without_execution(monkeypatch):
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents", "cancel"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)
    assert any("Cancelled pending action." in message for message in _chat_messages(ws))


def test_session_unrelated_input_cancels_pending_without_execution(monkeypatch):
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)
    ws = _ScriptedWebSocket(["open documents", "what can you do?"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)
    chat_messages = _chat_messages(ws)
    assert any("Cancelled the pending action before handling your new command." in message for message in chat_messages)
