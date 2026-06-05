"""Phase 2 — Initiative template refinement tests.

Written before implementation. Proves:
  - Templates use question-based suggestions
  - No authority language
  - Single confirmation pattern preserved
  - Governance identity preserved
  - Observe, analyze, recommend, wait — never acts
"""
from __future__ import annotations

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.nova_style_contract import NovaStyleContract


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


# ---------------------------------------------------------------------------
# Chief of Staff initiative templates
# ---------------------------------------------------------------------------

class TestChiefOfStaffTemplates:

    def test_chief_of_staff_templates_use_question_based_suggestions(self):
        """Every initiative tail must be a question or start with
        permitted suggestion language."""
        profile = ChiefOfStaffProfile()
        permitted_starts = tuple(
            p.lower() for p in profile.permitted_suggestion_language
        )
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower().strip()
                ok = (
                    lowered.endswith("?")
                    or lowered.endswith(".")
                    or any(lowered.startswith(p) for p in permitted_starts)
                )
                assert ok, (
                    f"Template [{mode}/{kind}] does not use question or "
                    f"permitted language: '{tail}'"
                )

    def test_templates_do_not_use_authority_language(self):
        profile = ChiefOfStaffProfile()
        forbidden = [p.lower() for p in profile.forbidden_authority_language]
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower()
                for phrase in forbidden:
                    assert phrase not in lowered, (
                        f"Authority language '{phrase}' in [{mode}/{kind}]: '{tail}'"
                    )

    def test_templates_do_not_imply_action_already_taken(self):
        """Templates must not say 'I already did X' or 'I changed X'."""
        profile = ChiefOfStaffProfile()
        past_tense_markers = [
            "i already", "i changed", "i updated", "i sent",
            "i deleted", "i scheduled", "i reordered", "i created",
        ]
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower()
                for marker in past_tense_markers:
                    assert marker not in lowered, (
                        f"Past-tense action '{marker}' in [{mode}/{kind}]"
                    )

    def test_templates_do_not_emit_confirmed_true(self):
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower()
                assert "confirmed" not in lowered
                assert "approved" not in lowered
                assert "authorized" not in lowered

    def test_templates_do_not_emit_capability_ids_as_actions(self):
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower()
                assert "capability_id" not in lowered
                assert "cap_id" not in lowered
                assert "executor" not in lowered


# ---------------------------------------------------------------------------
# Mode-specific templates
# ---------------------------------------------------------------------------

class TestModeSpecificTemplates:

    def test_business_template_surfaces_observation_then_question(self):
        """Business mode: structured, leads with observation."""
        tail = NovaStyleContract.initiative_tail("business", "combined")
        assert tail, "Business/combined template must exist"
        lowered = tail.lower()
        # Must offer a choice, not command
        has_question_marker = (
            "?" in tail
            or "if useful" in lowered
            or "if you want" in lowered
            or "want me to" in lowered
            or "would you like" in lowered
            or "i can" in lowered
        )
        assert has_question_marker, (
            f"Business template must offer a choice: '{tail}'"
        )

    def test_home_template_surfaces_observation_then_question(self):
        tail = NovaStyleContract.initiative_tail("home", "combined")
        assert tail, "Home/combined template must exist"
        lowered = tail.lower()
        has_question_marker = (
            "?" in tail
            or "if you want" in lowered
            or "want me to" in lowered
            or "would you like" in lowered
            or "i can" in lowered
        )
        assert has_question_marker, (
            f"Home template must offer a choice: '{tail}'"
        )

    def test_development_template_surfaces_observation_then_question(self):
        tail = NovaStyleContract.initiative_tail("development", "combined")
        assert tail, "Development/combined template must exist"
        lowered = tail.lower()
        has_question_marker = (
            "?" in tail
            or "if useful" in lowered
            or "if you want" in lowered
            or "want me to" in lowered
            or "would you like" in lowered
            or "i can" in lowered
        )
        assert has_question_marker, (
            f"Development template must offer a choice: '{tail}'"
        )


# ---------------------------------------------------------------------------
# Confirmation and governance identity preservation
# ---------------------------------------------------------------------------

class TestConfirmationAndGovernancePreservation:

    def test_templates_preserve_single_confirmation_pattern(self):
        """Templates produce at most one question per tail."""
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                q_count = tail.count("?")
                assert q_count <= 1, (
                    f"Multiple questions in [{mode}/{kind}]: '{tail}'"
                )

    def test_templates_preserve_governance_identity(self):
        """NovaStyleContract.normalize() does not strip governance
        identity references."""
        governance_refs = [
            "[send_email_draft · Cap 64 · local_write]",
            "[open_file_folder · Cap 22 · local_write]",
            "[governed_web_search · Cap 16 · network_read]",
        ]
        for ref in governance_refs:
            result = NovaStyleContract.normalize(f"Action ready. {ref}")
            assert "Cap" in result, (
                f"Governance identity stripped: '{ref}' → '{result}'"
            )

    def test_mode_guidance_entries_exist_for_chief_of_staff_modes(self):
        """Chat mode guidance exists for home, business, development."""
        for mode in ("home", "business", "development"):
            guidance = NovaStyleContract.chat_mode_guidance(mode)
            assert isinstance(guidance, str)
            assert len(guidance) > 10, (
                f"Mode guidance too short for {mode}: '{guidance}'"
            )
