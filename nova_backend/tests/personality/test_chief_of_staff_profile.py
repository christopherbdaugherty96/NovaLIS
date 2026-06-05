from __future__ import annotations

import dataclasses

from src.personality.chief_of_staff_profile import (
    ChiefOfStaffProfile,
    ConfirmationTemplate,
    InitiativeTier,
    ModeProfile,
)


def test_profile_loads_defaults():
    profile = ChiefOfStaffProfile()
    assert profile.role_name == "Nova"
    assert profile.operating_principle
    assert profile.governance_principle
    assert profile.initiative_rule
    assert profile.initiative_tiers
    assert profile.modes
    assert profile.confirmation_template
    assert profile.permitted_suggestion_language
    assert profile.forbidden_authority_language


def test_initiative_tiers_defined():
    profile = ChiefOfStaffProfile()
    assert len(profile.initiative_tiers) == 4
    levels = [t.level for t in profile.initiative_tiers]
    assert levels == [1, 2, 3, 4]
    labels = [t.label for t in profile.initiative_tiers]
    assert labels == ["Observe", "Flag", "Recommend", "Prepare"]


def test_tier3_and_4_require_question():
    profile = ChiefOfStaffProfile()
    for tier in profile.initiative_tiers:
        if tier.level >= 3:
            assert tier.requires_question is True
        else:
            assert tier.requires_question is False


def test_mode_profiles_defined():
    profile = ChiefOfStaffProfile()
    names = [m.name for m in profile.modes]
    assert "home" in names
    assert "business" in names
    assert "development" in names
    for mode in profile.modes:
        assert mode.tone_label
        assert mode.initiative_ceiling > 0
        assert mode.example_greeting


def test_cooldown_values_positive():
    profile = ChiefOfStaffProfile()
    for tier in profile.initiative_tiers:
        assert tier.cooldown_seconds >= 0
    for tier in profile.initiative_tiers:
        if tier.level >= 2:
            assert tier.cooldown_seconds > 0


def test_profile_is_frozen():
    profile = ChiefOfStaffProfile()
    assert dataclasses.is_dataclass(profile)
    try:
        profile.role_name = "Something else"
        assert False, "Should have raised FrozenInstanceError"
    except (dataclasses.FrozenInstanceError, AttributeError):
        pass


def test_mode_by_name():
    profile = ChiefOfStaffProfile()
    biz = profile.mode_by_name("business")
    assert biz is not None
    assert biz.name == "business"
    assert profile.mode_by_name("nonexistent") is None


def test_tier_by_level():
    profile = ChiefOfStaffProfile()
    t3 = profile.tier_by_level(3)
    assert t3 is not None
    assert t3.label == "Recommend"
    assert profile.tier_by_level(99) is None


def test_profile_contains_no_capability_ids():
    profile = ChiefOfStaffProfile()
    all_fields = dataclasses.fields(profile)
    for f in all_fields:
        assert "capability" not in f.name.lower()
        assert "executor" not in f.name.lower()
        assert "api_client" not in f.name.lower()
        assert "store" not in f.name.lower()


def test_profile_contains_no_authority_state():
    profile = ChiefOfStaffProfile()
    all_fields = dataclasses.fields(profile)
    for f in all_fields:
        assert "permission" not in f.name.lower()
        assert "enabled_cap" not in f.name.lower()
        assert "auth_token" not in f.name.lower()


def test_forbidden_language_covers_authority_patterns():
    profile = ChiefOfStaffProfile()
    forbidden = profile.forbidden_authority_language
    assert any("I will" in f for f in forbidden)
    assert any("I already" in f for f in forbidden)
    assert any("I changed" in f for f in forbidden)
    assert any("I sent" in f for f in forbidden)


def test_staleness_threshold_positive():
    profile = ChiefOfStaffProfile()
    assert profile.default_staleness_threshold_seconds > 0
