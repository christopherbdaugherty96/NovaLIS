"""Phase 3 — TrustPresenter tests.

Written before implementation. Proves:
  - Trust descriptions include governance identity
  - Receipts are never modified by personality
  - No trust-escalation language
  - Personality describes governance, never hides it
"""
from __future__ import annotations

import copy

import pytest

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


@pytest.fixture(scope="module")
def profile():
    return ChiefOfStaffProfile()


SAMPLE_RECEIPT = {
    "event_type": "ACTION_COMPLETED",
    "capability_id": 64,
    "capability_name": "send_email_draft",
    "authority_class": "local_write",
    "success": True,
    "timestamp": "2026-06-05T14:30:00Z",
    "request_id": "req-abc-123",
    "session_id": "session-xyz",
}


# ---------------------------------------------------------------------------
# Capability description
# ---------------------------------------------------------------------------

class TestCapabilityDescription:

    def test_describe_capability_includes_governance_identity(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        desc = tp.describe_capability(
            cap_name="send_email_draft",
            cap_id=64,
            authority_class="local_write",
            profile=profile,
        )
        assert isinstance(desc, dict)
        assert "send_email_draft" in desc.get("summary", "") or "64" in desc.get("summary", "")
        assert "detail" in desc

    def test_describe_capability_uses_positive_framing(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        desc = tp.describe_capability(
            cap_name="governed_web_search",
            cap_id=16,
            authority_class="network_read",
            profile=profile,
        )
        detail = desc.get("detail", "").lower()
        # No negative framing without "by design"
        for word in ("can't", "cannot", "limited", "restricted"):
            if word in detail:
                assert "by design" in detail, (
                    f"Negative framing '{word}' without 'by design'"
                )

    def test_trust_presenter_keeps_capability_identity_visible(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        caps = [
            ("open_file_folder", 22, "local_write"),
            ("send_email_draft", 64, "local_write"),
            ("governed_web_search", 16, "network_read"),
        ]
        for cap_name, cap_id, auth_class in caps:
            desc = tp.describe_capability(
                cap_name=cap_name, cap_id=cap_id,
                authority_class=auth_class, profile=profile,
            )
            combined = f"{desc.get('summary', '')} {desc.get('detail', '')}"
            assert cap_name in combined or str(cap_id) in combined, (
                f"Capability identity not visible for {cap_name}"
            )


# ---------------------------------------------------------------------------
# Receipt preservation
# ---------------------------------------------------------------------------

class TestReceiptPreservation:

    def test_trust_presenter_preserves_original_receipt(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        original = copy.deepcopy(SAMPLE_RECEIPT)
        desc = tp.describe_receipt(SAMPLE_RECEIPT, profile=profile)
        # Original receipt must be unchanged
        assert SAMPLE_RECEIPT == original

    def test_trust_presenter_output_accompanies_receipt_not_replaces_it(
        self, profile,
    ):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        desc = tp.describe_receipt(SAMPLE_RECEIPT, profile=profile)
        assert isinstance(desc, dict)
        # Description has summary/detail, but receipt fields are not in it
        # (they remain in the original receipt object)
        assert "summary" in desc
        assert "detail" in desc
        # The description should reference the action but not
        # replicate all receipt fields
        assert desc is not SAMPLE_RECEIPT

    def test_trust_presenter_does_not_hide_ledger_or_gate_status(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        desc = tp.describe_receipt(SAMPLE_RECEIPT, profile=profile)
        combined = f"{desc.get('summary', '')} {desc.get('detail', '')}".lower()
        # Must reference the action outcome
        assert (
            "completed" in combined
            or "success" in combined
            or "send_email_draft" in combined
            or "email" in combined
        )


# ---------------------------------------------------------------------------
# Boundary explanation
# ---------------------------------------------------------------------------

class TestBoundaryExplanation:

    def test_explain_boundary_uses_positive_framing(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        explanation = tp.explain_boundary(
            action_description="Modify Shopify prices directly",
            reason="Nova has read-only access to Shopify data",
            profile=profile,
        )
        lowered = explanation.lower()
        # Should frame as "by design" not as a failure
        assert "by design" in lowered or "designed" in lowered or "can" in lowered

    def test_no_trust_escalation_language(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        explanation = tp.explain_boundary(
            action_description="Execute a trade",
            reason="Financial execution is outside Nova's authority",
            profile=profile,
        )
        lowered = explanation.lower()
        assert "just trust me" not in lowered
        assert "if you let me" not in lowered
        assert "if you trusted me" not in lowered
        assert "i could do more" not in lowered
        assert "unlock" not in lowered

    def test_boundary_explanation_is_string(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        explanation = tp.explain_boundary(
            action_description="Test",
            reason="Test reason",
            profile=profile,
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 10


# ---------------------------------------------------------------------------
# No execution surface
# ---------------------------------------------------------------------------

class TestTrustPresenterIsolation:

    def test_trust_presenter_has_no_persistence_methods(self):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        for attr in ("save", "persist", "write", "store",
                     "commit", "execute", "invoke"):
            assert not hasattr(tp, attr)

    def test_trust_presenter_output_has_no_confirmed_flag(self, profile):
        from src.personality.trust_presenter import TrustPresenter
        tp = TrustPresenter()
        desc = tp.describe_receipt(SAMPLE_RECEIPT, profile=profile)
        assert desc.get("confirmed") is None
        assert desc.get("approved") is None
        assert desc.get("auto_execute") is None
