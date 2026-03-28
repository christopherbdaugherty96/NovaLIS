from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE8_MAP_PATH = PROJECT_ROOT / "docs" / "design" / "Phase 8" / "PHASE_8_DOCUMENT_MAP.md"
PHASE8_PROOF_INDEX_PATH = PROJECT_ROOT / "docs" / "PROOFS" / "Phase-8" / "PHASE_8_PROOF_PACKET_INDEX.md"
PHASE8_MASTER_REFERENCE_PATH = (
    PROJECT_ROOT / "docs" / "design" / "Phase 8" / "NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md"
)
PHASE8_HOME_AGENT_PLAN_PATH = (
    PROJECT_ROOT / "docs" / "design" / "Phase 8" / "PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md"
)


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start) if next_heading and next_heading in text[start + 1 :] else len(text)
    return text[start:end]


def test_phase8_document_map_points_to_current_proof_packet_and_verification_package():
    content = PHASE8_MAP_PATH.read_text(encoding="utf-8")

    assert "Current proof packet:" in content
    assert "`docs/PROOFS/Phase-8/PHASE_8_PROOF_PACKET_INDEX.md`" in content
    assert "Current dedicated verification package:" in content
    assert "`nova_backend/tests/phase8/`" in content


def test_phase8_document_map_keeps_current_runtime_truth_separate_from_full_canonical_model():
    content = PHASE8_MAP_PATH.read_text(encoding="utf-8")

    assert "This is the current repo-grounded Phase-8 reference." in content
    assert "this document wins" in content.lower()
    assert "the full canonical Phase-8 automation model is live in runtime" in content


def test_phase8_proof_packet_separates_canonical_foundation_from_adjacent_companion_slices():
    content = PHASE8_PROOF_INDEX_PATH.read_text(encoding="utf-8")
    canonical = _section(
        content,
        "## Current canonical live Phase-8 foundation packet",
        "## Adjacent Phase-8 companion slices",
    )
    adjacent = _section(
        content,
        "## Adjacent Phase-8 companion slices",
        "## Scope captured across the current packets",
    )

    assert "PHASE_8_MANUAL_FOUNDATION_AND_DELIVERY_INBOX_RUNTIME_SLICE_2026-03-27.md" in canonical
    assert "PHASE_8_5_NARROW_SCHEDULER_RUNTIME_SLICE_2026-03-27.md" in canonical
    assert "PHASE_8_5_SCHEDULER_POLICY_SUPPRESSION_AND_END_TO_END_VALIDATION_2026-03-28.md" in canonical
    assert "PHASE_8_DEDICATED_VERIFICATION_AND_PROOF_ALIGNMENT_2026-03-28.md" in canonical
    assert "PHASE_8_OPENCLAW_REMOTE_BOUNDARY_AND_SETUP_READINESS_RUNTIME_SLICE_2026-03-27.md" not in canonical
    assert "PHASE_8_BOUNDED_ASSISTIVE_NOTICING_RUNTIME_SLICE_2026-03-27.md" not in canonical
    assert "PHASE_8_OPENCLAW_REMOTE_BOUNDARY_AND_SETUP_READINESS_RUNTIME_SLICE_2026-03-27.md" in adjacent
    assert "PHASE_8_ASSISTIVE_NOTICE_HISTORY_AND_TYPE_COOLDOWNS_RUNTIME_SLICE_2026-03-27.md" in adjacent


def test_phase8_proof_packet_includes_dedicated_phase8_verification_lane():
    content = PHASE8_PROOF_INDEX_PATH.read_text(encoding="utf-8")

    assert "Run these commands from `nova_backend/`." in content
    assert "`python -m pytest tests\\phase8 -q`" in content
    assert "phase8 dedicated verification package" in content.lower()


def test_phase8_master_reference_keeps_scheduler_boundary_truthful():
    content = PHASE8_MASTER_REFERENCE_PATH.read_text(encoding="utf-8")

    assert "No background scheduler beyond the explicit narrow briefing scheduler carve-out is live" in content
    assert "only the explicit narrow briefing scheduler carve-out is live" in content
    assert "delivery modes control presentation channels for manual runs and the explicit narrow scheduled briefing lane" in content
    assert "no scheduler is live yet" not in content
    assert "they do not imply proactive scheduled delivery" not in content


def test_phase8_home_agent_plan_marks_narrow_scheduler_live_but_broad_autonomy_deferred():
    content = PHASE8_HOME_AGENT_PLAN_PATH.read_text(encoding="utf-8")

    assert "a narrow scheduled briefing lane behind explicit runtime settings control" in content
    assert "quiet-hours and hourly rate-limit suppression for that narrow scheduled lane" in content
    assert "no broad autonomous scheduling beyond the explicit narrow briefing scheduler" in content
    assert "Nova can now run narrow scheduled briefing templates when the scheduler setting is enabled" in content
    assert "no background scheduler" not in content
