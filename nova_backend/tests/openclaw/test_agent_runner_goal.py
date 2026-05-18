"""Tests for OpenClawAgentRunner.run_goal() — the freeform goal execution path."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.openclaw.agent_runner import OpenClawAgentRunner, RunCancelledError
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
from src.openclaw.run_state_machine import run_event_hub
from src.openclaw.thinking_loop import StepPhase, ThoughtStep


def _make_weather_thought() -> ThoughtStep:
    """Return a successful ThoughtStep using the 'weather' tool (in allowlist)."""
    return ThoughtStep(
        step=1,
        phase=StepPhase.EXPLORATION,
        reasoning="Check weather to satisfy goal",
        selected_tools=["weather"],
        parameters={"weather": {"location": "auto"}},
        results={"weather": {"temperature": "72°F", "condition": "sunny"}},
        success=True,
        duration_seconds=0.05,
    )


def _make_thinking_loop_success(thought: ThoughtStep | None = None) -> dict:
    t = thought or _make_weather_thought()
    return {
        "success": True,
        "steps": 1,
        "thoughts": [t],
        "synthesis": "Goal completed.",
        "total_duration_seconds": 0.1,
    }


def _make_runner():
    """Create a runner with mocked dependencies."""
    store = MagicMock()
    store.get_template = MagicMock(return_value=None)
    store.set_active_run = MagicMock()
    store.update_active_run = MagicMock()
    store.clear_active_run = MagicMock()
    store.finish_active_run = MagicMock()
    store.is_cancel_requested = MagicMock(return_value=False)
    return OpenClawAgentRunner(store=store, network=None)


@pytest.mark.asyncio
async def test_run_goal_empty_raises():
    runner = _make_runner()
    with pytest.raises(ValueError, match="empty"):
        await runner.run_goal("")


@pytest.mark.asyncio
async def test_run_goal_returns_structured_result():
    """With mocked LLM, run_goal should return a structured result."""
    runner = _make_runner()

    call_count = 0

    def mock_generate_chat(prompt, **kwargs):
        nonlocal call_count
        call_count += 1
        if "What should be done next" in prompt:
            return "Check the current time"
        if "Which tools" in prompt:
            return '["system"]'
        if "What parameters" in prompt:
            return '{}'
        if "Has the goal been achieved" in prompt:
            return "yes"
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await runner.run_goal("What time is it?")

    assert result["goal"] == "What time is it?"
    assert result["triggered_by"] == "user"
    assert isinstance(result["steps"], int)
    assert "summary" in result
    assert "per_tool_budget" in result


@pytest.mark.asyncio
async def test_run_goal_records_execution_memory():
    """run_goal should record allowlisted tool executions to execution memory."""
    runner = _make_runner()

    def mock_generate_chat(prompt, **kwargs):
        if "What should be done next" in prompt:
            return "Check the weather"
        if "Which tools" in prompt:
            return '["weather"]'
        if "What parameters" in prompt:
            return '{"location": "auto"}'
        if "Has the goal been achieved" in prompt:
            return "yes"
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        await runner.run_goal("Weather check")

    stats = runner._execution_memory.stats("weather")
    assert stats.get("total_calls", 0) >= 1


@pytest.mark.asyncio
async def test_run_goal_finishes_active_run_with_terminal_event(tmp_path):
    """run_goal() must clear active_run, write recent_run, and emit events on success.

    Previously used a 'system' tool mock via LLM patching. Updated after PATCH A
    (freeform goal allowlist) correctly excluded 'system' from the filtered
    registry — 'system' is not an allowlisted read-only tool for the goal path.
    Now patches ThinkingLoop.run directly, which is the right abstraction level
    for testing run_goal() store and event mechanics.
    """
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store, network=None)
    queue = run_event_hub.subscribe()

    try:
        with patch(
            "src.openclaw.agent_runner.ThinkingLoop.run",
            new_callable=AsyncMock,
            return_value=_make_thinking_loop_success(),
        ):
            result = await runner.run_goal("Get a weather summary")

        assert result["success"] is True
        assert store.snapshot()["active_run"] is None
        assert store.snapshot()["recent_runs"][0]["template_id"] == "goal"
        assert store.snapshot()["delivery_ready_count"] == 1
        assert result["run_record"]["template_id"] == "goal"
        events = []
        while not queue.empty():
            events.append(queue.get_nowait())
        assert any(event["status"] == "running" for event in events)
        assert any(event["status"] == "succeeded" for event in events)
    finally:
        run_event_hub.unsubscribe(queue)


@pytest.mark.asyncio
async def test_run_goal_records_cancelled_run(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store, network=None)

    with patch(
        "src.openclaw.agent_runner.ThinkingLoop.run",
        side_effect=RunCancelledError("Goal cancelled by user request."),
    ):
        result = await runner.run_goal("Cancel this goal")

    snapshot = store.snapshot()
    assert result["cancelled"] is True
    assert result["run_record"]["status"] == "cancelled"
    assert snapshot["active_run"] is None
    assert snapshot["recent_runs"][0]["status"] == "cancelled"
    assert snapshot["delivery_ready_count"] == 0


@pytest.mark.asyncio
async def test_run_goal_records_failed_run(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store, network=None)

    with patch(
        "src.openclaw.agent_runner.ThinkingLoop.run",
        side_effect=RuntimeError("provider unavailable"),
    ):
        with pytest.raises(RuntimeError, match="provider unavailable"):
            await runner.run_goal("Fail this goal")

    snapshot = store.snapshot()
    assert snapshot["active_run"] is None
    assert snapshot["recent_runs"][0]["status"] == "failed"
    assert "provider unavailable" in snapshot["recent_runs"][0]["summary"]
    assert snapshot["delivery_ready_count"] == 0


@pytest.mark.asyncio
async def test_run_goal_per_tool_budget_resets_between_runs():
    """Per-tool budget must reset between successive run_goal() calls.

    Previously used a 'system' tool mock via LLM patching. Updated after PATCH A
    (freeform goal allowlist) correctly excluded 'system' from the filtered
    registry. Now uses a 'weather' thought (an allowlisted tool) returned
    directly from a ThinkingLoop.run mock, which is the correct approach for
    testing budget-reset mechanics independently of LLM behaviour.
    """
    runner = _make_runner()

    with patch(
        "src.openclaw.agent_runner.ThinkingLoop.run",
        new_callable=AsyncMock,
        return_value=_make_thinking_loop_success(),
    ):
        first = await runner.run_goal("Check the weather")
        second = await runner.run_goal("Check the weather again")

    assert first["per_tool_budget"]["per_tool"]["weather"]["calls"] == 1
    assert second["per_tool_budget"]["per_tool"]["weather"]["calls"] == 1
