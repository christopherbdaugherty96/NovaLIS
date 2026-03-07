from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TRUTH = ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"
CHECK_FILES = [
    ROOT / "README.md",
    ROOT / "REPO_MAP.md",
    ROOT / "CONTRIBUTING.md",
]
RUNTIME_TRUTH_REF = "docs/current_runtime/CURRENT_RUNTIME_STATE.md"

# These markers indicate runtime capability claims that should live only in
# CURRENT_RUNTIME_STATE.md.
BANNED_PATTERNS = [
    re.compile(r"\bCurrent\s+Phase\b", re.IGNORECASE),
    re.compile(r"\bExecution\s+gate\s+enabled\b", re.IGNORECASE),
    re.compile(r"\bCapabilities?\s+(enabled|disabled|using)\b", re.IGNORECASE),
    re.compile(r"\bRuntime\s+Fingerprint\b", re.IGNORECASE),
]


def _active_capability_names(runtime_doc: str) -> set[str]:
    names: set[str] = set()
    for line in runtime_doc.splitlines():
        # Table row format: | 16 | governed_web_search | ...
        match = re.match(r"^\|\s*\d+\s*\|\s*([a-z0-9_]+)\s*\|", line.strip(), flags=re.IGNORECASE)
        if match:
            names.add(match.group(1).lower())
    return names


def main() -> int:
    errors: list[str] = []

    if not RUNTIME_TRUTH.exists():
        print(f"ERROR: Missing runtime truth file: {RUNTIME_TRUTH}")
        return 1

    runtime_text = RUNTIME_TRUTH.read_text(encoding="utf-8")
    capability_names = _active_capability_names(runtime_text)

    for file_path in CHECK_FILES:
        if not file_path.exists():
            errors.append(f"{file_path}: file missing")
            continue

        text = file_path.read_text(encoding="utf-8")
        lower_text = text.lower()

        if RUNTIME_TRUTH_REF.lower() not in lower_text:
            errors.append(f"{file_path}: missing required runtime truth reference `{RUNTIME_TRUTH_REF}`")

        for pattern in BANNED_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"{file_path}: contains runtime claim marker `{pattern.pattern}`; "
                    "move runtime truth to CURRENT_RUNTIME_STATE.md"
                )

        for capability in sorted(capability_names):
            if re.search(rf"\b{re.escape(capability)}\b", lower_text):
                errors.append(
                    f"{file_path}: contains capability name `{capability}`; "
                    "runtime capability claims must stay in CURRENT_RUNTIME_STATE.md"
                )

    if errors:
        print("Runtime documentation drift check failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Runtime documentation drift check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
