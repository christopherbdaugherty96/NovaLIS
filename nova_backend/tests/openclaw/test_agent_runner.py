import pytest

from src.openclaw.agent_runner import OpenClawAgentRunner
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore


@pytest.mark.asyncio
async def test_agent_runner_records_manual_brief_without_network(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

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
    monkeypatch.setattr(runner, "_summarize_with_local_model", lambda _template, _prompt: "62 degrees and clear with one meeting at 10.")

    result = await runner.run_template("morning_brief", triggered_by="test")

    assert result["delivery_channels"] == {"widget": True, "chat": True}
    assert result["presented_message"].startswith("Here's your morning.")
    assert result["estimated_total_tokens"] > 0
    assert store.snapshot()["recent_runs"][0]["template_id"] == "morning_brief"


@pytest.mark.asyncio
async def test_agent_runner_rejects_template_that_is_not_ready(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    with pytest.raises(RuntimeError):
        await runner.run_template("inbox_check", triggered_by="test")
