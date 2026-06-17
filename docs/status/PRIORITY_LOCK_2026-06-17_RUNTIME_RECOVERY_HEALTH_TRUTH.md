# Runtime Recovery And Health Truth Priority Lock - 2026-06-17

Status: proposed next product lane.

Scope: make Nova fail clearly when the local runtime stalls, without adding
new capabilities or broad UX redesign.

## Product Signal

The latest deeper browser/computer-use product pass found the clearest current
trust gap:

```text
Nova can look alive while the local runtime is not actually responding.
```

Observed user-facing state:

```text
UI still visible
buttons still visible
pages still visible
status says CONNECTING
Trust can still imply Normal
local APIs time out
chat can remain stuck
```

This creates the highest-risk product state:

```text
The system looks usable, but the user cannot tell whether it actually is.
```

## Decision

The next highest-value product lane is:

```text
P1: Runtime recovery and health truth.
```

This supersedes broad UX cleanup as the immediate product priority.

The core question for this lane:

```text
When Nova stalls, does the user know what happened and what to do?
```

Current answer:

```text
Not reliably.
```

## Allowed Scope

This lock allows a focused future implementation PR for:

```text
canonical health truth
runtime timeout/degraded/unavailable status modeling
stuck-response detection and user-facing recovery copy
chat/action timeout recovery affordances
Trust explanation of product failures, not only governed receipts
tests proving stale/timeout health cannot be shown as Normal
tests proving no execution authority is added
```

User-facing recovery copy should answer:

```text
What happened?
Did anything run?
Did anything leave my device?
Is Nova healthy?
What can I do next?
```

Example stuck-response state:

```text
Nova is taking longer than expected.
Your request may not have completed.
Nothing new was confirmed.
[Retry] [Check status]
```

Example backend-unreachable state:

```text
Nova's local runtime is not responding.
The page is still open, but requests are timing out.
Try restarting Nova or checking status.
```

## Canonical Health States

The future implementation should converge pages onto one health truth model:

```text
Connected
Connecting
Degraded
Unavailable
Timed out
Recovering
```

No page should report:

```text
Failure state: Normal
```

while local API probes are timing out or core runtime health is stale.

## Explicit Non-Goals

This lock does not authorize:

```text
Plan My Week
model presets
more agents
more providers
bigger dashboard redesign
advanced navigation cleanup
empty-state simplification as a broad lane
Second Brain implementation
browser/computer-use expansion
OpenClaw expansion
GovernorMediator changes unless strictly needed for read-only health truth
CapabilityRegistry changes
ExecuteBoundary changes
capability_locks.json changes
scheduler or background loops
external writes
Shopify writes
Gmail/calendar writes
autonomous workflow execution
```

## Priority Stack

Current product priority order:

```text
P1: Runtime recovery and health truth
P2: First-run simplification
P3: Status/trust surface consolidation
P4: Advanced navigation hiding
P5: Empty-state simplification
```

Only P1 is authorized by this lock.

## Authority Boundary

Recovery visibility is not execution authority.

This lane may make runtime health clearer, make stalls visible, and help the
user choose a recovery step. It must not cause Nova to execute, retry, repair,
restart, or mutate anything silently.

Any recovery action with side effects must remain explicit and user-visible.

## Success Criteria

The future implementation PR should prove:

```text
stuck chat/action states become visible before user trust collapses
backend timeout/unreachable states are reflected in canonical health truth
Trust explains product/runtime failures even when no governed action ran
no stale timeout state is shown as Normal
the user receives a clear next step
no new execution capability is added
no autonomous recovery action is introduced
```

## Final Rule

```text
The next product improvement is not making Nova do more.
It is making Nova fail clearly.
```
