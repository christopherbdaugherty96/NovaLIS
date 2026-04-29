from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
START_DAEMON_PATH = PROJECT_ROOT / "scripts" / "start_daemon.py"
START_BAT_PATH = PROJECT_ROOT / "start_nova.bat"


def test_startup_script_waits_for_phase_status_readiness():
    """The startup pipeline must health-check /phase-status before
    declaring Nova ready.  The logic now lives in start_daemon.py
    (called by start_nova.bat)."""
    source = START_DAEMON_PATH.read_text(encoding="utf-8")

    # Health endpoint is hit before declaring success
    assert "/phase-status" in source
    # Checks whether Nova is already running
    assert "_is_running" in source
    assert "Already running" in source
    # Stale unhealthy Nova listeners should not leave the dashboard stuck.
    assert "_clear_stale_nova_listener" in source
    assert "_current_nova_listener_pid" in source


def test_start_bat_delegates_to_daemon():
    """start_nova.bat should delegate to start_daemon.py."""
    source = START_BAT_PATH.read_text(encoding="utf-8")
    assert "start_daemon" in source
