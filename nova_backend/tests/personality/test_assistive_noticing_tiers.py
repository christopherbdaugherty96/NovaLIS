"""Phase 1B — AssistiveNoticing tier extensions (Tier 2-4).

Tests for new notice tiers: Flag, Recommend, Prepare.
Written before implementation per the test-first rule.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.working_context.assistive_noticing import (
    NOTICE_TYPE_AUTO_SURFACE_COOLDOWN_SECONDS,
    _auto_surface_ready,
    _clean,
)


@pytest.fixture()
def profile():
    return ChiefOfStaffProfile()


def _utc_now():
    return datetime.now(timezone.utc)


# ---- Tier 2: Flag notice ---------------------------------------------------

class TestTier2FlagNotice:

    def test_tier2_flag_notice_format(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier2_flag_notice,
        )
        notice = build_tier2_flag_notice(
            metric_name="order_count",
            current_value=42,
            threshold=30,
            source_label="Shopify Cap 65",
            source_timestamp=_utc_now().isoformat(),
        )
        assert notice is not None
        assert notice["type"] == "tier2_flag"
        assert "id" in notice
        assert "summary" in notice
        assert isinstance(notice.get("suggested_actions"), list)

    def test_tier2_flag_below_threshold_returns_none(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier2_flag_notice,
        )
        notice = build_tier2_flag_notice(
            metric_name="order_count",
            current_value=10,
            threshold=30,
            source_label="Shopify Cap 65",
            source_timestamp=_utc_now().isoformat(),
        )
        assert notice is None

    def test_tier2_flag_suggested_actions_are_chat_strings(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier2_flag_notice,
        )
        notice = build_tier2_flag_notice(
            metric_name="traffic_spike",
            current_value=500,
            threshold=200,
            source_label="Shopify Cap 65",
            source_timestamp=_utc_now().isoformat(),
        )
        assert notice is not None
        for action in notice["suggested_actions"]:
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()
            assert "executor" not in action["command"].lower()


# ---- Tier 3: Recommend notice ----------------------------------------------

class TestTier3RecommendNotice:

    def test_tier3_recommend_ends_with_question(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier3_recommend_notice,
        )
        notice = build_tier3_recommend_notice(
            pattern_description="Order volume has been rising for 3 consecutive days",
            recommendation="Review your inventory levels",
            source_label="Shopify Cap 65",
        )
        assert notice is not None
        assert notice["summary"].rstrip().endswith("?") or "opt" in notice["summary"].lower()

    def test_tier3_recommend_format(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier3_recommend_notice,
        )
        notice = build_tier3_recommend_notice(
            pattern_description="Repeated API failures",
            recommendation="Check Shopify API status",
            source_label="Runtime activity",
        )
        assert notice is not None
        assert notice["type"] == "tier3_recommend"
        assert "id" in notice
        assert isinstance(notice.get("suggested_actions"), list)

    def test_tier3_actions_are_chat_strings(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier3_recommend_notice,
        )
        notice = build_tier3_recommend_notice(
            pattern_description="Stale memory items",
            recommendation="Review memory items",
            source_label="Cap 61",
        )
        assert notice is not None
        for action in notice["suggested_actions"]:
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()


# ---- Tier 4: Prepare notice ------------------------------------------------

class TestTier4PrepareNotice:

    def test_tier4_prepare_is_ephemeral(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier4_prepare_notice,
        )
        notice = build_tier4_prepare_notice(
            preview_summary="Draft morning briefing based on session data",
            source_label="Briefing Composer",
            source_timestamp=_utc_now().isoformat(),
            profile=profile,
        )
        assert notice is not None
        assert notice["type"] == "tier4_prepare"
        assert notice.get("ephemeral") is True

    def test_tier4_discloses_data_age(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier4_prepare_notice,
        )
        stale_time = (_utc_now() - timedelta(hours=2)).isoformat()
        notice = build_tier4_prepare_notice(
            preview_summary="Draft briefing from prior session",
            source_label="Briefing Composer",
            source_timestamp=stale_time,
            profile=profile,
        )
        assert notice is not None
        summary_lower = notice["summary"].lower()
        assert any(word in summary_lower for word in [
            "ago", "stale", "older", "hour",
        ])

    def test_tier4_stale_not_presented_as_current(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier4_prepare_notice,
        )
        stale_time = (_utc_now() - timedelta(hours=3)).isoformat()
        notice = build_tier4_prepare_notice(
            preview_summary="Shopify snapshot ready",
            source_label="Cap 65",
            source_timestamp=stale_time,
            profile=profile,
        )
        assert notice is not None
        summary_lower = notice["summary"].lower()
        for word in ("current", "latest", "just now", "live"):
            assert word not in summary_lower

    def test_tier4_fresh_data_no_stale_warning(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier4_prepare_notice,
        )
        fresh_time = _utc_now().isoformat()
        notice = build_tier4_prepare_notice(
            preview_summary="Calendar snapshot ready",
            source_label="Cap 57",
            source_timestamp=fresh_time,
            profile=profile,
        )
        assert notice is not None
        summary_lower = notice["summary"].lower()
        assert "stale" not in summary_lower

    def test_tier4_actions_are_chat_strings(self, profile):
        from src.working_context.assistive_noticing import (
            build_tier4_prepare_notice,
        )
        notice = build_tier4_prepare_notice(
            preview_summary="Draft briefing",
            source_label="Briefing Composer",
            source_timestamp=_utc_now().isoformat(),
            profile=profile,
        )
        assert notice is not None
        for action in notice["suggested_actions"]:
            assert isinstance(action["command"], str)
            assert "capability_id" not in action["command"].lower()


# ---- Cooldown integration --------------------------------------------------

class TestTierCooldowns:

    def test_tier2_cooldown_from_profile(self, profile):
        tier2 = profile.tier_by_level(2)
        assert tier2 is not None
        assert tier2.cooldown_seconds > 0

    def test_tier3_cooldown_from_profile(self, profile):
        tier3 = profile.tier_by_level(3)
        assert tier3 is not None
        assert tier3.cooldown_seconds > tier2_cooldown(profile)

    def test_tier4_cooldown_from_profile(self, profile):
        tier4 = profile.tier_by_level(4)
        assert tier4 is not None
        assert tier4.cooldown_seconds > 0


def tier2_cooldown(profile: ChiefOfStaffProfile) -> int:
    tier = profile.tier_by_level(2)
    return tier.cooldown_seconds if tier else 0
