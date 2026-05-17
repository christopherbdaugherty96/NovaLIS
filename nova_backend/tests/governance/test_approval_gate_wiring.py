"""
Approval gate wiring - governance regression tests.

Verifies that the pending / approved / denied paths for confirmation-required
capabilities stay governed and non-bypassing.

Capabilities with risk_level="confirm": 22 (open_file_folder), 64 (send_email_draft).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Registry truth: only expected capabilities have risk_level="confirm"
# ---------------------------------------------------------------------------

def _load_registry() -> dict:
    registry_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "config" / "registry.json"
    )
    return json.loads(registry_path.read_text(encoding="utf-8"))


class _RecordingLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, dict(payload or {})))


def _event_types(ledger: _RecordingLedger) -> list[str]:
    return [event_type for event_type, _payload in ledger.events]


def test_only_expected_capabilities_require_confirmation():
    registry = _load_registry()
    confirm_caps = {
        c["id"]
        for c in registry["capabilities"]
        if c.get("risk_level") == "confirm"
    }
    assert confirm_caps == {22, 64}, (
        f"Unexpected confirmation-required capabilities: {confirm_caps}. "
        "Adding a new confirm-risk capability requires a reviewed approval "
        "gate wiring update."
    )


def test_confirm_capabilities_have_requires_confirmation_true():
    registry = _load_registry()
    for cap in registry["capabilities"]:
        if cap.get("risk_level") == "confirm":
            assert cap.get("requires_confirmation") is True, (
                f"Cap {cap['id']} ({cap['name']}) has risk_level=confirm "
                "but requires_confirmation is not True"
            )


def test_non_confirm_capabilities_do_not_require_confirmation():
    registry = _load_registry()
    for cap in registry["capabilities"]:
        if cap.get("risk_level") != "confirm":
            assert cap.get("requires_confirmation") is not True, (
                f"Cap {cap['id']} ({cap['name']}) has requires_confirmation=True "
                "but risk_level is not 'confirm'"
            )


# ---------------------------------------------------------------------------
# Governor enforcement: confirm-risk caps are refused without confirmed=True
# ---------------------------------------------------------------------------

def test_governor_refuses_cap22_without_confirmation():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(22, {"target": "documents"})
    assert result.success is False
    assert "requires confirmation" in result.message.lower()


def test_governor_refuses_cap64_without_confirmation():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(
        64, {"to": "test@example.com", "subject": "test"}
    )
    assert result.success is False
    assert "requires confirmation" in result.message.lower()


def test_governor_passes_cap22_with_confirmation():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(
        22, {"target": "documents", "confirmed": True}
    )
    # Should not be a confirmation refusal - may fail for other reasons
    # (e.g. path validation) but the approval gate must not block.
    if not result.success:
        assert "requires confirmation" not in result.message.lower(), (
            "Cap 22 was refused for confirmation even with confirmed=True"
        )


def test_governor_passes_cap64_with_confirmation():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(
        64,
        {"to": "test@example.com", "subject": "test", "confirmed": True},
    )
    if not result.success:
        assert "requires confirmation" not in result.message.lower(), (
            "Cap 64 was refused for confirmation even with confirmed=True"
        )


def test_governor_refuses_confirmed_false():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(
        22, {"target": "documents", "confirmed": False}
    )
    assert result.success is False
    assert "requires confirmation" in result.message.lower()


def test_governor_refuses_confirmed_empty_string():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(
        22, {"target": "documents", "confirmed": ""}
    )
    assert result.success is False
    assert "requires confirmation" in result.message.lower()


def test_pending_cap22_does_not_dispatch_or_log_action_attempted(monkeypatch):
    import src.governor.governor as governor_mod
    from src.governor.governor import Governor

    ledger = _RecordingLedger()
    monkeypatch.setattr(governor_mod.ledger_mod, "LedgerWriter", lambda: ledger)

    with patch(
        "src.executors.open_folder_executor.OpenFolderExecutor.execute",
        side_effect=AssertionError("pending cap 22 must not dispatch"),
    ):
        result = Governor().handle_governed_invocation(22, {"target": "documents"})

    assert result.success is False
    assert "requires confirmation" in result.message.lower()
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)


def test_pending_cap64_does_not_dispatch_or_log_action_attempted(monkeypatch):
    import src.governor.governor as governor_mod
    from src.governor.governor import Governor

    ledger = _RecordingLedger()
    monkeypatch.setattr(governor_mod.ledger_mod, "LedgerWriter", lambda: ledger)

    with patch(
        "src.executors.send_email_draft_executor.SendEmailDraftExecutor.execute",
        side_effect=AssertionError("pending cap 64 must not dispatch"),
    ):
        result = Governor().handle_governed_invocation(
            64, {"to": "test@example.com", "subject": "test"}
        )

    assert result.success is False
    assert "requires confirmation" in result.message.lower()
    assert "ACTION_ATTEMPTED" not in _event_types(ledger)
    assert "ACTION_COMPLETED" not in _event_types(ledger)


def test_approved_cap22_runs_only_after_governor_attempt_ledger(monkeypatch):
    import src.governor.governor as governor_mod
    from src.governor.governor import Governor

    ledger = _RecordingLedger()
    repo_root = Path(__file__).resolve().parents[3]
    monkeypatch.setattr(governor_mod.ledger_mod, "LedgerWriter", lambda: ledger)

    with patch(
        "src.system_control.system_control_executor.SystemControlExecutor.open_path",
        return_value=True,
    ):
        result = Governor().handle_governed_invocation(
            22, {"path": str(repo_root), "confirmed": True}
        )

    assert result.success is True
    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1


def test_approved_cap64_runs_only_after_governor_attempt_ledger(monkeypatch):
    import src.governor.governor as governor_mod
    from src.governor.governor import Governor

    ledger = _RecordingLedger()
    monkeypatch.setattr(governor_mod.ledger_mod, "LedgerWriter", lambda: ledger)

    with (
        patch("src.executors.send_email_draft_executor.generate_chat", return_value="body"),
        patch(
            "src.executors.send_email_draft_executor.SendEmailDraftExecutor._open_mailto",
            return_value=True,
        ),
    ):
        result = Governor().handle_governed_invocation(
            64,
            {
                "to": "test@example.com",
                "subject": "test",
                "body_intent": "write a short test draft",
                "confirmed": True,
            },
        )

    assert result.success is True
    assert result.external_effect is True
    assert _event_types(ledger).count("ACTION_ATTEMPTED") == 1
    assert _event_types(ledger).count("ACTION_COMPLETED") == 1


# ---------------------------------------------------------------------------
# Low-risk capabilities must NOT be blocked by confirmation gate
# ---------------------------------------------------------------------------

def test_low_risk_capability_not_blocked_by_confirmation_gate():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(16, {"query": "test search"})
    if not result.success:
        assert "requires confirmation" not in result.message.lower(), (
            "Low-risk capability was incorrectly blocked by confirmation gate"
        )


# ---------------------------------------------------------------------------
# Session-level confirmation resolution
# ---------------------------------------------------------------------------

def test_confirmation_resolver_accepts_yes():
    from src.websocket.session_handler import (
        pending_confirmation_resolution_action,
    )
    from src.conversation.session_router import SessionRouter

    assert pending_confirmation_resolution_action(SessionRouter, "yes") == "confirm"
    assert pending_confirmation_resolution_action(SessionRouter, "yeah") == "confirm"
    assert pending_confirmation_resolution_action(SessionRouter, "ok") == "confirm"
    assert pending_confirmation_resolution_action(SessionRouter, "sure") == "confirm"


def test_confirmation_resolver_accepts_no():
    from src.websocket.session_handler import (
        pending_confirmation_resolution_action,
    )
    from src.conversation.session_router import SessionRouter

    assert pending_confirmation_resolution_action(SessionRouter, "no") == "cancel"
    assert pending_confirmation_resolution_action(SessionRouter, "cancel") == "cancel"
    assert pending_confirmation_resolution_action(SessionRouter, "stop") == "cancel"


def test_confirmation_resolver_rejects_ambiguous_input():
    from src.websocket.session_handler import (
        pending_confirmation_resolution_action,
    )
    from src.conversation.session_router import SessionRouter

    result = pending_confirmation_resolution_action(
        SessionRouter, "tell me about the weather"
    )
    assert result == "", (
        "Ambiguous input should not resolve to confirm or cancel"
    )


# ---------------------------------------------------------------------------
# Session handler: confirm-risk caps set pending_governed_confirm in state
# ---------------------------------------------------------------------------

def test_session_handler_sets_pending_for_cap22():
    """Session handler source must set pending_governed_confirm for cap 22."""
    handler_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "websocket" / "session_handler.py"
    )
    source = handler_path.read_text(encoding="utf-8")
    assert re.search(
        r'capability_id\s*==\s*22\s+and\s+not\s+params\.get\(\s*"confirmed"\s*\)',
        source,
    ), "Session handler must gate cap 22 on pending_governed_confirm"


def test_session_handler_sets_pending_for_cap64():
    """Session handler source must set pending_governed_confirm for cap 64."""
    handler_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "websocket" / "session_handler.py"
    )
    source = handler_path.read_text(encoding="utf-8")
    assert re.search(
        r'capability_id\s*==\s*64\s+and\s+not\s+params\.get\(\s*"confirmed"\s*\)',
        source,
    ), "Session handler must gate cap 64 on pending_governed_confirm"


def test_session_handler_pending_confirm_sets_confirmed_true():
    """When user confirms, session handler must set confirmed=True in params."""
    handler_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "websocket" / "session_handler.py"
    )
    source = handler_path.read_text(encoding="utf-8")
    assert 'params["confirmed"] = True' in source, (
        "Session handler must set confirmed=True before re-invoking "
        "a confirmation-gated capability"
    )


def test_session_handler_clears_pending_on_cancel():
    """When user cancels, pending_governed_confirm must be cleared."""
    handler_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "websocket" / "session_handler.py"
    )
    source = handler_path.read_text(encoding="utf-8")
    cancel_block = re.search(
        r'confirm_action\s*==\s*"cancel".*?'
        r'session_state\["pending_governed_confirm"\]\s*=\s*None',
        source,
        re.DOTALL,
    )
    assert cancel_block, (
        "Session handler must clear pending_governed_confirm on cancel"
    )


def test_session_handler_clears_pending_on_unrelated_input():
    """Unrelated input after a confirmation prompt must clear pending state."""
    handler_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "websocket" / "session_handler.py"
    )
    source = handler_path.read_text(encoding="utf-8")
    # After the confirm and cancel blocks, there should be a fallthrough
    # that also clears pending_governed_confirm
    pending_none_count = source.count(
        'session_state["pending_governed_confirm"] = None'
    )
    assert pending_none_count >= 3, (
        f"Expected at least 3 pending_governed_confirm=None (confirm, cancel, "
        f"fallthrough), found {pending_none_count}"
    )


# ---------------------------------------------------------------------------
# ConfirmationGate class: dead code contract
# ---------------------------------------------------------------------------

def test_confirmation_gate_has_no_set_pending():
    from src.gates.confirmation_gate import ConfirmationGate
    gate = ConfirmationGate()
    assert not hasattr(gate, "set_pending"), (
        "set_pending was removed as dead code - it must not reappear"
    )


def test_confirmation_gate_not_imported_by_session_handler():
    """Session handler must not import ConfirmationGate (dead code path)."""
    handler_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "websocket" / "session_handler.py"
    )
    source = handler_path.read_text(encoding="utf-8")
    assert "confirmation_gate" not in source.lower().replace("_", ""), (
        "Session handler must not import or reference ConfirmationGate - "
        "the live flow uses pending_governed_confirm state"
    )
