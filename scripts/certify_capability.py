#!/usr/bin/env python3
"""
certify_capability.py — Capability Verification CLI
=====================================================
Manages the lifecycle of capability certification in Nova.

Usage:
  python scripts/certify_capability.py status
  python scripts/certify_capability.py status 64
  python scripts/certify_capability.py advance <cap_id> <phase>
  python scripts/certify_capability.py live-signoff <cap_id> [--notes "text"]
  python scripts/certify_capability.py lock <cap_id>
  python scripts/certify_capability.py unlock <cap_id> --reason "text"
  python scripts/certify_capability.py check-tests <cap_id>

Phases (for 'advance'): p1_unit, p2_routing, p3_integration, p4_api

Examples:
  python scripts/certify_capability.py status
  python scripts/certify_capability.py advance 64 p3_integration
  python scripts/certify_capability.py live-signoff 64 --notes "all tests pass on Windows 11"
  python scripts/certify_capability.py lock 64
  python scripts/certify_capability.py unlock 64 --reason "breaking change to confirm flow"
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_NOVA_ROOT = _SCRIPT_DIR.parent
_NOVA_BACKEND = _NOVA_ROOT / "nova_backend"
_LOCKS_FILE = _NOVA_BACKEND / "src" / "config" / "capability_locks.json"
_CERT_TESTS_DIR = _NOVA_BACKEND / "tests" / "certification"

AUTOMATED_PHASES = ("p1_unit", "p2_routing", "p3_integration", "p4_api")
ALL_PHASES = ("p1_unit", "p2_routing", "p3_integration", "p4_api", "p5_live")

# ANSI colours
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _stdout_supports_unicode() -> bool:
    encoding = str(getattr(sys.stdout, "encoding", "") or "").lower()
    return "utf" in encoding or encoding == "cp65001"


_USE_UNICODE_GLYPHS = _stdout_supports_unicode()


# ---------------------------------------------------------------------------
# Lock file I/O
# ---------------------------------------------------------------------------

def _load() -> dict:
    return json.loads(_LOCKS_FILE.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    _LOCKS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  -> Saved {_LOCKS_FILE.name}")


def _cap_entry(data: dict, cap_id: str) -> dict:
    caps = data.get("capabilities", {})
    entry = caps.get(str(cap_id))
    if entry is None:
        print(f"{_RED}Error:{_RESET} Capability {cap_id} not found in lock file.")
        sys.exit(1)
    return entry


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

_PHASE_LABELS = {
    "p1_unit": "P1 Unit",
    "p2_routing": "P2 Routing",
    "p3_integration": "P3 Integration",
    "p4_api": "P4 API",
    "p5_live": "P5 Live",
}

_STATUS_ICONS = {
    "pass": f"{_GREEN}[pass]{_RESET}",
    "pending": f"{_YELLOW}[pending]{_RESET}",
    "blocked": f"{_RED}[blocked]{_RESET}",
    "skipped": "[skipped]",
}


def _status_icon(status: str) -> str:
    return _STATUS_ICONS.get(status, f"? {status}")


def _lock_icon(locked: bool) -> str:
    return f"{_GREEN}[LOCKED]{_RESET}" if locked else f"{_YELLOW}[open]{_RESET}"


def _phase_status_glyph(status: str) -> str:
    if _USE_UNICODE_GLYPHS:
        return "✅" if status == "pass" else ("⏳" if status == "pending" else "🚫")
    return "OK" if status == "pass" else (".." if status == "pending" else "NO")


def _lock_glyph(locked: bool) -> str:
    if _USE_UNICODE_GLYPHS:
        return "🔒" if locked else "🔓"
    return "LOCK" if locked else "OPEN"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(args) -> None:
    """Print status table for all capabilities (or one)."""
    data = _load()
    caps = data["capabilities"]

    filter_id = str(args.cap_id) if args.cap_id else None
    items = {k: v for k, v in caps.items() if filter_id is None or k == filter_id}

    if not items:
        print(f"{_RED}Capability {filter_id} not found.{_RESET}")
        sys.exit(1)

    print()
    print(f"  {'ID':<6} {'Name':<30} {'P1':<12} {'P2':<12} {'P3':<12} {'P4':<12} {'P5':<12} {'Lock'}")
    print("  " + "-" * 102)

    for cap_id, entry in sorted(items.items(), key=lambda x: int(x[0])):
        p1 = (entry.get("p1_unit") or {}).get("status", "pending")
        p2 = (entry.get("p2_routing") or {}).get("status", "pending")
        p3 = (entry.get("p3_integration") or {}).get("status", "pending")
        p4 = (entry.get("p4_api") or {}).get("status", "pending")
        p5 = (entry.get("p5_live") or {}).get("status", "pending")
        locked = entry.get("locked", False)

        def _s(st: str) -> str:
            return _phase_status_glyph(st).ljust(4)

        print(
            f"  {cap_id:<6} {entry['name']:<30} {_s(p1):<12} {_s(p2):<12} {_s(p3):<12} "
            f"{_s(p4):<12} {_s(p5):<12} {_lock_glyph(locked)}"
        )

    total = len(caps)
    locked_count = sum(1 for e in caps.values() if e.get("locked"))
    print()
    print(f"  {locked_count}/{total} capabilities locked")

    # Count how many need work
    needs_work = []
    for cap_id, entry in caps.items():
        for phase in ALL_PHASES:
            if (entry.get(phase) or {}).get("status", "pending") == "pending":
                needs_work.append(cap_id)
                break

    if needs_work:
        print(f"  {len(needs_work)} capabilities still need work: {', '.join(sorted(needs_work, key=int))}")
    print()


def cmd_advance(args) -> None:
    """Mark an automated phase as passed for a capability."""
    cap_id = str(args.cap_id)
    phase = args.phase

    if phase not in AUTOMATED_PHASES:
        print(f"{_RED}Error:{_RESET} Phase must be one of: {', '.join(AUTOMATED_PHASES)}")
        sys.exit(1)

    data = _load()
    entry = _cap_entry(data, cap_id)

    print(f"\n  Advancing cap {cap_id} ({entry['name']}) -> {_PHASE_LABELS[phase]}")

    # Run the test suite for this cap to verify it actually passes
    cert_dir = _CERT_TESTS_DIR / f"cap_{cap_id}_{entry['name']}"
    phase_test_file = cert_dir / f"test_{phase}.py"

    if phase_test_file.exists():
        print(f"  Running: pytest {phase_test_file.relative_to(_NOVA_BACKEND)} ...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(phase_test_file), "-q", "--tb=short"],
            cwd=_NOVA_BACKEND,
        )
        if result.returncode != 0:
            print(f"\n{_RED}Tests failed. Phase NOT advanced.{_RESET}")
            sys.exit(1)
        print(f"  {_GREEN}Tests passed.{_RESET}")
    else:
        print(
            f"  {_YELLOW}Warning:{_RESET} No test file found at {phase_test_file}\n"
            "  Marking phase as pass anyway (manual advance). "
            "Create the test file to enable automated verification."
        )

    entry[phase] = {
        "status": "pass",
        "date": date.today().isoformat(),
        "test_file": str(phase_test_file.relative_to(_NOVA_BACKEND)).replace("\\", "/") if phase_test_file.exists() else None,
    }
    _save(data)
    print(f"  {_GREEN}Cap {cap_id} {_PHASE_LABELS[phase]} -> pass{_RESET}\n")


def cmd_live_signoff(args) -> None:
    """Mark p5_live as passed for a capability after manual testing."""
    cap_id = str(args.cap_id)
    notes = args.notes or ""

    data = _load()
    entry = _cap_entry(data, cap_id)

    # Check that P1-P3 are already passing
    missing = []
    for phase in ("p1_unit", "p2_routing", "p3_integration"):
        if (entry.get(phase) or {}).get("status") != "pass":
            missing.append(_PHASE_LABELS[phase])
    if missing:
        print(
            f"{_YELLOW}Warning:{_RESET} The following phases have not passed yet:\n"
            + "\n".join(f"  - {p}" for p in missing)
            + "\n  You can still sign off, but complete these before locking."
        )

    checklist_file = (
        _NOVA_ROOT / "docs" / "capability_verification" / "live_checklists"
        / f"cap_{cap_id}_{entry['name']}.md"
    )
    if checklist_file.exists():
        print(f"\n  Checklist: {checklist_file}")
    else:
        print(f"  {_YELLOW}No checklist file found at {checklist_file}{_RESET}")

    print(f"\n  Recording live sign-off for cap {cap_id} ({entry['name']}) ...")

    entry["p5_live"] = {
        "status": "pass",
        "date": date.today().isoformat(),
        "signed_off_by": "user",
        "notes": notes,
    }
    _save(data)
    print(f"  {_GREEN}Cap {cap_id} P5 Live -> pass{_RESET}")
    print(f"  Now run: python scripts/certify_capability.py lock {cap_id}\n")


def cmd_lock(args) -> None:
    """Lock a capability — all phases must be passing."""
    cap_id = str(args.cap_id)
    data = _load()
    entry = _cap_entry(data, cap_id)

    problems = []
    for phase in ALL_PHASES:
        status = (entry.get(phase) or {}).get("status", "pending")
        if status != "pass":
            problems.append(f"  {_PHASE_LABELS[phase]}: {status}")

    if problems:
        print(
            f"\n{_RED}Cannot lock cap {cap_id} — phases not yet passing:{_RESET}\n"
            + "\n".join(problems)
            + f"\n\n  Run: python scripts/certify_capability.py status {cap_id}\n"
        )
        sys.exit(1)

    # Run the full certification test suite one final time
    cert_dir = _CERT_TESTS_DIR / f"cap_{cap_id}_{entry['name']}"
    if cert_dir.exists():
        print(f"\n  Running full certification suite for cap {cap_id} ...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(cert_dir), "-q", "--tb=short"],
            cwd=_NOVA_BACKEND,
        )
        if result.returncode != 0:
            print(f"\n{_RED}Certification tests failed. Not locking.{_RESET}\n")
            sys.exit(1)
        print(f"  {_GREEN}All certification tests pass.{_RESET}")

    # Lock
    entry["locked"] = True
    entry["locked_date"] = date.today().isoformat()
    # Snapshot the governance fields at lock time
    entry["authority_class"] = entry.get("authority_class", "")
    entry["risk_level"] = entry.get("risk_level", "")
    entry["external_effect"] = entry.get("external_effect", False)
    entry["reversible"] = entry.get("reversible", True)
    _save(data)
    lock_prefix = "🔒" if _USE_UNICODE_GLYPHS else "[LOCKED]"
    print(f"\n  {_BOLD}{_GREEN}{lock_prefix} Cap {cap_id} ({entry['name']}) is now LOCKED.{_RESET}")
    print("  Regression guard is active. All CI runs will enforce this capability.\n")


def cmd_unlock(args) -> None:
    """Unlock a capability to allow modification (resets p5_live and locked)."""
    cap_id = str(args.cap_id)
    reason = args.reason or "(no reason given)"

    data = _load()
    entry = _cap_entry(data, cap_id)

    if not entry.get("locked"):
        print(f"  Cap {cap_id} is not currently locked.")
        return

    entry["locked"] = False
    entry["locked_date"] = None
    entry["p5_live"] = {"status": "pending", "date": None, "signed_off_by": None, "notes": None}
    entry["_unlock_reason"] = f"{date.today().isoformat()}: {reason}"
    _save(data)
    print(
        f"\n  {_YELLOW}{'🔓' if _USE_UNICODE_GLYPHS else '[OPEN]'} Cap {cap_id} ({entry['name']}) unlocked.{_RESET}\n"
        f"  Reason: {reason}\n"
        "  Complete your changes then run live-signoff and lock again.\n"
    )


def cmd_check_tests(args) -> None:
    """Run the certification test suite for a specific capability."""
    cap_id = str(args.cap_id)
    data = _load()
    entry = _cap_entry(data, cap_id)

    cert_dir = _CERT_TESTS_DIR / f"cap_{cap_id}_{entry['name']}"
    if not cert_dir.exists():
        print(f"{_YELLOW}No certification directory found at {cert_dir}{_RESET}")
        sys.exit(1)

    print(f"\n  Running certification tests for cap {cap_id} ({entry['name']}) ...\n")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(cert_dir), "-v", "--tb=short"],
        cwd=_NOVA_BACKEND,
    )
    sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nova Capability Verification CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = sub.add_parser("status", help="Show verification status table")
    p_status.add_argument("cap_id", nargs="?", type=int, help="Cap ID (optional — show all if omitted)")
    p_status.set_defaults(func=cmd_status)

    # advance
    p_advance = sub.add_parser("advance", help="Mark an automated phase as passed")
    p_advance.add_argument("cap_id", type=int)
    p_advance.add_argument("phase", choices=AUTOMATED_PHASES)
    p_advance.set_defaults(func=cmd_advance)

    # live-signoff
    p_live = sub.add_parser("live-signoff", help="Record live user sign-off for P5")
    p_live.add_argument("cap_id", type=int)
    p_live.add_argument("--notes", default="", help="Optional notes about the live test")
    p_live.set_defaults(func=cmd_live_signoff)

    # lock
    p_lock = sub.add_parser("lock", help="Lock a capability (all phases must pass first)")
    p_lock.add_argument("cap_id", type=int)
    p_lock.set_defaults(func=cmd_lock)

    # unlock
    p_unlock = sub.add_parser("unlock", help="Unlock a capability for modification")
    p_unlock.add_argument("cap_id", type=int)
    p_unlock.add_argument("--reason", required=True, help="Reason for unlocking")
    p_unlock.set_defaults(func=cmd_unlock)

    # check-tests
    p_check = sub.add_parser("check-tests", help="Run certification tests for a capability")
    p_check.add_argument("cap_id", type=int)
    p_check.set_defaults(func=cmd_check_tests)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
