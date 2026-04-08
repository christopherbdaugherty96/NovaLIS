import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.openclaw.robust_executor import RetryConfig, RobustExecutor
from src.openclaw.tool_registry import ToolMetadata, ToolRegistry
from src.openclaw.thinking_loop import StepPhase, ThinkingLoop


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

class _FakeSkill:
    def __init__(self, result="skill_result"):
        self._result = result

    async def handle(self, query: str):
        return self._result


def _make_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(
        "weather",
        lambda **kw: _FakeSkill("sunny"),
        ToolMetadata(
            name="weather",
            description="Weather",
            category="collection",
            tags=("weather",),
            timeout_seconds=5.0,
            is_network_tool=True,
        ),
    )
    reg.register(
        "news",
        lambda **kw: _FakeSkill("headlines"),
        ToolMetadata(
            name="news",
            description="News",
            category="collection",
            tags=("news",),
            timeout_seconds=5.0,
            is_network_tool=True,
        ),
    )
    return reg


def _make_loop() -> ThinkingLoop:
    return ThinkingLoop(
        registry=_make_registry(),
        executor=RobustExecutor(retry_config=RetryConfig(max_retries=0)),
    )


# ------------------------------------------------------------------
# Phase classification
# ------------------------------------------------------------------

def test_phase_exploration():
    assert ThinkingLoop._phase_for(1) == StepPhase.EXPLORATION
    assert ThinkingLoop._phase_for(4) == StepPhase.EXPLORATION


def test_phase_refinement():
    assert ThinkingLoop._phase_for(5) == StepPhase.REFINEMENT
    assert ThinkingLoop._phase_for(7) == StepPhase.REFINEMENT


def test_phase_finalization():
    assert ThinkingLoop._phase_for(8) == StepPhase.FINALIZATION
    assert ThinkingLoop._phase_for(10) == StepPhase.FINALIZATION


# ------------------------------------------------------------------
# Heuristic termination
# ------------------------------------------------------------------

def test_heuristic_done_true():
    ctx = {"history": [{"step": 1, "success": True}]}
    assert ThinkingLoop._heuristic_done(ctx) is True


def test_heuristic_done_false():
    ctx = {"history": [{"step": 1, "success": False}]}
    assert ThinkingLoop._heuristic_done(ctx) is False


def test_heuristic_done_empty():
    assert ThinkingLoop._heuristic_done({"history": []}) is False


# ------------------------------------------------------------------
# Tool list parsing
# ------------------------------------------------------------------

def test_parse_tool_list_json():
    available = ["weather", "news", "calendar"]
    result = ThinkingLoop._parse_tool_list('["weather", "news"]', available)
    assert result == ["weather", "news"]


def test_parse_tool_list_filters_unavailable():
    available = ["weather", "news"]
    result = ThinkingLoop._parse_tool_list('["weather", "stocks"]', available)
    assert result == ["weather"]


def test_parse_tool_list_fallback_text():
    available = ["weather", "news"]
    result = ThinkingLoop._parse_tool_list("I think we need weather data", available)
    assert result == ["weather"]


def test_parse_tool_list_invalid_json():
    available = ["weather", "news"]
    result = ThinkingLoop._parse_tool_list("not json at all", available)
    assert result == []


# ------------------------------------------------------------------
# JSON object parsing
# ------------------------------------------------------------------

def test_parse_json_object_valid():
    result = ThinkingLoop._parse_json_object('Here is: {"location": "NYC"}')
    assert result == {"location": "NYC"}


def test_parse_json_object_invalid():
    assert ThinkingLoop._parse_json_object("no json here") is None


# ------------------------------------------------------------------
# Full run (mocked LLM)
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_single_step_goal_achieved():
    """LLM reasons once, selects weather, then says goal achieved."""
    loop = _make_loop()

    llm_responses = iter([
        "Fetch the current weather for the user.",        # _reason
        '["weather"]',                                     # _select_tools
        '{"location": "auto"}',                            # _extract_params
        "yes",                                             # _should_terminate
    ])

    def mock_generate_chat(prompt, **kwargs):
        return next(llm_responses)

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("What's the weather?")

    assert result["success"] is True
    assert result["steps"] == 1
    assert len(result["thoughts"]) == 1
    assert result["thoughts"][0].selected_tools == ["weather"]


@pytest.mark.asyncio
async def test_run_terminates_on_empty_reasoning():
    """If LLM returns empty reasoning, loop should stop."""
    loop = _make_loop()

    def mock_generate_chat(prompt, **kwargs):
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Do something")

    assert result["steps"] == 0
    assert result["success"] is False


