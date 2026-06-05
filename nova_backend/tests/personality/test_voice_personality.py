"""Phase 3 — VoicePersonality tests.

Written before implementation. Proves:
  - Voice shortens text for TTS
  - Voice requires visual confirmation for high-authority actions
  - Voice never lowers confirmation requirements
  - Voice failure messages are calm and non-authorizing
  - Voice output contains no execution requests
"""
from __future__ import annotations

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


# ---------------------------------------------------------------------------
# Voice output formatting
# ---------------------------------------------------------------------------

class TestVoiceOutputFormatting:

    def test_voice_output_shorter_than_text(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        long_text = (
            "Summary: Three project threads are currently active. "
            "The Shopify Integration thread has an open blocker on "
            "API rate limits. The Dashboard Redesign thread is waiting "
            "on mockup review from the design team. The Nova Phase 2 "
            "thread is in planning status with no blockers recorded. "
            "Try next: Check the Shopify thread status. Review the "
            "Dashboard Redesign mockups. Plan the Nova Phase 2 scope."
        )
        result = vp.format_for_voice(long_text, profile=profile)
        assert len(result.spoken_text) < len(long_text)
        assert len(result.spoken_text) > 0

    def test_voice_mode_aware(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        text = "47 orders today, revenue is $3,842."
        home = vp.format_for_voice(text, mode="home", profile=profile)
        business = vp.format_for_voice(text, mode="business", profile=profile)
        # Both produce valid output
        assert len(home.spoken_text) > 0
        assert len(business.spoken_text) > 0
        assert home.mode == "home"
        assert business.mode == "business"

    def test_voice_result_is_frozen(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        result = vp.format_for_voice("Hello", profile=profile)
        with pytest.raises(AttributeError):
            result.spoken_text = "Modified"

    def test_voice_strips_markdown(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        md_text = "**Bold heading**\n- Item one\n- Item two\n```code block```"
        result = vp.format_for_voice(md_text, profile=profile)
        assert "**" not in result.spoken_text
        assert "```" not in result.spoken_text


# ---------------------------------------------------------------------------
# Voice confirmation
# ---------------------------------------------------------------------------

class TestVoiceConfirmation:

    def test_voice_high_authority_requires_visual_confirmation(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        for cap_id in (22, 64):
            result = vp.format_for_voice(
                f"Action requires confirmation for Cap {cap_id}.",
                is_confirmation=True,
                confirmation_cap_id=cap_id,
                profile=profile,
            )
            assert result.requires_visual_confirmation is True, (
                f"Cap {cap_id} must require visual confirmation"
            )

    def test_voice_yes_for_cap22_or_cap64_routes_to_visual_gate(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        for cap_id in (22, 64):
            result = vp.format_for_voice(
                "yes, do it",
                is_confirmation=True,
                confirmation_cap_id=cap_id,
                profile=profile,
            )
            assert result.requires_visual_confirmation is True

    def test_voice_personality_never_lowers_confirmation_requirements(
        self, profile,
    ):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        # Non-confirmation voice output should not have bypass flags
        result = vp.format_for_voice("hello", profile=profile)
        assert not hasattr(result, "skip_confirmation")
        assert not hasattr(result, "bypass_gate")
        assert not hasattr(result, "auto_approve")

    def test_voice_confirmation_includes_action_description(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        result = vp.format_for_voice(
            "Open the Documents folder",
            is_confirmation=True,
            confirmation_cap_id=22,
            profile=profile,
        )
        lowered = result.spoken_text.lower()
        assert "document" in lowered or "folder" in lowered or "open" in lowered

    def test_voice_never_emits_confirmed_true(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        result = vp.format_for_voice(
            "Confirmed action",
            is_confirmation=True,
            confirmation_cap_id=22,
            profile=profile,
        )
        assert not hasattr(result, "confirmed")
        assert not hasattr(result, "approved")


# ---------------------------------------------------------------------------
# Voice failure handling
# ---------------------------------------------------------------------------

class TestVoiceFailure:

    def test_voice_no_alarm_words(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        result = vp.format_for_voice(
            "CRITICAL ERROR: Capability 65 timed out",
            is_failure=True,
            profile=profile,
        )
        upper = result.spoken_text.upper()
        assert "ERROR" not in upper
        assert "CRITICAL" not in upper
        assert "ALERT" not in upper
        assert "FAILURE" not in upper

    def test_voice_failure_message_is_natural_but_non_authorizing(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        result = vp.format_for_voice(
            "ERROR: NetworkMediator rejected outbound request",
            is_failure=True,
            profile=profile,
        )
        lowered = result.spoken_text.lower()
        # Natural — offers next step
        assert "try" in lowered or "alternative" in lowered or "again" in lowered
        # Non-authorizing — no forbidden language
        for phrase in profile.forbidden_authority_language:
            assert phrase.lower() not in lowered

    def test_voice_failure_shorter_than_text_failure(self, profile):
        from src.personality.voice_personality import VoicePersonality
        from src.personality.interface_agent import PersonalityInterfaceAgent
        vp = VoicePersonality()
        agent = PersonalityInterfaceAgent()
        error = "ERROR: Capability 'governed_web_search' timed out after 30s"
        voice_result = vp.format_for_voice(error, is_failure=True, profile=profile)
        text_result = agent.humanize_failure(error, profile=profile)
        assert len(voice_result.spoken_text) <= len(text_result)


# ---------------------------------------------------------------------------
# Voice execution isolation
# ---------------------------------------------------------------------------

class TestVoiceExecutionIsolation:

    def test_voice_output_contains_no_execution_request(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        texts = [
            "Open the Documents folder",
            "Send email to Sarah about Q3",
            "Check Shopify store status",
            "Run the test suite",
        ]
        for text in texts:
            result = vp.format_for_voice(text, profile=profile)
            result_str = str(result).lower()
            assert "execute" not in result_str or "executor" not in result_str
            assert "invoke" not in result_str
            assert "dispatch" not in result_str

    def test_voice_result_fields_are_exactly_four(self, profile):
        from src.personality.voice_personality import VoicePersonality
        vp = VoicePersonality()
        result = vp.format_for_voice("test", profile=profile)
        fields = set(result.__dataclass_fields__.keys())
        assert fields == {
            "spoken_text", "display_text",
            "requires_visual_confirmation", "mode",
        }
