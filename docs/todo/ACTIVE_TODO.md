# Active TODO - Nova

Last reviewed: 2026-05-25 (post-PR #231)

---

## Current Active Task

```text
Phase: Goal Card persistence / frontend wiring.
Goal Card local display-state: COMPLETED (PR #229, 2026-05-23).
Goal Card UX polish: COMPLETED (PR #230, 2026-05-24).
Goal Card persistence design doc: COMPLETED (2026-05-24).
Goal Card persistence Phase 2 backend: COMPLETED (PR #231, 2026-05-25).
  Local JSON goal store + CRUD API. 73 boundary tests.
  No execution authority. No scheduler. No GovernorMediator changes.

Next: Phase 3 — wire frontend Goal Cards to /api/goals.
  Remove DEMO_GOAL_CARDS. Keep localStorage for UI prefs only.
  Preserve DISPLAY ONLY. Add empty/error/loading states.
  No execution, no scheduler, no GovernorMediator integration.
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
frontend not wired to API yet (DEMO_GOAL_CARDS still in use)
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
   Frontend not wired to API yet. Still display-only.
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
Phase 3 — wire frontend Goal Cards to /api/goals.
  Fetch persisted goals from API.
  Remove DEMO_GOAL_CARDS.
  Keep localStorage for UI preferences only.
  Preserve DISPLAY ONLY badge.
  Add empty/error/loading states.
```

Important boundary:

```text
Goal persistence != execution authority
Goal Card != scheduler
Goal Card != action engine
frontend wiring != execution wiring
```

Strict limits:

```text
no backend execution
no scheduler
no GovernorMediator changes
no capability expansion
no autonomy
no automatic step advancement
no OpenClaw integration
```

Do not start next:

```text
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
Goal Card persistence design and backend are complete
(design doc + PR #231). Frontend API wiring is next.
Phase 3 wires the existing Goal Card UI to /api/goals.
No execution authority. No scheduler. No GovernorMediator changes.
```
