# Nova - Capability Verification Status
Updated: 2026-07-09 (synced to `python scripts/certify_capability.py status`: 4/27 locked — Cap 16, 22, 64, 65)

> Live command truth: `python scripts/certify_capability.py status`
> Framework: `FRAMEWORK.md`

---

## Purpose
This file tracks capability certification progress.
It should not be confused with the overall product priority roadmap.

## Current Product Priority
Phase 3 observation period is the active state (see `docs/status/DAILY_COMMAND_CENTER.md`).
Further capability lock work is gated on observed daily-use evidence, not queued.

---

## Highlighted Capabilities

| ID | Capability | Current State |
|---|---|---|
| 16 | governed_web_search | P1-P5 passed. LOCKED (2026-05-10). |
| 22 | open_file_folder | P1-P5 passed. LOCKED (2026-05-20). |
| 64 | send_email_draft | P1-P5 passed. LOCKED (2026-05-20). Local `mailto:` draft only. |
| 65 | shopify_intelligence_report | P1-P5 passed. LOCKED (2026-05-22). Read-only. |
| 58 | screen_capture | Important trust-facing capability for user usefulness. |
| 61 | memory_governance | Important for continuity and daily value. |
| 63 | openclaw_execute | Future-facing surface requiring careful governance expansion. |

---

## Important Truth
A capability being technically certifiable does not automatically make it the best next product move.

Current direction favors improving the core assistant experience first.

---

## Operational Note
Use the script command output as the source of exact pass/fail phase truth.