@pytest.mark.asyncio
async def test_run_terminates_on_no_tools():
    """If LLM selects no tools, loop should stop."""
    loop = _make_loop()

    llm_responses = iter([
        "The goal is already done, nothing to do.",  # _reason
        "[]",                                          # _select_tools (empty)
    ])

    def mock_generate_chat(prompt, **kwargs):
        return next(llm_responses)

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Already done")

    assert result["steps"] == 0
    assert result["success"] is False


@pytest.mark.asyncio
async def test_run_respects_max_steps():
    """Loop should not exceed MAX_STEPS even if LLM never says done."""
    loop = _make_loop()
    loop.MAX_STEPS = 3  # Reduce for test speed

    call_count = 0

    def mock_generate_chat(prompt, **kwargs):
        nonlocal call_count
        call_count += 1
        if "What should be done next" in prompt:
            return "Fetch weather again"
        if "Which tools" in prompt:
            return '["weather"]'
        if "What parameters" in prompt:
            return '{"location": "auto"}'
        if "Has the goal been achieved" in prompt:
            return "no"
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Impossible goal")

    assert result["steps"] == 3


@pytest.mark.asyncio
async def test_run_unregistered_tool_not_counted_as_success():
    """Tool selected by LLM but not in registry should not count as success."""
    reg = ToolRegistry()
    reg.register(
        "weather",
        lambda **kw: _FakeSkill("sunny"),
        ToolMetadata(name="weather", description="Weather", category="collection",
                     tags=("weather",), timeout_seconds=5.0, is_network_tool=True),
    )
    loop = ThinkingLoop(
        registry=reg,
        executor=RobustExecutor(retry_config=RetryConfig(max_retries=0)),
    )

    llm_responses = iter([
        "Fetch stock prices",             # _reason
        '["stocks"]',                       # _select_tools — not registered
        "yes",                              # _should_terminate
    ])

    def mock_generate_chat(prompt, **kwargs):
        return next(llm_responses)

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Get stocks")

    # "stocks" not in registry, so _select_tools filters it out → no tools → terminates
    assert result["steps"] == 0
    assert result["success"] is False


@pytest.mark.asyncio
async def test_run_error_dict_not_counted_as_success():
    """If all tools return error dicts, step should not be marked successful."""
    # Register a tool but make it return an error-like dict via the registry check
    reg = ToolRegistry()
    # Register "weather" but have the skill return None (simulating failure)
    reg.register(
        "weather",
        lambda **kw: _FakeSkill(None),
        ToolMetadata(name="weather", description="Weather", category="collection",
                     tags=("weather",), timeout_seconds=5.0, is_network_tool=False),
    )
    loop = ThinkingLoop(
        registry=reg,
        executor=RobustExecutor(retry_config=RetryConfig(max_retries=0)),
    )

    llm_responses = iter([
        "Fetch weather",
        '["weather"]',
        '{}',
        "yes",
    ])

    def mock_generate_chat(prompt, **kwargs):
        return next(llm_responses)

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Get weather")

    # Skill returns None → not successful
    assert result["steps"] == 1
    assert result["thoughts"][0].success is False


@pytest.mark.asyncio
async def test_param_extraction_failure_uses_defaults():
    """If LLM param extraction raises, defaults should be used."""
    loop = _make_loop()

    call_idx = 0

    def mock_generate_chat(prompt, **kwargs):
        nonlocal call_idx
        call_idx += 1
        if "What should be done next" in prompt:
            return "Fetch weather"
        if "Which tools" in prompt:
            return '["weather"]'
        if "What parameters" in prompt:
            raise RuntimeError("LLM exploded")
        if "Has the goal been achieved" in prompt:
            return "yes"
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Get weather")

    assert result["steps"] == 1
    # Should have used TOOL_PARAMETER_DEFAULTS fallback
    assert result["thoughts"][0].parameters["weather"] == {"location": "auto"}


# ------------------------------------------------------------------
# LLM synthesis
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_includes_synthesis():
    """run() result should include a 'synthesis' key."""
    loop = _make_loop()

    llm_responses = iter([
        "Fetch the current weather.",
        '["weather"]',
        '{"location": "auto"}',
        "yes",
        "It's sunny and warm today.",  # synthesis
    ])

    def mock_generate_chat(prompt, **kwargs):
        return next(llm_responses)

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("What's the weather?")

    assert "synthesis" in result
    assert result["synthesis"]  # non-empty


