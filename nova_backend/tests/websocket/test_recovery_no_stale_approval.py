"""Recovery evidence: pending confirmation must not survive WebSocket disconnect.

When a user requests a confirmation-bound action (Cap 22 or Cap 64) and then
the WebSocket disconnects before they confirm, the pending action must not
execute on reconnect. A fresh session must not inherit stale approval state.

This closes the last remaining evidence gap for both Cap 22 and Cap 64
operator journeys.
"""
from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

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
    return [et for et, _ in ledger.events]


def _install_gate_baseline(monkeypatch, routes):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *a, **kw: GateResult(handled=False)),
    )

    def _fake_parse(text, session_id=None):
        normalized = str(text or "").strip().lower().rstrip(".!?")
        return routes.get(normalized)

    monkeypatch.setattr(
        GovernorMediator,
        "parse_governed_invocation",
        staticmethod(_fake_parse),
    )


# ---------------------------------------------------------------------------
# Cap 22 recovery: disconnect after pending, reconnect with "yes"
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_cap22_disconnect_clears_pending_state(monkeypatch):
    """After a WebSocket session ends with a pending Cap 22 action,
    a new session sending 'yes' must NOT execute the stale action."""
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()

    _install_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_gov, capability_id, params):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="stale-cap22")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    # Session 1: request creates pending state, then disconnects (no yes/no)
    ws1 = _ScriptedWebSocket(["open documents"])
    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model should not run"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws1))

    # Verify pending was created but not executed
    assert calls == []
    assert any(
        "open_file_folder" in m and "Cap 22" in m for m in _chat_messages(ws1)
    )

    # Session 2: new connection sends "yes" — must NOT resume stale pending
    ws2 = _ScriptedWebSocket(["yes"])
    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="I'm here when you're ready.",
    ):
        asyncio.run(brain_server.websocket_endpoint(ws2))

    # The stale pending must not have been executed
    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)


# ---------------------------------------------------------------------------
# Cap 64 recovery: disconnect after pending, reconnect with "yes"
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_cap64_disconnect_clears_pending_state(monkeypatch):
    """After a WebSocket session ends with a pending Cap 64 action,
    a new session sending 'yes' must NOT execute the stale action."""
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()

    _install_gate_baseline(
        monkeypatch,
        {
            "draft email": Invocation(
                capability_id=64,
                params={"to": "test@example.com", "subject": "Recovery test"},
            )
        },
    )

    async def _fake_invoke(_gov, capability_id, params):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Draft opened.", request_id="stale-cap64")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    # Session 1: request creates pending state, then disconnects
    ws1 = _ScriptedWebSocket(["draft email"])
    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model should not run"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws1))

    assert calls == []
    assert any(
        "send_email_draft" in m and "Cap 64" in m
        for m in _chat_messages(ws1)
    )

    # Session 2: new connection sends "yes"
    ws2 = _ScriptedWebSocket(["yes"])
    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="I'm here when you're ready.",
    ):
        asyncio.run(brain_server.websocket_endpoint(ws2))

    # Stale pending must not have been executed
    assert calls == []
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)


# ---------------------------------------------------------------------------
# Same-session fresh request after disconnect (no cross-session bleed)
# ---------------------------------------------------------------------------


def test_new_session_can_still_create_fresh_pending(monkeypatch):
    """A new session must be able to create its own fresh pending action
    even if a prior session had a pending action that was never resolved."""
    calls: list[tuple[int, dict]] = []
    ledger = _RecordingLedger()

    _install_gate_baseline(
        monkeypatch,
        {"open documents": Invocation(capability_id=22, params={"target": "documents"})},
    )

    async def _fake_invoke(_gov, capability_id, params):
        calls.append((capability_id, dict(params)))
        ledger.log_event("ACTION_ATTEMPTED", {"capability_id": capability_id})
        ledger.log_event("ACTION_COMPLETED", {"capability_id": capability_id})
        return ActionResult.ok("Opened.", request_id="fresh-cap22")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

    # Session 1: create pending, disconnect without resolving
    ws1 = _ScriptedWebSocket(["open documents"])
    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model should not run"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws1))

    assert calls == []

    # Session 2: make the SAME request fresh, then confirm
    ws2 = _ScriptedWebSocket(["open documents", "yes"])
    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=AssertionError("model should not run"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws2))

    # Fresh request should have been created and confirmed
    assert len(calls) == 1
    assert calls[0][0] == 22
    assert calls[0][1]["confirmed"] is True
    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1
