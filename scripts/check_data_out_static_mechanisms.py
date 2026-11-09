#!/usr/bin/env python3
"""Fail on unregistered or stale supported Data-Out mechanism sites."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "nova_backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.audit.data_out_static_mechanisms import (  # noqa: E402
    report_as_dict,
    validate_repository_dispositions,
)


def main() -> int:
    report = validate_repository_dispositions(REPOSITORY_ROOT)
    payload = report_as_dict(report)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if report.unregistered or report.stale:
        print(
            "Data-Out static mechanism check failed: register every new site and "
            "remove or update stale exact-site dispositions.",
            file=sys.stderr,
        )
        return 1
    print(
        "Data-Out static mechanism check passed without claiming runtime closure."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
