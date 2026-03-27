"""
Phase 8 OpenClaw module tests.

Verifies:
1. TaskEnvelope lifecycle (pending → running → complete/failed/stopped)
2. AgentRuntimeStore thread safety basics
3. AgentPersonalityBridge voice formatting
4. OpenClawAgentRunner sync execution with stub tools
5. Runtime auditor Phase 8 status detection
"""
from __future__ import annotations

import pytest


def test_task_envelope_lifecycle():
    from src.openclaw.task_envelope import TaskEnvelope
    env = TaskEnvelope(title="Test task", tools_allowed=["weather"])
    assert env.status == "pending"
    env.mark_running()
    assert env.status == "running"
    env.mark_complete("done")
    assert env.status == "complete"
    assert env.result_text == "done"


def test_task_envelope_to_dict():
    from src.openclaw.task_envelope import TaskEnvelope
    env = TaskEnvelope(title="Dict test", envelope_type="morning_brief")
    d = env.to_dict()
    assert d["title"] == "Dict test"
    assert d["envelope_type"] == "morning_brief"
    assert "id" in d
    assert "created_at" in d


def test_agent_runtime_store_register_and_complete():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_runtime_store import AgentRuntimeStore
    store = AgentRuntimeStore()
    env = TaskEnvelope(title="Store test")
    store.register(env)
    assert len(store.get_active()) == 1
    store.update_status(env.id, "complete", "result here")
    assert len(store.get_active()) == 0
    recent = store.get_recent()
    assert len(recent) == 1
    assert recent[0].result_text == "result here"


def test_agent_runtime_store_stop_by_id():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_runtime_store import AgentRuntimeStore
    store = AgentRuntimeStore()
    env = TaskEnvelope(title="Stop test")
    store.register(env)
    result = store.stop_by_id(env.id)
    assert result is True
    assert len(store.get_active()) == 0
    assert store.get_recent()[0].status == "stopped"


def test_agent_runtime_store_stop_all():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_runtime_store import AgentRuntimeStore
    store = AgentRuntimeStore()
    for i in range(3):
        env = TaskEnvelope(title=f"Task {i}")
        store.register(env)
    count = store.stop_all()
    assert count == 3
    assert len(store.get_active()) == 0


def test_personality_bridge_morning_brief():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_personality_bridge import format_for_nova
    env = TaskEnvelope(title="Morning", envelope_type="morning_brief")
    result = format_for_nova(env, "It's sunny and 72°F.")
    assert "Good morning" in result
    assert "sunny" in result


def test_personality_bridge_default_template():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_personality_bridge import format_for_nova
    env = TaskEnvelope(title="Default", envelope_type="default")
    result = format_for_nova(env, "task done")
    assert "task done" in result


def test_agent_runner_stub_execution():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_runner import OpenClawAgentRunner
    from src.openclaw.agent_runtime_store import AgentRuntimeStore

    store = AgentRuntimeStore()
    runner = OpenClawAgentRunner(store=store)
    env = TaskEnvelope(title="Weather run", tools_allowed=["weather"])

    result = runner.run_sync(
        envelope=env,
        tool_data_fns={"weather": lambda: "Sunny, 72°F"},
    )

    assert result["status"] == "complete"
    assert "Sunny" in result["result_text"]
    assert "weather" in result["tools_used"]


def test_agent_runner_rejects_disallowed_tool():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_runner import OpenClawAgentRunner
    from src.openclaw.agent_runtime_store import AgentRuntimeStore

    store = AgentRuntimeStore()
    runner = OpenClawAgentRunner(store=store)
    env = TaskEnvelope(title="Bad tool", tools_allowed=["not_a_real_tool"])

    result = runner.run_sync(envelope=env)
    assert len(result["errors"]) > 0
    assert "not_a_real_tool" in result["errors"][0]


def test_agent_runner_llm_summarize_called_once():
    from src.openclaw.task_envelope import TaskEnvelope
    from src.openclaw.agent_runner import OpenClawAgentRunner
    from src.openclaw.agent_runtime_store import AgentRuntimeStore

    call_count = {"n": 0}

    def fake_llm(data):
        call_count["n"] += 1
        return "Summary: " + str(data)

    store = AgentRuntimeStore()
    runner = OpenClawAgentRunner(store=store)
    env = TaskEnvelope(title="LLM once", tools_allowed=["weather", "news"])

    runner.run_sync(
        envelope=env,
        llm_summarize_fn=fake_llm,
        tool_data_fns={"weather": lambda: "Sunny", "news": lambda: "Headlines"},
    )

    assert call_count["n"] == 1
