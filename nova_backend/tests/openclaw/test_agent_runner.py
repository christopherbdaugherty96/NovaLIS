import pytest

from src.openclaw.agent_runner import OpenClawAgentRunner, RunCancelledError
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore


@pytest.mark.asyncio
async def test_agent_runner_records_manual_brief_without_network(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)
    calendar_file = tmp_path / "calendar.ics"
    calendar_file.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR\n", encoding="utf-8")

    async def _fake_collect(_template_id):
        assert store.snapshot()["active_run"]["template_id"] == "morning_brief"
        meter = runner._active_budget_meter
        assert meter is not None
        meter.record_step("Collecting weather")
        meter.record_network_call("https://weather.visualcrossing.com/forecast")
        meter.record_network_bytes({"temperature": 62, "condition": "clear"})
        meter.record_step("Collecting calendar")
        meter.record_file_read(calendar_file)
        meter.record_step("Collecting news")
        for url in (
            "https://www.reuters.com/rssFeed/topNews",
            "https://feeds.apnews.com/apnews/topnews",
            "https://feeds.npr.org/1001/rss.xml",
            "https://feeds.bbci.co.uk/news/rss.xml",
        ):
            meter.record_network_call(url)
            meter.record_network_bytes({"headline": "Loaded"})
        meter.record_step("Reviewing reminders")
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
    assert "weather.visualcrossing.com" in result["envelope"]["allowed_hostnames"]
    assert result["run_record"]["scope_summary"].startswith("Uses ")
    assert result["run_record"]["budget_summary"].startswith("Can take up to 6 steps")
    assert result["budget_usage"]["metering_mode"] == "measured_narrow_lane"
    assert result["budget_usage"]["steps_used"] == 5
    assert result["budget_usage"]["files_touched_used"] == 1
    assert result["budget_usage"]["network_calls_used"] == 5
    assert result["budget_usage"]["bytes_read_used"] > 0
    assert "Used so far:" in result["budget_usage"]["summary"]
    assert store.snapshot()["recent_runs"][0]["template_id"] == "morning_brief"
    assert store.snapshot()["recent_runs"][0]["budget_summary"].startswith("Can take up to 6 steps")
    assert store.snapshot()["recent_runs"][0]["budget_usage"]["network_calls_used"] == 5
    assert store.snapshot()["active_run"] is None


