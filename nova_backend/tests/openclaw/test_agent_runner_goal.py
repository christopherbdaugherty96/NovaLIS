"""Tests for OpenClawAgentRunner.run_goal() — the freeform goal execution path."""

from unittest.mock import MagicMock, patch

import pytest

from src.openclaw.agent_runner import OpenClawAgentRunner


def _make_runner():
    """Create a runner with mocked dependencies."""
    store = MagicMock()
    store.get_template = MagicMock(return_value=None)
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
    """run_goal should record tool executions to execution memory."""
    runner = _make_runner()

    def mock_generate_chat(prompt, **kwargs):
        if "What should be done next" in prompt:
            return "Get system status"
        if "Which tools" in prompt:
            return '["system"]'
        if "What parameters" in prompt:
            return '{}'
        if "Has the goal been achieved" in prompt:
            return "yes"
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        await runner.run_goal("System health check")

    stats = runner._execution_memory.stats("system")
    assert stats.get("total_calls", 0) >= 1
