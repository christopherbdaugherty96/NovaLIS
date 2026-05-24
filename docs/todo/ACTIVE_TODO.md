# Active TODO - Nova

Last reviewed: 2026-05-23 (post-PR #229)

---

## Current Active Task

```text
Phase: Observe and refine.
Goal Card local display-state: COMPLETED (PR #229, 2026-05-23).
Goal Cards are now interactive workflow visibility — still display-only.
No execution authority added. No backend persistence.

Use the system briefly. Observe friction. Then decide:
  - Goal Card UX polish
  - Goal Card persistence design doc
  - Second Brain Slice 1 planning
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
not persistence-backed yet
```

---

## Remaining Known Gaps

```text
1. Local LLM throughput
   Tracked by #227. Current 8GB CPU-only hardware limits conversational continuity.

2. Goal Cards
   Display-only. No local display-state wiring, persistence, scheduler,
   or governed execution envelope yet.

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
Goal Card local display-state wiring
```

Strict limits:

```text
frontend/local state only
no backend execution
no scheduler
no persistence unless separately designed
no GovernorMediator changes
no capability expansion
no autonomy
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
The repo is clean enough to stop cleaning and resume small product work.
The next work should make Goal Cards more usable without giving them authority.
```
