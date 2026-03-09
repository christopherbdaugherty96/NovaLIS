from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE5_DIR = PROJECT_ROOT / "docs" / "PROOFS" / "Phase-5"


def test_tone_calibration_spec_contains_key_constraints():
    spec = (PHASE5_DIR / "TONE_CALIBRATION_ARCHITECTURE_SPEC_2026-03-09.md").read_text(
        encoding="utf-8"
    )
    assert "Class C" in spec
    assert "No proactive adaptation announcements." in spec
    assert "User override and reset must be available." in spec
    assert "No new execution capability is granted." in spec


def test_pattern_detection_spec_is_opt_in_and_non_autonomous():
    spec = (
        PHASE5_DIR / "PATTERN_DETECTION_OPT_IN_GUARDRAILS_SPEC_2026-03-09.md"
    ).read_text(encoding="utf-8")
    assert "opt-in only" in spec
    assert "No auto-apply of detected patterns." in spec
    assert "No background cognition loop is permitted." in spec
    assert "does not unlock autonomous behavior" in spec


def test_notification_boundary_spec_requires_explicit_schedule_control():
    spec = (
        PHASE5_DIR / "NOTIFICATION_SCHEDULING_BOUNDARY_SPEC_2026-03-09.md"
    ).read_text(encoding="utf-8")
    assert "explicit user request" in spec
    assert "No inferred reminders from observed behavior." in spec
    assert "inspectable and cancellable" in spec
    assert "does not grant background autonomy" in spec
