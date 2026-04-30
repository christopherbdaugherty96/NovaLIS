import pytest

from src.brain.task_understanding import (
    ApprovalLevel,
    ContextSource,
    TaskEnvelope,
    TaskUnderstanding,
    build_simple_task_plan,
    build_task_envelope,
    understand_task,
)


def test_task_understanding_returns_structured_output():
    out = understand_task("summarize this task", session_context={"task": "Prepare a planning-only outline."})
    payload = out.to_dict()

    assert payload["goal"] == "summarize this task"
    assert payload["context_used"][0]["source"] == "session_context"
    assert payload["constraints"]
    assert payload["assumptions"] == []
    assert 0.0 <= payload["confidence"] <= 1.0
    assert payload["clarification_needed"] is False
    assert payload["suggested_next_step"]


def test_task_understanding_does_not_execute_or_authorize():
    out = understand_task("open browser tabs and compare these sites")

    assert out.execution_performed is False
    assert out.authorization_granted is False
    assert out.authority_effect == "none"
    assert "no browser tabs opened" in out.constraints
    assert "no OpenClaw execution" in out.constraints


def test_task_understanding_rejects_authorizing_instances():
    with pytest.raises(ValueError, match="non-authorizing"):
        TaskUnderstanding(
            goal="bad",
            authority_effect="approved",
        )


def test_ambiguous_task_triggers_clarification():
    out = understand_task("turn this script into a scene plan")

    assert out.clarification_needed is True
    assert out.suggested_next_step == "Ask one focused clarification before making a plan."
    assert "No script text was available in session context." in out.assumptions


def test_known_session_context_reduces_unnecessary_clarification():
    out = understand_task(
        "turn this script into a scene plan",
        session_context={"script": "A founder interviews customers and revises the prototype."},
    )

    assert out.clarification_needed is False
    assert out.confidence > 0.7
    assert any(item.source == ContextSource.SESSION_CONTEXT for item in out.context_used)
    assert "The provided session script is the source material to plan from." in out.assumptions


def test_stable_memory_is_distinguished_from_session_context_when_provided():
    out = understand_task(
        "make a bounded task envelope",
        session_context={"task": "Plan a repo review."},
        stable_memory=["User prefers small implementation steps."],
    )

    sources = [item.source for item in out.context_used]
    assert ContextSource.SESSION_CONTEXT in sources
    assert ContextSource.STABLE_MEMORY in sources
    assert ContextSource.SYSTEM_LIMITATION not in sources


def test_missing_memory_integration_is_stubbed_honestly():
    out = understand_task("make a bounded task envelope")

    assert any(item.source == ContextSource.SYSTEM_LIMITATION for item in out.context_used)
    assert "No runtime memory integration was read" in " ".join(item.value for item in out.context_used)


def test_task_envelope_includes_blocked_actions_and_stop_condition():
    envelope = build_task_envelope(step_limit=3)

    assert envelope.allowed_actions
    assert "use OpenClaw" in envelope.blocked_actions
    assert "send email" in envelope.blocked_actions
    assert envelope.stop_condition
    assert envelope.failure_behavior.startswith("Ask for clarification")
    assert envelope.approval_level == ApprovalLevel.USER_REVIEW_ONLY
    assert envelope.authority_effect == "none"


def test_task_envelope_rejects_invalid_step_limit():
    with pytest.raises(ValueError, match="step_limit"):
        TaskEnvelope(
            allowed_actions=("summarize",),
            blocked_actions=("execute",),
            environment_scope=("local_conversation",),
            step_limit=0,
            approval_level=ApprovalLevel.USER_REVIEW_ONLY,
            stop_condition="stop",
            failure_behavior="ask",
        )


def test_simple_task_mode_stays_planning_only():
    plan = build_simple_task_plan(
        "find what clarification is needed",
        session_context={"task": "Compare two unnamed websites."},
    )

    assert plan.mode == "simple_task_mode"
    assert plan.planning_only is True
    assert plan.execution_performed is False
    assert plan.authorization_granted is False
    assert "open browser tabs" in plan.envelope.blocked_actions
    assert "authorize capabilities" in plan.envelope.blocked_actions
    assert plan.plan_steps == (
        "List what is known.",
        "List what is missing or ambiguous.",
        "Ask the smallest useful clarification.",
    )


def test_simple_task_mode_scene_plan_uses_only_provided_context():
    plan = build_simple_task_plan(
        "turn this script into a scene plan",
        session_context={"script": "A customer discovers Nova, tests it, and approves the plan."},
    )

    assert plan.understanding.clarification_needed is False
    assert plan.envelope.environment_scope == (
        "local_conversation",
        "provided_session_context",
        "caller_provided_stable_memory",
    )
    assert plan.plan_steps[-1] == "Return the scene plan for user review."
