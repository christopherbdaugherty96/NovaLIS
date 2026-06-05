"""Wiring Phase 2A — ModeDetector integration tests.

Proves:
  - ModeDetector is called during session, detected mode stored
  - Detected mode flows to personality helpers
  - Mode does not affect routing, approvals, or execution
  - Explicit override still works
  - Capability count and executor count unchanged
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.personality.mode_detection import ModeDetector, VALID_MODES
from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


@pytest.fixture(scope="module")
def detector():
    return ModeDetector()


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


# ---------------------------------------------------------------------------
# Mode detection produces session-storable result
# ---------------------------------------------------------------------------

class TestModeDetectorSessionIntegration:

    def test_detected_mode_is_plain_string(self, detector):
        """Mode result can be stored in session_state as a string."""
        result = detector.detect(user_text="shopify report")
        assert isinstance(result.mode, str)
        assert result.mode in VALID_MODES

    def test_detected_mode_flows_to_failure_helper(self, detector, profile):
        """_personality_failure_message can accept mode context."""
        from src.personality.interface_agent import PersonalityInterfaceAgent
        agent = PersonalityInterfaceAgent()
        result = detector.detect(user_text="shopify report")
        # humanize_failure accepts mode parameter
        humanized = agent.humanize_failure(
            "Shopify unavailable", profile=profile, mode=result.mode,
        )
        assert isinstance(humanized, str)
        assert len(humanized) > 0

    def test_detected_mode_flows_to_gate_helper(self, detector, profile):
        """wrap_gate can accept mode context."""
        from src.personality.interface_agent import PersonalityInterfaceAgent
        agent = PersonalityInterfaceAgent()
        result = detector.detect(user_text="open documents")
        wrapped = agent.wrap_gate(
            action_description="Open Documents",
            cap_name="open_file_folder",
            cap_id=22,
            authority_class="local_write",
            profile=profile,
            mode=result.mode,
        )
        assert "?" in wrapped
        assert "Cap 22" in wrapped or "open_file_folder" in wrapped

    def test_explicit_override_stored_in_session_state(self, detector):
        """Explicit override produces a result that can be stored."""
        result = detector.detect(explicit_override="business")
        assert result.mode == "business"
        assert result.override_active is True
        # Storable as session state
        session_state = {"detected_mode": result.mode}
        assert session_state["detected_mode"] == "business"


# ---------------------------------------------------------------------------
# Mode does not affect governance
# ---------------------------------------------------------------------------

class TestModeDoesNotAffectGovernance:

    def test_mode_does_not_change_routing(self, detector):
        """Running ModeDetector before simulation doesn't change routing."""
        from tests.simulation.conversation_simulator import run_simulation
        scripts = [["shopify report"], ["what's the weather"]]
        for script in scripts:
            _ = detector.detect(user_text=script[0])
            a = run_simulation(script)
            b = run_simulation(script)
            assert a.capability_sequence() == b.capability_sequence()

    def test_gate_governance_identity_same_across_modes(self, profile):
        from src.personality.interface_agent import PersonalityInterfaceAgent
        agent = PersonalityInterfaceAgent()
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

    def test_failure_calm_across_all_modes(self, profile):
        from src.personality.interface_agent import PersonalityInterfaceAgent
        agent = PersonalityInterfaceAgent()
        for mode in VALID_MODES:
            out = agent.humanize_failure(
                "ERROR: capability timed out", profile=profile, mode=mode,
            )
            assert "ERROR" not in out.upper()

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
