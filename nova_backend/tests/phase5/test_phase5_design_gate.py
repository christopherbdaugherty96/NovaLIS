from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_STATE_PATH = PROJECT_ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"


def test_phase5_runtime_slices_are_reflected_in_runtime_truth():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")
    assert "| Phase 5 | COMPLETE |" in content
    assert "governed memory, continuity, tone, scheduling, and pattern-review surfaces are complete and sealed" in content.lower()


def test_runtime_invariants_preserve_non_autonomous_boundary():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")
    assert "- No broad autonomy" in content
    assert "- No hidden background execution outside the explicit OpenClaw scheduler carve-out" in content
    assert "- All actions must pass GovernorMediator" in content
