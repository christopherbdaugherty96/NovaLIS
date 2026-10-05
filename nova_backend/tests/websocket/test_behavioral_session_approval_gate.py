from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult
from src.governor.approval_grants import ApprovalGrantError, ApprovalGrantStore
from src.governor.governor_mediator import GovernorMediator, Invocation
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket


class _RecordingLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((str(event_type), dict(payload or {})))


def _event_types(ledger: _RecordingLedger) -> list[str]:
    return [event_type for event_type, _payload in ledger.events]


def _receive_completed_turn(ws, *, required_text: str = "") -> list[dict]:
    frames: list[dict] = []
    found_required = not required_text
    while True:
        frame = ws.receive_json()
        frames.append(frame)
        if required_text in str(frame.get("message") or ""):
            found_required = True
        if frame.get("type") == "chat_done" and found_required:
            return frames


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
    parse_calls = _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert parse_calls == ["open documents"]
    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)
    assert any("?" in message and ("open_file_folder" in message or "Cap 22" in message) for message in _chat_messages(ws))


def test_cap22_outside_root_path_is_refused_before_confirmation(monkeypatch):
    calls: list[tuple[int, dict]] = []
    outside_root = Path(Path.cwd().anchor) / "nova-wave-c-outside-root"
    routed = GovernorMediator.parse_governed_invocation(f"open file {outside_root}")
    assert isinstance(routed, Invocation)
    assert routed.capability_id == 22
    assert routed.params["path"] == str(outside_root)

    command = "open documents"
    parse_calls = _install_session_gate_baseline(
        monkeypatch,
        {
            command.lower(): Invocation(
                capability_id=22,
                params=dict(routed.params),
            )
        },
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict, **_authority):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("should not run", request_id="outside-root-should-not-run")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket([command])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert parse_calls == [command.lower()]
    assert calls == []
    messages = _chat_messages(ws)
    assert any("outside Nova's allowed local roots" in message for message in messages), messages
    assert any("No open request was attempted" in message for message in messages)
    assert not any("?" in message and ("open_file_folder" in message or "Cap 22" in message) for message in messages)


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

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
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
    assert any("?" in message and ("send_email_draft" in message or "Cap 64" in message) for message in chat_messages)


def test_session_yes_resumes_pending_cap22_only_through_governed_invocation(monkeypatch):
    ledger = _RecordingLedger()
    parse_calls = _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok(
            "Open request sent for Documents. I couldn't verify that the file manager became visible.",
            data={
                "outcome_state": "accepted_unverified",
                "launch_request_accepted": True,
                "visible_effect_verified": False,
            },
            request_id="confirmed-cap22",
        )

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert parse_calls == ["open documents"]
    assert len(calls) == 1
    capability_id, params = calls[0]
    assert capability_id == 22
    assert params["target"] == "documents"
    assert "confirmed" not in params
    assert params["_authority"]["session_id"] == params["session_id"]
    assert str(params["_authority"]["approval_id"]).strip()
    assert str(params.get("session_id") or "").strip()
    assert _event_types(ledger) == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]
    messages = _chat_messages(ws)
    assert any("Open request sent for Documents." in message for message in messages)
    assert any("couldn't verify that the file manager became visible" in message for message in messages)
    assert not any("Opened documents." in message for message in messages)


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

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
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
    assert "confirmed" not in params
    assert params["_authority"]["session_id"] == params["session_id"]
    assert str(params["_authority"]["approval_id"]).strip()
    assert str(params.get("session_id") or "").strip()
    assert _event_types(ledger) == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]
    assert any("Draft opened." in message for message in _chat_messages(ws))


