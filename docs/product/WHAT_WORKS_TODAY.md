# What Works Today

Last reviewed: 2026-04-28

This page separates Nova's current surfaces by readiness level.

Use generated runtime docs for exact active capability truth.
Use this page for user-facing readiness expectations.

Latest proof package: [2026-04-28 user test](../demo_proof/2026-04-28_user_test/USER_TEST_REPORT.md).

---

## Proven / Core Paths

| Area | Status | Notes |
|---|---|---|
| Chat / conversations | Proven core path | Core local assistant runtime is available. |
| Dashboard UI | Proven core path | Local dashboard surfaces load in the local-first follow-up pass: Intro, Home, Chat, News, Workspace, Memory, Rules/Policies, Trust, and Settings. |
| Runtime truth docs | Proven core path | Generated runtime state and capability references exist. |
| Research / summaries | Proven core path | Primary read-oriented assistant value. |
| Trust receipts API | Proven core path | `/api/trust/receipts` and `/api/trust/receipts/summary` expose governed-action receipt evidence from the ledger. |
| Trust receipts UI | Proven core path with label friction | The Trust page renders Action Receipts in the local-first proof pass; some receipt rows still need friendlier names when ledger payloads only include capability IDs. |
| Local self-description fallback | Proven core path | Core prompts such as `What works today?` and memory-authority questions now answer from local runtime truth even when the daily metered token budget is exhausted. |

---

## Works With Setup / Environment Dependence

| Area | Status | Notes |
|---|---|---|
| Local device controls | Setup-dependent | OS and hardware behavior may vary. |
| Weather / news / calendar snapshots | Setup-dependent | Some surfaces depend on local config, data sources, or connector setup. |
| Voice input/output | Setup-dependent | Requires local speech tooling and model paths. |
| Shopify intelligence | Setup-dependent, read-only | Requires Shopify environment variables and credentials. Current implementation is read-only reporting, not store automation. |

---

## Implemented But Still Maturing

| Area | Status | Notes |
|---|---|---|
| Memory / continuity | Implemented, evolving UX | Useful surface, still being refined. Memory supports continuity; it does not authorize execution. |
| Screen capture / analysis | Experimental | Request-time capture exists, but the experience is still maturing. |
| Email draft | Implemented, safety-limited | Opens a local mail client draft through `mailto:` after confirmation. Nova does not use SMTP, access inboxes, or send autonomously. Latest proof reached the confirmation boundary; full live mail-client signoff remains open. |
| OpenClaw execution surface | Advanced / constrained | Governed, limited, not broad autonomy. |
| Action Receipts | Implemented, maturing UX | Visible receipt surface exists for governed-action outcomes. A fuller Trust Panel remains future work. |

---

## Not Yet Product-Ready

| Area | Status | Notes |
|---|---|---|
| Fuller Trust Panel / Trust Review Card | Partial / future work | Action Receipts and trust receipt API exist; richer blocked-reason drill-down, confirmation previews, proof browsing, and polished demo flow remain future work. |
| One-click installer | Not implemented | Needed for broader adoption. |
| Mainstream consumer onboarding | Not ready | Current setup expects a technical user. |
| Broad autonomous execution | Intentionally limited | Not current product direction. |
| Cap 64 live lock | Ready for human P5 | Automated checks and confirmation-boundary proof are strong, but local mail-client live proof is still a human step before lock. |
| Cap 65 live lock | Blocked on credentials | Requires real Shopify credentials and read-only live proof before lock. |

---

## What This Means

Nova already has meaningful working surfaces.

The current focus is no longer raw feature count.
The focus is:
- clarity
- trust visibility
- onboarding quality
- usability
- proof
