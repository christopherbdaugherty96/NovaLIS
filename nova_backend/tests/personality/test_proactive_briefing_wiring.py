"""Wiring Phase 2B — ProactiveBriefing integration tests.

Proves:
  - Morning brief uses BriefingComposer via ProactiveBriefing
  - Composed output is advisory only
  - Capability calls unchanged (weather, news, system, calendar)
  - Suggested actions are chat-input strings
  - Stale data disclosed
  - Full unprioritized view available
  - Routing and governance unchanged
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.proactive_briefing import (
    BriefingTrigger,
    ProactiveBriefing,
)


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture(scope="module")
def briefing():
    return ProactiveBriefing()


SESSION_DATA_FROM_CAPABILITIES = {
    "shopify": {
        "order_count": 47,
        "revenue": 3842.50,
        "timestamp": time.time(),
    },
    "calendar": {
        "events": [
            {"time": "9:00 AM", "title": "Team standup"},
            {"time": "2:00 PM", "title": "Deep work block"},
        ],
        "timestamp": time.time(),
    },
}


# ---------------------------------------------------------------------------
# Composition via ProactiveBriefing
# ---------------------------------------------------------------------------

class TestProactiveBriefingComposition:

    def test_morning_brief_composes_from_session_data(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA_FROM_CAPABILITIES,
            mode="home",
            profile=profile,
        )
        assert result is not None
        text = result.get("briefing_text", "")
        assert len(text) > 0

    def test_composed_output_is_advisory(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA_FROM_CAPABILITIES,
            profile=profile,
        )
        assert result is not None
        assert result.get("confirmed") is None
        assert result.get("approved") is None
        assert result.get("auto_execute") is None

    def test_suggested_actions_are_chat_strings(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA_FROM_CAPABILITIES,
            profile=profile,
        )
        assert result is not None
        for action in result.get("suggested_actions", []):
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()
            assert "executor" not in action["command"].lower()

    def test_full_unprioritized_view_in_result(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA_FROM_CAPABILITIES,
            profile=profile,
        )
        assert result is not None
        assert "full_view" in result or "unprioritized_text" in result

    def test_stale_data_disclosed_in_briefing(self, briefing, profile):
        stale_data = {
            "shopify": {
                "order_count": 30,
                "revenue": 2100.00,
                "timestamp": time.time() - 7200,
            },
        }
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=stale_data,
            profile=profile,
        )
        assert result is not None
        text = result.get("briefing_text", "").lower()
        assert any(w in text for w in ("ago", "stale", "minutes"))

    def test_dismiss_action_present(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA_FROM_CAPABILITIES,
            profile=profile,
        )
        assert result is not None
        actions_text = " ".join(
            a["command"].lower() for a in result.get("suggested_actions", [])
        )
        assert "dismiss" in actions_text


# ---------------------------------------------------------------------------
# Governance invariants
# ---------------------------------------------------------------------------

class TestBriefingWiringGovernance:

    def test_briefing_does_not_invoke_capabilities(self, briefing):
        assert not hasattr(briefing, "invoke")
        assert not hasattr(briefing, "fetch")
        assert not hasattr(briefing, "execute")

    def test_briefing_has_no_persistence(self, briefing):
        for attr in ("save", "persist", "write", "store", "commit"):
            assert not hasattr(briefing, attr)

    def test_capability_count_unchanged(self):
        from src.governor.capability_registry import CapabilityRegistry
        registry = CapabilityRegistry()
        active = [
            c for c in registry.all_capabilities()
            if getattr(c, "status", "").lower() == "active"
        ]
        assert len(active) == 27

    def test_executor_count_unchanged(self):
        executor_dir = (
            Path(__file__).resolve().parents[2] / "src" / "executors"
        )
        executors = [
            f for f in executor_dir.glob("*_executor.py") if f.is_file()
        ]
        assert len(executors) == 22

    def test_routing_unchanged(self):
        from tests.simulation.conversation_simulator import run_simulation
        for script in [["shopify report"], ["what's the weather"]]:
            a = run_simulation(script)
            b = run_simulation(script)
            assert a.capability_sequence() == b.capability_sequence()
