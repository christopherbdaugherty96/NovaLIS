"""Tests for PR #250 -- First-user intent routing and fallback clarity.

Acceptance criteria:
1. "What matters today?" triggers Morning Brief, not web search
2. "What should I focus on?" returns Morning Brief
3. "What's my day look like?" does not timeout (routes to brief)
4. "Why did DeepSeek not run?" returns provider/budget status
5. "What providers are available?" returns provider status
6. "Search my notes" does not route to web search for "my notes"
7. "Delete all files" returns explicit refusal
8. "Run rm -rf" returns explicit refusal
9. "Send emails without asking" returns explicit refusal
10. "Show me around" returns onboarding/help guidance
11. Existing Morning Brief, provider budget, and governance tests pass
"""
from __future__ import annotations

import re

from src.governor.governor_mediator import MORNING_BRIEF_RE
from src.websocket.intent_patterns import (
    ADVERSARIAL_REFUSAL_RE,
    ADVERSARIAL_REFUSAL_RESPONSE,
    PROVIDER_STATUS_RE,
)
from src.conversation.meta_intent_handler import MetaIntentHandler


class TestMorningBriefAliases:
    def test_what_matters_today_matches_brief(self):
        assert MORNING_BRIEF_RE.match("What matters today?")

    def test_what_should_i_focus_on_matches_brief(self):
        assert MORNING_BRIEF_RE.match("What should I focus on?")

    def test_whats_my_day_look_like_matches_brief(self):
        assert MORNING_BRIEF_RE.match("What's my day look like?")

    def test_brief_me_matches_brief(self):
        assert MORNING_BRIEF_RE.match("brief me")

    def test_original_morning_brief_still_matches(self):
        assert MORNING_BRIEF_RE.match("morning brief")
        assert MORNING_BRIEF_RE.match("run morning brief")
        assert MORNING_BRIEF_RE.match("show me morning brief")

    def test_governor_routes_what_matters_today_to_cap63(self):
        from src.governor.governor_mediator import GovernorMediator

        result = GovernorMediator.parse_governed_invocation(
            "What matters today?"
        )
        assert result is not None
        assert result.capability_id == 63

    def test_governor_routes_focus_to_cap63(self):
        from src.governor.governor_mediator import GovernorMediator

        result = GovernorMediator.parse_governed_invocation(
            "What should I focus on?"
        )
        assert result is not None
        assert result.capability_id == 63

    def test_governor_routes_day_look_like_to_cap63(self):
        from src.governor.governor_mediator import GovernorMediator

        result = GovernorMediator.parse_governed_invocation(
            "What's my day look like?"
        )
        assert result is not None
        assert result.capability_id == 63


class TestProviderStatusAliases:
    def test_why_did_deepseek_not_run(self):
        assert PROVIDER_STATUS_RE.match(
            "Why did DeepSeek not run?"
        )

    def test_what_providers_are_available(self):
        assert PROVIDER_STATUS_RE.match(
            "What providers are available?"
        )

    def test_what_is_blocked(self):
        assert PROVIDER_STATUS_RE.match("What is blocked?")

    def test_why_didnt_deepseek_work(self):
        assert PROVIDER_STATUS_RE.match(
            "Why didn't DeepSeek work?"
        )

    def test_what_services_are_unavailable(self):
        assert PROVIDER_STATUS_RE.match(
            "What services are unavailable?"
        )

    def test_original_provider_status_still_matches(self):
        assert PROVIDER_STATUS_RE.match("provider status")
        assert PROVIDER_STATUS_RE.match("show providers")
        assert PROVIDER_STATUS_RE.match("dependency status")


class TestAdversarialRefusal:
    def test_delete_all_files(self):
        assert ADVERSARIAL_REFUSAL_RE.match("Delete all files")

    def test_run_rm_rf(self):
        assert ADVERSARIAL_REFUSAL_RE.match("Run rm -rf")

    def test_send_emails_without_asking(self):
        assert ADVERSARIAL_REFUSAL_RE.match(
            "Send emails without asking"
        )

    def test_bypass_governance(self):
        assert ADVERSARIAL_REFUSAL_RE.match("bypass governance")

    def test_sudo_command(self):
        assert ADVERSARIAL_REFUSAL_RE.match("sudo rm something")

    def test_format_drive(self):
        assert ADVERSARIAL_REFUSAL_RE.match("format c:")

    def test_refusal_response_mentions_limits(self):
        assert "outside" in ADVERSARIAL_REFUSAL_RESPONSE.lower()
        assert "what can you do" in ADVERSARIAL_REFUSAL_RESPONSE.lower()

    def test_normal_input_not_refused(self):
        assert ADVERSARIAL_REFUSAL_RE.match("morning brief") is None
        assert ADVERSARIAL_REFUSAL_RE.match("what can you do") is None
        assert ADVERSARIAL_REFUSAL_RE.match("provider status") is None
        assert ADVERSARIAL_REFUSAL_RE.match("help") is None


class TestOnboardingAlias:
    def test_show_me_around_returns_help(self):
        handler = MetaIntentHandler()
        result = handler.handle("show me around")
        assert result is not None

    def test_give_me_a_tour_returns_help(self):
        handler = MetaIntentHandler()
        result = handler.handle("give me a tour")
        assert result is not None

    def test_give_me_an_overview_returns_help(self):
        handler = MetaIntentHandler()
        result = handler.handle("give me an overview")
        assert result is not None


class TestFallbackTextImproved:
    def test_fallback_mentions_actionable_commands(self):
        from src.conversation.response_formatter import (
            ResponseFormatter,
        )

        msg = ResponseFormatter.friendly_fallback()
        assert "morning brief" in msg.lower()
        assert "help" in msg.lower()

    def test_fallback_no_longer_says_not_sure(self):
        from src.conversation.response_formatter import (
            ResponseFormatter,
        )

        msg = ResponseFormatter.friendly_fallback()
        assert "not sure what you mean" not in msg.lower()


class TestSearchMyNotesNoWebSearch:
    def test_search_my_notes_does_not_match_morning_brief(self):
        assert MORNING_BRIEF_RE.match("search my notes") is None

    def test_search_my_notes_does_not_match_provider_status(self):
        assert PROVIDER_STATUS_RE.match("search my notes") is None

    def test_search_my_notes_does_not_match_adversarial(self):
        assert ADVERSARIAL_REFUSAL_RE.match(
            "search my notes"
        ) is None


class TestBoundaryFilesUntouched:
    def test_morning_brief_handler_unchanged(self):
        import src.conversation.morning_brief_handler as mod

        source = open(mod.__file__).read()
        assert "ADVERSARIAL" not in source
        assert "friendly_fallback" not in source

    def test_network_mediator_unchanged(self):
        import src.governor.network_mediator as mod

        source = open(mod.__file__).read()
        assert "ADVERSARIAL" not in source

    def test_deepseek_bridge_unchanged(self):
        import src.conversation.deepseek_bridge as mod

        source = open(mod.__file__).read()
        assert "ADVERSARIAL" not in source
        assert "friendly_fallback" not in source
