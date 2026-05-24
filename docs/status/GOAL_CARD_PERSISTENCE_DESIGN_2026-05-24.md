# Goal Card Persistence Design — 2026-05-24

Status:

```text
design doc only — no runtime changes yet
```

---

## Problem

Goal Cards currently render from a hardcoded `DEMO_GOAL_CARDS` array
in `dashboard.js`. The display-state layer (PR #229) added
expand/collapse, filtering, sorting, and progress bars backed by
`localStorage` — but localStorage stores only UI preferences
(which cards are expanded, current sort mode, active filter).

The actual goal data — titles, steps, statuses, permission envelopes,
receipts — has no persistence. If the demo array changes, all
goal state resets. There is no way for Nova to create, update, or
archive a goal across sessions.

This means Goal Cards cannot yet show real work in progress. They
demonstrate the governed workflow surface but do not track anything.

---

## What persistence means here

Persistence means saving goal state so it survives page reloads
and server restarts. It does not mean any of the following:

```text
persistence != execution
persistence != scheduling
persistence != automation
persistence != background processing
persistence != authority expansion
```

A persisted goal is a saved record of intent and progress.
It is not a task queue. It is not a scheduler input.
It is not an action trigger.

---

## Proposed design

### Storage location

```text
Local JSON file: nova_backend/data/goals.json
```

Not a database. Not an external service. A single JSON file on disk
that the backend reads on startup and writes when goal state changes.

Rationale:

```text
- Nova is a local-first platform
- No external dependencies
- Human-inspectable (open the file, read the goals)
- Git-ignorable (goal state is personal, not repo state)
- Simple enough that the persistence layer cannot hide authority
```

### Data model

The persisted schema matches the current `DEMO_GOAL_CARDS` shape
with minimal additions:

```json
{
  "version": 1,
  "goals": [
    {
      "goal_id": "goal_auralis_launch_001",
      "title": "Prepare Auralis Shopify launch",
      "status": "planning",
      "created_at": "2026-05-22T12:00:00Z",
      "updated_at": "2026-05-22T14:30:00Z",
      "steps": [
        {
          "step_id": "step_001",
          "title": "Run read-only Shopify intelligence report",
          "status": "completed",
          "required_capability": 65,
          "approval_required": false
        }
      ],
      "permission_envelope": {
        "allowed_capabilities": [
          { "id": 16, "name": "Web search" }
        ],
        "blocked_actions": ["Shopify writes"],
        "requires_confirmation": [22, 64]
      },
      "ledger_refs": [
        {
          "type": "ACTION_COMPLETED",
          "capability_id": 65,
          "summary": "Shopify intelligence report (read-only)"
        }
      ]
    }
  ]
}
```

Key constraints:

```text
- version field for future schema migration
- no execution_schedule field
- no trigger field
- no automation_config field
- no background_run field
- ledger_refs are references to existing receipts, not new authority
```

### Read path

```text
1. Server starts → reads goals.json (or creates empty default)
2. Dashboard loads → fetches /api/goals (GET, read-only)
3. Frontend renders Goal Cards from API response
4. DEMO_GOAL_CARDS removed — real data replaces demo data
```

### Write path

```text
1. Goal created/updated from explicit user request or
   user-visible conversation context
2. GovernorMediator is NOT involved (goals are not capabilities)
3. Goal state written to goals.json via a simple file write
4. Frontend polls or receives WebSocket push for updated goals
5. No execution happens as a result of the write
```

Clarifying rule:

```text
Conversation-created goal updates are record updates only.
They may be initiated by explicit user request or by
user-visible workflow state changes.
They cannot be inferred silently as autonomous work.
```

Important: the write path saves state. It does not dispatch actions.
A goal moving from "planning" to "ready" does not trigger execution.
A step moving to "completed" records that something already happened
through the normal governed capability path — it does not cause it
to happen.

### What the API exposes

```text
GET  /api/goals          → list all goals
GET  /api/goals/:id      → single goal detail
POST /api/goals          → create a new visible goal record
                            from explicit user/conversation context
PUT  /api/goals/:id      → update goal state (status, steps)
```

What the API does NOT expose:

```text
POST /api/goals/:id/run      → does not exist
POST /api/goals/:id/execute  → does not exist
POST /api/goals/:id/schedule → does not exist
DELETE /api/goals/:id        → not in initial scope
```

---

## Scope constraints

```text
Persistence applies ONLY to:
  - goal metadata (title, status, timestamps)
  - step state (which steps exist, their status)
  - permission envelope (what is allowed/blocked for this goal)
  - ledger references (pointers to existing receipts)

Persistence does NOT provide:
  - execution authority
  - scheduled runs
  - background processing
  - automatic step advancement
  - capability invocation
  - GovernorMediator bypass
  - action dispatch
```

---

## Authority boundary

The persistence layer must not create a path from "goal exists"
to "action happens." The only path to action remains:

```text
user request → session handler → GovernorMediator → capability
  → approval gate (if confirmation-required) → executor → ledger
```

A persisted goal can be updated as a side effect of this path
(e.g., "step completed" after a governed action succeeds), but
the goal itself never initiates the path.

```text
goal → action:  PROHIBITED
action → goal update:  ALLOWED (record-keeping only)
```

---

## What changes in the frontend

```text
1. DEMO_GOAL_CARDS array removed
2. Goal Cards fetched from /api/goals on page load
3. Goal Card display-state (expand, filter, sort) stays in localStorage
4. Goal Card data comes from the API, not hardcoded JS
5. DISPLAY ONLY badge remains until execution envelopes exist
```

---

## What does NOT change

```text
- GovernorMediator: no changes
- CapabilityRegistry: no changes
- capability_locks.json: no changes
- ExecuteBoundary: no changes
- Approval gates: no changes
- Ledger: no changes
- Trust surfaces: no changes
- OpenClaw: no changes
```

---

## Migration path

```text
Phase 1 (this design doc): define boundaries
Phase 2 (next PR): implement read/write API + goals.json
Phase 3 (later): wire frontend to API, remove DEMO_GOAL_CARDS
Phase 4 (much later, separate design): execution envelopes
```

Phase 4 requires its own design doc and is not authorized by this
document. This design doc authorizes persistence only.

---

## Testing requirements

```text
1. Goal CRUD works (create, read, update)
2. goals.json survives server restart
3. No GovernorMediator calls from goal persistence code
4. No capability invocations from goal persistence code
5. No ledger writes from goal persistence code
6. API does not expose /run, /execute, or /schedule endpoints
7. Frontend renders persisted goals identically to demo goals
```

---

## Invariants

```text
1. Saving a goal never executes an action.
2. Loading a goal never executes an action.
3. Updating a goal status never executes an action.
4. Goal persistence code never imports GovernorMediator.
5. Goal persistence code never imports any executor.
6. Goal persistence code never calls the ledger.
7. The word "schedule" does not appear in goal persistence code.
8. DISPLAY ONLY badge remains on the Goals page.
```

---

## Verdict

```text
This design doc authorizes:
  - local file persistence for goal state
  - read/write API endpoints for goal CRUD
  - frontend migration from demo data to API data

This design doc does NOT authorize:
  - execution
  - scheduling
  - background processing
  - capability expansion
  - GovernorMediator changes
  - authority of any kind

Design doc before code. Boundaries before features.
```
