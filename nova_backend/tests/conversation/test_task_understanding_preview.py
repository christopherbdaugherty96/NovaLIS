from src.brain.task_understanding import SimpleTaskPlan
from src.conversation.task_understanding_preview import (
    build_task_understanding_preview,
    format_task_understanding_preview,
)


def test_casual_chat_does_not_enable_task_understanding_preview():
    preview = build_task_understanding_preview("hey")

    assert preview.enabled is False
    assert preview.plan is None
    assert preview.prompt_block == ""
    assert preview.authority_effect == "none"


def test_task_like_request_gets_structured_preview_block():
    preview = build_task_understanding_preview(
        "summarize this task",
        session_context={"task": "Prepare a bounded planning-only summary."},
    )

    assert preview.enabled is True
    assert isinstance(preview.plan, SimpleTaskPlan)
    assert preview.plan.execution_performed is False
    assert preview.plan.authorization_granted is False
    assert "Task understanding preview" in preview.prompt_block
    assert "Goal: summarize this task" in preview.prompt_block
    assert "Confidence:" in preview.prompt_block
    assert "Clarification needed: false" in preview.prompt_block
    assert "Suggested next step:" in preview.prompt_block
    assert "Authority effect: none" in preview.prompt_block


def test_preview_block_can_include_task_envelope():
    preview = build_task_understanding_preview("make a bounded task envelope")

    assert preview.plan is not None
    block = format_task_understanding_preview(preview.plan, include_envelope=True)

    assert "Task envelope:" in block
    assert "Allowed actions:" in block
    assert "Blocked actions:" in block
    assert "use OpenClaw" in block
    assert "send email" in block
    assert "Stop condition:" in block
    assert "Failure behavior:" in block


def test_preview_block_can_omit_task_envelope():
    preview = build_task_understanding_preview("make a bounded task envelope")

    assert preview.plan is not None
    block = format_task_understanding_preview(preview.plan, include_envelope=False)

    assert "Task understanding preview" in block
    assert "Task envelope:" not in block


def test_ambiguous_task_preview_preserves_clarification_needed():
    preview = build_task_understanding_preview("turn this script into a scene plan")

    assert preview.plan is not None
    assert preview.plan.understanding.clarification_needed is True
    assert "Clarification needed: true" in preview.prompt_block
    assert "Ask one focused clarification" in preview.prompt_block
