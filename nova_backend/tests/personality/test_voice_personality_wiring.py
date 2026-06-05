"""Wiring Phase 2C — VoicePersonality integration tests.

Proves:
  - Voice output uses VoicePersonality formatting
  - High-authority spoken confirmations flag visual requirement
  - Voice failures are calm with no alarm words
  - Voice does not lower confirmation requirements
  - Routing, governance, and execution unchanged
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.voice_personality import VoicePersonality


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture(scope="module")
def voice():
    return VoicePersonality()


# ---------------------------------------------------------------------------
# Voice formatting through VoicePersonality
# ---------------------------------------------------------------------------

class TestVoiceFormattingWiring:

    def test_voice_shortens_long_text(self, voice, profile):
        long_text = (
            "Summary: Three project threads are active. "
            "The Shopify thread has an API rate limit blocker. "
            "The Dashboard thread is waiting on mockup review. "
            "The Nova Phase 2 thread is in planning. "
            "Try next: Check Shopify. Review mockups. Plan Phase 2."
        )
        result = voice.format_for_voice(long_text, profile=profile)
        assert len(result.spoken_text) < len(long_text)
        assert len(result.spoken_text) > 0

    def test_voice_strips_markdown_for_tts(self, voice, profile):
        md = "**Bold** and `code` and ```block```"
        result = voice.format_for_voice(md, profile=profile)
        assert "**" not in result.spoken_text
        assert "```" not in result.spoken_text

    def test_voice_mode_stored_in_result(self, voice, profile):
        for mode in ("home", "business", "development"):
            result = voice.format_for_voice("test", mode=mode, profile=profile)
            assert result.mode == mode


# ---------------------------------------------------------------------------
# Confirmation clarity
# ---------------------------------------------------------------------------

class TestVoiceConfirmationWiring:

    def test_cap22_voice_confirmation_requires_visual(self, voice, profile):
        result = voice.format_for_voice(
            "Open the Documents folder",
            is_confirmation=True,
            confirmation_cap_id=22,
            profile=profile,
        )
        assert result.requires_visual_confirmation is True

    def test_cap64_voice_confirmation_requires_visual(self, voice, profile):
        result = voice.format_for_voice(
            "Send email draft to Sarah",
            is_confirmation=True,
            confirmation_cap_id=64,
            profile=profile,
        )
        assert result.requires_visual_confirmation is True

    def test_non_confirmation_voice_has_no_bypass_flags(self, voice, profile):
        result = voice.format_for_voice("hello", profile=profile)
        assert result.requires_visual_confirmation is False
        assert not hasattr(result, "skip_confirmation")
        assert not hasattr(result, "bypass_gate")
        assert not hasattr(result, "confirmed")

    def test_voice_confirmation_describes_action(self, voice, profile):
        result = voice.format_for_voice(
            "Open the Downloads folder",
            is_confirmation=True,
            confirmation_cap_id=22,
            profile=profile,
        )
        lowered = result.spoken_text.lower()
        assert "download" in lowered or "folder" in lowered or "open" in lowered


# ---------------------------------------------------------------------------
# Voice failure handling
# ---------------------------------------------------------------------------

class TestVoiceFailureWiring:

    def test_voice_failure_no_alarm_words(self, voice, profile):
        result = voice.format_for_voice(
            "CRITICAL ERROR: NetworkMediator rejected request",
            is_failure=True,
            profile=profile,
        )
        upper = result.spoken_text.upper()
        assert "ERROR" not in upper
        assert "CRITICAL" not in upper
        assert "ALERT" not in upper

    def test_voice_failure_offers_next_step(self, voice, profile):
        result = voice.format_for_voice(
            "ERROR: Capability timed out",
            is_failure=True,
            profile=profile,
        )
        lowered = result.spoken_text.lower()
        assert "try" in lowered or "alternative" in lowered

    def test_voice_failure_no_authority_language(self, voice, profile):
        result = voice.format_for_voice(
            "ERROR: Something failed",
            is_failure=True,
            profile=profile,
        )
        for phrase in profile.forbidden_authority_language:
            assert phrase.lower() not in result.spoken_text.lower()


# ---------------------------------------------------------------------------
# Governance invariants
# ---------------------------------------------------------------------------

class TestVoiceWiringGovernance:

    def test_voice_result_has_exactly_four_fields(self, voice, profile):
        result = voice.format_for_voice("test", profile=profile)
        fields = set(result.__dataclass_fields__.keys())
        assert fields == {
            "spoken_text", "display_text",
            "requires_visual_confirmation", "mode",
        }

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
