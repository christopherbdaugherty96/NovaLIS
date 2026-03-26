#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/nova_backend"
PID_DIR="$ROOT_DIR/scripts/pids"
PID_FILE="$PID_DIR/nova_backend.pid"
OUT_LOG="$PID_DIR/nova_backend.out.log"
ERR_LOG="$PID_DIR/nova_backend.err.log"
DASHBOARD_URL="http://127.0.0.1:8000"

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "[Nova] Missing backend directory: $BACKEND_DIR"
  exit 1
fi

mkdir -p "$PID_DIR"

PYTHON_EXE="$BACKEND_DIR/venv/bin/python"
if [[ ! -x "$PYTHON_EXE" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_EXE="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_EXE="$(command -v python)"
  else
    echo "[Nova] Could not find python or python3."
    exit 1
  fi
fi

check_ready() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsS "$DASHBOARD_URL/phase-status" >/dev/null 2>&1
    return $?
  fi

  "$PYTHON_EXE" -c "import sys, urllib.request; urllib.request.urlopen('$DASHBOARD_URL/phase-status', timeout=2); sys.exit(0)" >/dev/null 2>&1
}

open_dashboard() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$DASHBOARD_URL" >/dev/null 2>&1 &
  elif command -v open >/dev/null 2>&1; then
    open "$DASHBOARD_URL" >/dev/null 2>&1 &
  else
    echo "[Nova] Dashboard: $DASHBOARD_URL"
  fi
}

if [[ -f "$PID_FILE" ]]; then
  NOVA_PID="$(head -n 1 "$PID_FILE" | tr -d '\r\n' || true)"
  if [[ -n "${NOVA_PID:-}" ]] && kill -0 "$NOVA_PID" >/dev/null 2>&1; then
    ready=false
    for _ in {1..6}; do
      if ! kill -0 "$NOVA_PID" >/dev/null 2>&1; then
        break
      fi
      if check_ready; then
        ready=true
        break
      fi
      sleep 0.5
    done

    if [[ "$ready" == "true" ]]; then
      echo "[Nova] Backend already running (PID $NOVA_PID)."
      open_dashboard
      exit 0
    fi

    echo "[Nova] Existing backend process (PID $NOVA_PID) is running but not ready at $DASHBOARD_URL/phase-status."
    echo "[Nova] Check logs:"
    echo "[Nova]   stdout: $OUT_LOG"
    echo "[Nova]   stderr: $ERR_LOG"
    exit 1
  fi

  rm -f "$PID_FILE"
fi

echo "[Nova] Starting backend..."
(
  cd "$BACKEND_DIR"
  nohup "$PYTHON_EXE" -m uvicorn src.brain_server:app --host 127.0.0.1 --port 8000 >"$OUT_LOG" 2>"$ERR_LOG" &
  echo $! >"$PID_FILE"
)

if [[ ! -f "$PID_FILE" ]]; then
  echo "[Nova] Failed to create PID file."
  exit 1
fi

NOVA_PID="$(head -n 1 "$PID_FILE" | tr -d '\r\n')"
ready=false
for _ in {1..20}; do
  if ! kill -0 "$NOVA_PID" >/dev/null 2>&1; then
    echo "[Nova] Backend process exited before readiness completed."
    echo "[Nova] Check logs:"
    echo "[Nova]   stdout: $OUT_LOG"
    echo "[Nova]   stderr: $ERR_LOG"
    exit 1
  fi
  if check_ready; then
    ready=true
    break
  fi
  sleep 0.5
done

if [[ "$ready" != "true" ]]; then
  echo "[Nova] Backend did not become ready at $DASHBOARD_URL/phase-status."
  echo "[Nova] Check logs:"
  echo "[Nova]   stdout: $OUT_LOG"
  echo "[Nova]   stderr: $ERR_LOG"
  exit 1
fi

echo "[Nova] Backend started."
echo "[Nova] Dashboard: $DASHBOARD_URL"
open_dashboard
