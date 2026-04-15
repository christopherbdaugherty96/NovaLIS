from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "nova_backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.audit.runtime_auditor import write_current_runtime_state_snapshot
from generate_obsidian_overlay import main as refresh_obsidian_overlay


def main() -> None:
    out = write_current_runtime_state_snapshot()
    print(f"Generated runtime docs: {out}")
    refresh_obsidian_overlay()


if __name__ == "__main__":
    main()
