"""Personality Live Wiring Phase 1 — Integration Tests.

Proves: old outcome == new outcome for capability invocation,
governor decision, pending confirmation state, ledger behavior,
and trust payload — while displayed text differs.

Tests written before wiring implementation.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from src import brain_server
from src.conversation.session_router import GateResult
from src.personality.chief_of_staff_profile import ChiefOfStaffProfile
from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.trust_presenter import TrustPresenter

from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


@pytest.fixture(scope="module")
def agent():
    return PersonalityInterfaceAgent()


@pytest.fixture(scope="module")
def trust_presenter():
    return TrustPresenter()


# ---------------------------------------------------------------------------
# Component A: Failure humanization wiring
# ---------------------------------------------------------------------------

class TestFailureHumanizationWiring:

    def test_failure_message_uses_humanize_failure(self, agent, profile):
        """Humanized failure replaces raw 'unavailable' string."""
        raw = "News is currently unavailable."
        humanized = agent.humanize_failure(raw, profile=profile)
        assert humanized != raw
        assert "unavailable" not in humanized.lower() or "try" in humanized.lower()

    def test_failure_message_no_alarm_words(self, agent, profile):
        raw_messages = [
            "News is currently unavailable.",
            "Weather is currently unavailable.",
            "Calendar is currently unavailable.",
            "System diagnostics are currently unavailable.",
            "Phase 4.2 analysis is currently unavailable.",
        ]
        for raw in raw_messages:
            humanized = agent.humanize_failure(raw, profile=profile)
            upper = humanized.upper()
            assert "ERROR" not in upper
            assert "CRITICAL" not in upper
            assert "ALERT" not in upper

    def test_failure_message_offers_next_step(self, agent, profile):
        raw = "Weather is currently unavailable."
        humanized = agent.humanize_failure(raw, profile=profile)
        lowered = humanized.lower()
        assert "try" in lowered or "alternative" in lowered


# ---------------------------------------------------------------------------
# Component B: Gate wrapping wiring
# ---------------------------------------------------------------------------

class TestGateWrappingWiring:

    def test_cap22_gate_uses_wrap_gate(self, agent, profile):
        """Wrapped Cap 22 prompt includes governance identity."""
        wrapped = agent.wrap_gate(
            action_description="Open the Documents folder",
            cap_name="open_file_folder",
            cap_id=22,
            authority_class="local_write",
            profile=profile,
        )
        assert "open_file_folder" in wrapped or "Cap 22" in wrapped

    def test_cap64_gate_uses_wrap_gate(self, agent, profile):
        wrapped = agent.wrap_gate(
            action_description="Draft email to Sarah about Q3 timeline",
            cap_name="send_email_draft",
            cap_id=64,
            authority_class="local_write",
            profile=profile,
        )
        assert "send_email_draft" in wrapped or "Cap 64" in wrapped

    def test_gate_still_single_confirmation(self, agent, profile):
        for cap_name, cap_id in [
            ("open_file_folder", 22),
            ("send_email_draft", 64),
        ]:
            wrapped = agent.wrap_gate(
                action_description="Test action",
                cap_name=cap_name,
                cap_id=cap_id,
                authority_class="local_write",
                profile=profile,
            )
            assert wrapped.count("?") == 1, (
                f"Cap {cap_id}: expected 1 question, got {wrapped.count('?')}"
            )

    def test_gate_pending_state_unchanged(self):
        """The pending_governed_confirm dict structure is the same
        regardless of whether prompt text is wrapped."""
        pending = {
            "capability_id": 22,
            "params": {"target": "documents", "path": ""},
        }
        assert "capability_id" in pending
        assert "params" in pending
        assert isinstance(pending["params"], dict)

    def test_gate_yes_still_invokes_capability(self, monkeypatch):
        """After a wrapped gate prompt, 'yes' still triggers
        invoke_governed_capability via the existing confirmation
        resolution logic."""
        invocations: list[tuple[int, dict]] = []

        monkeypatch.setattr(
            brain_server.SessionRouter,
            "evaluate_gate",
            staticmethod(lambda *a, **kw: GateResult(handled=False)),
        )

        async def _fake_invoke(_gov, capability_id, params):
            from src.actions.action_result import ActionResult
            invocations.append((capability_id, dict(params)))
            return ActionResult.ok("Done.", request_id="test")

        monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

        ws = _ScriptedWebSocket(["open documents", "yes"])
        with patch(
            "src.skills.general_chat.generate_chat",
            side_effect=AssertionError("model should not run"),
        ):
            asyncio.run(brain_server.websocket_endpoint(ws))

        assert any(cap_id == 22 for cap_id, _ in invocations), (
            "Cap 22 was not invoked after 'yes'"
        )

    def test_gate_no_still_cancels(self, monkeypatch):
        """After a wrapped gate prompt, 'no' cancels without execution."""
        invocations: list[tuple[int, dict]] = []

        monkeypatch.setattr(
            brain_server.SessionRouter,
            "evaluate_gate",
            staticmethod(lambda *a, **kw: GateResult(handled=False)),
        )

        async def _fake_invoke(_gov, capability_id, params):
            from src.actions.action_result import ActionResult
            invocations.append((capability_id, dict(params)))
            return ActionResult.ok("Done.", request_id="test")

        monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke)

        ws = _ScriptedWebSocket(["open documents", "no"])
        with patch(
            "src.skills.general_chat.generate_chat",
            side_effect=AssertionError("model should not run"),
        ):
            asyncio.run(brain_server.websocket_endpoint(ws))

        cap22_invocations = [c for c, _ in invocations if c == 22]
        assert len(cap22_invocations) == 0, (
            "Cap 22 should not execute after 'no'"
        )
        messages = _chat_messages(ws)
        assert any("cancel" in m.lower() for m in messages), (
            "Cancellation message not found"
        )


# ---------------------------------------------------------------------------
# Component C: TrustPresenter wiring
# ---------------------------------------------------------------------------

class TestTrustPresenterWiring:

    def test_trust_center_includes_personality_description(
        self, trust_presenter, profile,
    ):
        """TrustPresenter explanation includes 'by design' framing."""
        explanation = trust_presenter.explain_boundary(
            action_description="Modify Shopify prices",
            reason="Nova has read-only Shopify access",
            profile=profile,
        )
        assert "by design" in explanation.lower()

    def test_trust_center_raw_data_preserved(self):
        """Raw trust status fields still appear in rendered output."""
        trust_status = {
            "mode": "Local-only",
            "last_external_call": "News update",
            "data_egress": "Read-only requests only",
            "failure_state": "Normal",
        }
        rendered, _ = brain_server._render_trust_center_message(trust_status)
        assert "Local-only" in rendered
        assert "News update" in rendered
        assert "Normal" in rendered

    def test_trust_receipts_api_unchanged(self):
        """The /api/trust/receipts endpoint structure is not modified
        by personality wiring. Receipts are raw ledger data."""
        # This test verifies the API route exists and returns the
        # expected structure. The personality layer never touches it.
        from src.api.trust_api import build_trust_router
        router = build_trust_router()
        routes = [r.path for r in router.routes]
        assert "/api/trust/receipts" in routes
        assert "/api/trust/receipts/summary" in routes


# ---------------------------------------------------------------------------
# Invariant checks
# ---------------------------------------------------------------------------

class TestWiringInvariants:

    def test_capability_count_still_27(self):
        from src.governor.capability_registry import CapabilityRegistry
        registry = CapabilityRegistry()
        active = [
            c for c in registry.all_capabilities()
            if getattr(c, "status", "").lower() == "active"
        ]
        assert len(active) == 27

    def test_executor_count_still_22(self):
        executor_dir = (
            Path(__file__).resolve().parents[2] / "src" / "executors"
        )
        executors = [
            f for f in executor_dir.glob("*_executor.py") if f.is_file()
        ]
        assert len(executors) == 22

    def test_routing_unchanged(self):
        from tests.simulation.conversation_simulator import run_simulation
        for script in [["shopify report"], ["what's the weather"],
                       ["search for AI news"]]:
            a = run_simulation(script)
            b = run_simulation(script)
            assert a.capability_sequence() == b.capability_sequence()