def test_session_receipt_failure_reports_no_authority_and_does_not_invoke(monkeypatch):
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )
    invoke = Mock(side_effect=AssertionError("capability must not run"))
    monkeypatch.setattr(brain_server, "invoke_governed_capability", invoke)
    monkeypatch.setattr(
        brain_server.RUNTIME_GOVERNOR,
        "issue_approval_grant",
        Mock(side_effect=ApprovalGrantError("receipt unavailable")),
    )

    ws = _ScriptedWebSocket(["open documents", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    invoke.assert_not_called()
    assert any(
        "nothing was authorized or executed" in message
        for message in _chat_messages(ws)
    )


def test_session_disabled_capability_reports_the_actual_failure(monkeypatch):
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )
    invoke = Mock(side_effect=AssertionError("capability must not run"))
    monkeypatch.setattr(brain_server, "invoke_governed_capability", invoke)
    monkeypatch.setattr(brain_server.RUNTIME_GOVERNOR.registry, "is_enabled", lambda capability_id: False)

    ws = _ScriptedWebSocket(["open documents", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    invoke.assert_not_called()
    messages = _chat_messages(ws)
    assert any("capability was disabled" in message for message in messages)
    assert not any("couldn't record your approval" in message for message in messages)


def test_session_approved_cap22_uses_real_governor_ledger_sequence(monkeypatch):
    from src.system_control.system_control_executor import (
        OpenPathLaunchResult,
        OpenPathLaunchState,
    )

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
            "src.system_control.system_control_executor.SystemControlExecutor.open_path_result",
            return_value=OpenPathLaunchResult(OpenPathLaunchState.ACCEPTED, "test_accept"),
        ),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1
    messages = _chat_messages(ws)
    assert any("Open request sent" in message for message in messages)
    assert any("couldn't verify that the file manager became visible" in message for message in messages)
    assert not any(message.startswith("Opened ") for message in messages)


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

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
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

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
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


@pytest.mark.slow
def test_session_duplicate_yes_does_not_double_execute_cap64(monkeypatch):
    """A second 'yes' after the pending action is already consumed must not
    trigger a second governed invocation.  This closes the duplicate-yes
    evidence gap in the Cap 64 proof scaffold."""
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {
            "draft email": Invocation(
                capability_id=64,
                params={"to": "test@example.com", "subject": "Duplicate yes test"},
            )
        },
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Draft opened.", request_id="dup-yes-cap64")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["draft email", "yes", "yes"])
    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="I'm here when you're ready.",
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    # The first "yes" should have consumed the pending action — exactly one invocation.
    assert len(calls) == 1
    assert calls[0][0] == 64
    assert "confirmed" not in calls[0][1]
    assert calls[0][1]["_authority"]["approval_id"]

    # Ledger must show exactly one ACTION_ATTEMPTED and one ACTION_COMPLETED.
    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1


@pytest.mark.slow
def test_session_duplicate_yes_does_not_double_execute_cap22(monkeypatch):
    """Same duplicate-yes protection test for Cap 22."""
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="dup-yes-cap22")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    ws = _ScriptedWebSocket(["open documents", "yes", "yes"])
    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="I'm here when you're ready.",
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(calls) == 1
    assert calls[0][0] == 22
    assert "confirmed" not in calls[0][1]
    assert calls[0][1]["_authority"]["approval_id"]
    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1


def test_session_unrelated_input_cancels_pending_without_execution(monkeypatch):
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
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


@pytest.mark.parametrize(
    "message",
    [
        "why is my code not working",
        "I can't sleep tonight",
        "tell me about Japan, no rush",
        "stop sign colors",
    ],
)
def test_session_without_pending_action_does_not_hijack_normal_chat(monkeypatch, message):
    _install_session_gate_baseline(monkeypatch, {})
    ws = _ScriptedWebSocket([message])
    with patch("src.skills.general_chat.generate_chat", return_value="ordinary model reply"):
        asyncio.run(brain_server.websocket_endpoint(ws))

    messages = _chat_messages(ws)
    assert any("ordinary model reply" in reply for reply in messages)
    assert not any("No action is waiting for confirmation" in reply for reply in messages)


def test_session_mixed_confirmation_reprompts_then_accepts_clean_yes(monkeypatch):
    calls: list[tuple[int, dict]] = []
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_governor, capability_id: int, params: dict, **authority):
        calls.append((capability_id, {**params, "_authority": authority}))
        return ActionResult.ok("Opened.", request_id="mixed-then-yes")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)
    ws = _ScriptedWebSocket(["open documents", "yes, don't", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(calls) == 1
    assert calls[0][0] == 22
    assert any("Reply 'yes' to continue or 'no' to cancel" in message for message in _chat_messages(ws))


@pytest.mark.slow
def test_real_websocket_composes_grant_issuance_consumption_and_replay_refusal(monkeypatch):
    """Exercise the complete /ws -> shared Governor -> harmless dispatch boundary."""
    _install_session_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )
    governor = brain_server.RUNTIME_GOVERNOR
    dispatch = Mock(return_value=ActionResult.ok("Opened harmless test target."))
    monkeypatch.setattr(governor, "_approval_grants", ApprovalGrantStore())
    monkeypatch.setattr(governor, "_ledger", _RecordingLedger())
    monkeypatch.setattr(governor, "_dispatch_capability", dispatch)

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="I'm here when you're ready.",
    ), TestClient(brain_server.app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "chat", "text": "open documents"})
            pending_frames = _receive_completed_turn(ws, required_text="Cap 22")
            assert dispatch.call_count == 0
            assert any("Cap 22" in str(frame.get("message") or "") for frame in pending_frames)

            ws.send_json({"type": "chat", "text": "yes"})
            completed_frames = _receive_completed_turn(
                ws, required_text="Opened harmless test target."
            )
            assert any(
                "Opened harmless test target." in str(frame.get("message") or "")
                for frame in completed_frames
            )

        assert dispatch.call_count == 1
        request = dispatch.call_args.args[0]
        assert request.approval_id
        assert request.params["session_id"]
        assert "confirmed" not in request.params

        replay = governor.handle_governed_invocation(
            22,
            dict(request.params),
            session_id=str(request.params["session_id"]),
            approval_id=request.approval_id,
        )
        assert replay.success is False
        assert replay.data["approval_reason"] == "replayed"
        assert dispatch.call_count == 1

        with client.websocket_connect("/ws") as second_ws:
            second_ws.send_json({"type": "chat", "text": "yes"})
            _receive_completed_turn(second_ws)
        assert dispatch.call_count == 1
