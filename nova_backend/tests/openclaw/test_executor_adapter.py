"""Tests for ExecutorSkillAdapter — generic executor-to-skill bridge."""

import pytest

from src.skills.executor_adapter import ExecutorSkillAdapter


class _FakeActionResult:
    def __init__(self, success=True, message="ok", data=None):
        self.success = success
        self.message = message
        self.data = data or {}


class _FakeExecutor:
    def __init__(self, result=None):
        self._result = result or _FakeActionResult()
        self.last_request = None

    def execute(self, request):
        self.last_request = request
        return self._result


class _FailingExecutor:
    def execute(self, request):
        raise RuntimeError("hardware error")


def _make_adapter(**kwargs) -> ExecutorSkillAdapter:
    defaults = dict(
        name="test_tool",
        description="A test tool",
        executor_factory=_FakeExecutor,
        capability_id=99,
    )
    defaults.update(kwargs)
    return ExecutorSkillAdapter(**defaults)


def test_can_handle_nonempty():
    adapter = _make_adapter()
    assert adapter.can_handle("do something") is True


def test_can_handle_empty():
    adapter = _make_adapter()
    assert adapter.can_handle("") is False
    assert adapter.can_handle("   ") is False


@pytest.mark.asyncio
async def test_handle_success():
    adapter = _make_adapter(
        executor_factory=lambda: _FakeExecutor(_FakeActionResult(
            success=True, message="Volume set to 50%", data={"level": 50},
        ))
    )
    result = await adapter.handle("set volume 50")
    assert result.success is True
    assert "Volume set" in result.message
    assert result.skill == "test_tool"


@pytest.mark.asyncio
async def test_handle_executor_failure():
    adapter = _make_adapter(executor_factory=_FailingExecutor)
    result = await adapter.handle("do something")
    assert result.success is False
    assert "unavailable" in result.message


@pytest.mark.asyncio
async def test_custom_param_extractor():
    captured = {}

    class _CapturingExecutor:
        def execute(self, request):
            captured["params"] = request.params
            return _FakeActionResult()

    adapter = _make_adapter(
        executor_factory=_CapturingExecutor,
        param_extractor=lambda q: {"url": q, "new_tab": True},
    )
    await adapter.handle("https://example.com")
    assert captured["params"] == {"url": "https://example.com", "new_tab": True}


@pytest.mark.asyncio
async def test_capability_id_passed_to_request():
    captured = {}

    class _CapturingExecutor:
        def execute(self, request):
            captured["capability_id"] = request.capability_id
            return _FakeActionResult()

    adapter = _make_adapter(
        executor_factory=_CapturingExecutor,
        capability_id=42,
    )
    await adapter.handle("test")
    assert captured["capability_id"] == 42
