# Nova Current Work Status

Last reviewed: 2026-08-20.

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
WAVE B1 — runtime-truth instrumentation
STATUS: IN PROGRESS
BRANCH: codex/b1-runtime-truth-instrumentation-20260820
POST-A2 BASE: 060380f2e8c6437ff888773f0078647547ff4622
```

The base SHA is the B1 planning checkpoint, not a permanent alias for current `main` and not a validated baseline.

## Completed Gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622
```

A1 synchronized operational truth. A2 reconciled the three durable August strategy documents and classified the Governed Protection Wall as long-term security/digital-sovereignty reference material. Neither gate authorizes later runtime lanes.

## Current Repository Truth

### Merged stabilization packages

The August stabilization repairs below are merged and must not be presented as pending:

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

A merged repair does not by itself prove universal product readiness. Live-proof scope and current capability readiness remain evidence-specific.

### PR #335 — Google Workspace Foundation

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base SHA: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

#335 must not be merged in that historical state. Reconciliation is deferred until Wave C establishes an exact validated baseline.

### GitHub Actions infrastructure

Issue #354 tracks repeated zero-step hosted GitHub Actions failures across CI/governance/runtime-doc/fingerprint workflows.

Classification:

```text
infrastructure/open
not behavioral test evidence
needed before Wave C validated-baseline proof can rely on hosted CI
```

This does not invalidate A1/A2 content and is not a B1 runtime-behavior defect.

## Current Ordering

```text
Wave B1 — runtime-truth instrumentation
-> Wave B2 — capability narration
-> Wave B3 — memory governance
-> Wave B4 — reproducibility hygiene
-> Wave C — semantic/proof stabilization and validated baseline
-> reconstruct/reconcile #335 onto exact validated baseline
-> independent security/architecture review
-> separate #335 merge decision
-> Google identity-only live proof
-> Google Tasks READ / first real provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

## Wave B1 Scope Lock

B1 repairs generated/runtime truth instrumentation. The reproduced problems are:

- `BYPASS_SURFACES.md` can detect direct `requests` usage while the main discrepancy list reports none;
- `nova_backend/src/api/connections_api.py` is a known direct-network path outside NetworkMediator but lacked generated discrepancy classification;
- Phase 9 status used retired placeholder-file existence instead of live import/symbol checks;
- fingerprint coverage omitted behaviorally active source families used by generated truth;
- generated invariants used whole-repository absolutes beyond what the auditor mechanically proves;
- the existing runtime-doc drift checker does not verify agreement among active operational truth surfaces.

B1 may change:

```text
runtime-auditor instrumentation
focused tests
generated runtime truth required by the instrumentation
runtime fingerprint scope
separate operational-truth consistency checker
minimal current-status synchronization
```

B1 does not change:

```text
network behavior or connections_api.py wiring
capability narration semantics
GeneralChat persistence behavior
capability registry
OAuth behavior
PR #335 implementation
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
```

The known network finding remains a finding, not a runtime fix:

```text
path: nova_backend/src/api/connections_api.py
classification: local administrative health probe
status: detected outside NetworkMediator; pending explicit disposition
```

## Three Control Planes

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

Generated runtime documents are authoritative only for claims their generators actually measure. B1 tightens that contract; it does not convert generated structure checks into live behavioral proof.

A future `validated_baseline_sha` is immutable evidence for a completed Wave C verification package. It is not the same thing as whichever commit later becomes current HEAD.

## Strategic State

The consolidated August Product/Platform strategy is merged through PR #355 and remains strategy-only/non-authorizing.

Operational Continuity remains strategically accepted and implementation-inactive. Future Continuity work still requires a separate evidence-based warrant, exact scope, provenance/persistence contract, tests, implementation authorization, and fresh-main proof.

The Governed Protection Wall remains `REFERENCE / LONG-TERM SECURITY / DIGITAL-SOVEREIGNTY EXTENSION` material and does not activate implementation work.

## Explicitly Deferred

Until the stabilization gate permits them, do not begin:

- B2 capability narration inside B1;
- B3 memory-governance behavior;
- B4 dependency/reproducibility repair;
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

A1 and A2 are merged. B1 is the active lane. Its job is to make Nova's generated runtime truth expose known discrepancies, prove only what its checks actually measure, fingerprint the behaviorally active code it depends on, and detect drift among active operational truth surfaces. No capability or authority expansion is part of B1.
