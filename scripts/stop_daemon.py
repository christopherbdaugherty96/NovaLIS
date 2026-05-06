#!/usr/bin/env python3
"""Stop the Nova backend background process safely.

The Windows ``stop_nova.bat`` wrapper delegates here so stop behavior can
clean stale PID files and fall back to a Nova-owned port listener when the PID
file is missing or stale. Unknown processes on the configured port are left
alone.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

PORT = int(os.environ.get("NOVA_PORT", "8000"))
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "nova_backend"
PID_DIR = Path(__file__).resolve().parent / "pids"
PID_FILE = PID_DIR / "nova_backend.pid"


def _pid_from_file() -> int | None:
    try:
        raw = PID_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _port_listener() -> tuple[int, str] | None:
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
    return "uvicorn" in normalized and "src.brain_server:app" in normalized and backend in normalized


def _command_line_for_pid(pid: int) -> str | None:
    try:
        import psutil

        return " ".join(psutil.Process(pid).cmdline())
    except Exception:
        return None


def _stop_pid(pid: int) -> bool:
    try:
        import psutil
    except Exception:
        psutil = None  # type: ignore[assignment]

    if psutil is not None:
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)
            print(f"[Nova] Stopping backend (PID {pid})...")
            proc.terminate()
            for child in children:
                child.terminate()
            _, alive = psutil.wait_procs([proc, *children], timeout=8)
            for process in alive:
                process.kill()
            return True
        except psutil.NoSuchProcess:
            return True
        except Exception:
            pass

    # Fallback for machines without psutil.
    print(f"[Nova] Stopping backend (PID {pid})...")
    result = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _cleanup_pid_file() -> None:
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


def stop_nova() -> int:
    stopped = False
    pid = _pid_from_file()
    if pid is not None:
        command_line = _command_line_for_pid(pid)
        if command_line is None:
            print(f"[Nova] PID file points to a process that is no longer running (PID {pid}).")
        elif _is_nova_backend_command(command_line):
            stopped = _stop_pid(pid)
            time.sleep(0.5)
        else:
            print(f"[Nova] PID file points to a non-Nova process (PID {pid}); leaving it alone.")

    listener = _port_listener()
    if listener is not None:
        listener_pid, command_line = listener
        if _is_nova_backend_command(command_line):
            if listener_pid != pid:
                stopped = _stop_pid(listener_pid) or stopped
        else:
            print(
                f"[Nova] Port {PORT} is owned by a non-Nova process (PID {listener_pid}); leaving it alone.",
                file=sys.stderr,
            )
            _cleanup_pid_file()
            return 1

    _cleanup_pid_file()
    if stopped:
        print("[Nova] Backend stopped.")
    else:
        print("[Nova] Backend was not running.")
    return 0


if __name__ == "__main__":
    sys.exit(stop_nova())
