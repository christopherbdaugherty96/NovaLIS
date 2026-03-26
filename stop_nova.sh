#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/scripts/pids/nova_backend.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "[Nova] No backend PID file found."
  exit 0
fi

NOVA_PID="$(head -n 1 "$PID_FILE" | tr -d '\r\n' || true)"
if [[ -z "${NOVA_PID:-}" ]]; then
  echo "[Nova] PID file is empty. Cleaning up."
  rm -f "$PID_FILE"
  exit 0
fi

echo "[Nova] Stopping backend (PID $NOVA_PID)..."
if kill -0 "$NOVA_PID" >/dev/null 2>&1; then
  kill "$NOVA_PID" >/dev/null 2>&1 || true
  for _ in {1..10}; do
    if ! kill -0 "$NOVA_PID" >/dev/null 2>&1; then
      break
    fi
    sleep 0.2
  done
  if kill -0 "$NOVA_PID" >/dev/null 2>&1; then
    kill -9 "$NOVA_PID" >/dev/null 2>&1 || true
  fi
fi

rm -f "$PID_FILE"
echo "[Nova] Backend stopped."
