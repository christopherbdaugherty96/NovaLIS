"""Phase 2 — Mode authority neutrality tests.

Proves that ModeDetector output cannot affect permissions,
routing, approvals, capability count, or execution semantics.
Mode changes presentation label only.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.mode_detection import (
    ModeDetectionResult,
    ModeDetector,
    VALID_MODES,
)
from src.personality.tone_profile_store import ToneProfileStore


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture(scope="module")
def detector():
    return ModeDetector()


@pytest.fixture(scope="module")
def agent(tmp_path_factory):
    p = tmp_path_factory.mktemp("tone")
    return PersonalityInterfaceAgent(tone_store=ToneProfileStore(p / "tone.json"))


# ---------------------------------------------------------------------------
# Capability and executor counts unchanged by mode
# ---------------------------------------------------------------------------

class TestModeDoesNotChangeRegistryCounts:

    def test_mode_does_not_change_capability_count(self, detector):
        from src.governor.capability_registry import CapabilityRegistry
        registry = CapabilityRegistry()
        baseline = len([
            c for c in registry.all_capabilities()
            if getattr(c, "status", "").lower() == "active"
        ])
        for mode in VALID_MODES:
            _ = detector.detect(explicit_override=mode)
            current = len([
                c for c in registry.all_capabilities()
                if getattr(c, "status", "").lower() == "active"
            ])
            assert current == baseline == 27, (
                f"Capability count changed in {mode} mode: {current} vs {baseline}"
            )

    def test_mode_does_not_change_executor_count(self, detector):
        executor_dir = (
            Path(__file__).resolve().parents[2]
            / "src" / "executors"
        )
        baseline = len([
            f for f in executor_dir.glob("*_executor.py") if f.is_file()
        ])
        for mode in VALID_MODES:
            _ = detector.detect(explicit_override=mode)
            current = len([
                f for f in executor_dir.glob("*_executor.py") if f.is_file()
            ])
            assert current == baseline == 22, (
                f"Executor count changed in {mode} mode: {current} vs {baseline}"
            )


# ---------------------------------------------------------------------------
# Mode result cannot influence action flow
# ---------------------------------------------------------------------------

class TestModeOutputCannotInfluenceActions:

    def test_mode_output_cannot_confirm_actions(self, detector):
        """ModeDetectionResult has no field that could confirm an action."""
        for mode in VALID_MODES:
            result = detector.detect(explicit_override=mode)
            assert not hasattr(result, "confirmed")
            assert not hasattr(result, "approved")
            assert not hasattr(result, "accepted")
            assert not hasattr(result, "yes")
            assert not hasattr(result, "allow")

    def test_mode_output_cannot_skip_approval(self, detector):
        """ModeDetectionResult has no bypass or skip flags."""
        for mode in VALID_MODES:
            result = detector.detect(explicit_override=mode)
            assert not hasattr(result, "skip_confirmation")
            assert not hasattr(result, "bypass_gate")
            assert not hasattr(result, "auto_approve")
            assert not hasattr(result, "force")
            assert not hasattr(result, "silent_execute")

    def test_mode_output_cannot_select_capability(self, detector):
        """ModeDetectionResult has no capability selection field."""
        for mode in VALID_MODES:
            result = detector.detect(explicit_override=mode)
            assert not hasattr(result, "capability_id")
            assert not hasattr(result, "capability")
            assert not hasattr(result, "executor")
            assert not hasattr(result, "invoke")
            assert not hasattr(result, "dispatch")
            assert not hasattr(result, "route_to")

    def test_mode_result_fields_are_exactly_four(self, detector):
        """ModeDetectionResult has exactly mode, confidence, reason,
        override_active. No extra fields can sneak in."""
        result = detector.detect()
        fields = set(result.__dataclass_fields__.keys())
        assert fields == {"mode", "confidence", "reason", "override_active"}


# ---------------------------------------------------------------------------
# Override changes label only
# ---------------------------------------------------------------------------

class TestModeOverrideChangesLabelOnly:

    def test_mode_override_changes_label_only(self, detector):
        """Switching mode changes only the mode string — no side effects."""
        home = detector.detect(explicit_override="home")
        business = detector.detect(explicit_override="business")
        dev = detector.detect(explicit_override="development")

        # Mode differs
        assert home.mode != business.mode != dev.mode

        # Confidence always explicit
        assert home.confidence == business.confidence == dev.confidence == "explicit"

        # Override always active
        assert home.override_active is True
        assert business.override_active is True
        assert dev.override_active is True

        # No other fields differ in structure
        for result in (home, business, dev):
            assert isinstance(result.reason, str)
            assert len(result.reason) > 0


# ---------------------------------------------------------------------------
# Same input, different modes → governance snapshot identical
# ---------------------------------------------------------------------------

class TestGovernanceSnapshotPreservedAcrossModes:

    GATE_SCENARIOS = [
        ("Open the Documents folder", "open_file_folder", 22, "local_write"),
        ("Send email draft to Sarah", "send_email_draft", 64, "local_write"),
    ]

    def test_same_input_different_modes_preserves_governance_snapshot(
        self, agent, profile,
    ):
        """Gate wrapping across all modes produces the same governance
        identity (cap name, cap ID, authority class) regardless of mode.
        Only presentation text may differ."""
        for action_desc, cap_name, cap_id, auth_class in self.GATE_SCENARIOS:
            outputs = {}
            for mode in VALID_MODES:
                wrapped = agent.wrap_gate(
                    action_description=action_desc,
                    cap_name=cap_name,
                    cap_id=cap_id,
                    authority_class=auth_class,
                    profile=profile,
                    mode=mode,
                )
                outputs[mode] = wrapped

            # Every mode's output contains the governance footer
            for mode, text in outputs.items():
                assert f"Cap {cap_id}" in text or cap_name in text, (
                    f"Governance identity missing in {mode} mode for {cap_name}"
                )
                # Single confirmation point
                assert text.count("?") == 1, (
                    f"Multiple questions in {mode} mode for {cap_name}"
                )

    def test_gate_question_suffix_identical_across_modes(self, agent, profile):
        """The confirmation question is the same regardless of mode."""
        suffix = profile.confirmation_template.question_suffix
        for mode in VALID_MODES:
            wrapped = agent.wrap_gate(
                action_description="Test action",
                cap_name="test",
                cap_id=0,
                authority_class="test",
                profile=profile,
                mode=mode,
            )
            assert suffix in wrapped, (
                f"Question suffix missing in {mode} mode"
            )

    def test_failure_humanization_calm_across_all_modes(self, agent, profile):
        """Failure messages are calm regardless of mode."""
        error = "CRITICAL ERROR: Capability 65 timed out"
        for mode in VALID_MODES:
            out = agent.humanize_failure(error, profile=profile, mode=mode)
            upper = out.upper()
            assert "ERROR" not in upper
            assert "CRITICAL" not in upper
            assert "ALERT" not in upper

    def test_forbidden_language_absent_across_all_modes(self, agent, profile):
        """No authority language in any mode's output."""
        texts = [
            "Open the Documents folder",
            "Send email to Sarah",
            "Check Shopify store",
            "Run the test suite",
        ]
        for text in texts:
            for mode in VALID_MODES:
                out = agent.present_with_mode(
                    text, mode=mode, profile=profile,
                )
                for phrase in profile.forbidden_authority_language:
                    assert phrase.lower() not in out.lower(), (
                        f"Authority language '{phrase}' in {mode} mode"
                    )
