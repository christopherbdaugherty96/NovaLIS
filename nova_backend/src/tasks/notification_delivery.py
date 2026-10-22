from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Protocol

from src.tasks.notification_schedule_store import NotificationScheduleStore
from src.tasks.windows_resume import WindowsResumeProbe

log = logging.getLogger("nova.reminder_delivery")


@dataclass(frozen=True)
class NotificationRequest:
    schedule_id: str
    occurrence_id: str
    title: str
    body: str
    original_due_at: datetime
    overdue: bool


@dataclass(frozen=True)
class NotificationResult:
    accepted: bool
    adapter: str
    error_code: str = ""
    visible_observed: bool | None = None


@dataclass(frozen=True)
class DeliveryTickResult:
    delivered: int = 0
    uncertain: int = 0
    suppressed: int = 0


class Notifier(Protocol):
    def notify(self, request: NotificationRequest) -> NotificationResult: ...


class WindowsToastNotifier:
    """Display already-authorized text through the pinned Windows toast package."""

    def __init__(self, app_name: str = "Nova") -> None:
        self._app_name = str(app_name or "Nova").strip() or "Nova"

    def notify(self, request: NotificationRequest) -> NotificationResult:
        try:
            from windows_toasts import Toast, WindowsToaster

            failures: list[str] = []
            toast = Toast([request.title, request.body])
            toast.on_failed = lambda event: failures.append(str(event.error_code))
            WindowsToaster(self._app_name).show_toast(toast)
            if failures:
                return NotificationResult(False, "windows_toasts", failures[0])
            return NotificationResult(True, "windows_toasts")
        except Exception as exc:
            log.exception("Windows toast delivery failed")
            return NotificationResult(False, "windows_toasts", type(exc).__name__)


