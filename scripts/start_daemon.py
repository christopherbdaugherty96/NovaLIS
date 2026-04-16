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
STARTUP_TIMEOUT = 30  # seconds


def _is_running() -> bool:
    """Return True if Nova is already responding on PORT."""
    try:
        import urllib.request
        with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=3):
            return True
    except Exception:
        return False


def _ensure_ollama() -> None:
    """Start Ollama serve if it's installed but not running."""
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3)
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
        print("[Nova] Started Ollama in background.")
        time.sleep(2)  # give it a moment to bind
    except FileNotFoundError:
        print("[Nova] WARNING: Ollama not found. LLM features will be unavailable.")


def _find_nova_command() -> list[str]:
    """Return the command list to start Nova."""
    # Prefer the installed console script
    nova_start = "nova-start"
    try:
        subprocess.run(
            [nova_start, "--help"],
            capture_output=True,
            timeout=5,
        )
        return [nova_start]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

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

    creation_flags = 0
    if platform.system() == "Windows":
        creation_flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )

    # Wait for the health endpoint
    start = time.time()
    while time.time() - start < STARTUP_TIMEOUT:
        if _is_running():
            print(f"[Nova] Running at {BASE_URL} (PID {proc.pid})")
            if open_browser:
                webbrowser.open(BASE_URL)
            return 0
        time.sleep(1)

    print(
        f"[Nova] ERROR: Server did not respond within {STARTUP_TIMEOUT}s.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    open_browser = "--no-browser" not in sys.argv
    return start_nova(open_browser=open_browser)


if __name__ == "__main__":
    sys.exit(main())
