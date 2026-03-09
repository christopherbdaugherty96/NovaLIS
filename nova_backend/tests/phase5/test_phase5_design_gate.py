from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_STATE_PATH = PROJECT_ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"


def test_phase5_remains_design_locked_in_runtime_truth():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")
    assert "| Phase 5 | DESIGN |" in content


def test_runtime_invariants_preserve_non_autonomous_boundary():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")
    assert "- No autonomy" in content
    assert "- No background execution" in content
    assert "- All actions must pass GovernorMediator" in content
