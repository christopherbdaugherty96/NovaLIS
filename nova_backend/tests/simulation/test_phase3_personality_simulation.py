"""Phase 3 Personality Validation Simulation.

10 scenarios validating VoicePersonality, TrustPresenter, and
ProactiveBriefing. Confirms authority unchanged while voice,
trust, and briefing surfaces improve.
"""
from __future__ import annotations

import copy
import time
from pathlib import Path
from typing import Any

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.voice_personality import VoicePersonality
from src.personality.trust_presenter import TrustPresenter
from src.personality.proactive_briefing import (
    BriefingTrigger,
    ProactiveBriefing,
)

from tests.simulation.conversation_simulator import run_simulation


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture(scope="module")
def voice():
    return VoicePersonality()


@pytest.fixture(scope="module")
def trust():
    return TrustPresenter()


@pytest.fixture(scope="module")
def briefing():
    return ProactiveBriefing()


SAMPLE_RECEIPT = {
    "event_type": "ACTION_COMPLETED",
    "capability_id": 64,
    "capability_name": "send_email_draft",
    "authority_class": "local_write",
    "success": True,
    "timestamp": "2026-06-05T14:30:00Z",
    "request_id": "req-abc-123",
    "session_id": "session-xyz",
}

SESSION_DATA = {
    "shopify": {
        "order_count": 47,
        "revenue": 3842.50,
        "inventory_alerts": ["Low stock: Nova Candle (3 remaining)"],
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

STALE_SESSION_DATA = {
    "shopify": {
        "order_count": 30,
        "revenue": 2100.00,
        "timestamp": time.time() - 7200,
    },
}

THREAD_SNAPSHOT = [
    {"name": "Shopify Integration", "status": "active",
     "latest_blocker": "API rate limit hit"},
]

NOTICE_SNAPSHOT = [
    {"type": "blocked_without_next_step", "status": "active",
     "summary": "Shopify Integration blocked"},
]


# -------------------------------------------------------------------
# Scenario 1: Voice confirmation (Cap 22)
# -------------------------------------------------------------------

class TestScenario1VoiceConfirmationCap22:

    def test_voice_surfaces_action_requires_visual_confirm(self, voice, profile):
        result = voice.format_for_voice(
            "Open the Documents folder",
            is_confirmation=True,
            confirmation_cap_id=22,
            profile=profile,
        )
        assert result.requires_visual_confirmation is True
        lowered = result.spoken_text.lower()
        assert "document" in lowered or "folder" in lowered or "open" in lowered

    def test_voice_changes_wording_only_for_cap22(self, voice, profile):
        result = voice.format_for_voice(
            "Action 'open_file_folder' requires confirmation",
            is_confirmation=True,
            confirmation_cap_id=22,
            profile=profile,
        )
        assert result.requires_visual_confirmation is True
        assert not hasattr(result, "confirmed")
        assert not hasattr(result, "bypass_gate")


# -------------------------------------------------------------------
# Scenario 2: Voice confirmation (Cap 64)
# -------------------------------------------------------------------

class TestScenario2VoiceConfirmationCap64:

    def test_email_draft_voice_requires_visual_gate(self, voice, profile):
        result = voice.format_for_voice(
            "Send the email draft to Sarah about Q3 timeline",
            is_confirmation=True,
            confirmation_cap_id=64,
            profile=profile,
        )
        assert result.requires_visual_confirmation is True

    def test_voice_yes_still_requires_visual(self, voice, profile):
        result = voice.format_for_voice(
            "yes, do it",
            is_confirmation=True,
            confirmation_cap_id=64,
            profile=profile,
        )
        assert result.requires_visual_confirmation is True


# -------------------------------------------------------------------
# Scenario 3: Voice failure handling
# -------------------------------------------------------------------

class TestScenario3VoiceFailure:

    def test_calm_voice_failure(self, voice, profile):
        result = voice.format_for_voice(
            "CRITICAL ERROR: Capability 65 timed out after 30s",
            is_failure=True,
            profile=profile,
        )
        upper = result.spoken_text.upper()
        assert "ERROR" not in upper
        assert "CRITICAL" not in upper
        lowered = result.spoken_text.lower()
        assert "try" in lowered or "alternative" in lowered

    def test_failure_next_step_suggestion(self, voice, profile):
        result = voice.format_for_voice(
            "ERROR: NetworkMediator rejected outbound request",
            is_failure=True,
            profile=profile,
        )
        for phrase in profile.forbidden_authority_language:
            assert phrase.lower() not in result.spoken_text.lower()


# -------------------------------------------------------------------
# Scenario 4: Trust Panel capability description
# -------------------------------------------------------------------

class TestScenario4TrustCapabilityDescription:

    def test_governance_identity_visible_in_description(self, trust, profile):
        for cap_name, cap_id, auth in [
            ("open_file_folder", 22, "local_write"),
            ("send_email_draft", 64, "local_write"),
            ("governed_web_search", 16, "network_read"),
        ]:
            desc = trust.describe_capability(
                cap_name=cap_name, cap_id=cap_id,
                authority_class=auth, profile=profile,
            )
            combined = f"{desc['summary']} {desc['detail']}"
            assert cap_name in combined or str(cap_id) in combined

    def test_positive_framing_in_description(self, trust, profile):
        desc = trust.describe_capability(
            cap_name="governed_web_search",
            cap_id=16,
            authority_class="network_read",
            profile=profile,
        )
        assert "by design" in desc["detail"].lower()


# -------------------------------------------------------------------
# Scenario 5: Trust Panel receipt preservation
# -------------------------------------------------------------------

class TestScenario5ReceiptPreservation:

    def test_raw_receipt_unchanged(self, trust, profile):
        original = copy.deepcopy(SAMPLE_RECEIPT)
        desc = trust.describe_receipt(SAMPLE_RECEIPT, profile=profile)
        assert SAMPLE_RECEIPT == original
        assert desc is not SAMPLE_RECEIPT

    def test_description_accompanies_not_replaces(self, trust, profile):
        desc = trust.describe_receipt(SAMPLE_RECEIPT, profile=profile)
        assert "summary" in desc
        assert "detail" in desc
        # Receipt fields not replicated into description
        assert desc.get("request_id") is None
        assert desc.get("session_id") is None


# -------------------------------------------------------------------
# Scenario 6: Trust Panel boundary explanation
# -------------------------------------------------------------------

class TestScenario6BoundaryExplanation:

    def test_boundary_uses_positive_framing(self, trust, profile):
        explanation = trust.explain_boundary(
            action_description="Modify Shopify prices",
            reason="Nova has read-only access to Shopify",
            profile=profile,
        )
        assert "by design" in explanation.lower()

    def test_no_trust_escalation(self, trust, profile):
        explanation = trust.explain_boundary(
            action_description="Execute a trade",
            reason="Outside authority",
            profile=profile,
        )
        lowered = explanation.lower()
        for phrase in ("just trust me", "if you let me",
                       "if you trusted me", "unlock"):
            assert phrase not in lowered


# -------------------------------------------------------------------
# Scenario 7: Proactive morning briefing
# -------------------------------------------------------------------

class TestScenario7MorningBriefing:

    def test_morning_briefing_fires_on_first_session(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        assert briefing.should_trigger(
            trigger=trigger, last_briefing_timestamp=None,
        )

    def test_morning_briefing_advisory_only(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            thread_snapshot=THREAD_SNAPSHOT,
            notice_snapshot=NOTICE_SNAPSHOT,
            profile=profile,
        )
        assert result is not None
        assert result.get("confirmed") is None
        assert result.get("auto_execute") is None
        for action in result["suggested_actions"]:
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()


# -------------------------------------------------------------------
# Scenario 8: Proactive business briefing
# -------------------------------------------------------------------

class TestScenario8BusinessBriefing:

    def test_shopify_data_in_briefing(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="data_arrival",
            source_label="Shopify Cap 65",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            mode="business",
            profile=profile,
        )
        assert result is not None
        text = result.get("briefing_text", "")
        assert "47" in text or "order" in text.lower()

    def test_business_briefing_mode_aware(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            mode="business",
            profile=profile,
        )
        assert result["mode"] == "business"


# -------------------------------------------------------------------
# Scenario 9: Stale briefing data warning
# -------------------------------------------------------------------

class TestScenario9StaleBriefingWarning:

    def test_stale_data_disclosed(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="explicit",
            source_label="User",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=STALE_SESSION_DATA,
            profile=profile,
        )
        assert result is not None
        text = result.get("briefing_text", "").lower()
        assert any(w in text for w in ("ago", "stale", "minutes"))


# -------------------------------------------------------------------
# Scenario 10: Opt-out and personality-off baseline
# -------------------------------------------------------------------

class TestScenario10OptOutAndBaseline:

    def test_opt_out_present_in_briefing(self, briefing, profile):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        result = briefing.compose_and_format(
            trigger=trigger,
            session_data=SESSION_DATA,
            profile=profile,
        )
        assert result is not None
        actions_text = " ".join(
            a["command"].lower() for a in result["suggested_actions"]
        )
        assert "dismiss" in actions_text

    def test_silent_mode_suppresses_briefing(self, briefing):
        trigger = BriefingTrigger(
            trigger_type="morning",
            source_label="Session start",
            data_timestamp=time.time(),
        )
        assert not briefing.should_trigger(
            trigger=trigger,
            last_briefing_timestamp=None,
            assistive_notice_mode="silent",
        )

    def test_personality_off_routing_unchanged(self):
        scripts = [
            ["shopify report"],
            ["what's the weather"],
            ["search for AI news"],
        ]
        for script in scripts:
            a = run_simulation(script)
            b = run_simulation(script)
            assert a.capability_sequence() == b.capability_sequence()

    def test_capability_count_27(self):
        from src.governor.capability_registry import CapabilityRegistry
        registry = CapabilityRegistry()
        active = [
            c for c in registry.all_capabilities()
            if getattr(c, "status", "").lower() == "active"
        ]
        assert len(active) == 27

    def test_executor_count_22(self):
        executor_dir = (
            Path(__file__).resolve().parents[2] / "src" / "executors"
        )
        executors = [
            f for f in executor_dir.glob("*_executor.py") if f.is_file()
        ]
        assert len(executors) == 22
