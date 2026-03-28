from __future__ import annotations

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PAIRS = (
    (PROJECT_ROOT / "nova_backend" / "static" / "index.html", PROJECT_ROOT / "Nova-Frontend-Dashboard" / "index.html"),
    (PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js", PROJECT_ROOT / "Nova-Frontend-Dashboard" / "dashboard.js"),
    (PROJECT_ROOT / "nova_backend" / "static" / "style.phase1.css", PROJECT_ROOT / "Nova-Frontend-Dashboard" / "style.phase1.css"),
    (PROJECT_ROOT / "nova_backend" / "static" / "orb.js", PROJECT_ROOT / "Nova-Frontend-Dashboard" / "orb.js"),
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
