# What Works Today

This page separates Nova's current surfaces by readiness level.

Use generated runtime docs for exact active capability truth.
Use this page for user-facing readiness expectations.

---

## Proven / Core Paths

| Area | Status | Notes |
|---|---|---|
| Chat / conversations | Proven core path | Core local assistant runtime is available. |
| Dashboard UI | Proven core path | Local dashboard surfaces exist, though polish is still evolving. |
| Runtime truth docs | Proven core path | Generated runtime state and capability references exist. |
| Research / summaries | Proven core path | Primary read-oriented assistant value. |
| Trust receipts API | Proven core path | `/api/trust/receipts` exposes recent governed-action receipt events from the ledger. |

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
| Email draft | Implemented, safety-limited | Opens a local mail client draft through `mailto:`. Nova does not use SMTP, access inboxes, or send autonomously. |
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
| Cap 64 live lock | Ready for human P5 | Automated checks are strong, but local mail-client live proof is still a human step before lock. |
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
