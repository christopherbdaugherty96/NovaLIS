#!/usr/bin/env python3
"""Start (or verify) the Nova backend as a background process.

Designed to be called by the installer's final step, by the Start Menu
shortcut, or manually. The fixed backend child is admitted and evidenced
before process creation.

Usage:
    python scripts/start_daemon.py          # start and open browser
    python scripts/start_daemon.py --no-browser  # start only

The script:
  1. Checks if Nova is already running on the target port.
  2. Clears an unhealthy stale Nova process if it owns the target port.
  3. Ensures Ollama is running (starts it if not).
  4. Launches ``nova-start`` (or uvicorn fallback) as a background process.
  5. Waits for the /phase-status endpoint to respond.
  6. Opens the browser to the dashboard.

Exit codes:
    0 — Nova is running and reachable
    1 — failed to start
"""

from __future__ import annotations

import os
import subprocess  # noqa: F401 - retained for launcher-test monkeypatch compatibility
import sys
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "nova_backend"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from local_readiness_probe import probe_phase_status
from src.governor.backend_startup_admission import (
    BackendStartupAdmissionError,
    record_backend_outcome,
    spawn_admitted_backend,
)
from src.governor.disclosure_policy import InitiationClass
from src.governor.url_handoff_admission import (
    URLHandoffAdmissionError,
    URLHandoffKind,
    open_governed_url_handoff,
)
from src.llm.local_ollama_bootstrap import (
    LocalOllamaStartupStatus,
    verified_local_ollama_startup_status,
)
from src.llm.ollama_serve_admission import (
    OllamaServeAdmissionError,
    spawn_verified_ollama_server,
)
from src.utils.loopback_bind import require_loopback_bind_host

HOST = require_loopback_bind_host(os.environ.get("NOVA_HOST", "127.0.0.1"))
PORT = int(os.environ.get("NOVA_PORT", "8000"))
URL_HOST = f"[{HOST}]" if ":" in HOST else HOST
BASE_URL = f"http://{URL_HOST}:{PORT}"
HEALTH_ENDPOINT = f"{BASE_URL}/phase-status"
STARTUP_TIMEOUT = int(os.environ.get("NOVA_STARTUP_TIMEOUT", "90"))  # seconds
PID_DIR = Path(__file__).resolve().parent / "pids"
PID_FILE = PID_DIR / "nova_backend.pid"


def _is_running() -> bool:
    """Return True if Nova is already responding on PORT."""
    return probe_phase_status(host=HOST, port=PORT, timeout=3)


def _port_listener() -> tuple[int, str] | None:
    """Return the PID and command line for the process listening on HOST:PORT."""
    try:
        import psutil
    except Exception:
        return None

    for conn in psutil.net_connections(kind="tcp"):
        try:
            if not conn.laddr or conn.laddr.port != PORT:
                continue
            if conn.status != psutil.CONN_LISTEN or not conn.pid:
                continue
            proc = psutil.Process(conn.pid)
            return conn.pid, " ".join(proc.cmdline())
        except (psutil.Error, OSError):
            continue
    return None


def _is_nova_backend_command(command_line: str) -> bool:
    normalized = command_line.replace("\\", "/").lower()
    backend = str(BACKEND_DIR).replace("\\", "/").lower()
    return (
        "uvicorn" in normalized and "src.brain_server:app" in normalized and backend in normalized
    )


def _port_available_for_startup() -> bool:
    """Preserve an existing listener when readiness could not be confirmed."""
    listener = _port_listener()
    if listener is None:
        return True

    pid, command_line = listener
    if _is_nova_backend_command(command_line):
        print(
            f"[Nova] ERROR: Nova owns port {PORT} (PID {pid}), but readiness could not be confirmed.\n"
            "[Nova] If it is unresponsive, explicitly stop it before restarting.",
            file=sys.stderr,
        )
    else:
        print(
            f"[Nova] ERROR: Port {PORT} is occupied by a non-Nova process (PID {pid}).\n"
            "[Nova] Stop that process or set NOVA_PORT before starting Nova.",
            file=sys.stderr,
        )
    return False


def _current_nova_listener_pid(fallback_pid: int) -> int:
    """Return the real listening Nova PID when wrappers spawn a child process."""
    listener = _port_listener()
    if listener is None:
        return fallback_pid

    pid, command_line = listener
    if _is_nova_backend_command(command_line):
        return pid
    return fallback_pid


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e4b")


def _startup_ollama_status(*, timeout: float, attempt: int) -> LocalOllamaStartupStatus:
    return verified_local_ollama_startup_status(
        base_url=OLLAMA_URL,
        model=OLLAMA_MODEL,
        request_id=f"startup-ollama-{attempt}",
        session_id="startup-daemon",
        timeout=timeout,
    )


def _ensure_ollama() -> bool:
    """Start Ollama only after a trusted probe proves it is genuinely offline."""
    status = _startup_ollama_status(timeout=3, attempt=0)
    if status is LocalOllamaStartupStatus.AVAILABLE:
        return True
    if status is LocalOllamaStartupStatus.DENIED:
        print(
            "[Nova] WARNING: Ollama startup admission was denied; "
            "the local model will remain unavailable.",
            file=sys.stderr,
        )
        return False

    try:
        spawn_verified_ollama_server(
            correlation_id="startup-daemon-ollama-serve",
        )
        print("[Nova] Started Ollama in background — waiting for it to be ready...")
        # Poll the Ollama health endpoint instead of sleeping a fixed amount.
        # Ollama typically binds within 1-3 seconds but can be slower on first run.
        for attempt in range(1, 31):
            status = _startup_ollama_status(timeout=1, attempt=attempt)
            if status is LocalOllamaStartupStatus.AVAILABLE:
                return True
            if status is LocalOllamaStartupStatus.DENIED:
                print(
                    "[Nova] WARNING: Ollama readiness admission was denied; "
                    "startup polling stopped.",
                    file=sys.stderr,
                )
                return False
            time.sleep(0.5)
        return False
    except OllamaServeAdmissionError as error:
        print(
            f"[Nova] WARNING: Ollama startup was not admitted ({error}); "
            "LLM features will be unavailable.",
            file=sys.stderr,
        )
        return False


