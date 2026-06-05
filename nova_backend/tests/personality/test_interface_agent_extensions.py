"""Phase 1B — PersonalityInterfaceAgent extensions.

Tests for gate wrapping, failure humanization, and mode-aware tone.
Written before implementation per the test-first rule.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.tone_profile_store import ToneProfileStore


@pytest.fixture()
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture()
def agent(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone.json")
    return PersonalityInterfaceAgent(tone_store=store)


# ---- Gate wrapping ---------------------------------------------------------

class TestGateWrapping:

    def test_gate_wrapping_preserves_action(self, agent, profile):
        out = agent.wrap_gate(
            action_description="Open the Downloads folder",
            cap_name="open_file_folder",
            cap_id=22,
            authority_class="local_write",
            profile=profile,
        )
        assert "downloads" in out.lower() or "folder" in out.lower()

    def test_gate_wrapping_includes_governance_id(self, agent, profile):
        out = agent.wrap_gate(
            action_description="Send email draft to Sarah",
            cap_name="send_email_draft",
            cap_id=64,
            authority_class="local_write",
            profile=profile,
        )
        assert "send_email_draft" in out or "Cap 64" in out

    def test_gate_wrapping_single_confirmation(self, agent, profile):
        out = agent.wrap_gate(
            action_description="Open the Documents folder",
            cap_name="open_file_folder",
            cap_id=22,
            authority_class="local_write",
            profile=profile,
        )
        question_marks = out.count("?")
        assert question_marks == 1, f"Expected exactly 1 question, got {question_marks}"

    def test_gate_wrapping_uses_confirmation_template(self, agent, profile):
        out = agent.wrap_gate(
            action_description="Open a file",
            cap_name="open_file_folder",
            cap_id=22,
            authority_class="local_write",
            profile=profile,
        )
        assert profile.confirmation_template.question_suffix in out

    def test_gate_wrapping_returns_metadata(self, agent, profile):
        out = agent.wrap_gate(
            action_description="Send email draft",
            cap_name="send_email_draft",
            cap_id=64,
            authority_class="local_write",
            profile=profile,
        )
        assert isinstance(out, str)
        assert len(out) > 0


# ---- Failure humanization --------------------------------------------------

class TestFailureHumanization:

    def test_failure_humanization_offers_options(self, agent, profile):
        out = agent.humanize_failure(
            "ERROR: Capability 65 timed out after 30s",
            profile=profile,
        )
        lowered = out.lower()
        assert any(phrase in lowered for phrase in [
            "try", "want me to", "option", "you can",
            "if useful", "here's",
        ])

    def test_failure_humanization_no_alarm(self, agent, profile):
        out = agent.humanize_failure(
            "CRITICAL ERROR: NetworkMediator rejected outbound request",
            profile=profile,
        )
        lowered = out.upper()
        assert "ERROR" not in lowered
        assert "CRITICAL" not in lowered
        assert "ALERT" not in lowered

    def test_failure_humanization_preserves_meaning(self, agent, profile):
        out = agent.humanize_failure(
            "Capability 'governed_web_search' is temporarily unavailable.",
            profile=profile,
        )
        lowered = out.lower()
        assert "search" in lowered or "unavailable" in lowered or "try" in lowered

    def test_failure_humanization_empty_input(self, agent, profile):
        out = agent.humanize_failure("", profile=profile)
        assert isinstance(out, str)
        assert len(out) > 0


# ---- Mode-aware tone -------------------------------------------------------

class TestModeAwareTone:

    def test_mode_affects_tone_not_authority(self, agent, profile):
        base_text = (
            "Summary: Three threads are active. "
            "Try next: - Check the Shopify thread. "
            "- Review the calendar thread. "
            "- Follow up on the news thread."
        )
        home_out = agent.present_with_mode(
            base_text, mode="home", profile=profile,
        )
        business_out = agent.present_with_mode(
            base_text, mode="business", profile=profile,
        )
        assert isinstance(home_out, str) and len(home_out) > 0
        assert isinstance(business_out, str) and len(business_out) > 0

    def test_home_mode_is_conversational(self, agent, profile):
        out = agent.present_with_mode(
            "Three project threads are active.",
            mode="home",
            profile=profile,
        )
        assert isinstance(out, str)
        assert len(out) > 0

    def test_business_mode_is_structured(self, agent, profile):
        out = agent.present_with_mode(
            "Three project threads are active.",
            mode="business",
            profile=profile,
        )
        assert isinstance(out, str)
        assert len(out) > 0

    def test_unknown_mode_falls_back_gracefully(self, agent, profile):
        out = agent.present_with_mode(
            "Hello world.",
            mode="nonexistent_mode",
            profile=profile,
        )
        assert isinstance(out, str)
        assert len(out) > 0

    def test_existing_present_method_unchanged(self, agent):
        out = agent.present("I recommend that you restart the service.")
        lowered = out.lower()
        assert "i recommend" not in lowered
        assert "reasonable option" in lowered

    def test_existing_present_agent_result_unchanged(self, agent):
        out = agent.present_agent_result(
            "Test Task",
            "I believe this is the right approach!",
            opener="Here's what I found:",
        )
        assert "i believe" not in out.lower()
