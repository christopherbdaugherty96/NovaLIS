from __future__ import annotations

import hashlib
from pathlib import Path
import sys


PAIRS = (
    (Path('nova_backend/static/index.html'), Path('Nova-Frontend-Dashboard/index.html')),
    (Path('nova_backend/static/dashboard.js'), Path('Nova-Frontend-Dashboard/dashboard.js')),
    (Path('nova_backend/static/style.phase1.css'), Path('Nova-Frontend-Dashboard/style.phase1.css')),
    (Path('nova_backend/static/orb.js'), Path('Nova-Frontend-Dashboard/orb.js')),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    mismatches: list[str] = []

    for left, right in PAIRS:
        if not left.exists() or not right.exists():
            missing = [str(p) for p in (left, right) if not p.exists()]
            mismatches.append(f"missing file(s): {', '.join(missing)}")
            continue
        if _sha256(left) != _sha256(right):
            mismatches.append(f"mirror drift: {left} != {right}")

    if mismatches:
        print("Frontend mirror check failed:")
        for item in mismatches:
            print(f"- {item}")
        return 1

    print("Frontend mirror check passed.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
