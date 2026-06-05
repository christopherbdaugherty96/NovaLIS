"""Phase 3 — ProactiveBriefing tests.

Written before implementation. Proves:
  - Briefings use snapshots only
  - Briefings are advisory-only
  - Cooldowns respected
  - Stale data disclosed
  - Full unprioritized view available
  - Opt-out behavior works
  - Suggested actions are chat-input strings
"""
from __future__ import annotations

import time

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


SESSION_DATA = {
    "shopify": {
        "order_count": 47,
        "revenue": 3842.50,
        "timestamp": time.time(),
    },
    "calendar": {
        "events": [
            {"time": "9:00 AM", "title": "Team standup"},
        ],
        "timestamp": time.time(),
    },
}

STALE_SESSION_DATA = {
    "shopify": {
        "order_count": 30,
        "revenue": 2100.00,
        "timestamp": time.time() - 7200,  # 2 hours ago
    },
}

THREAD_SNAPSHOT = [
    {"name": "Shopify Integration", "status": "active",
     "latest_blocker": "API rate limit"},
]

NOTICE_SNAPSHOT = [
    {"type": "blocked_without_next_step", "status": "active",
     "summary": "Shopify Integration blocked"},
]


# ---------------------------------------------------------------------------
# Trigger logic
# ---------------------------------------------------------------------------

class TestBriefingTriggers:

    def test_morning_trigger_respects_daily_cooldown(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        # First trigger: should fire
        assert pb.should_trigger(trigger=trigger, last_briefing_timestamp=None)
        # Second trigger same day: should not fire
        assert not pb.should_trigger(
            trigger=trigger,
            last_briefing_timestamp=time.time() - 3600,  # 1 hour ago
        )

    def test_data_arrival_trigger_respects_staleness_cooldown(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="data_arrival",
            source_label="Shopify Cap 65",
            data_timestamp=time.time(),
        )
        # Recent briefing: should not fire
        assert not pb.should_trigger(
            trigger=trigger,
            last_briefing_timestamp=time.time() - 600,  # 10 min ago
            cooldown_seconds=1800,
        )
        # Old briefing: should fire
        assert pb.should_trigger(
            trigger=trigger,
            last_briefing_timestamp=time.time() - 3600,  # 1 hour ago
            cooldown_seconds=1800,
        )

    def test_explicit_request_has_no_cooldown(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User request",
            data_timestamp=time.time(),
        )
        # Even with very recent briefing: should fire
        assert pb.should_trigger(
            trigger=trigger,
            last_briefing_timestamp=time.time() - 10,
        )

    def test_silent_mode_suppresses_proactive_triggers(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        assert not pb.should_trigger(
            trigger=trigger,
            last_briefing_timestamp=None,
            assistive_notice_mode="silent",
        )


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

class TestBriefingComposition:

    def test_compose_returns_advisory_dict(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = pb.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            thread_snapshot=THREAD_SNAPSHOT,
            notice_snapshot=NOTICE_SNAPSHOT,
            profile=profile,
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("confirmed") is None
        assert result.get("approved") is None
        assert result.get("auto_execute") is None

    def test_proactive_briefing_uses_snapshots_only(self):
        from src.personality.proactive_briefing import ProactiveBriefing
        pb = ProactiveBriefing()
        # No capability invocation methods
        assert not hasattr(pb, "invoke")
        assert not hasattr(pb, "fetch")
        assert not hasattr(pb, "execute")
        assert not hasattr(pb, "request")

    def test_proactive_briefing_outputs_advisory_items_only(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User",
            data_timestamp=time.time(),
        )
        result = pb.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            profile=profile,
        )
        assert result is not None
        result_str = str(result).lower()
        assert "execute" not in result_str or "executor" not in result_str
        assert "invoke" not in result_str

    def test_proactive_briefing_suggested_actions_are_chat_input_strings(
        self, profile,
    ):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = pb.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            thread_snapshot=THREAD_SNAPSHOT,
            profile=profile,
        )
        assert result is not None
        actions = result.get("suggested_actions", [])
        for action in actions:
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()
            assert "executor" not in action["command"].lower()

    def test_proactive_briefing_includes_opt_out(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = pb.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            profile=profile,
        )
        assert result is not None
        actions_text = " ".join(
            a.get("command", "").lower()
            for a in result.get("suggested_actions", [])
        )
        result_str = str(result).lower()
        has_opt_out = (
            "dismiss" in actions_text
            or "silent" in actions_text
            or "opt" in result_str
            or "dismiss" in result_str
        )
        assert has_opt_out, "Proactive briefing must include opt-out"


# ---------------------------------------------------------------------------
# Stale data and full view
# ---------------------------------------------------------------------------

class TestBriefingDataHandling:

    def test_proactive_briefing_discloses_stale_data(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User",
            data_timestamp=time.time(),
        )
        result = pb.compose_and_format(
            trigger=trigger,
            session_data=STALE_SESSION_DATA,
            profile=profile,
        )
        assert result is not None
        text = result.get("briefing_text", "").lower()
        assert any(word in text for word in [
            "ago", "stale", "older", "hour", "minutes ago",
        ]), f"Stale data not disclosed in: {text[:200]}"

    def test_proactive_briefing_full_unprioritized_view_available(self, profile):
        from src.personality.proactive_briefing import (
            BriefingTrigger, ProactiveBriefing,
        )
        pb = ProactiveBriefing()
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User",
            data_timestamp=time.time(),
        )
        result = pb.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            thread_snapshot=THREAD_SNAPSHOT,
            notice_snapshot=NOTICE_SNAPSHOT,
            profile=profile,
        )
        assert result is not None
        assert "full_view" in result or "unprioritized_text" in result

    def test_compose_does_not_invoke_capabilities(self, profile):
        from src.personality.proactive_briefing import ProactiveBriefing
        pb = ProactiveBriefing()
        assert not hasattr(pb, "invoke_capability")
        assert not hasattr(pb, "call_cap")
        assert not hasattr(pb, "governor")


# ---------------------------------------------------------------------------
# No persistence
# ---------------------------------------------------------------------------

class TestBriefingNoPersistence:

    def test_proactive_briefing_has_no_persistence_methods(self):
        from src.personality.proactive_briefing import ProactiveBriefing
        pb = ProactiveBriefing()
        for attr in ("save", "persist", "write", "store",
                     "commit", "insert", "update", "delete"):
            assert not hasattr(pb, attr)
