from datetime import datetime, timezone

import pytest

from src.brain.run_manager import Run, RunManager, RunStatus, RunStep
from src.brain.task_understanding import TaskUnderstanding, build_simple_task_plan
from src.conversation.task_understanding_preview import build_task_understanding_preview


def _manager() -> RunManager:
    return RunManager(
        id_factory=lambda: "run_test_1",
        clock=lambda: datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc),
    )


def test_run_can_be_created_from_task_understanding_preview():
    preview = build_task_understanding_preview(
        "summarize this task",
        session_context={"task": "Prepare a planning-only implementation outline."},
    )
    assert preview.plan is not None

    manager = _manager()
    run = manager.create_run(preview.plan)

    assert run.run_id == "run_test_1"
    assert run.status == RunStatus.PLANNING
    assert run.goal == "summarize this task"
    assert run.planning_only is True
    assert run.execution_performed is False
    assert run.authorization_granted is False
    assert run.authority_effect == "none"
    assert run.envelope.blocked_actions
    assert manager.get_run("run_test_1") == run


def test_run_steps_are_planning_only_and_non_authorizing():
    plan = build_simple_task_plan(
        "make a bounded task envelope",
        session_context={"task": "Plan a safe repo review."},
    )
    run = _manager().create_run(plan)

    assert run.steps
    assert all(step.status == "planned" for step in run.steps)
    assert all(step.authority_effect == "none" for step in run.steps)
    assert all(step.execution_performed is False for step in run.steps)
    assert all(step.authorization_granted is False for step in run.steps)


def test_run_lifecycle_list_pause_cancel():
    manager = _manager()
    run = manager.create_run(build_simple_task_plan("find what clarification is needed"))

    assert manager.list_runs() == (run,)

    paused = manager.pause_run(run.run_id, reason="waiting for source material")
    assert paused is not None
    assert paused.status == RunStatus.PAUSED
    assert paused.pause_reason == "waiting for source material"
    assert paused.execution_performed is False
    assert manager.get_run(run.run_id) == paused

    cancelled = manager.cancel_run(run.run_id, reason="user changed direction")
    assert cancelled is not None
    assert cancelled.status == RunStatus.CANCELLED
    assert cancelled.cancel_reason == "user changed direction"
    assert cancelled.authorization_granted is False
    assert manager.get_run(run.run_id) == cancelled


def test_pause_cancel_unknown_run_return_none():
    manager = _manager()

    assert manager.get_run("missing") is None
    assert manager.pause_run("missing") is None
    assert manager.cancel_run("missing") is None
    assert manager.update_focus("missing") is None


def test_focus_tracking_uses_last_interacted_run():
    ids = iter(["run_one", "run_two"])
    manager = RunManager(id_factory=lambda: next(ids))

    one = manager.create_run(build_simple_task_plan("summarize this task", session_context={"task": "one"}))
    two = manager.create_run(build_simple_task_plan("make a bounded task envelope"))

    assert manager.last_interacted_run_id == two.run_id
    assert manager.last_interacted_run() == two

    focused = manager.update_focus(one.run_id)
    assert focused == one
    assert manager.last_interacted_run_id == one.run_id
    assert manager.last_interacted_run() == one


def test_run_dict_serializes_without_permission_claims():
    run = _manager().create_run(build_simple_task_plan("make a bounded task envelope"))
    payload = run.to_dict()

    assert payload["status"] == "planning"
    assert payload["planning_only"] is True
    assert payload["authority_effect"] == "none"
    assert payload["execution_performed"] is False
    assert payload["authorization_granted"] is False
    assert payload["envelope"]["authority_effect"] == "none"
    assert "execute" not in payload


def test_run_manager_rejects_non_planning_plan():
    plan = build_simple_task_plan("make a bounded task envelope")
    bad_plan = type(
        "BadPlan",
        (),
        {
            "planning_only": False,
            "execution_performed": False,
            "authorization_granted": False,
        },
    )()

    manager = _manager()
    assert plan.planning_only is True
    with pytest.raises(ValueError, match="planning-only"):
        manager.create_run(bad_plan)  # type: ignore[arg-type]


def test_models_reject_execution_or_authorization_fields():
    with pytest.raises(ValueError, match="must not record executed"):
        RunStep(step_id="bad", description="bad", execution_performed=True)

    understanding = TaskUnderstanding(goal="bad")
    plan = build_simple_task_plan("make a bounded task envelope")
    with pytest.raises(ValueError, match="must not grant authorization"):
        Run(
            run_id="bad",
            goal="bad",
            status=RunStatus.PLANNING,
            created_at="2026-04-30T12:00:00+00:00",
            updated_at="2026-04-30T12:00:00+00:00",
            understanding=understanding,
            envelope=plan.envelope,
            authorization_granted=True,
        )


def test_run_manager_has_no_execution_method():
    manager = _manager()

    assert not hasattr(manager, "execute")
    assert not hasattr(manager, "execute_run")
    assert not hasattr(manager, "run_capability")
