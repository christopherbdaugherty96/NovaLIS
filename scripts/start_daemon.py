#!/usr/bin/env python3
"""Start (or verify) the Nova backend as a background process.

Designed to be called by the installer's final step, by the Start Menu
shortcut, or manually. On Windows this uses ``subprocess.CREATE_NO_WINDOW``
so the server runs without a visible console.

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
import platform
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

HOST = os.environ.get("NOVA_HOST", "127.0.0.1")
PORT = int(os.environ.get("NOVA_PORT", "8000"))
BASE_URL = f"http://{HOST}:{PORT}"
HEALTH_ENDPOINT = f"{BASE_URL}/phase-status"
STARTUP_TIMEOUT = int(os.environ.get("NOVA_STARTUP_TIMEOUT", "90"))  # seconds
PID_DIR = Path(__file__).resolve().parent / "pids"
PID_FILE = PID_DIR / "nova_backend.pid"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "nova_backend"


def _is_running() -> bool:
    """Return True if Nova is already responding on PORT."""
    try:
        import urllib.request
        with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=3):
            return True
    except Exception:
        return False


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
        "uvicorn" in normalized
        and "src.brain_server:app" in normalized
        and backend in normalized
    )


def _clear_stale_nova_listener() -> bool:
    """Stop an unhealthy Nova process that still owns the configured port.

    Returns True when startup may continue. Unknown port owners are left alone
    and reported as a startup blocker.
    """
    listener = _port_listener()
    if listener is None:
        return True

    pid, command_line = listener
    if not _is_nova_backend_command(command_line):
        print(
            f"[Nova] ERROR: Port {PORT} is occupied by a non-Nova process (PID {pid}).\n"
            "[Nova] Stop that process or set NOVA_PORT before starting Nova.",
            file=sys.stderr,
        )
        return False

    print(f"[Nova] Found stale Nova listener on port {PORT} (PID {pid}); stopping it...")
    try:
        import psutil

        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except psutil.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    except Exception as exc:
        print(f"[Nova] ERROR: Could not stop stale Nova process {pid}: {exc}", file=sys.stderr)
        return False

    return True


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


def _ensure_ollama() -> None:
    """Start Ollama serve if it's installed but not running."""
    try:
        import urllib.request
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return  # already running
    except Exception:
        pass

    try:
        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )
        print("[Nova] Started Ollama in background — waiting for it to be ready...")
        # Poll the Ollama health endpoint instead of sleeping a fixed amount.
        # Ollama typically binds within 1-3 seconds but can be slower on first run.
        for _ in range(30):
            try:
                urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1)
                break  # Ollama is up
            except Exception:
                time.sleep(0.5)
    except FileNotFoundError:
        print("[Nova] WARNING: Ollama not found. LLM features will be unavailable.")


def _find_nova_command() -> list[str]:
    """Return the command list to start Nova."""
    import shutil

    # Prefer the installed console script (don't invoke it — just check PATH)
    nova_start = shutil.which("nova-start")
    if nova_start is not None:
        return [nova_start]

    # Fallback: uvicorn from the nova_backend directory
    return [
        sys.executable, "-m", "uvicorn",
        "src.brain_server:app",
        "--host", HOST,
        "--port", str(PORT),
        "--app-dir", str(BACKEND_DIR),
    ]


def start_nova(open_browser: bool = True) -> int:
    if _is_running():
        print(f"[Nova] Already running at {BASE_URL}")
        if open_browser:
            webbrowser.open(BASE_URL)
        return 0

    if not _clear_stale_nova_listener():
        return 1

    _ensure_ollama()

    cmd = _find_nova_command()
    print(f"[Nova] Starting: {' '.join(cmd)}")

    # Log Nova's stdout + stderr so startup failures are diagnosable.
    # The log file lives next to start_daemon.py's sibling pids/ directory,
    # matching where start_nova.bat puts its logs.
    PID_DIR.mkdir(exist_ok=True)
    _nova_log = PID_DIR / "nova.log"
    print(f"[Nova] Server output -> {_nova_log}")
    _log_fh = open(_nova_log, "a")

    creation_flags = 0
    if platform.system() == "Windows":
        creation_flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

    proc = subprocess.Popen(
        cmd,
        stdout=_log_fh,
        stderr=_log_fh,
        creationflags=creation_flags,
    )

    # Wait for the health endpoint
    start = time.time()
    while time.time() - start < STARTUP_TIMEOUT:
        if _is_running():
            running_pid = _current_nova_listener_pid(proc.pid)
            print(f"[Nova] Running at {BASE_URL} (PID {running_pid})")
            PID_FILE.write_text(str(running_pid), encoding="utf-8")
            _log_fh.close()
            if open_browser:
                webbrowser.open(BASE_URL)
            return 0
        exit_code = proc.poll()
        if exit_code is not None:
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
    return start_nova(open_browser=open_browser)


if __name__ == "__main__":
    sys.exit(main())
