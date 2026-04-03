import pytest

from src.openclaw.agent_runner import OpenClawAgentRunner
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore


@pytest.mark.asyncio
async def test_agent_runner_records_manual_brief_without_network(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    async def _fake_collect(_template_id):
        assert store.snapshot()["active_run"]["template_id"] == "morning_brief"
        return {
            "weather_summary": "62 degrees and clear.",
            "weather_detail": {
                "temp": "62",
                "condition": "clear",
                "location": "Seattle",
                "forecast": "Cool through the afternoon.",
            },
            "calendar_summary": "10:00 AM standup.",
            "calendar_events": [
                {"time": "10:00 AM", "title": "Standup"},
                {"time": "1:30 PM", "title": "Planning review"},
            ],
            "news_summary": "Two technology stories are worth watching.",
            "headline_titles": ["Headline one", "Headline two"],
            "schedule_summary": "0 due | 2 upcoming",
            "source_notes": {"weather": "available", "calendar": "available", "news": "available"},
        }

    monkeypatch.setattr(runner, "_collect_payload", _fake_collect)
    local_calls = {"count": 0}

    def _fake_local_summary(_template, _prompt):
        local_calls["count"] += 1
        return "This should not be used for morning brief."

    monkeypatch.setattr(runner, "_summarize_with_local_model", _fake_local_summary)

    result = await runner.run_template("morning_brief", triggered_by="test")

    assert result["delivery_channels"] == {"widget": True, "chat": True}
    assert result["presented_message"].startswith("Here's your morning.")
    assert result["strict_preflight"]["allowed"] is True
    assert local_calls["count"] == 0
    assert result["summary"].startswith("Morning Brief")
    assert "Weather: 62°F, clear in Seattle. Cool through the afternoon." in result["summary"]
    assert "Schedule:\n  10:00 AM" in result["summary"]
    assert "Headline one" in result["summary"]
    assert result["estimated_total_tokens"] == 0
    assert result["usage_meta"]["route"] == "deterministic_fallback"
    assert result["llm_summary_used"] is False
    assert store.snapshot()["recent_runs"][0]["template_id"] == "morning_brief"
    assert store.snapshot()["active_run"] is None


@pytest.mark.asyncio
async def test_agent_runner_rejects_template_that_is_not_ready(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    with pytest.raises(RuntimeError):
        await runner.run_template("inbox_check", triggered_by="test")


@pytest.mark.asyncio
async def test_agent_runner_blocks_manual_template_that_fails_strict_preflight(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    monkeypatch.setattr(
        store,
        "get_template",
        lambda _template_id: {
            "id": "unsafe_task",
            "title": "Unsafe Task",
            "manual_run_available": True,
            "tools_allowed": ["weather", "email_read"],
            "delivery_mode": "widget",
            "max_steps": 3,
            "max_duration_s": 60,
        },
    )

    with pytest.raises(RuntimeError, match="strict home-agent preflight"):
        await runner.run_template("unsafe_task", triggered_by="agent_page")


@pytest.mark.asyncio
async def test_agent_runner_uses_metered_openai_fallback_when_local_summary_is_unavailable(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    openai_calls = {"count": 0}

    class _FakeOpenAILane:
        def plan_for_openclaw_fallback(self):
            return {"allowed": True, "preferred_model": "gpt-5.4-mini"}

        def summarize_task_report(self, **_kwargs):
            openai_calls["count"] += 1
            return {
                "text": "OpenAI produced the final task report.",
                "usage_meta": {
                    "route": "openai_metered",
                    "route_label": "OpenAI metered lane",
                    "provider_label": "OpenAI",
                    "model_label": "gpt-5.4-mini",
                    "metered": True,
                    "local_only": False,
                    "exact_total_tokens": 180,
                    "estimated_cost_usd": 0.0009,
                    "budget_state_label": "Normal",
                    "summary": "Morning Brief used OpenAI gpt-5.4-mini.",
                },
            }

    runner = OpenClawAgentRunner(store=store, openai_lane=_FakeOpenAILane())

    async def _fake_collect(_template_id):
        return {
            "weather_summary": "62 degrees and clear.",
            "calendar_summary": "10:00 AM standup.",
            "news_summary": "Two technology stories are worth watching.",
            "headline_titles": ["Headline one", "Headline two"],
            "schedule_summary": "0 due | 2 upcoming",
            "source_notes": {"weather": "available", "calendar": "available", "news": "available"},
        }

    monkeypatch.setattr(runner, "_collect_payload", _fake_collect)
    monkeypatch.setattr(runner, "_summarize_with_local_model", lambda _template, _prompt: "")

    result = await runner.run_template("morning_brief", triggered_by="test")

    assert openai_calls["count"] == 0
    assert result["summary"].startswith("Morning Brief")
    assert result["usage_meta"]["route"] == "deterministic_fallback"
    assert result["llm_summary_used"] is False
    assert store.snapshot()["recent_runs"][0]["usage_meta"]["route"] == "deterministic_fallback"


@pytest.mark.asyncio
async def test_agent_runner_clears_active_run_after_failure(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    async def _boom(_template_id):
        assert store.snapshot()["active_run"]["template_id"] == "morning_brief"
        raise RuntimeError("collector failed")

    monkeypatch.setattr(runner, "_collect_payload", _boom)

    with pytest.raises(RuntimeError, match="collector failed"):
        await runner.run_template("morning_brief", triggered_by="test")

    assert store.snapshot()["active_run"] is None
