from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOVA_BACKEND = ROOT / "nova_backend"
if str(NOVA_BACKEND) not in sys.path:
    sys.path.insert(0, str(NOVA_BACKEND))

from src.ledger.health import (  # noqa: E402
    DEFAULT_LEDGER_ROTATION_THRESHOLD_BYTES,
    inspect_ledger_health,
)
from src.ledger.writer import LEDGER_PATH  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect Nova's append-only ledger without mutating it."
    )
    parser.add_argument("--path", default=str(LEDGER_PATH), help="Ledger path to inspect.")
    parser.add_argument(
        "--threshold-bytes",
        type=int,
        default=DEFAULT_LEDGER_ROTATION_THRESHOLD_BYTES,
        help="Size at which rotation should be recommended.",
    )
    args = parser.parse_args()

    health = inspect_ledger_health(
        Path(args.path),
        rotation_threshold_bytes=args.threshold_bytes,
    )
    print(json.dumps(health.as_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
