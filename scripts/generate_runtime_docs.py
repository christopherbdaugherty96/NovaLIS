from __future__ import annotations

from src.audit.runtime_auditor import write_current_runtime_state_snapshot


def main() -> None:
    out = write_current_runtime_state_snapshot()
    print(f"Generated runtime docs: {out}")


if __name__ == "__main__":
    main()