def _open_dashboard(open_as_app: bool = False) -> bool:
    """Ask the OS default browser to accept the exact local dashboard URL.

    Acceptance is not proof that the browser loaded or rendered the dashboard.
    Direct browser executable discovery remains disabled pending F09 proof.
    """
    if open_as_app:
        print(
            "[Nova] App-window mode uses the governed default-browser handoff; "
            "direct browser execution is disabled."
        )
    try:
        accepted = open_governed_url_handoff(
            uri=BASE_URL,
            kind=URLHandoffKind.STARTUP_DASHBOARD,
            request_id=f"startup-dashboard-{uuid.uuid4().hex}",
            session_id="startup-daemon",
        )
    except URLHandoffAdmissionError as error:
        if error.handoff_attempted:
            print(
                "[Nova] WARNING: Dashboard browser handoff was attempted, but its "
                f"outcome could not be verified ({error}).",
                file=sys.stderr,
            )
        else:
            print(
                f"[Nova] WARNING: Dashboard browser handoff was not admitted ({error}).",
                file=sys.stderr,
            )
        return False

    if accepted:
        print("[Nova] The default browser accepted the local dashboard handoff.")
    else:
        print(
            "[Nova] WARNING: The default browser rejected the local dashboard handoff.",
            file=sys.stderr,
        )
    return accepted


def start_nova(
    open_browser: bool = True,
    *,
    app_window: bool = False,
    initiation: InitiationClass = InitiationClass.USER_INITIATED,
) -> int:
    if _is_running():
        print(f"[Nova] Already running at {BASE_URL}")
        if open_browser:
            _open_dashboard(open_as_app=app_window)
        return 0

    if not _port_available_for_startup():
        return 1

    _ensure_ollama()

    print("[Nova] Starting the admitted local backend command.")

    # Log Nova's stdout + stderr so startup failures are diagnosable.
    # The log file lives next to start_daemon.py's sibling pids/ directory,
    # matching where start_nova.bat puts its logs.
    PID_DIR.mkdir(exist_ok=True)
    _nova_log = PID_DIR / "nova.log"
    print(f"[Nova] Server output -> {_nova_log}")
    _log_fh = open(_nova_log, "a")

    try:
        launch = spawn_admitted_backend(
            executable=Path(sys.executable),
            backend_dir=BACKEND_DIR,
            host=HOST,
            port=PORT,
            stdout=_log_fh,
            stderr=_log_fh,
            initiation=initiation,
        )
    except BackendStartupAdmissionError as error:
        _log_fh.close()
        print(
            f"[Nova] ERROR: Backend startup was not admitted ({error}).",
            file=sys.stderr,
        )
        return 1
    proc = launch.process

    # Wait for the health endpoint
    start = time.time()
    while time.time() - start < STARTUP_TIMEOUT:
        if _is_running():
            running_pid = _current_nova_listener_pid(proc.pid)
            try:
                record_backend_outcome(
                    launch,
                    outcome="ready",
                    listener_pid=running_pid,
                )
            except BackendStartupAdmissionError as error:
                try:
                    proc.terminate()
                except Exception:
                    pass
                _log_fh.close()
                print(
                    f"[Nova] ERROR: Backend readiness evidence failed ({error}).",
                    file=sys.stderr,
                )
                return 1
            print(f"[Nova] Running at {BASE_URL} (PID {running_pid})")
            PID_FILE.write_text(str(running_pid), encoding="utf-8")
            _log_fh.close()
            if open_browser:
                _open_dashboard(open_as_app=app_window)
            return 0
        exit_code = proc.poll()
        if exit_code is not None:
            try:
                record_backend_outcome(
                    launch,
                    outcome="exited_before_ready",
                    exit_code=exit_code,
                )
            except BackendStartupAdmissionError as error:
                print(
                    f"[Nova] WARNING: Backend exit evidence failed ({error}).",
                    file=sys.stderr,
                )
            print(
                f"[Nova] ERROR: Nova process exited before health check succeeded "
                f"(PID {proc.pid}, exit code {exit_code}).\n"
                f"[Nova] Check {_nova_log} for details.",
                file=sys.stderr,
            )
            try:
                PID_FILE.unlink()
            except FileNotFoundError:
                pass
            _log_fh.close()
            return 1
        time.sleep(1)

    try:
        record_backend_outcome(launch, outcome="readiness_timeout")
    except BackendStartupAdmissionError as error:
        print(
            f"[Nova] WARNING: Backend timeout evidence failed ({error}).",
            file=sys.stderr,
        )
    print(
        f"[Nova] ERROR: Server did not respond within {STARTUP_TIMEOUT}s.\n"
        f"[Nova] Check {_nova_log} for details.",
        file=sys.stderr,
    )
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass
    _log_fh.close()
    return 1


def main() -> int:
    open_browser = "--no-browser" not in sys.argv
    app_window = (
        "--app-window" in sys.argv or os.environ.get("NOVA_BROWSER_MODE", "").lower() == "app"
    )
    initiation = (
        InitiationClass.AUTOMATIC
        if "--automatic-startup" in sys.argv
        else InitiationClass.USER_INITIATED
    )
    return start_nova(
        open_browser=open_browser,
        app_window=app_window,
        initiation=initiation,
    )


if __name__ == "__main__":
    sys.exit(main())
