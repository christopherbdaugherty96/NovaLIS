from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
START_SCRIPT_PATH = PROJECT_ROOT / "start_nova.bat"


def test_startup_script_waits_for_phase_status_readiness():
    source = START_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "/phase-status" in source
    assert "Invoke-WebRequest" in source
    assert "Get-Process -Id" in source
    assert "Existing backend process" in source
    assert "Backend already running" in source
