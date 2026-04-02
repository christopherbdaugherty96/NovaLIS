from __future__ import annotations

import asyncio
import pytest

from src.openclaw.agent_runner import OpenClawAgentRunner
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore


def _make_store(tmp_path):
    return OpenClawAgentRuntimeStore(path=tmp_path / "agent_runtime.json")


def test_inbox_check_collect_payload_raises(tmp_path):
    """_collect_payload must raise for inbox_check — no fallthrough to morning_brief."""
    runner = OpenClawAgentRunner(store=_make_store(tmp_path))

    with pytest.raises(RuntimeError, match="inbox_check"):
        asyncio.run(runner._collect_payload("inbox_check"))


def test_inbox_check_run_template_blocked_by_manual_run_available(tmp_path):
    """run_template must refuse inbox_check because manual_run_available is False."""
    runner = OpenClawAgentRunner(store=_make_store(tmp_path))

    with pytest.raises(RuntimeError):
        asyncio.run(
            runner.run_template("inbox_check", triggered_by="test")
        )


def test_morning_brief_collect_payload_does_not_raise(tmp_path):
    """Sanity: morning_brief reaches its own collector without raising."""
    runner = OpenClawAgentRunner(store=_make_store(tmp_path))
    # Should not raise (skills may return None but the collector handles that)
    result = asyncio.run(runner._collect_payload("morning_brief"))
    assert isinstance(result, dict)


def test_evening_digest_collect_payload_does_not_raise(tmp_path):
    runner = OpenClawAgentRunner(store=_make_store(tmp_path))
    result = asyncio.run(runner._collect_payload("evening_digest"))
    assert isinstance(result, dict)


def test_market_watch_collect_payload_does_not_raise(tmp_path):
    runner = OpenClawAgentRunner(store=_make_store(tmp_path))
    result = asyncio.run(runner._collect_payload("market_watch"))
    assert isinstance(result, dict)
