from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable

from src.openclaw.agent_runner import OpenClawAgentRunner, openclaw_agent_runner
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore, openclaw_agent_runtime_store
from src.settings.runtime_settings_store import RuntimeSettingsStore, runtime_settings_store


LedgerLogger = Callable[[str, dict[str, Any]], None]


class OpenClawAgentScheduler:
    """Narrow scheduled runner for named briefing templates only."""

    POLL_SECONDS = 30.0

    def __init__(
        self,
        *,
        store: OpenClawAgentRuntimeStore | None = None,
        runner: OpenClawAgentRunner | None = None,
        settings: RuntimeSettingsStore | None = None,
        ledger_logger: LedgerLogger | None = None,
    ) -> None:
        self._store = store or openclaw_agent_runtime_store
        self._runner = runner or openclaw_agent_runner
        self._settings = settings or runtime_settings_store
        self._ledger_logger = ledger_logger
        self._task: asyncio.Task | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self.running:
            return
        self._task = asyncio.create_task(self._run_loop(), name="nova_openclaw_agent_scheduler")

    async def stop(self) -> None:
        task = self._task
        self._task = None
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return

    async def tick(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        if not self._settings.is_permission_enabled("home_agent_enabled"):
            return []
        if not self._settings.is_permission_enabled("home_agent_scheduler_enabled"):
            return []

        claims = self._store.claim_due_scheduled_templates(now=now)
        completed: list[dict[str, Any]] = []
        for claim in claims:
            template_id = str(claim.get("template_id") or "").strip()
            if not template_id:
                continue
            self._log(
                "OPENCLAW_AGENT_SCHEDULE_TRIGGERED",
                {
                    "template_id": template_id,
                    "slot_key": str(claim.get("slot_key") or "").strip(),
                    "source": "agent_scheduler",
                },
            )
            try:
                result = await self._runner.run_template(template_id, triggered_by="scheduler")
                self._store.record_scheduled_run_outcome(
                    template_id,
                    outcome="completed",
                    note="Scheduled run completed.",
                    now=now,
                )
                self._log(
                    "OPENCLAW_AGENT_SCHEDULE_COMPLETED",
                    {
                        "template_id": template_id,
                        "envelope_id": str(dict(result.get("envelope") or {}).get("id") or "").strip(),
                        "estimated_total_tokens": int(result.get("estimated_total_tokens") or 0),
                        "source": "agent_scheduler",
                    },
                )
                completed.append(result)
            except Exception as exc:
                self._store.record_scheduled_run_outcome(
                    template_id,
                    outcome="failed",
                    note=str(exc),
                    now=now,
                )
                self._log(
                    "OPENCLAW_AGENT_SCHEDULE_FAILED",
                    {
                        "template_id": template_id,
                        "error": str(exc),
                        "source": "agent_scheduler",
                    },
                )
        return completed

    async def _run_loop(self) -> None:
        while True:
            await self.tick()
            await asyncio.sleep(self.POLL_SECONDS)

    def _log(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self._ledger_logger is None:
            return
        try:
            self._ledger_logger(event_type, metadata)
        except Exception:
            return


openclaw_agent_scheduler = OpenClawAgentScheduler()
