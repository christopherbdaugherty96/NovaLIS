# Active TODO - Nova

Last reviewed: 2026-05-26 (post-PR #234)

---

## Current Active Task

```text
Phase: Goal Card persistence complete through Phase 3 (2026-05-26).
Goal Card local display-state: COMPLETED (PR #229, 2026-05-23).
Goal Card UX polish: COMPLETED (PR #230, 2026-05-24).
Goal Card persistence design doc: COMPLETED (2026-05-24).
Goal Card persistence Phase 2 backend: COMPLETED (PR #231, 2026-05-25).
  Local JSON goal store + CRUD API. 73 boundary tests.
  No execution authority. No scheduler. No GovernorMediator changes.
Goal Card Phase 3 frontend wiring: COMPLETED (PR #232, 2026-05-26).
  Frontend fetches from /api/goals. Fallback to demo data with
  visible notice. Loading state. DISPLAY ONLY preserved.
  No execution authority. No GovernorMediator changes.
UI simplification slice: COMPLETED (PR #233, 2026-05-26).
  Priority lock and UI audit landed.
  Dashboard clarity improved without authority expansion.
  Activity & Receipts terminology restored.
  Runtime Permissions and bounded OpenAI lane wording preserved.
  Frontend mirror synced. UI boundary tests hardened.
  No backend runtime/governance changes.
Second Brain Slice 1 priority lock: ACCEPTED (PR #234, 2026-05-26).
  Lock-only. No implementation code.
  Next authorized implementation PR is schema/parser/wikilink/vault lint/no-mutation tests only.
  No vector DB, MCP, dashboard graph, memory promotion, proposal writes,
  execution integration, scheduler, OpenClaw integration, or capability expansion.

Goal Card persistence is complete. Phase 4 (execution envelopes)
requires a separate design doc and is not authorized.
Dashboard clarity is improved. Goal Cards remain display-only.
Second Brain Slice 1 priority lock is accepted.
```

Current lock truth:

```text
Cap 16 — locked (2026-05-10) — governed_web_search
Cap 22 — locked (2026-05-20) — open_file_folder
Cap 64 — locked (2026-05-20) — send_email_draft
Cap 65 — locked (2026-05-22) — shopify_intelligence_report (read-only)
```

Important discipline:

```text
active != certified != locked
```

Most active capabilities are not certification-locked.

---

## Recently Closed Cleanup / Hardening Lanes

```text
#220 — open issue accounting fixed
#221 — security scan #163 verified and closed
#222 — certification directory guards fixed
#223 — #143 session-state ambient context guard tested and closed
#224 — #142 capability help frontend collapse fixed and closed
#225 — #214 deterministic continuity investigation documented
#226 — preamble-tolerant routing fixed
#214 — closed and reclassified
#227 — opened as hardware/model throughput backlog
```

Additional completed lanes:

```text
Everyday live-session reliability hardening — complete (2026-05-19).
Approval-gate certification closeout — certified (2026-05-19).
Conversation quality tuning — complete (2026-05-20).
Cap 65 P5 live proof — complete and locked (2026-05-22).
```

---

## Current Open Issues

There are currently no active implementation follow-up issues.

Open issues are planning/future/backlog only:

```text
#67  — planning/future: agent workspaces + Google email/calendar coordination
#71  — planning/future: governed local memory workspace
#73  — planning/future: governed learning layer
#74  — planning/future: Brain matrix / Daily Brief boundary
#189 — planning/future: ecosystem simulation / operator proof / advisory layer
#227 — backlog: local LLM throughput on 8GB CPU-only hardware
```

---

## Current Product Truth

Nova is not product-complete.

Current accurate state:

```text
clean governed runtime baseline
locked core capabilities
honest visible Goal Card surface
remaining conversational weakness isolated to hardware/model throughput
```

Goal Cards are currently:

```text
visible
display-only
non-executing
not scheduled
persistence-backed (PR #231, local JSON + CRUD API)
frontend wired to API (PR #232, fetches from /api/goals)
fallback to demo data with visible notice when API unreachable
dashboard clarity improved (PR #233 UI simplification)
  clearer Goals copy, cleaner nav hierarchy, Activity & Receipts
  terminology, Runtime Permissions, bounded OpenAI lane
```

---

## Remaining Known Gaps

```text
1. Local LLM throughput
   Tracked by #227. Current 8GB CPU-only hardware limits conversational continuity.

2. Goal Cards
   PR #229 completed interactive display-state.
   PR #230 completed UX polish.
   PR #231 completed backend persistence (local JSON + CRUD API).
   PR #232 completed frontend API wiring.
   PR #233 completed UI simplification/product clarity.
   Persistence complete end to end. Still display-only.
   No scheduler or governed execution envelope.

3. Memory / learning
   Planning/future only. Memory cannot authorize execution.
   Learning cannot become silent authority.

4. Google / workspace connectors
   Planning/future only. Read-only and draft-only surfaces must come
   before writes.

5. Trust / receipt maturity
   Existing trust surfaces must not be overstated as a complete mature
   trust system unless runtime truth and proof docs support it.

6. OpenClaw
   Runtime systems exist, but OpenClaw is not broadly autonomous or
   fully certified.
```

---

## Recommended Next Safe Product Move

```text
Goal Card persistence is complete through Phase 3.
UI simplification slice is complete.
Second Brain Slice 1 priority lock is accepted.
Phase 4 (execution envelopes) requires a separate design doc
and is not authorized.

Next authorized implementation PR:
  - Second Brain Slice 1: schema/parser/wikilink/vault lint/no-mutation tests only
```

Important boundary:

```text
Goal persistence != execution authority
Goal Card != scheduler
Goal Card != action engine
```

Do not start next:

```text
Goal Card execution or click-to-run
Shopify writes
Printify automation
Gmail send
Google Calendar writes
phone/SMS control
browser/computer-use
autonomous routines
OpenClaw freeform execution expansion
memory auto-promotion
learning-based permission
background task loops
```

---

## Final Operational Direction

```text
Goal Card persistence is complete end to end (design doc +
PR #231 backend + PR #232 frontend wiring). UI simplification
is complete (PR #233). Dashboard clarity improved without
authority expansion. Goal Cards remain display-only. No
execution, no scheduler, no GovernorMediator changes. Second
Brain Slice 1 priority lock is accepted (PR #234). Next
implementation PR is limited to schema, parser, wikilink
extraction, vault health/lint, and non-authorizing/no-mutation
tests only.
```
