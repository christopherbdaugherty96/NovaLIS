from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE5_DIR = PROJECT_ROOT / "docs" / "PROOFS" / "Phase-5"


def test_phase5_proof_packet_files_exist():
    required = [
        "PHASE_5_PROOF_PACKET_INDEX.md",
        "PHASE_5_ADMISSION_GATE_CHECKLIST_2026-03-09.md",
        "MEMORY_GOVERNANCE_RATIFICATION_ACT_2026-03-09.md",
        "TONE_CALIBRATION_ARCHITECTURE_SPEC_2026-03-09.md",
        "PATTERN_DETECTION_OPT_IN_GUARDRAILS_SPEC_2026-03-09.md",
        "NOTIFICATION_SCHEDULING_BOUNDARY_SPEC_2026-03-09.md",
        "PHASE_5_CONSTITUTIONAL_AUDIT_PRECHECK_2026-03-09.md",
        "NOVA_CONSOLIDATED_CANONICAL_STATE_2026-03-09.md",
        "PHASE_5_ADMISSION_GATE_OPERATOR_CHECKLIST_2026-03-09.md",
        "PHASE_5_IMPLEMENTATION_MAP_2026-03-13.md",
        "PHASE_5_CLOSED_ACT_2026-03-13.md",
    ]
    missing = [name for name in required if not (PHASE5_DIR / name).exists()]
    assert missing == []


def test_phase5_checklist_reports_current_gate_status():
    checklist = (PHASE5_DIR / "PHASE_5_ADMISSION_GATE_CHECKLIST_2026-03-09.md").read_text(
        encoding="utf-8"
    )
    assert "Status: Admission gate satisfied for current repository state" in checklist
    assert "PASS" in checklist
    assert "Phase-5 admission gate is SATISFIED for the current repository state." in checklist


def test_phase5_closed_act_records_closed_package():
    closed_act = (PHASE5_DIR / "PHASE_5_CLOSED_ACT_2026-03-13.md").read_text(encoding="utf-8")
    assert "Status: CLOSED" in closed_act
    assert "declarative identity/preferences" in closed_act


def test_consolidated_state_doc_captures_can_and_cannot_boundaries():
    consolidated = (PHASE5_DIR / "NOVA_CONSOLIDATED_CANONICAL_STATE_2026-03-09.md").read_text(
        encoding="utf-8"
    )
    assert "What Nova Can Do Now" in consolidated
    assert "What Nova Cannot Do" in consolidated
    assert "Long-Term Direction Under Lock" in consolidated
