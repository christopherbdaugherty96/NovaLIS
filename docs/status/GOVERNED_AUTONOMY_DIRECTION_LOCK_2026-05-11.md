# Governed Autonomy Direction Lock

**Date:** 2026-05-11
**Status:** DIRECTION LOCK — planning / governance doctrine
**Scope:** NovaLIS autonomous workflow direction, OpenClaw agent direction, future autonomy envelope design

This document records Christopher's direction that autonomous agents and autonomous workflows are allowed in Nova only as governed autonomy.

This is not a runtime permission grant. It does not approve the current OpenClaw freeform goal execution path. It does not add capabilities, expand OpenClaw, approve external writes, or authorize autonomous execution outside the Governor-mediated path.

---

## Primary Direction

```text
Autonomous agents may be allowed in Nova only as governed autonomy.

Autonomy is not authority.
Agents may plan, monitor, coordinate, and continue bounded work inside explicit missions.
All real actions remain governed, visible, bounded, reviewable, and interruptible.
```

Nova should not become an unbounded agent runner. Nova should become a governed local-first mission system where autonomous workflows can operate only inside approved envelopes.

---

## Core Rule

```text
Agent autonomy = permission to continue reasoning or coordinating inside a bounded mission.
Execution authority = still belongs to the Governor and the user.
```

Autonomous workflow support must preserve Nova's central invariant:

```text
Intelligence is not authority.
```

---

## Required Execution Shape

Approved future shape:

```text
User-approved objective
  -> Governor-approved autonomy envelope
  -> bounded agent loop
  -> tool/action proposal
  -> GovernorMediator / CapabilityRegistry / ExecuteBoundary
  -> confirmation gate where required
  -> NetworkMediator where applicable
  -> ledger / receipt
  -> stop condition, budget exhaustion, or human interruption
```

Disallowed shape:

```text
User gives broad goal
  -> LLM chooses tools from full registry
  -> executor.execute()
```

---

## Required Autonomy Envelope Fields

Every autonomous mission must have explicit limits before execution:

- objective
- mission type
- allowed tools
- denied tools
- allowed capability IDs, if applicable
- denied capability IDs, if applicable
- max steps
- max runtime
- max network calls
- max file reads
- max file writes
- external write policy
- confirmation policy
- stop conditions
- cancellation path
- receipt/logging path
- user-visible status

Read-only must be the default.

Mutation-capable tools must be denied unless the envelope explicitly allows them and the action still routes through the governed capability path.

---

## Autonomy Tiers

### Tier 1 — Read-only autonomous missions

Allowed:

- inspect repo/docs
- summarize
- compare status
- search approved sources
- produce audit reports
- produce recommendations
- prepare patch roadmaps

Blocked:

- runtime edits
- external writes
- tool mutation
- system setting changes
- publishing
- sending
- scheduling recurring jobs

Recommended first mission type:

```text
Repo Guardian Mission
```

Purpose:

```text
Watch current Nova work for governance drift, stale docs, unsafe authority expansion, and missing tests.
Produce reports and patch recommendations only.
```

### Tier 2 — Draft-only autonomous missions

Allowed:

- draft email
- draft calendar event
- draft GitHub issue
- draft PR body
- draft roadmap update
- draft Shopify/POD plan
- draft social post

Blocked:

- send
- publish
- merge
- schedule externally
- buy
- delete
- modify system settings

### Tier 3 — Confirmed-action missions

Allowed only after explicit envelope approval and per-action governance where needed:

- create local file within allowed branch/scope
- create GitHub issue/PR if explicitly allowed
- apply Gmail label after connector approval exists
- create calendar event after connector approval exists
- open website after governed capability path approval
- adjust local settings only through governed capability path

### Tier 4 — Routine agents

Future only.

Examples:

- Daily Nova Review Agent
- Repo Guardian scheduled check
- Creator Business Intelligence Brief
- Inbox/Calendar Coordination Board

Routine agents require:

- explicit schedule
- visible status
- bounded budget
- reviewable output
- no silent external writes
- stop/pause/cancel
- receipts

---

## Current Runtime Boundary

As of PASS4 OpenClaw inspection:

```text
The current OpenClaw freeform goal path is not governance-safe.
```

Reason:

- `run_goal()` exposes full ToolRegistry to ThinkingLoop
- mutation-capable tools are reachable
- `ExecutorSkillAdapter` calls executor directly
- the path does not traverse GovernorMediator, Governor, CapabilityRegistry, SingleActionQueue, or ExecuteBoundary
- `/api/openclaw/approve-action` auto-allows and is not wired into execution

Therefore:

```text
Current freeform OpenClaw execution is not approved as the governed autonomy model.
```

---

## Required Immediate Safety Patch

PATCH A from PASS4 remains required before any autonomy implementation work resumes:

```text
Allowlist enforcement in run_goal() / ThinkingLoop.
```

Minimum requirement:

- exclude mutation-capable tools from freeform goal execution
- exclude `volume`, `brightness`, `media`, `open_webpage`, and `screen_capture`
- allow read-only/informational tools only
- add tests proving mutation-capable tools are not offered or executed

This is containment, not expansion.

---

## Product Direction

The recommended long-term product surface is:

```text
Nova Mission Control
```

Mission Control should let Christopher start and monitor bounded autonomous missions with visible constraints:

- goal
- allowed tools
- denied tools
- budgets
- risk tier
- live log
- proposed actions
- approval requests
- final receipt

First realistic mission:

```text
Repo Guardian Mission — read-only audit agent for Nova work.
```

Second realistic mission:

```text
Creator Business Intelligence Mission — read-only Shopify/POD opportunity report.
```

Third realistic mission:

```text
Daily Operating Brief Mission — read-only morning brief with proposed actions only.
```

---

## Non-Goals

This lock does not authorize:

- unbounded autonomous agents
- persistent hidden agents
- recursive agent chains
- cross-model self-delegation loops
- direct executor calls
- bypassing GovernorMediator
- bypassing CapabilityRegistry
- bypassing ExecuteBoundary
- mutation-capable freeform tool execution
- external writes without confirmation
- Shopify writes
- email sending
- social posting
- finance automation
- Google connector runtime implementation
- Cap 64 P5
- UI simplification
- browser/computer-use expansion

---

## Correct Next Sequence

1. Merge PASS4 audit doc.
2. Implement PATCH A as a narrow containment patch.
3. Add tests proving mutation-capable tools are unavailable in freeform goal mode.
4. Only then design the governed autonomy envelope.
5. Start with Tier 1 read-only missions.
6. Add draft-only missions later.
7. Add confirmed-action missions only after envelope, approval, and receipt surfaces are proven.

---

## Final Lock Statement

```text
Nova may support autonomous workflows, but only as governed autonomy.

Autonomous agents may continue bounded work, but they do not gain execution authority.
Every real action must remain Governor-mediated, bounded, visible, reviewable, interruptible, and receipted.

The current unmediated OpenClaw freeform goal path is not approved as-is.
```