"""Proactive briefing framework for the Chief of Staff personality layer.

Defines when and how BriefingComposer output reaches the user.
Triggers are session events, not background loops. All inputs
are snapshots. All outputs are advisory.

Governance boundaries:
  - No imports from src.governor, src.executors, src.ledger
  - No capability invocations
  - No persistence (save/write/store)
  - No background threads or timers
  - Snapshot-only inputs
  - Enforced by import boundary test
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from src.personality.briefing_composer import BriefingComposer

if TYPE_CHECKING:
    from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


_DAY_SECONDS = 86400
_DEFAULT_COOLDOWN = 1800


@dataclass(frozen=True)
class BriefingTrigger:
    """Describes what caused a briefing to be considered."""

    trigger_type: str       # "morning" | "data_arrival" | "explicit"
    source_label: str
    data_timestamp: float | None


class ProactiveBriefing:
    """Decides whether to surface a briefing and composes it.

    Presentation-only. Does not call capabilities, persist data,
    or run background loops.
    """

    def should_trigger(
        self,
        *,
        trigger: BriefingTrigger,
        last_briefing_timestamp: float | None,
        assistive_notice_mode: str = "suggestive",
        cooldown_seconds: int | None = None,
    ) -> bool:
        # Explicit requests always fire
        if trigger.trigger_type == "explicit":
            return True

        # Silent mode suppresses proactive triggers
        if assistive_notice_mode == "silent":
            return False

        # No prior briefing → fire
        if last_briefing_timestamp is None:
            return True

        now = time.time()

        if trigger.trigger_type == "morning":
            # Once per calendar day
            return (now - last_briefing_timestamp) >= _DAY_SECONDS

        if trigger.trigger_type == "data_arrival":
            cooldown = cooldown_seconds or _DEFAULT_COOLDOWN
            return (now - last_briefing_timestamp) >= cooldown

        return False

    def compose_and_format(
        self,
        *,
        trigger: BriefingTrigger,
        session_data: dict[str, Any] | None = None,
        thread_snapshot: list[dict[str, Any]] | None = None,
        notice_snapshot: list[dict[str, Any]] | None = None,
        mode: str = "home",
        profile: ChiefOfStaffProfile | None = None,
    ) -> dict[str, Any] | None:
        from src.personality.chief_of_staff_profile import (
            ChiefOfStaffProfile as _P,
        )
        p = profile or _P()

        composer = BriefingComposer(profile=p)
        briefing = composer.compose(
            session_data=session_data,
            thread_snapshot=thread_snapshot,
            notice_snapshot=notice_snapshot,
            mode=mode,
        )

        briefing_text = briefing.as_text()
        unprioritized_text = briefing.as_unprioritized_text()

        actions = [
            {"label": "Full view", "command": "show full briefing"},
            {"label": "Dismiss", "command": "dismiss briefing"},
        ]

        if thread_snapshot:
            actions.insert(
                0,
                {"label": "Show threads", "command": "show threads"},
            )

        return {
            "type": "proactive_briefing",
            "trigger_type": trigger.trigger_type,
            "source_label": trigger.source_label,
            "briefing_text": briefing_text,
            "full_view": unprioritized_text,
            "unprioritized_text": unprioritized_text,
            "mode": mode,
            "suggested_actions": actions,
        }