class ReminderDeliveryService:
    """Wall-clock reminder worker owned by the backend daemon, not the dashboard."""

    def __init__(
        self,
        *,
        store: NotificationScheduleStore,
        notifier: Notifier,
        governor: Any,
        ledger_logger: Callable[[str, dict[str, Any]], None],
        tick_seconds: int = 30,
        resume_probe: Any | None = None,
        presence_probe: Any | None = None,
    ) -> None:
        self._store = store
        self._notifier = notifier
        self._governor = governor
        self._ledger_logger = ledger_logger
        self._tick_seconds = max(1, min(int(tick_seconds), 30))
        self._presence_probe = presence_probe or resume_probe or WindowsResumeProbe()
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()
        self._last_wall_clock: datetime | None = None
        self._awaiting_resume_interaction = False

    @property
    def running(self) -> bool:
        return bool(self._task and not self._task.done())

    async def start(self) -> None:
        if self.running:
            return
        self._stopping = asyncio.Event()
        await asyncio.to_thread(self.run_tick, startup=True)
        self._task = asyncio.create_task(self._run_loop(), name="nova-reminder-delivery")

    async def stop(self) -> None:
        self._stopping.set()
        task = self._task
        self._task = None
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def _run_loop(self) -> None:
        while not self._stopping.is_set():
            await asyncio.sleep(self._tick_seconds)
            now = datetime.now(timezone.utc)
            wake_jump = bool(
                self._last_wall_clock
                and now - self._last_wall_clock > timedelta(seconds=self._tick_seconds * 2)
            )
            await asyncio.to_thread(self.run_tick, now=now, wake=wake_jump)

    def run_tick(
        self,
        *,
        now: datetime | None = None,
        startup: bool = False,
        wake: bool = False,
    ) -> DeliveryTickResult:
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        self._last_wall_clock = current
        delivered = 0
        uncertain = 0
        suppressed = 0

        try:
            resume_state = dict(self._presence_probe.observe(current) or {})
        except Exception:
            log.exception("Windows resume observation failed")
            resume_state = {
                "resume_detected": False,
                "user_present": False,
                "display": "unknown",
                "session": "unknown",
            }
        if bool(resume_state.get("resume_detected")):
            self._awaiting_resume_interaction = True
        resumed_for_user = self._awaiting_resume_interaction and bool(
            resume_state.get("user_present")
        )
        if resumed_for_user:
            self._awaiting_resume_interaction = False

        if startup:
            for recovered in self._store.recover_interrupted_claims(now=current):
                uncertain += 1
                self._ledger_logger(
                    "NOTIFICATION_DELIVERY_UNCERTAIN",
                    {
                        "schedule_id": str(recovered.get("id") or ""),
                        "occurrence_id": str(recovered.get("delivery_occurrence_id") or ""),
                        "adapter": "startup_recovery",
                        "error_code": "INTERRUPTED_AFTER_CLAIM",
                    },
                )

        for item in self._store.list_due_schedules(now=current):
            schedule_id = str(item.get("id") or "").strip()
            if not schedule_id:
                continue
            authority = self._store.delivery_authority_decision(
                schedule_id, channel="windows_toast"
            )
            if not bool(authority.get("allowed")):
                self._store.mark_delivery_needs_confirmation(
                    schedule_id,
                    reason=str(authority.get("reason") or "delivery authority unavailable"),
                )
                suppressed += 1
                continue

            display_state = str(
                resume_state.get("display")
                or ("on" if bool(resume_state.get("user_present")) else "unknown")
            ).lower()
            session_state = str(resume_state.get("session") or "unlocked").lower()
            if self._awaiting_resume_interaction and not resumed_for_user:
                display_state = "off"
            hold_reason = ""
            if display_state == "off":
                hold_reason = "display_off"
            elif session_state == "locked":
                hold_reason = "session_locked"
            elif display_state != "on" or session_state != "unlocked":
                hold_reason = "state_unknown"
            if hold_reason:
                self._hold(schedule_id, reason=hold_reason, now=current)
                suppressed += 1
                continue
            try:
                policy = self._store.evaluate_delivery_policy(schedule_id, now=current)
            except KeyError:
                continue
            if not bool(policy.get("allowed")):
                if str(policy.get("reason") or "") == "quiet_hours":
                    self._hold(schedule_id, reason="quiet_hours", now=current)
                suppressed += 1
                continue

            prior_hold_reason = str(item.get("delivery_hold_reason") or "")
            self._store.clear_delivery_hold(schedule_id)

            allowed, governor_reason = self._governor.allow_notification_delivery(
                {
                    "schedule_id": schedule_id,
                    "kind": str(item.get("kind") or ""),
                    "title": str(item.get("title") or ""),
                }
            )
            if not allowed:
                suppressed += 1
                self._ledger_logger(
                    "NOTIFICATION_DELIVERY_SUPPRESSED",
                    {"schedule_id": schedule_id, "reason": "governor_policy", "detail": governor_reason},
                )
                continue

            claim = self._store.claim_due_occurrence(schedule_id, now=current)
            if not claim.get("claimed"):
                continue
            occurrence_id = str(claim["occurrence_id"])
            due_at = datetime.fromisoformat(str(claim["next_run_at"])).astimezone(timezone.utc)
            overdue = startup or wake or resumed_for_user or current - due_at > timedelta(minutes=2)
            original_body = str(claim.get("body") or "Reminder")
            if overdue:
                local_due = due_at.astimezone().strftime("%I:%M %p").lstrip("0")
                if startup:
                    prefix = "Missed while Nova wasn't running"
                elif prior_hold_reason == "session_locked":
                    prefix = "Delivered late — the reminder was held while the screen was locked"
                elif prior_hold_reason == "display_off" or resumed_for_user or wake:
                    prefix = "Delivered late — your laptop was asleep or the screen was off"
                else:
                    prefix = "Delivered late"
                body = f"{prefix}: {original_body} (due {local_due})"
            else:
                body = original_body
            request = NotificationRequest(
                schedule_id=schedule_id,
                occurrence_id=occurrence_id,
                title=str(claim.get("title") or "Nova reminder"),
                body=body,
                original_due_at=due_at,
                overdue=overdue,
            )
            with self._store.authorized_claimed_delivery(
                schedule_id,
                occurrence_id=occurrence_id,
                channel="windows_toast",
            ) as authorized_item:
                if authorized_item is None:
                    suppressed += 1
                    continue
                self._ledger_logger(
                    "NOTIFICATION_DELIVERY_ATTEMPTED",
                    {"schedule_id": schedule_id, "occurrence_id": occurrence_id, "overdue": overdue},
                )
                try:
                    result = self._notifier.notify(request)
                except Exception as exc:
                    result = NotificationResult(False, type(self._notifier).__name__, type(exc).__name__)

            if result.accepted:
                self._store.finish_claimed_occurrence(
                    schedule_id,
                    occurrence_id=occurrence_id,
                    outcome="delivered",
                    note=f"Accepted by {result.adapter}; visibility not inferred.",
                    now=current,
                )
                delivered += 1
                self._ledger_logger(
                    "NOTIFICATION_DELIVERY_COMPLETED",
                    {"schedule_id": schedule_id, "occurrence_id": occurrence_id, "adapter": result.adapter},
                )
            else:
                self._store.finish_claimed_occurrence(
                    schedule_id,
                    occurrence_id=occurrence_id,
                    outcome="delivery_uncertain",
                    note=f"{result.adapter}: {result.error_code or 'not accepted'}",
                    now=current,
                )
                uncertain += 1
                self._ledger_logger(
                    "NOTIFICATION_DELIVERY_UNCERTAIN",
                    {
                        "schedule_id": schedule_id,
                        "occurrence_id": occurrence_id,
                        "adapter": result.adapter,
                        "error_code": result.error_code,
                    },
                )

        return DeliveryTickResult(delivered=delivered, uncertain=uncertain, suppressed=suppressed)

    def _hold(
        self,
        schedule_id: str,
        *,
        reason: str,
        now: datetime,
        detail: str = "",
    ) -> None:
        saved = self._store.record_delivery_hold(
            schedule_id,
            reason=reason,
            retry_state="waiting_for_safe_state",
            now=now,
        )
        if not bool(saved.get("hold_changed")):
            return
        self._ledger_logger(
            "NOTIFICATION_DELIVERY_HELD",
            {
                "schedule_id": schedule_id,
                "reason": reason,
                "retry_state": "waiting_for_safe_state",
                "detail": str(detail or "")[:120],
            },
        )

