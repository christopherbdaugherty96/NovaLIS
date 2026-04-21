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
  2. Ensures Ollama is running (starts it if not).
  3. Launches ``nova-start`` (or uvicorn fallback) as a background process.
  4. Waits for the /phase-status endpoint to respond.
  5. Opens the browser to the dashboard.

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


def _is_running() -> bool:
    """Return True if Nova is already responding on PORT."""
    try:
        import urllib.request
        with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=3):
            return True
    except Exception:
        return False


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
    backend_dir = Path(__file__).resolve().parents[1] / "nova_backend"
    return [
        sys.executable, "-m", "uvicorn",
        "src.brain_server:app",
        "--host", HOST,
        "--port", str(PORT),
        "--app-dir", str(backend_dir),
    ]


def start_nova(open_browser: bool = True) -> int:
    if _is_running():
        print(f"[Nova] Already running at {BASE_URL}")
        if open_browser:
            webbrowser.open(BASE_URL)
        return 0

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
            print(f"[Nova] Running at {BASE_URL} (PID {proc.pid})")
            PID_FILE.write_text(str(proc.pid), encoding="utf-8")
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
