from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_STATE_PATH = PROJECT_ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"


def test_phase4_runtime_truth_is_closed_and_sealed():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")
    assert "| Phase 4 | COMPLETE |" in content
    assert "governed execution spine, mediation, queueing, ledger, and boundary controls are complete and sealed" in content.lower()
