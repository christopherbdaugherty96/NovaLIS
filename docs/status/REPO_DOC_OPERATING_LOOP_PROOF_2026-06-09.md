# Repo-Doc Operating Loop Proof - 2026-06-09

Status: docs-only operating-loop proof.

Scope: prove the reviewed repo-document workflow without expanding Nova runtime
authority.

## Purpose

This note records the narrow operating loop for repo-document work:

```text
approved repo-doc update
-> branch
-> PR
-> checks
-> review
-> merge decision
-> continuity handoff
```

The proof is intentionally limited to repository documentation. It does not
start runtime implementation, Obsidian automation, Shopify automation, OpenClaw
execution, scheduler work, browser/computer-use expansion, or capability
changes.

## Proof Object

This document is the repo-doc update used for the proof.

It is safe because it changes only reviewed documentation and generated
navigation, if regeneration is required. It does not change code paths that can
execute actions.

## Operating Loop

1. Human approval defines a narrow repo-doc objective.
2. Codex creates a scoped branch from current `main`.
3. Codex edits only the approved repo-doc surface.
4. Codex runs relevant local validation.
5. Codex opens a PR with the exact scope and safety boundary.
6. GitHub checks provide CI evidence.
7. Human review decides whether to merge.
8. After merge, the next lane is selected explicitly.

## Authority Boundary

```text
Repo docs can describe scope.
Repo docs can record decisions.
Repo docs can link evidence.
Repo docs cannot authorize execution.
```

Execution authority remains governed by:

```text
human approval
Nova governance
capability registry and locks
GovernorMediator
execution boundary
receipts and logs
```

Obsidian remains:

```text
context
navigation
memory
planning
```

Obsidian does not authorize execution.

## Not Authorized By This Proof

This proof does not authorize or implement:

```text
runtime behavior changes
capability_locks.json changes
GovernorMediator changes
Shopify writes or commerce mutation
OpenClaw integration or expansion
browser/computer-use expansion
scheduler or background loops
external writes
memory promotion
Second Brain implementation
Obsidian execution authority
```

## Required Evidence

The PR for this proof should show:

```text
branch name
files changed
local validation commands
GitHub check results
scope confirmation
safety confirmation
remaining follow-up, if any
```

## Success Criteria

The proof passes when:

```text
the diff stays docs/navigation scoped
checks pass or any failure is classified without expanding scope
the PR body records the proof evidence
human review can decide from the record
no runtime authority is added
```

## Final Rule

```text
Obsidian ranks and navigates reality.
GitHub records reviewed project truth.
Nova governance controls execution authority.
Notes do not grant permission.
```
