import asyncio

import pytest

from src.openclaw.robust_executor import RetryConfig, RobustExecutor


class _FakeSkill:
    """Skill that succeeds on the Nth call."""

    def __init__(self, fail_count: int = 0, result: str = "ok"):
        self._fail_count = fail_count
        self._calls = 0
        self._result = result

    async def handle(self, query: str):
        self._calls += 1
        if self._calls <= self._fail_count:
            raise RuntimeError(f"Transient failure #{self._calls}")
        return self._result


class _SlowSkill:
    async def handle(self, query: str):
        await asyncio.sleep(10)
        return "too late"


@pytest.mark.asyncio
async def test_call_skill_success():
    executor = RobustExecutor()
    skill = _FakeSkill()
    result = await executor.call_skill(skill, "q", timeout_seconds=5, tool_name="test")
    assert result == "ok"
    assert len(executor.call_log) == 1
    assert executor.call_log[0].success is True


@pytest.mark.asyncio
async def test_call_skill_retry_then_succeed():
    executor = RobustExecutor(retry_config=RetryConfig(
        max_retries=2, base_delay_seconds=0.01,
    ))
    skill = _FakeSkill(fail_count=1)
    result = await executor.call_skill(skill, "q", timeout_seconds=5, tool_name="test")
    assert result == "ok"
    assert len(executor.call_log) == 2
    assert executor.call_log[0].success is False
    assert executor.call_log[1].success is True


@pytest.mark.asyncio
async def test_call_skill_all_retries_fail():
    executor = RobustExecutor(retry_config=RetryConfig(
        max_retries=1, base_delay_seconds=0.01,
    ))
    skill = _FakeSkill(fail_count=999)
    result = await executor.call_skill(skill, "q", timeout_seconds=5, tool_name="test")
    assert result is None
    assert len(executor.call_log) == 2
    assert all(not r.success for r in executor.call_log)


@pytest.mark.asyncio
async def test_call_skill_timeout():
    executor = RobustExecutor(retry_config=RetryConfig(
        max_retries=0, base_delay_seconds=0.01,
    ))
    result = await executor.call_skill(
        _SlowSkill(), "q", timeout_seconds=0.05, tool_name="slow",
    )
    assert result is None
    assert executor.call_log[0].success is False
    assert "TimeoutError" in (executor.call_log[0].error or "")


@pytest.mark.asyncio
async def test_parallel_execution():
    executor = RobustExecutor()
    calls = [
        {"skill": _FakeSkill(result="w"), "query": "q", "timeout": 5, "tool_name": "weather"},
        {"skill": _FakeSkill(result="c"), "query": "q", "timeout": 5, "tool_name": "calendar"},
        {"skill": _FakeSkill(result="n"), "query": "q", "timeout": 5, "tool_name": "news"},
    ]
    results = await executor.call_many_parallel(calls)
    assert results == {"weather": "w", "calendar": "c", "news": "n"}


@pytest.mark.asyncio
async def test_parallel_falls_back_to_sequential_on_budget():
    executor = RobustExecutor()
    calls = [
        {"skill": _FakeSkill(result="w"), "query": "q", "timeout": 5,
         "tool_name": "weather", "is_network_tool": True},
        {"skill": _FakeSkill(result="n"), "query": "q", "timeout": 5,
         "tool_name": "news", "is_network_tool": True},
    ]
    # Budget only allows 1 network call — should fall back to sequential
    results = await executor.call_many_parallel(
        calls, budget_network_remaining=1,
    )
    assert results["weather"] == "w"
    assert results["news"] == "n"


@pytest.mark.asyncio
async def test_stats_for():
    executor = RobustExecutor()
    skill = _FakeSkill(result="ok")
    await executor.call_skill(skill, "q", timeout_seconds=5, tool_name="t")
    stats = executor.stats_for("t")
    assert stats["total_calls"] == 1
    assert stats["successes"] == 1
    assert stats["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_stats_for_nonexistent():
    executor = RobustExecutor()
    assert executor.stats_for("nonexistent") == {}


@pytest.mark.asyncio
async def test_stats_for_all_failures():
    executor = RobustExecutor(retry_config=RetryConfig(max_retries=0))
    await executor.call_skill(_FakeSkill(fail_count=999), "q", timeout_seconds=5, tool_name="t")
    stats = executor.stats_for("t")
    assert stats["total_calls"] == 1
    assert stats["failures"] == 1
    assert stats["success_rate"] == 0.0
