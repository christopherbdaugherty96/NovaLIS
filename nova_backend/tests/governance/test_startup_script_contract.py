from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
START_DAEMON_PATH = PROJECT_ROOT / "scripts" / "start_daemon.py"
STOP_DAEMON_PATH = PROJECT_ROOT / "scripts" / "stop_daemon.py"
START_BAT_PATH = PROJECT_ROOT / "start_nova.bat"
STOP_BAT_PATH = PROJECT_ROOT / "stop_nova.bat"
START_SH_PATH = PROJECT_ROOT / "start_nova.sh"


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
    assert "--app-window" in source


def test_start_daemon_supports_app_window_mode():
    """Windows launcher should be able to open Nova like an app window."""
    source = START_DAEMON_PATH.read_text(encoding="utf-8")
    assert "--app-window" in source
    assert "NOVA_BROWSER_MODE" in source
    assert "_open_dashboard" in source
    assert "--app=" in source


def test_start_daemon_uses_bounded_readiness_probe():
    source = START_DAEMON_PATH.read_text(encoding="utf-8")
    running_block = source.split("def _is_running", 1)[1].split("def _port_listener", 1)[0]
    assert "probe_phase_status" in running_block
    assert "urlopen" not in running_block


def test_shell_launcher_uses_bounded_readiness_probe_without_curl():
    source = START_SH_PATH.read_text(encoding="utf-8")
    readiness_block = source.split("check_ready()", 1)[1].split("open_dashboard()", 1)[0]
    assert "local_readiness_probe.py" in readiness_block
    assert "curl" not in readiness_block
    assert "urllib.request" not in readiness_block
    assert '127.0.0.1|::1' in source


def test_stop_bat_delegates_to_stop_daemon():
    """stop_nova.bat should use the Python stop daemon for robust cleanup."""
    source = STOP_BAT_PATH.read_text(encoding="utf-8")
    assert "stop_daemon" in source


def test_stop_daemon_only_stops_nova_listener():
    """Stop script should clean stale PID files and avoid unknown port owners."""
    source = STOP_DAEMON_PATH.read_text(encoding="utf-8")
    assert "_is_nova_backend_command" in source
    assert "_command_line_for_pid" in source
    assert "src.brain_server:app" in source
    assert "non-Nova process" in source
    assert "PID_FILE.unlink" in source
