import asyncio

import pytest

from src.openclaw.robust_executor import RetryConfig, RobustExecutor
from src.openclaw.tool_chain import ToolChain


class _FakeSkill:
    def __init__(self, result="ok"):
        self._result = result
        self.call_count = 0

    async def handle(self, query: str):
        self.call_count += 1
        return self._result


class _FailSkill:
    async def handle(self, query: str):
        raise RuntimeError("boom")


@pytest.fixture
def executor():
    return RobustExecutor(retry_config=RetryConfig(max_retries=0))


# ------------------------------------------------------------------
# Sequential
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sequential_basic(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("sunny"), "get weather")
    chain.add("news", _FakeSkill("headlines"), "get news")

    results = await chain.run_sequential()
    assert results["weather"] == "sunny"
    assert results["news"] == "headlines"


@pytest.mark.asyncio
async def test_sequential_condition_skip(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("sunny"), "get weather")
    chain.add(
        "alert",
        _FakeSkill("storm alert"),
        "check alert",
        condition=lambda r: r.get("weather") == "rainy",
    )

    results = await chain.run_sequential()
    assert results["weather"] == "sunny"
    assert "alert" not in results


@pytest.mark.asyncio
async def test_sequential_condition_met(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("rainy"), "get weather")
    chain.add(
        "alert",
        _FakeSkill("storm alert"),
        "check alert",
        condition=lambda r: r.get("weather") == "rainy",
    )

    results = await chain.run_sequential()
    assert results["alert"] == "storm alert"


@pytest.mark.asyncio
async def test_sequential_fallback(executor):
    chain = ToolChain(executor)
    chain.add(
        "weather",
        _FailSkill(),
        "get weather",
        fallback_skill=_FakeSkill("fallback_data"),
    )

    results = await chain.run_sequential()
    assert results["weather"] == "fallback_data"


@pytest.mark.asyncio
async def test_sequential_param_builder(executor):
    skill = _FakeSkill("details")
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("NYC"), "get weather")
    chain.add(
        "detail",
        skill,
        "placeholder",
        param_builder=lambda r: f"details for {r.get('weather')}",
    )

    results = await chain.run_sequential()
    assert results["detail"] == "details"


# ------------------------------------------------------------------
# Parallel
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parallel_basic(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("sunny"), "get weather")
    chain.add("news", _FakeSkill("headlines"), "get news")
    chain.add("calendar", _FakeSkill("events"), "get events")

    results = await chain.run_parallel()
    assert results == {"weather": "sunny", "news": "headlines", "calendar": "events"}


@pytest.mark.asyncio
async def test_parallel_with_failure(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("sunny"), "get weather")
    chain.add("news", _FailSkill(), "get news")

    results = await chain.run_parallel()
    assert results["weather"] == "sunny"
    assert results["news"] is None


# ------------------------------------------------------------------
# Phased
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_phased_separates_independent_and_dependent(executor):
    chain = ToolChain(executor)
    # Independent (will run in parallel)
    chain.add("weather", _FakeSkill("sunny"), "get weather")
    chain.add("news", _FakeSkill("headlines"), "get news")
    # Dependent (has condition, will run sequentially after phase 1)
    chain.add(
        "umbrella",
        _FakeSkill("bring umbrella"),
        "check umbrella",
        condition=lambda r: r.get("weather") == "rainy",
    )

    results = await chain.run_phased()
    assert results["weather"] == "sunny"
    assert results["news"] == "headlines"
    assert "umbrella" not in results  # condition not met


@pytest.mark.asyncio
async def test_phased_dependent_runs_when_condition_met(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("rainy"), "get weather")
    chain.add(
        "umbrella",
        _FakeSkill("bring umbrella"),
        "check umbrella",
        condition=lambda r: r.get("weather") == "rainy",
    )

    results = await chain.run_phased()
    assert results["weather"] == "rainy"
    assert results["umbrella"] == "bring umbrella"


# ------------------------------------------------------------------
# Fluent API
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_phased_fallback_in_phase1(executor):
    """Phase 1 (independent/parallel) steps should also use fallback_skill."""
    chain = ToolChain(executor)
    chain.add(
        "weather",
        _FailSkill(),
        "get weather",
        fallback_skill=_FakeSkill("fallback_weather"),
    )

    results = await chain.run_phased()
    assert results["weather"] == "fallback_weather"


# ------------------------------------------------------------------
# Results reset between runs
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sequential_resets_results_between_runs(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("sunny"), "get weather")

    r1 = await chain.run_sequential()
    assert r1["weather"] == "sunny"

    # Second run should start clean, not carry over
    r2 = await chain.run_sequential()
    assert r2 == {"weather": "sunny"}
    assert "stale" not in r2


@pytest.mark.asyncio
async def test_parallel_resets_results_between_runs(executor):
    chain = ToolChain(executor)
    chain.add("weather", _FakeSkill("sunny"), "get weather")

    await chain.run_parallel()
    r2 = await chain.run_parallel()
    assert r2 == {"weather": "sunny"}


# ------------------------------------------------------------------
# Fluent API
# ------------------------------------------------------------------

def test_fluent_chaining(executor):
    chain = (
        ToolChain(executor)
        .add("a", _FakeSkill(), "q")
        .add("b", _FakeSkill(), "q")
        .add("c", _FakeSkill(), "q")
    )
    assert len(chain._steps) == 3
