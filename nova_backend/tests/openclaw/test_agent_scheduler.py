from __future__ import annotations

from datetime import datetime

import pytest

from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
from src.openclaw.agent_scheduler import OpenClawAgentScheduler
from src.settings.runtime_settings_store import RuntimeSettingsStore


@pytest.mark.asyncio
async def test_agent_scheduler_does_nothing_while_scheduler_permission_is_paused(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    settings = RuntimeSettingsStore(tmp_path / "runtime_settings.json")
    store.set_template_schedule_enabled("morning_brief", True)
    calls: list[str] = []

    class _FakeRunner:
        async def run_template(self, template_id: str, *, triggered_by: str = "scheduler"):
            calls.append(f"{template_id}:{triggered_by}")
            return {}

    scheduler = OpenClawAgentScheduler(store=store, runner=_FakeRunner(), settings=settings)
    now = datetime.now().astimezone().replace(hour=7, minute=5, second=0, microsecond=0)

    completed = await scheduler.tick(now=now)

    assert completed == []
    assert calls == []


@pytest.mark.asyncio
async def test_agent_scheduler_runs_due_template_and_records_outcome(tmp_path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    settings = RuntimeSettingsStore(tmp_path / "runtime_settings.json")
    settings.set_permission("home_agent_scheduler_enabled", True, source="test")
    store.set_template_schedule_enabled("morning_brief", True)
    events: list[tuple[str, dict[str, object]]] = []

    class _FakeRunner:
        async def run_template(self, template_id: str, *, triggered_by: str = "scheduler"):
            assert template_id == "morning_brief"
            assert triggered_by == "scheduler"
            run_record = store.record_run(
                {
                    "envelope_id": "ENV-SCH-1",
                    "template_id": template_id,
                    "title": "Morning Brief",
                    "status": "completed",
                    "triggered_by": triggered_by,
                    "delivery_mode": "hybrid",
                    "delivery_channels": {"widget": True, "chat": True},
                    "presented_message": "Here's your morning. Clear skies and one meeting at 10.",
                    "summary": "Clear skies and one meeting at 10.",
                    "started_at": "2026-03-27T11:00:00+00:00",
                    "completed_at": "2026-03-27T11:00:05+00:00",
                    "llm_summary_used": True,
                    "estimated_input_tokens": 120,
                    "estimated_output_tokens": 40,
                    "estimated_total_tokens": 160,
                }
            )
            return {
                "envelope": {"id": "ENV-SCH-1"},
                "delivery_channels": {"widget": True, "chat": True},
                "presented_message": run_record["presented_message"],
                "estimated_total_tokens": run_record["estimated_total_tokens"],
                "run_record": run_record,
            }

    scheduler = OpenClawAgentScheduler(
        store=store,
        runner=_FakeRunner(),
        settings=settings,
        ledger_logger=lambda event_type, metadata: events.append((event_type, dict(metadata))),
    )
    now = datetime.now().astimezone().replace(hour=7, minute=5, second=0, microsecond=0)

    completed = await scheduler.tick(now=now)

    assert len(completed) == 1
    snapshot = store.snapshot()
    morning = next(item for item in snapshot["templates"] if item["id"] == "morning_brief")
    assert morning["last_scheduled_outcome"] == "completed"
    assert snapshot["delivery_ready_count"] == 1
    assert any(event_type == "OPENCLAW_AGENT_SCHEDULE_TRIGGERED" for event_type, _ in events)
    assert any(event_type == "OPENCLAW_AGENT_SCHEDULE_COMPLETED" for event_type, _ in events)
