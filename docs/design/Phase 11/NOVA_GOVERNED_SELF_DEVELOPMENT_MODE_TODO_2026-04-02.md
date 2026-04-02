# Nova Governed Self-Development Mode TODO
Date: 2026-04-02
Status: Future design backlog
Scope: Define a safe path for Nova to inspect its own codebase, propose bounded improvements, and apply approved changes without collapsing authority boundaries

## Core Rule
Nova may analyze itself broadly, but modification must remain narrow.

The target is not free self-modification.

The target is governed self-development:
- inspect the repo
- identify missing capability or wiring gaps
- produce a visible change plan
- generate a bounded patch
- run validation
- require explicit approval before promotion

## Why This Belongs In The Roadmap
This fits Nova's architecture unusually well because the repo already centers:
- explicit capability boundaries
- runtime truth
- authority classes
- governance and ledger surfaces
- visible user approval gates

If done correctly, self-development becomes a strength of the product rather than a trust failure.

## Product Position
Nova should be allowed to say:
- this capability does not currently exist
- it appears feasible
- it seems consistent with Nova's constitutional scope
- I can draft the implementation plan
- I can prepare a patch for your approval

Nova should not be allowed to:
- decide its own roadmap
- expand its own authority without explicit approval
- add, enable, and immediately use a new capability in one loop
- silently self-upgrade into production

The line to preserve is:
- implementation improvement can be governed
- constitutional authority expansion must stay explicit

## Four-Layer Model
### 1. Self-Analysis
Nova may:
- read its own repo
- inspect capabilities, registry entries, tests, docs, and runtime truth
- detect missing wiring, stale docs, incomplete paths, broken references, and feature gaps
- compare a user request against current implementation
- produce a structured gap report

### 2. Change Proposal
Before any write path, Nova should produce a visible artifact containing:
- what is missing
- whether the work is feasible
- which files would change
- why those files
- expected capability or architecture impact
- risk class
- whether the work is a bug fix, completion, refactor, or new capability
- exact execution plan

### 3. Governed Code Editing
Only after explicit approval, Nova may:
- modify allowed files in an approved workspace
- create files in approved directories
- run formatting, linting, and tests
- generate a patch, branch, or PR draft
- summarize results, diffs, and failures

### 4. Human Gate Before Promotion
Even after editing, Nova should not silently promote changes.

Promotion flow should remain:
1. analyze
2. propose
3. patch
4. run tests
5. show diff
6. receive approval
7. commit to branch
8. optionally open PR
9. optionally merge after review

## Missing-Capability Handling Contract
When a user asks for something Nova cannot yet do, the governed sequence should be:
1. check the current capability registry and runtime wiring
2. state clearly that the capability is not currently implemented
3. estimate feasibility
4. explain whether it appears to fit constitutional scope
5. determine whether the gap is missing wiring or a truly new capability
6. ask permission to enter Self-Development Mode for that task
7. generate the implementation plan, affected files, patch preview, and tests
8. wait for approval before writing
9. run validation and show the outcome
10. wait for merge or promotion approval

This sequence must replace the dangerous pattern:
- "I couldn't do X, so I added X, enabled X, and then did X."

## Mode Contract
Self-Development Mode should be explicit and separately governed.

When enabled explicitly, Nova may:
- inspect the repo
- diagnose missing features
- draft patches
- write code only inside an approved repo
- touch only allowlisted paths
- run only allowlisted commands

When enabled explicitly, Nova still may not:
- merge or deploy automatically
- alter Governor rules casually
- relax policy boundaries to make future edits easier
- create hidden self-improvement loops

## File Allowlist Tiers
### Tier 1 - safe-ish
- docs
- tests
- non-governance UI files
- renderer and formatter components
- capability stubs
- prompts
- runbooks

### Tier 2 - guarded
- executor implementations
- capability registry
- repo analysis tools
- adapters and integrations

### Tier 3 - restricted
- Governor
- policy validator
- ledger writer
- execution boundary
- permission model
- the self-development system itself

Tier 3 should require a higher approval class or remain blocked by default.

## Capability Family Direction
A future capability family could be split into separate authority levels:
- `self_inspect_repo`
- `self_gap_analysis`
- `self_generate_patch`
- `self_apply_patch`
- `self_run_validation`
- `self_open_pr`

Recommended classification direction:
- read-only self-analysis: lower authority
- patch generation: medium authority
- patch application: higher authority
- promotion, merge, or deploy: highest authority

## Strong Safety Rules
The system should enforce:
- patch-first, not direct-write-first
- explicit diff visibility
- branch or patch bundle output
- reversible workflow
- audit clarity at every step
- no hidden background self-improvement
- no automatic capability expansion
- no automatic enablement of newly added authority

## Best Near-Term Use
This is most valuable first as a governed developer-assist lane for:
- finishing incomplete capabilities
- fixing bounded bugs
- improving prompts and docs
- refining UI surfaces
- adding tests
- repairing missing wiring

This should not become a back door for:
- new execution authority
- new automation powers
- new background behavior
- policy changes
- silent autonomy expansion

## Recommended Next Step
When this becomes active work, the first slice should be a design and governance packet, not implementation.

Best first deliverables:
1. define the Self-Development Mode contract
2. classify the capability family and authority classes
3. define allowlisted paths and command policies
4. define patch, test, and approval workflow artifacts
5. define explicit restrictions for governance-kernel files
6. add proof expectations before any runtime implementation begins

## Anchor Principle
Nova can read itself, understand its gaps, draft improvements, and apply them under explicit bounded permission.

Nova must not notice a gap and evolve itself whenever it wants.
