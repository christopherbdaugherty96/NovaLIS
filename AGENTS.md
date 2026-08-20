# AGENTS.md

Guidance for AI agents working on NovaLIS.

Start here before editing the repository.

## Core Rule

**Intelligence is not authority.**

Reasoning may clarify, plan, search, summarize, compare, and propose. Governed capability execution remains subject to Nova's authority and execution boundaries.

## Project Positioning

Nova is a governance-first local AI system that separates intelligence from execution authority.

Nova prioritizes visible authority boundaries, inspectable execution, and user-controlled AI operation.

Operational Continuity is strategic direction, not current runtime authority.

The separate August Product/Platform strategy and validation package is input to Wave A2. Wave A1 does not import or canonize that package's product doctrine.

## Read Order

Before selecting work, read:

1. `docs/CANONICAL/00_INDEX.md`
2. `docs/status/DAILY_COMMAND_CENTER.md`
3. `.agent_context/current_priority.md`
4. `docs/status/CURRENT_WORK_STATUS.md`
5. `docs/todo/ACTIVE_TODO.md`
6. `docs/capability_verification/CAPABILITY_INVENTORY.md`
7. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
8. `docs/CANONICAL/07_ROADMAP_TRUTH.md`

For exact runtime-existence claims, inspect code and the generated runtime surfaces that mechanically measure the relevant claim. Generated documents are authoritative only for the properties their generators actually inspect.

## Wave A1 Current Development State — 2026-08-20

Wave A1 is a documentation/truth-reconciliation lane.

The merged-main checkpoint used to start this lane is:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

That SHA is a planning checkpoint, not a permanent alias for `main`. Verify the actual current GitHub head before future work.

Merged stabilization work already includes:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session activity/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit weather-location repair / WebSocket preservation
#345         brightness outcome truth
#346         volume command wording/routing
#347         current-information freshness/source-boundary routing
#348         broad awareness follow-up interpretation
#349         Calendar source-selection overmatch repair
#350         Calendar tomorrow-scope preservation
#351         local schedule-cancellation routing
#352         private Drive source-selection truth
```

Do **not** select any of those as if they are still unimplemented.

PR #335 remains:

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Do not merge or extend PR #335 in its historical state. It is deferred until the stabilization checkpoint defined by Issue #343.

## Current Ordered Gate

The current sequencing is:

```text
Wave A1 — operational truth synchronization
-> Wave A2 — strategy reconciliation
-> Wave B — truth-integrity repairs
-> Wave C — proof / validated-baseline checkpoint
-> reconstruct/reconcile #335 onto the exact validated baseline
-> separate #335 review/merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

This is a stabilization gate around the existing roadmap. It is **not** a roadmap rewrite.

## Wave A1 Lock

Wave A1 may change operational/canonical documentation and Issue #343 only.

Wave A1 must not change:

```text
runtime behavior
runtime auditor
GeneralChat persistence behavior
self-awareness behavior
capability registry
Google #335 implementation
OAuth behavior
Operational Continuity runtime
OpenClaw authority
provider routing
capability authority
external-write behavior
```

## Permanent Control-Plane Distinction

Nova has three distinct control planes.

### 1. Governed capability plane

```text
User
-> GovernorMediator
-> Governor
-> CapabilityRegistry
-> SingleActionQueue
-> LedgerWriter
-> ExecuteBoundary
-> Executor
```

This is the authority path for governed capabilities.

### 2. Local operator / administrative plane

Settings, credentials, connections, provider/runtime configuration, and other local operator controls are not automatically governed capabilities. They must remain explicitly classified and must not silently increase capability authority.

### 3. Bounded agent / routine plane

OpenClaw/routine/scheduler envelopes may have constrained enforcement of their own. They must not silently inherit or increase Nova capability authority.

Permanent invariant:

> No control plane may silently increase the authority available to another control plane.

Permanent distinctions:

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
execution != verified outcome
memory != Operational Continuity
```

## Evidence Discipline

Do not collapse these evidence levels:

```text
exists
enabled
configured
available_on_this_path
request_accepted
effect_verified
verification_status
authority_class
```

`authorized` is not static capability metadata. Approval/authority is request-specific.

Do not infer that a generated PASS proves behavior the generator does not measure. Do not infer that a historical proof packet is current proof. Do not call a candidate baseline validated until the required Wave C proof package has completed.

## Continuity Boundary

Operational Continuity remains strategically accepted but implementation-inactive.

Continuity may preserve/reconcile/project state, but it may never:

- authorize;
- execute;
- change permission;
- manufacture commitments;
- silently reopen decisions;
- convert learned behavior into authority.

Detailed Product/Platform strategy and validation doctrine remain outside A1 and are handled, if adopted, in Wave A2.

## Required Context Before Brain/Governance Changes

Read:

- `docs/brain.md`
- `docs/brain/README.md`
- `.agent_context/brain_loop.md`
- `.agent_context/environments.md`
- `.agent_context/governance.md`
- `.agent_context/current_priority.md`

## Do Not

- bypass `GovernorMediator` for governed capability execution;
- treat memory, conversation context, recommendations, model confidence, OAuth scopes, or repeated success as permission;
- claim conceptual/strategy docs are implemented behavior;
- infer broad autonomy from OpenClaw runtime presence;
- expand Google domain-data access before the ordered gate permits it;
- use old PR test totals as proof of a reconciled branch;
- direct work from a stale `current`, `next`, or `active` statement without checking the current truth surfaces first.

## Repo Truth Rule

Code is authoritative for implemented behavior. Tests and proof artifacts are evidence for the revisions/environments/scopes they actually cover. Generated runtime surfaces are authoritative for the exact mechanically measured claims they report. Hand-maintained operational docs establish current ordering and interpretation, but may go stale and must be reconciled when the repository changes.
