# Second Brain Slice 1 Foundation Activation - 2026-06-10

Status: docs-only lane activation.

Scope: explicitly choose Second Brain Slice 1 foundation as the next lane
without adding implementation code.

## Purpose

This note activates the previously accepted Second Brain Slice 1 priority lock
as the next planned lane.

Existing lock:

```text
docs/status/PRIORITY_LOCK_2026-05-26_SECOND_BRAIN_SLICE_1.md
```

This activation does not implement Second Brain Slice 1. It only confirms that
the next implementation PR, if opened, must stay within the existing lock.

## Current Decision

```text
Next lane: Second Brain Slice 1 foundation.
```

The next implementation PR may be prepared only after this activation is
reviewed and merged.

Recommended implementation PR title:

```text
feat: add second brain slice 1 vault metadata parser
```

## Allowed Implementation Scope

The future implementation lane is limited to:

```text
schema
frontmatter parser
wikilink extraction
vault health/lint
no-mutation tests
non-authorizing tests only
```

Equivalent lock language:

```text
KnowledgeEntry schema
Relationship schema
KnowledgeEvent schema
frontmatter parser
wikilink extraction
vault health/lint report
tests proving no mutation
tests proving knowledge cannot authorize execution
tests proving notes are context, not permission
```

Read-only file-derived scaffolding is allowed only if it remains deterministic,
rebuildable, deletable, and not a runtime authority source.

## Still Blocked

This activation does not authorize:

```text
runtime execution
memory promotion
scheduler or background loops
OpenClaw integration or expansion
Shopify writes or commerce mutation
browser/computer-use expansion
GovernorMediator changes
CapabilityRegistry changes
ExecuteBoundary changes
capability_locks.json changes
MCP tools
vector database
REST/API query surface
dashboard graph or living graph runtime
proposal writes
vault mutation or repair mode
Obsidian execution authority
external writes
```

## Authority Boundary

```text
Obsidian can help Nova understand.
Obsidian cannot authorize Nova to act.
Knowledge is context, not permission.
Notes are a knowledge source, not execution proof.
Read-only parsing is allowed.
Silent learning is prohibited.
Vault mutation is prohibited in Slice 1.
```

Execution authority remains governed by:

```text
human approval
Nova governance
capability registry and locks
GovernorMediator
ExecuteBoundary
receipts and logs
```

## Success Criteria For This Activation PR

```text
current priority points to Second Brain Slice 1 foundation
Daily Command Center names the chosen lane
current work status names the chosen lane
allowed and blocked scope are explicit
no implementation code is added
generated MOCs refresh if needed
checks pass
```

## Final Rule

```text
Activation chooses the lane.
Activation does not implement the lane.
Implementation remains a separate reviewed PR.
```
