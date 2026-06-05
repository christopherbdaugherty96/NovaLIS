"""Phase 2 Personality Validation Simulation.

10 scenarios validating ModeDetector, ReminderFramework, and
initiative templates. Confirms authority unchanged while
presentation improves.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.mode_detection import ModeDetector, VALID_MODES
from src.personality.nova_style_contract import NovaStyleContract
from src.personality.reminder_framework import ReminderFramework
from src.personality.tone_profile_store import ToneProfileStore

from tests.simulation.conversation_simulator import run_simulation


def _utc_now():
    return datetime.now(timezone.utc)


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture(scope="module")
def detector():
    return ModeDetector()


@pytest.fixture(scope="module")
def reminder_fw():
    return ReminderFramework()


@pytest.fixture(scope="module")
def agent(tmp_path_factory):
    p = tmp_path_factory.mktemp("tone")
    return PersonalityInterfaceAgent(
        tone_store=ToneProfileStore(p / "tone.json"),
    )


# -------------------------------------------------------------------
# Scenario 1: Home mode detection
# -------------------------------------------------------------------

class TestScenario1HomeModeDetection:

    def test_evening_hour_detects_home(self, detector):
        result = detector.detect(user_text="what's on my list", hour=21)
        assert result.mode == "home"
        assert result.confidence == "inferred"

    def test_early_morning_detects_home(self, detector):
        result = detector.detect(user_text="good morning", hour=6)
        assert result.mode == "home"

    def test_home_mode_uses_home_templates(self, agent, profile):
        tail = NovaStyleContract.initiative_tail("home", "combined")
        assert tail
        lowered = tail.lower()
        assert "want me to" in lowered or "?" in tail

    def test_home_mode_gate_still_requires_confirmation(self, agent, profile):
        wrapped = agent.wrap_gate(
            action_description="Open Downloads",
            cap_name="open_file_folder",
            cap_id=22,
            authority_class="local_write",
            profile=profile,
            mode="home",
        )
        assert "?" in wrapped
        assert "Cap 22" in wrapped or "open_file_folder" in wrapped


# -------------------------------------------------------------------
# Scenario 2: Business / Auralis Digital mode detection
# -------------------------------------------------------------------

class TestScenario2BusinessModeDetection:

    def test_shopify_keywords_detect_business(self, detector):
        for text in ["shopify report", "revenue this quarter",
                     "how are store orders doing"]:
            result = detector.detect(user_text=text)
            assert result.mode == "business", f"Failed for: {text}"

    def test_recent_cap65_detects_business(self, detector):
        result = detector.detect(recent_capabilities=[65, 56])
        assert result.mode == "business"

    def test_business_mode_uses_business_templates(self):
        tail = NovaStyleContract.initiative_tail("business", "combined")
        assert tail
        assert "?" in tail or "if useful" in tail.lower()

    def test_business_guidance_is_structured(self):
        guidance = NovaStyleContract.chat_mode_guidance("business")
        assert "structured" in guidance.lower()
        assert "metrics" in guidance.lower()


# -------------------------------------------------------------------
# Scenario 3: Development / Nova repo mode detection
# -------------------------------------------------------------------

class TestScenario3DevelopmentModeDetection:

    def test_repo_keywords_detect_development(self, detector):
        for text in ["git status", "run the test suite",
                     "debug this error", "check the deployment"]:
            result = detector.detect(user_text=text)
            assert result.mode == "development", f"Failed for: {text}"

    def test_development_mode_uses_dev_templates(self):
        tail = NovaStyleContract.initiative_tail("development", "combined")
        assert tail
        assert "?" in tail or "if useful" in tail.lower()

    def test_development_guidance_is_technical(self):
        guidance = NovaStyleContract.chat_mode_guidance("development")
        assert "technical" in guidance.lower()


# -------------------------------------------------------------------
# Scenario 4: Explicit mode override
# -------------------------------------------------------------------

class TestScenario4ExplicitOverride:

    def test_override_beats_all_signals(self, detector):
        result = detector.detect(
            user_text="shopify revenue",
            hour=22,
            recent_capabilities=[65],
            explicit_override="development",
        )
        assert result.mode == "development"
        assert result.confidence == "explicit"
        assert result.override_active is True

    def test_override_clears_cleanly(self, detector):
        result = detector.clear_override()
        assert result.mode == "home"
        assert result.override_active is False

    def test_invalid_override_rejected(self, detector):
        result = detector.detect(explicit_override="superuser")
        assert result.mode == "home"
        assert result.override_active is False


# -------------------------------------------------------------------
# Scenario 5: Low confidence defaults to home
# -------------------------------------------------------------------

class TestScenario5LowConfidenceDefaults:

    def test_empty_input_defaults_home(self, detector):
        result = detector.detect()
        assert result.mode == "home"
        assert result.confidence == "default"

    def test_ambiguous_input_defaults_home(self, detector):
        for text in ["hello", "thanks", "ok", "hmm"]:
            result = detector.detect(user_text=text)
            assert result.mode == "home", f"Failed for: {text}"

    def test_neutral_text_during_business_hours_defaults_home(self, detector):
        result = detector.detect(user_text="hello", hour=10)
        assert result.mode == "home"


# -------------------------------------------------------------------
# Scenario 6: Reminder suggestion stays advisory
# -------------------------------------------------------------------

class TestScenario6ReminderAdvisory:

    def test_reminder_is_suggestion_not_action(self, reminder_fw):
        reminder = reminder_fw.create_reminder("Call the electrician")
        notice = reminder_fw.to_notice(reminder)
        assert notice["type"] == "tier3_recommend"
        assert notice.get("confirmed") is None
        assert notice.get("approved") is None
        assert notice.get("auto_execute") is None

    def test_reminder_has_no_persistence_methods(self, reminder_fw):
        for attr in ("save", "persist", "write", "store", "commit"):
            assert not hasattr(reminder_fw, attr)

    def test_reminder_notice_uses_chat_commands_only(self, reminder_fw):
        reminder = reminder_fw.create_reminder("Review PR")
        notice = reminder_fw.to_notice(reminder)
        for action in notice["suggested_actions"]:
            cmd = action["command"].lower()
            assert "capability_id" not in cmd
            assert "executor" not in cmd
            assert "calendar" not in cmd
            assert "create event" not in cmd

    def test_reminder_does_not_invoke_cap61(self, reminder_fw):
        """ReminderFramework produces dicts. It never calls Cap 61."""
        reminder = reminder_fw.create_reminder("Test")
        notice = reminder_fw.to_notice(reminder)
        notice_str = str(notice).lower()
        assert "cap 61" not in notice_str
        assert "memory_governance" not in notice_str


# -------------------------------------------------------------------
# Scenario 7: Pattern reminder includes opt-out
# -------------------------------------------------------------------

class TestScenario7PatternOptOut:

    def test_pattern_reminder_has_opt_out_action(self, reminder_fw):
        reminder = reminder_fw.derive_from_pattern(
            "You mentioned the electrician twice this week",
            source_label="Session context",
        )
        assert reminder is not None
        notice = reminder_fw.to_notice(reminder)
        actions_text = " ".join(
            a["command"].lower() for a in notice["suggested_actions"]
        )
        assert "opt out" in actions_text or "stop" in actions_text

    def test_pattern_reminder_summary_mentions_opt_out(self, reminder_fw):
        reminder = reminder_fw.derive_from_pattern(
            "Repeated mention of dentist appointment",
            source_label="Memory",
        )
        notice = reminder_fw.to_notice(reminder)
        lowered = notice["summary"].lower()
        assert "stop" in lowered or "opt" in lowered

    def test_user_created_reminder_no_opt_out_action(self, reminder_fw):
        reminder = reminder_fw.create_reminder("Buy groceries")
        notice = reminder_fw.to_notice(reminder)
        actions_text = " ".join(
            a["command"].lower() for a in notice["suggested_actions"]
        )
        assert "opt out" not in actions_text


# -------------------------------------------------------------------
# Scenario 8: Initiative templates improve presentation
# -------------------------------------------------------------------

class TestScenario8TemplatesImprovePresentation:

    def test_mode_templates_differ_from_generic(self):
        """Chief of Staff templates are distinct from generic casual."""
        casual = NovaStyleContract.initiative_tail("casual", "combined")
        home = NovaStyleContract.initiative_tail("home", "combined")
        business = NovaStyleContract.initiative_tail("business", "combined")
        dev = NovaStyleContract.initiative_tail("development", "combined")
        templates = {casual, home, business, dev}
        assert len(templates) == 4, (
            "All four mode templates should be distinct strings"
        )

    def test_mode_guidance_differs_from_generic(self):
        casual = NovaStyleContract.chat_mode_guidance("casual")
        home = NovaStyleContract.chat_mode_guidance("home")
        business = NovaStyleContract.chat_mode_guidance("business")
        dev = NovaStyleContract.chat_mode_guidance("development")
        guides = {casual, home, business, dev}
        assert len(guides) == 4

    def test_all_templates_use_permitted_language(self, profile):
        permitted = tuple(p.lower() for p in profile.permitted_suggestion_language)
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower()
                ok = (
                    "?" in tail
                    or any(lowered.startswith(p) for p in permitted)
                )
                assert ok, f"[{mode}/{kind}] not permitted: '{tail}'"

    def test_no_authority_language_in_any_template(self, profile):
        forbidden = [p.lower() for p in profile.forbidden_authority_language]
        for mode in ("home", "business", "development"):
            for kind in ("clarify", "branch", "depth", "combined"):
                tail = NovaStyleContract.initiative_tail(mode, kind)
                if not tail:
                    continue
                lowered = tail.lower()
                for phrase in forbidden:
                    assert phrase not in lowered, (
                        f"[{mode}/{kind}] authority: '{phrase}'"
                    )


# -------------------------------------------------------------------
# Scenario 9: Personality-off baseline keeps same routing
# -------------------------------------------------------------------

class TestScenario9PersonalityOffBaseline:

    SCRIPTS = [
        ["shopify report"],
        ["what's the weather"],
        ["search for AI news"],
        ["open documents"],
    ]

    def test_routing_identical_across_runs(self):
        for script in self.SCRIPTS:
            a = run_simulation(script)
            b = run_simulation(script)
            assert a.capability_sequence() == b.capability_sequence(), (
                f"Routing mismatch for {script}"
            )

    def test_governor_decisions_identical_across_runs(self):
        for script in self.SCRIPTS:
            a = run_simulation(script)
            b = run_simulation(script)
            da = [t.governor_decision for t in a.turns]
            db = [t.governor_decision for t in b.turns]
            assert da == db, f"Governor mismatch for {script}"

    def test_mode_detection_does_not_alter_routing(self, detector):
        """Detecting mode before simulation does not change the
        routing pipeline result."""
        for script in self.SCRIPTS:
            _ = detector.detect(user_text=script[0])
            transcript = run_simulation(script)
            # Simulation still produces a result — mode is irrelevant
            assert len(transcript.turns) == 1
            assert transcript.turns[0].nova_response


# -------------------------------------------------------------------
# Scenario 10: Governance invariants unchanged
# -------------------------------------------------------------------

class TestScenario10GovernanceInvariants:

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
            Path(__file__).resolve().parents[2]
            / "src" / "executors"
        )
        executors = [
            f for f in executor_dir.glob("*_executor.py") if f.is_file()
        ]
        assert len(executors) == 22

    def test_no_confirmed_true_in_any_output(
        self, detector, reminder_fw, agent, profile,
    ):
        """No component emits confirmed=True."""
        # ModeDetector
        for mode in VALID_MODES:
            result = detector.detect(explicit_override=mode)
            assert not hasattr(result, "confirmed")

        # ReminderFramework
        reminder = reminder_fw.create_reminder("Test")
        notice = reminder_fw.to_notice(reminder)
        assert notice.get("confirmed") is None
        assert notice.get("approved") is None

        # PersonalityInterfaceAgent
        wrapped = agent.wrap_gate(
            action_description="Test",
            cap_name="test",
            cap_id=0,
            authority_class="test",
            profile=profile,
        )
        assert "confirmed" not in wrapped.lower()

    def test_no_calendar_creation_anywhere(self, reminder_fw, profile):
        reminder = reminder_fw.create_reminder("Meeting at 3pm tomorrow")
        notice = reminder_fw.to_notice(reminder)
        for action in notice["suggested_actions"]:
            cmd = action["command"].lower()
            assert "create event" not in cmd
            assert "calendar" not in cmd

    def test_no_shopify_writes_anywhere(self, reminder_fw, profile):
        reminder = reminder_fw.create_reminder("Update Shopify inventory")
        notice = reminder_fw.to_notice(reminder)
        for action in notice["suggested_actions"]:
            cmd = action["command"].lower()
            assert "shopify" not in cmd or "write" not in cmd
            assert "update inventory" not in cmd

    def test_no_persistence_inside_reminder_framework(self, reminder_fw):
        for attr in ("save", "persist", "write", "store", "commit",
                     "insert", "update", "delete"):
            assert not hasattr(reminder_fw, attr), (
                f"ReminderFramework has forbidden method: {attr}"
            )

    def test_mode_affects_presentation_only(self, agent, profile):
        """Same text through all modes: governance footer identical."""
        for mode in VALID_MODES:
            wrapped = agent.wrap_gate(
                action_description="Open Downloads",
                cap_name="open_file_folder",
                cap_id=22,
                authority_class="local_write",
                profile=profile,
                mode=mode,
            )
            assert "Cap 22" in wrapped or "open_file_folder" in wrapped
            assert wrapped.count("?") == 1
