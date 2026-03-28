from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE7_MAP_PATH = PROJECT_ROOT / "docs" / "design" / "Phase 7" / "PHASE_7_DOCUMENT_MAP.md"
PHASE7_PROOF_INDEX_PATH = PROJECT_ROOT / "docs" / "PROOFS" / "Phase-7" / "PHASE_7_PROOF_PACKET_INDEX.md"


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start) if next_heading and next_heading in text[start + 1 :] else len(text)
    return text[start:end]


def test_phase7_document_map_keeps_completion_bounded_to_external_reasoning():
    content = PHASE7_MAP_PATH.read_text(encoding="utf-8")

    assert "Phase 7 is now complete" in content
    assert "governed text-only external reasoning is active" in content
    assert "the reasoning lane remains advisory only" in content
    assert "it does not authorize action autonomy" in content


def test_phase7_proof_packet_separates_canonical_core_from_adjacent_later_slices():
    content = PHASE7_PROOF_INDEX_PATH.read_text(encoding="utf-8")
    canonical = _section(
        content,
        "## Current canonical Phase-7 completion packet",
        "## Adjacent late-Phase-7 / pre-Phase-8 access and foundation slices",
    )
    adjacent = _section(
        content,
        "## Adjacent late-Phase-7 / pre-Phase-8 access and foundation slices",
        "## Historical Note",
    )

    assert "PHASE_7_COMPLETION_AND_REASONING_TRANSPARENCY_RUNTIME_SLICE_2026-03-26.md" in canonical
    assert "PHASE_7_GOVERNED_REMOTE_BRIDGE_RUNTIME_SLICE_2026-03-26.md" not in canonical
    assert "PHASE_7_OPENCLAW_HOME_AGENT_FOUNDATION_RUNTIME_SLICE_2026-03-26.md" not in canonical
    assert "PHASE_7_GOVERNED_REMOTE_BRIDGE_RUNTIME_SLICE_2026-03-26.md" in adjacent
    assert "PHASE_7_OPENCLAW_HOME_AGENT_FOUNDATION_RUNTIME_SLICE_2026-03-26.md" in adjacent


def test_phase7_proof_packet_includes_dedicated_phase7_verification_lane():
    content = PHASE7_PROOF_INDEX_PATH.read_text(encoding="utf-8")

    assert "Run these commands from `nova_backend/`." in content
    assert "`python -m pytest tests\\phase7 -q`" in content
    assert "phase7 dedicated verification package" in content.lower()
