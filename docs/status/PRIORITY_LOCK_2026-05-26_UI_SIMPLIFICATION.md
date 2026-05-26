# UI Simplification Priority Lock — Product Clarity Slice

Locked: 2026-05-26

---

## 1. Current truth

```text
Goal Card persistence is complete end to end (PRs #229-#232).
All four certified capabilities locked (Cap 16, 22, 64, 65).
Goal Cards remain display-only and non-executing.
Open PRs: 0 (at time of lock).
Open issues: 6 total, all planning/future/backlog.
No execution authority has expanded.
```

## 2. Problem

The Nova dashboard has grown organically across certification,
reliability, and Goal Card workstreams. The result:

```text
- 11 navigation items with no grouping or priority
- Internal jargon visible to users ("governed", "bounded",
  "proof-tracked", "metered")
- Unclear distinction between what Nova can do vs. what is
  future/planning
- Goal Card purpose not immediately obvious to new users
- Trust/receipt surfaces exist but are not easy to find
- Some page headers use developer language, not user language
```

## 3. Goal

Make the existing dashboard easier to understand without
expanding authority:

```text
- What Nova can do now
- What Nova cannot do
- What Goal Cards are (and are not)
- Where trust/receipts/proof live
- What is display-only vs. executable
- What is current vs. future/planning
```

## 4. Authorized scope

```text
- Rename confusing labels to user-facing language
- Reduce duplicate or overly technical wording
- Improve page headers and section descriptions
- Make display-only / no-execution boundaries clearer
- Improve Goal Card empty/loading/fallback copy
- Improve trust/receipt discoverability via labels or links
- Improve current vs. future distinction
- Reduce visual clutter
- Keep existing UI architecture
- Keep frontend mirror synced (nova_backend/static ↔
  Nova-Frontend-Dashboard)
```

## 5. Explicit non-goals

```text
- New backend APIs
- New storage or data formats
- New capability IDs
- Goal Card execution, scheduler, or click-to-run
- GovernorMediator changes
- OpenClaw integration
- capability_locks.json changes
- Broad redesign or new page architecture
- Fake maturity claims about trust system
```

## 6. Authority boundary

This slice improves clarity only.
This slice does not authorize execution.
This slice does not authorize scheduling.
This slice does not authorize new capabilities.
This slice does not authorize GovernorMediator changes.
This slice does not authorize OpenClaw integration.
This slice does not authorize Goal Card Phase 4.
Goal Cards remain display-only.
DISPLAY ONLY badge must remain visible.
Trust/receipts may be made easier to find, but trust surfaces
must not be overstated as complete mature trust system unless
runtime truth supports it.

## 7. Files allowed to change

```text
nova_backend/static/index.html
nova_backend/static/dashboard.js
nova_backend/static/dashboard-chat-news.js
nova_backend/static/dashboard-config.js
nova_backend/static/style.phase1.css
Nova-Frontend-Dashboard/index.html
Nova-Frontend-Dashboard/dashboard.js
Nova-Frontend-Dashboard/dashboard-chat-news.js
Nova-Frontend-Dashboard/dashboard-config.js
Nova-Frontend-Dashboard/style.phase1.css
```

Not allowed to change:

```text
nova_backend/src/**
capability_locks.json
GovernorMediator / ExecuteBoundary / CapabilityRegistry
OpenClaw runtime
Goal persistence backend (goal_store.py, goals_api.py)
```

## 8. Test / verification requirements

```text
- DISPLAY ONLY badge remains present in HTML
- No forbidden execution labels introduced:
  /run, /execute, /schedule, click-to-run, scheduler,
  automation start
- Goal Card wording still says display-only / no execution
- Fallback notice remains in source
- No GovernorMediator / OpenClaw strings in Goal Card frontend
- Frontend mirror files are synced
- Manual browser verification of all pages
```

## 9. Exit criteria

```text
- Dashboard is noticeably clearer to a new user
- No authority expansion
- All existing functionality preserved
- Frontend mirror synced
- PR opened with explicit boundary statement
```

## 10. Final verdict

```text
This is a clarity-only slice. It improves labels, copy, and
discoverability. It does not expand what Nova can do. It does
not touch backend, governance, capabilities, or execution.
Goal Cards remain display-only. DISPLAY ONLY badge remains.
```
