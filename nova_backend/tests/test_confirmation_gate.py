from __future__ import annotations

from src.gates.confirmation_gate import ConfirmationGate, GateResult


def test_gate_silent_when_idle():
    gate = ConfirmationGate()
    result = gate.try_resolve("yes")
    assert result.message is None
    assert result.confirmed is False


def test_gate_silent_on_no_when_idle():
    gate = ConfirmationGate()
    result = gate.try_resolve("no")
    assert result.message is None


def test_gate_silent_on_arbitrary_input_when_idle():
    gate = ConfirmationGate()
    result = gate.try_resolve("do something dangerous")
    assert result.message is None


def test_has_pending_confirmation_false_when_idle():
    gate = ConfirmationGate()
    assert gate.has_pending_confirmation() is False


def test_clear_keeps_gate_idle():
    gate = ConfirmationGate()
    gate.clear()
    assert gate.has_pending_confirmation() is False
    assert gate.try_resolve("yes").message is None


def test_set_pending_not_present():
    """set_pending was removed as dead code. Confirm it no longer exists."""
    gate = ConfirmationGate()
    assert not hasattr(gate, "set_pending"), (
        "set_pending() was a dead placeholder and should have been removed from ConfirmationGate"
    )


def test_gate_result_has_no_gate_context_field():
    """gate_context was removed with set_pending. GateResult should not carry it."""
    result = GateResult()
    assert not hasattr(result, "gate_context"), (
        "gate_context was part of the dead set_pending placeholder and should be gone"
    )


def test_global_confirmation_gate_instance_exists():
    from src.gates.confirmation_gate import confirmation_gate
    assert isinstance(confirmation_gate, ConfirmationGate)
