import asyncio

from src.governor.governor_mediator import GovernorMediator
from src.gates.confirmation_gate import confirmation_gate
from src.skill_registry import skill_registry


def test_execution_like_input_is_refused():
    """
    Phase-3.5 runtime proof:
    Execution-looking input must not trigger any execution path.
    """

    text = "open calculator"

    # Governor mediation should return plain text only
    mediated = GovernorMediator.mediate(text)
    assert mediated == text

    # Confirmation gate must be idle and silent
    assert not confirmation_gate.has_pending_confirmation()
    gate_result = confirmation_gate.try_resolve(mediated)
    assert gate_result.message is None
    assert gate_result.confirmed is False

    # Skill registry may handle or ignore, but must not execute
    result = asyncio.run(skill_registry.handle_query(mediated))
    assert result is None or hasattr(result, "message")
