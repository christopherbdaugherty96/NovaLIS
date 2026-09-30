"""Fail when tracked files cross NovaLIS's deliberate public-source boundary."""

from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_EXACT = {
    "nova_backend/src/data/ledger.jsonl",
    "nova_backend/memory/quick_corrections.jsonl",
    "NovaLIS-Governance/OLD_VISION.md.html",
    "docs/archive/OLD_VISION.md_files/OLD_VISION.md.html",
}

FORBIDDEN_PREFIXES = (
    "docs/business/",
    "docs/private/",
    "docs/future/private_business/",
    "docs/future/auralis_digital/",
    "docs/future/ai_ecosystem_operating_model/vault_template/03_BUSINESS/",
)

FORBIDDEN_SUFFIXES = (".pem", ".p12", ".pfx", ".key", ".har", ".exe", ".msi", ".msix", ".appx", ".dmg")

FORBIDDEN_BASENAMES = {
    ".env",
    "credentials.json",
    "provider_keys.json",
}

KNOWN_PERSONAL_MARKERS = (
    b"christopherbdaugherty" + b"@gmail.com",
    b"C:\\Users\\" + b"Chris",
    b"C:/Users/" + b"Chris",
    b"cfConnecting" + b"Ip",
    b"WebAnonymousCookie" + b"ID",
)

TEXT_SCAN_MAX_BYTES = 5 * 1024 * 1024


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8", errors="surrogateescape") for item in result.stdout.split(b"\0") if item]


def path_violation(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    pure = PurePosixPath(normalized)
    lower = normalized.lower()
    if normalized in FORBIDDEN_EXACT:
        return "runtime or personal export path"
    if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return "private repository boundary"
    if pure.name.lower() in FORBIDDEN_BASENAMES and pure.name != ".env.example":
        return "credential/environment filename"
    if lower.endswith(FORBIDDEN_SUFFIXES):
        return "unapproved sensitive or release artifact type"
    if pure.name.lower().startswith("client_secret") and lower.endswith(".json"):
        return "OAuth client credential filename"
    if pure.name.lower().startswith("oauth_token") and lower.endswith(".json"):
        return "OAuth token filename"
    return None


def content_violations(path: str) -> list[str]:
    candidate = ROOT / Path(path)
    try:
        if not candidate.is_file() or candidate.stat().st_size > TEXT_SCAN_MAX_BYTES:
            return []
        data = candidate.read_bytes()
    except OSError:
        return []
    return [marker.decode("ascii", errors="replace") for marker in KNOWN_PERSONAL_MARKERS if marker in data]


def main() -> int:
    failures: list[str] = []
    for path in tracked_paths():
        reason = path_violation(path)
        if reason:
            failures.append(f"{path}: {reason}")
        for marker in content_violations(path):
            failures.append(f"{path}: known personal marker {marker!r}")

    if failures:
        print("Public-source hygiene check: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Public-source hygiene check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