@pytest.mark.asyncio
async def test_agent_runner_rejects_template_that_is_not_ready(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    with pytest.raises(RuntimeError):
        await runner.run_template("inbox_check", triggered_by="test")


@pytest.mark.asyncio
async def test_agent_runner_builds_read_only_project_snapshot(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / "README.md").write_text(
        "# Example Project\n\nExample Project is a governed workspace for local review and operator flows.\n",
        encoding="utf-8",
    )
    (project_root / "REPO_MAP.md").write_text(
        "# Repo Map\n\nThe repo is centered on docs, backend runtime, and frontend surfaces.\n",
        encoding="utf-8",
    )
    (project_root / "docs").mkdir()
    (project_root / "docs" / "reference").mkdir(parents=True)
    (project_root / "docs" / "reference" / "HUMAN_GUIDES").mkdir()
    (project_root / "docs" / "current_runtime").mkdir(parents=True)
    (project_root / "docs" / "design").mkdir(parents=True)
    (project_root / "docs" / "PROOFS").mkdir(parents=True)
    (project_root / "nova_backend").mkdir()
    (project_root / "scripts").mkdir()

    monkeypatch.setattr(runner, "_project_root", lambda: project_root)
    openai_calls = {"count": 0}

    def _fake_openai(_template, _prompt):
        openai_calls["count"] += 1
        return {"text": "should not be used"}

    monkeypatch.setattr(runner, "_summarize_with_metered_openai", _fake_openai)

    result = await runner.run_template("project_snapshot", triggered_by="test")

    assert result["usage_meta"]["route"] in {"local_model", "deterministic_fallback"}
    assert openai_calls["count"] == 0
    assert "Project Snapshot:" in result["summary"] or "Example Project" in result["summary"]
    assert result["envelope"]["template_id"] == "project_snapshot"
    assert result["budget_usage"]["network_calls_used"] == 0
    assert result["budget_usage"]["files_touched_used"] == 2
    assert store.snapshot()["recent_runs"][0]["template_id"] == "project_snapshot"


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


@pytest.mark.asyncio
async def test_agent_runner_records_failed_run_in_recent_runs(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    async def _boom(_template_id):
        raise RuntimeError("network timeout")

    monkeypatch.setattr(runner, "_collect_payload", _boom)

    with pytest.raises(RuntimeError):
        await runner.run_template("morning_brief", triggered_by="test")

    recent = store.snapshot()["recent_runs"]
    assert len(recent) == 1
    assert recent[0]["status"] == "failed"
    assert recent[0]["template_id"] == "morning_brief"
    assert "network timeout" in recent[0]["summary"]
    assert store.snapshot()["active_run"] is None


@pytest.mark.asyncio
async def test_agent_runner_fails_when_run_exceeds_envelope_network_budget(monkeypatch, tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    async def _over_budget(_template_id):
        meter = runner._active_budget_meter
        assert meter is not None
        meter.record_step("Collecting news")
        for _ in range(12):
            meter.record_network_call("https://feeds.npr.org/1001/rss.xml")
            meter.record_network_bytes({"headline": "Loaded"})
        return {
            "weather_summary": "",
            "weather_detail": {},
            "calendar_summary": "",
            "calendar_events": [],
            "news_summary": "",
            "headline_titles": [],
            "schedule_summary": "",
            "source_notes": {},
        }

    monkeypatch.setattr(runner, "_collect_payload", _over_budget)

    with pytest.raises(RuntimeError, match="network call budget"):
        await runner.run_template("morning_brief", triggered_by="test")

    recent = store.snapshot()["recent_runs"]
    assert len(recent) == 1
    assert recent[0]["status"] == "failed"
    assert "network call budget" in recent[0]["summary"]
    assert recent[0]["budget_usage"]["network_calls_used"] == 12


@pytest.mark.asyncio
async def test_cancel_at_collect_checkpoint_records_cancelled_run(monkeypatch, tmp_path):
    """Cancel requested before collect returns → RunCancelledError, status: cancelled."""
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    runner = OpenClawAgentRunner(store=store)

    async def _collect_then_request_cancel(template_id):
        # Signal cancel while "collecting" (simulates user clicking Cancel)
        store.request_cancel_active_run()
        return {
            "weather_summary": "",
            "weather_detail": {},
            "calendar_summary": "",
            "calendar_events": [],
            "news_summary": "",
            "headline_titles": [],
            "schedule_summary": "",
            "source_notes": {},
        }

    monkeypatch.setattr(runner, "_collect_payload", _collect_then_request_cancel)

    with pytest.raises(RunCancelledError):
        await runner.run_template("morning_brief", triggered_by="test")

    recent = store.snapshot()["recent_runs"]
    assert len(recent) == 1
    assert recent[0]["status"] == "cancelled"
    assert recent[0]["template_id"] == "morning_brief"
    assert store.snapshot()["active_run"] is None


def test_request_cancel_active_run_returns_false_when_no_active_run(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    assert store.request_cancel_active_run() is False


def test_is_cancel_requested_false_when_no_active_run(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    assert store.is_cancel_requested("any-id") is False


def test_request_cancel_active_run_sets_flag(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    store.set_active_run({
        "envelope_id": "env-001",
        "template_id": "morning_brief",
        "title": "Morning Brief",
        "status": "running",
        "triggered_by": "test",
        "delivery_mode": "widget",
        "delivery_channels": {"widget": True, "chat": False},
        "started_at": "2026-04-03T07:00:00+00:00",
        "summary": "Collecting sources.",
        "scope_summary": "Tools: weather.",
        "budget_summary": "Can take up to 6 steps.",
        "budget_usage": {"summary": "Used so far: 1/6 steps."},
    })
    assert store.is_cancel_requested("env-001") is False
    result = store.request_cancel_active_run("env-001")
    assert result is True
    assert store.is_cancel_requested("env-001") is True
    active = store.snapshot()["active_run"]
    assert active["cancel_requested"] is True
    assert active["status_label"] == "Cancelling\u2026"
    assert active["budget_summary"] == "Can take up to 6 steps."
    assert active["budget_usage"]["summary"] == "Used so far: 1/6 steps."
