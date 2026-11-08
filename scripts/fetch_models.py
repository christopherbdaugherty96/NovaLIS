#!/usr/bin/env python3
"""Fetch Nova's approved Ollama model through governed process admission.

Designed to be called by the installer or by a user running setup
manually. Checks whether the model is already present before pulling.

No command runs without trusted evidence storage and exact Ollama process
attestation.  Pulling additionally requires explicit online consent bound to a
correlation ID for this setup attempt.

Exit codes:
    0 — exact approved model is listed locally (inference usability unproven)
    1 — Ollama not installed / not reachable
    2 — pull failed
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from src.llm.ollama_setup_admission import (
    APPROVED_INSTALL_MODEL,
    OllamaSetupAdmissionError,
    OllamaSetupOperation,
    run_ollama_command,
)

DEFAULT_MODEL = APPROVED_INSTALL_MODEL


def _model_present(output: str, model: str) -> bool:
    """Return True if *model* already exists in Ollama's local store."""
    for line in output.splitlines()[1:]:
        columns = line.split()
        if columns and columns[0] == model:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--correlation-id", default="")
    parser.add_argument("--allow-online-pull", action="store_true")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if (
        not args.allow_online_pull
        or args.model != DEFAULT_MODEL
        or not args.correlation_id
    ):
        print(
            "[Nova] Model acquisition requires explicit consent for the approved "
            "model and a setup correlation ID.",
            file=sys.stderr,
        )
        return 3

    try:
        listed = run_ollama_command(
            operation=OllamaSetupOperation.LIST,
            model=args.model,
            correlation_id=args.correlation_id,
            online_consent=False,
            timeout=30,
        )
        if listed.returncode != 0:
            print("[Nova] ERROR: Ollama model inventory failed.", file=sys.stderr)
            return 1
        if _model_present(listed.stdout, args.model):
            print(f"[Nova] Model '{args.model}' is already present.")
            return 0
        print(f"[Nova] Pulling approved model '{args.model}'.")
        pulled = run_ollama_command(
            operation=OllamaSetupOperation.PULL,
            model=args.model,
            correlation_id=args.correlation_id,
            online_consent=True,
        )
        if pulled.returncode != 0:
            print("[Nova] ERROR: Ollama pull command failed.", file=sys.stderr)
            return 2
        verified = run_ollama_command(
            operation=OllamaSetupOperation.LIST,
            model=args.model,
            correlation_id=args.correlation_id,
            online_consent=False,
            timeout=30,
        )
        if verified.returncode != 0 or not _model_present(verified.stdout, args.model):
            print(
                "[Nova] ERROR: Pull exited successfully but the exact model was not listed.",
                file=sys.stderr,
            )
            return 2
    except (
        OllamaSetupAdmissionError,
        OSError,
        subprocess.SubprocessError,
        UnicodeError,
    ) as error:
        print(f"[Nova] ERROR: Model setup denied ({type(error).__name__}).", file=sys.stderr)
        return 1

    print(f"[Nova] Model '{args.model}' is listed locally; usability is not yet verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