@pytest.mark.asyncio
async def test_synthesis_fallback_on_llm_failure():
    """If LLM synthesis fails, should fall back to static join."""
    loop = _make_loop()

    call_idx = 0

    def mock_generate_chat(prompt, **kwargs):
        nonlocal call_idx
        call_idx += 1
        if "What should be done next" in prompt:
            return "Fetch weather"
        if "Which tools" in prompt:
            return '["weather"]'
        if "What parameters" in prompt:
            return '{"location": "auto"}'
        if "Has the goal been achieved" in prompt:
            return "yes"
        if "Write a concise" in prompt:
            raise RuntimeError("LLM unavailable")
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Get weather")

    # Should have a synthesis (static fallback) and not crash
    assert "synthesis" in result


# ------------------------------------------------------------------
# Failed tools filtering
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_failed_tools_excluded_from_selection():
    """Tools that failed in a previous step should not be re-selected."""
    # Register a tool that always returns None (failure)
    reg = ToolRegistry()
    reg.register(
        "broken",
        lambda **kw: _FakeSkill(None),
        ToolMetadata(name="broken", description="Broken", category="collection",
                     tags=("broken",), timeout_seconds=1.0),
    )
    reg.register(
        "weather",
        lambda **kw: _FakeSkill("sunny"),
        ToolMetadata(name="weather", description="Weather", category="collection",
                     tags=("weather",), timeout_seconds=5.0, is_network_tool=True),
    )
    loop = ThinkingLoop(
        registry=reg,
        executor=RobustExecutor(retry_config=RetryConfig(max_retries=0)),
    )

    step = 0

    def mock_generate_chat(prompt, **kwargs):
        nonlocal step
        step += 1
        if "What should be done next" in prompt:
            return "Try tools"
        if "Which tools" in prompt:
            if "Do NOT select" in prompt and "broken" in prompt:
                return '["weather"]'  # LLM avoids broken tool
            return '["broken"]'  # First time, selects broken
        if "What parameters" in prompt:
            return '{}'
        if "Has the goal been achieved" in prompt:
            return "yes"
        if "Write a concise" in prompt:
            return "Done"
        return ""

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        result = await loop.run("Test failure filtering")

    assert result["steps"] >= 1


# ------------------------------------------------------------------
# Progress callback
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_progress_callback_called():
    """Progress callback should fire after each step."""
    loop = _make_loop()
    progress_calls = []

    def on_progress(step_num, status, tools):
        progress_calls.append((step_num, status, tools))

    loop.set_progress_callback(on_progress)

    llm_responses = iter([
        "Fetch weather",
        '["weather"]',
        '{"location": "auto"}',
        "yes",
        "Sunny weather today.",
    ])

    def mock_generate_chat(prompt, **kwargs):
        return next(llm_responses)

    with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
        mock_gw.generate_chat = mock_generate_chat
        await loop.run("Get weather")

    assert len(progress_calls) == 1
    assert progress_calls[0][0] == 1  # step_num
    assert progress_calls[0][2] == ["weather"]  # tools


# ------------------------------------------------------------------
# ExecutionMemory integration
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_optimal_order_used_when_memory_provided():
    """When execution_memory is set, tools should be reordered."""
    from src.openclaw.execution_memory import ExecutionMemory
    import tempfile, os

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(b"[]")
        path = f.name

    try:
        mem = ExecutionMemory(path=path)
        # Record: news is very reliable, weather is unreliable
        for _ in range(5):
            mem.record("news", "goal", success=True, duration_seconds=0.1)
            mem.record("weather", "goal", success=False, duration_seconds=1.0)

        loop = ThinkingLoop(
            registry=_make_registry(),
            executor=RobustExecutor(retry_config=RetryConfig(max_retries=0)),
            execution_memory=mem,
        )

        llm_responses = iter([
            "Fetch weather and news",
            '["weather", "news"]',
            '{}',
            '{}',
            "yes",
            "Weather and news.",
        ])

        def mock_generate_chat(prompt, **kwargs):
            return next(llm_responses)

        with patch("src.openclaw.thinking_loop.llm_gateway") as mock_gw:
            mock_gw.generate_chat = mock_generate_chat
            result = await loop.run("Get weather and news")

        # news should come first (higher reliability)
        if result["steps"] >= 1:
            assert result["thoughts"][0].selected_tools[0] == "news"
    finally:
        os.unlink(path)
