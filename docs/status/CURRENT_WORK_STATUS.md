# Nova Current Work Status

Last reviewed: 2026-08-20.

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
WAVE A1 — operational truth synchronization
STATUS: IN PROGRESS on docs-only branch
BRANCH: codex/wave-a1-operational-truth-sync-20260820
MERGED-MAIN CHECKPOINT AT START: 1a517d8832a2c834c80b10a7062bed878f6312cc
```

The checkpoint SHA records what A1 was based on. It is not a permanent statement of current `main`; verify GitHub before subsequent work.

## Current Repository Truth

### Merged stabilization packages

The August 12–17 stabilization sequence has materially advanced. These implementation packages are merged and must not be presented as pending:

| PR | Current truth |
| --- | --- |
| #337 / #338 | P1-A commitment/capability truth merged |
| #339 | P1-B receipt-correlated session action/outcome history merged |
| #340 | Cap 19 outcome truth merged |
| #341 / #344 | explicit weather-location preservation + WebSocket repair merged |
| #345 | brightness outcome-truth repair merged |
| #346 | `turn down volume` routing/wording repair merged |
| #347 | current-information freshness/source-boundary routing merged |
| #348 | broad awareness follow-up interpretation repair merged |
| #349 | Calendar source-selection overmatch repair merged |
| #350 | Calendar tomorrow-scope preservation merged |
| #351 | local schedule-cancellation routing merged |
| #352 | private Drive source-selection repair merged |

A merged repair does not by itself prove universal product readiness. Live-proof scope and current capability readiness must remain evidence-specific.

### Current `main` checkpoint after those repairs

At the start of Wave A1, merged `main` was:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

That commit adds a future governed-protection-wall vision document. The document is strategic/reference material; it does not activate a runtime or roadmap lane.

### PR #335 — Google Workspace Foundation

Current GitHub state:

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
base branch: main
historical base SHA: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
2 commits / Foundation-only scope
```

#335 must not be merged in that historical state. Reconciliation is intentionally deferred until Wave C establishes an exact validated baseline.

## Current Ordering

```text
Wave A1 — operational truth synchronization
-> Wave A2 — strategy reconciliation
-> Wave B — focused truth-integrity repairs
-> Wave C — semantic/proof stabilization and validated baseline
-> reconstruct/reconcile #335 onto exact validated baseline
-> independent security/architecture review
-> separate #335 merge decision
-> Google identity-only live proof
-> Google Tasks READ / first real provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

This ordering is a stabilization gate around the existing roadmap. It is not a roadmap redesign.

## Wave A1 Scope Lock

A1 changes only operational/canonical documentation and Issue #343.

A1 does not modify:

```text
runtime behavior
runtime auditor
GeneralChat persistence behavior
self-awareness behavior
capability registry
OAuth behavior
PR #335 implementation
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
```

## Three Control Planes

Current architecture must be described as three distinct control planes:

1. **Governed capability plane** — `GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue -> LedgerWriter -> ExecuteBoundary -> Executor`.
2. **Local operator / administrative plane** — settings, credentials, connections, provider/runtime configuration, and local operator controls.
3. **Bounded agent / routine plane** — constrained OpenClaw/routine/scheduler execution envelopes.

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

## Runtime Truth vs Generated Proof

Generated runtime documents are authoritative for the claims their generators actually measure. They must not be represented as proving unrelated semantics, live-provider behavior, complete network mediation, memory governance, or other unmeasured properties.

A future `validated_baseline_sha` will be immutable evidence for a completed Wave C verification package. It is not the same thing as whichever commit later becomes current HEAD.

## Strategic State

Operational Continuity remains strategically accepted and implementation-inactive. It remains persistent reconciled state around Nova's five-system product architecture, not an authority plane.

Future Continuity work still requires a separate warrant, exact scope, provenance/persistence contract, tests, implementation authorization, and fresh-main proof.

The future governed protection wall is long-term security/digital-sovereignty reference material. It does not replace Nova's current product identity or activate implementation work.

## Current Blockers Before Google Evidence Work

The immediate blockers are **truth-integrity and proof quality**, not missing Google domain connectors:

```text
A1 operational docs must agree with reality
A2 strategy must be reconciled separately
B1 generated/runtime truth instrumentation must stop overstating what it proves
B2 capability narration must separate existence/readiness/path availability/authority
B3 ordinary GeneralChat persistence semantics must be explicit and governed
B4 dependency metadata must be reproducible
Wave C semantic-contract regression + current local-inference benchmark must pass
```

Only reproduced defects are eligible for repair. Failure classification must precede diagnosis.

## Explicitly Deferred

Until the stabilization gate exits, do not begin:

- Google Tasks domain work;
- Gmail expansion;
- Google Calendar writes;
- Operational Continuity runtime;
- broad multi-provider routing;
- large graph/memory infrastructure;
- predictive learning;
- multi-agent orchestration;
- broad browser/computer-use;
- expanded OpenClaw autonomy;
- autonomous business operation;
- broad SaaS productization;
- Protection Wall runtime expansion.

## Short Version

Nova's governed execution foundation is intact. The codebase is ahead of its operational documentation and some generated/self-narrated truth semantics.

The current job is to make repository instructions truthful, then repair truth instrumentation/narration/persistence contracts, prove one exact baseline, and only then reconstruct Google Foundation and resume the existing Google-evidence → Continuity sequence.
