from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_STATE_PATH = PROJECT_ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"


def test_phase42_runtime_truth_is_closed_and_sealed():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")
    assert "| Phase 4.2 | COMPLETE |" in content
    assert "orthogonal cognition stack, deep-mode arming, and report surfaces are complete and sealed" in content.lower()
