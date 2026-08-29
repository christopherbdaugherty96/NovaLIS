import pytest
from src.conversation.conversation_router import ConversationRouter
from src.conversation.session_router import SessionRouter


@pytest.mark.parametrize(
    "prompt",
    [
        "What do I have next?",
        "What changed?",
        "What am I waiting on?",
        "What did I need to finish?",
        "What should I do next?",
        "What did I finish today?",
    ],
)
def test_personal_operations_questions_fail_closed_before_capability_routing(prompt: str):
    decision = ConversationRouter.route(prompt)
    gate = SessionRouter.evaluate_gate(decision, {}, 0)

    assert gate.handled is True
    assert "private personal-operations question" in gate.message
    assert "don't have assembled private state" in gate.message
    assert "did not search the public web or run another capability" in gate.message


def test_personal_operations_gate_precedes_generic_clarification():
    decision = ConversationRouter.route("What changed?")

    assert decision.needs_clarification is False
    assert SessionRouter.evaluate_gate(decision, {}, 0).handled is True
