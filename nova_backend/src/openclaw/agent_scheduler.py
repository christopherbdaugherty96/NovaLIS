from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable

from src.openclaw.agent_runner import OpenClawAgentRunner, openclaw_agent_runner
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore, openclaw_agent_runtime_store
from src.settings.runtime_settings_store import RuntimeSettingsStore, runtime_settings_store
from src.tasks.notification_schedule_store import NotificationScheduleStore


import logging

logger = logging.getLogger(__name__)

LedgerLogger = Callable[[str, dict[str, Any]], None]

RUN_TIMEOUT_SECONDS = 150.0


class OpenClawAgentScheduler:
    """Narrow scheduled runner for named briefing templates only."""

    POLL_SECONDS = 30.0

    def __init__(
        self,
        *,
        store: OpenClawAgentRuntimeStore | None = None,
        runner: OpenClawAgentRunner | None = None,
        settings: RuntimeSettingsStore | None = None,
        notification_policy_store: NotificationScheduleStore | None = None,
        ledger_logger: LedgerLogger | None = None,
    ) -> None:
        self._store = store or openclaw_agent_runtime_store
        self._runner = runner or openclaw_agent_runner
        self._settings = settings or runtime_settings_store
        self._notification_policy_store = notification_policy_store or NotificationScheduleStore()
        self._ledger_logger = ledger_logger
        self._task: asyncio.Task | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self.running:
            return
        self._recover_interrupted_runs()
        self._task = asyncio.create_task(self._run_loop(), name="nova_openclaw_agent_scheduler")

    def _recover_interrupted_runs(self) -> None:
        """Mark any runs left in 'running' state as interrupted on startup."""
        try:
            self._store.recover_interrupted_runs()
        except Exception:
            pass

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

        completed: list[dict[str, Any]] = []
        due_templates = self._store.due_scheduled_templates(now=now)
        deliveries_last_hour = self._store.scheduled_delivery_count_last_hour(now=now)

        for claim in due_templates:
            template_id = str(claim.get("template_id") or "").strip()
            slot_key = str(claim.get("slot_key") or "").strip()
            if not template_id:
                continue
            policy_decision = self._notification_policy_store.delivery_policy_decision(
                now=now,
                deliveries_last_hour_override=deliveries_last_hour,
            )
            if not bool(policy_decision.get("allowed")):
                reason = str(policy_decision.get("reason") or "").strip()
                note = str(policy_decision.get("note") or "").strip()
                already_suppressed = (
                    str(claim.get("last_suppression_window") or "").strip() == slot_key
                    and str(claim.get("last_suppression_reason") or "").strip() == reason
                )
                if not already_suppressed:
                    self._store.record_schedule_suppression(
                        template_id,
                        slot_key=slot_key,
                        reason=reason,
                        note=note,
                        now=now,
                    )
                    self._log(
                        "OPENCLAW_AGENT_SCHEDULE_SUPPRESSED",
                        {
                            "template_id": template_id,
                            "slot_key": slot_key,
                            "reason": reason,
                            "note": note,
                            "deliveries_last_hour": deliveries_last_hour,
                            "source": "agent_scheduler",
                        },
                    )
                continue
            if not self._store.claim_scheduled_template(template_id, slot_key):
                continue
            self._log(
                "OPENCLAW_AGENT_SCHEDULE_TRIGGERED",
                {
                    "template_id": template_id,
                    "slot_key": slot_key,
                    "source": "agent_scheduler",
                },
            )
            try:
                result = await asyncio.wait_for(
                    self._runner.run_template(template_id, triggered_by="scheduler"),
                    timeout=RUN_TIMEOUT_SECONDS,
                )
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
                deliveries_last_hour += 1
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
            try:
                await self.tick()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("Scheduler tick failed: %s", exc)
            await asyncio.sleep(self.POLL_SECONDS)

    def _log(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self._ledger_logger is None:
            return
        try:
            self._ledger_logger(event_type, metadata)
        except Exception:
            return


openclaw_agent_scheduler = OpenClawAgentScheduler()
