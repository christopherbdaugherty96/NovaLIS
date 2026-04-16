#!/usr/bin/env python3
"""Fetch the default Ollama model for Nova.

Designed to be called by the installer or by a user running setup
manually. Checks whether the model is already present before pulling.

Usage:
    python scripts/fetch_models.py              # pull default model
    python scripts/fetch_models.py llama3:8b    # pull a specific model

Exit codes:
    0 — model ready (already present or freshly pulled)
    1 — Ollama not installed / not reachable
    2 — pull failed
"""
from __future__ import annotations

import subprocess
import sys


DEFAULT_MODEL = "gemma4:e4b"
OLLAMA_CMD = "ollama"


def _ollama_available() -> bool:
    try:
        subprocess.run(
            [OLLAMA_CMD, "--version"],
            capture_output=True,
            timeout=10,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _model_present(model: str) -> bool:
    """Return True if *model* already exists in Ollama's local store."""
    try:
        result = subprocess.run(
            [OLLAMA_CMD, "list"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # `ollama list` output has model names in the first column.
        # Each line looks like: "gemma4:e4b    3.4 GB    2 days ago"
        for line in result.stdout.splitlines():
            first_col = line.split()[0] if line.strip() else ""
            # Exact match on "name:tag" in the first column.
            if first_col == model:
                return True
            # Also match when tag is "latest" and column shows just the name.
            if ":" not in model and first_col.split(":")[0] == model:
                return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def pull_model(model: str) -> int:
    """Pull *model* via ``ollama pull``. Returns process exit code."""
    print(f"[Nova] Pulling model '{model}' — this may take several minutes …")
    result = subprocess.run([OLLAMA_CMD, "pull", model])
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    model = args[0] if args else DEFAULT_MODEL

    if not _ollama_available():
        print(
            "[Nova] ERROR: Ollama is not installed or not on PATH.\n"
            "       Install it from https://ollama.com then re-run this script.",
            file=sys.stderr,
        )
        return 1

    if _model_present(model):
        print(f"[Nova] Model '{model}' is already available. Nothing to do.")
        return 0

    rc = pull_model(model)
    if rc != 0:
        print(f"[Nova] ERROR: Failed to pull '{model}' (exit code {rc}).", file=sys.stderr)
        return 2

    print(f"[Nova] Model '{model}' ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
