# Active TODO — Nova

Last reviewed: 2026-08-20.

This file is the current actionable task inventory. Historical lane detail belongs in Git history and dated proof/strategy artifacts, not in the active queue.

## Active Now

### Wave A1 — operational truth synchronization

- [ ] Reconcile `AGENTS.md`.
- [ ] Reconcile `.agent_context/current_priority.md`.
- [ ] Reconcile `docs/status/CURRENT_WORK_STATUS.md`.
- [ ] Reconcile `docs/status/DAILY_COMMAND_CENTER.md`.
- [ ] Reconcile this `ACTIVE_TODO.md`.
- [ ] Reconcile `docs/CANONICAL/00_INDEX.md`.
- [ ] Reconcile `docs/CANONICAL/03_GOVERNANCE_TRUTH.md`.
- [ ] Reconcile `docs/CANONICAL/06_TEST_AND_PROOF_TRUTH.md`.
- [ ] Reconcile `docs/CANONICAL/07_ROADMAP_TRUTH.md`.
- [ ] Reconcile `docs/capability_verification/CAPABILITY_INVENTORY.md`.
- [ ] Add the current stabilization gate to `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md` without redesigning the roadmap.
- [ ] Reconcile or explicitly supersede `NovaLIS-Governance/STATUS.md` as a current-status surface.
- [ ] Remove resolved/stale items from `docs/todo/DOC_CLEANUP.md`.
- [ ] Replace Issue #343 with the three-wave stabilization gate.
- [ ] Review exact A1 diff for docs-only scope and current-truth consistency.
- [ ] Open a draft PR; do not merge from this task list.

A1 branch:

```text
codex/wave-a1-operational-truth-sync-20260820
```

Merged-main planning checkpoint when A1 started:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

The checkpoint is evidence of the planning base, not a permanent current-main alias.

## Already Merged — Not Active TODOs

Do not create new work merely to repeat these merged packages:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session activity/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit weather-location preservation / WebSocket repair
#345         brightness outcome-truth repair
#346         volume phrase/routing repair
#347         current-information freshness/source-boundary routing
#348         broad awareness follow-up interpretation
#349         Calendar source-selection overmatch repair
#350         Calendar tomorrow-scope preservation
#351         local schedule-cancellation routing
#352         private Drive source-selection truth
```

A merged package may still have bounded live-proof limits. That does not make the implementation itself pending again.

## Open but Deferred

### PR #335 — Google Workspace Foundation

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
```

Do not modify, mark ready, or merge #335 during Wave A1. It must later be reconstructed/reconciled onto the exact Wave C validated baseline.

## Ordered After A1

### Wave A2 — strategy reconciliation

Rebase/reconcile the consolidated August product/platform strategy onto the A1-merged truth baseline. Keep strategy separate from operational status and do not convert validation doctrine into implementation authority.

### Wave B — focused truth-integrity repairs

#### B1 — runtime-truth instrumentation

- feed detected direct-network offenders into discrepancy/warning state;
- mechanically represent known NetworkMediator exceptions;
- stop `Discrepancies: None` from coexisting with detected relevant exceptions;
- replace Phase 9 placeholder-file evidence with live implementation/import/class checks;
- expand fingerprint coverage over behaviorally active runtime modules;
- qualify generated invariants to their actual proof scope;
- add an operational-truth consistency check separate from the narrow doc-drift checker.

#### B2 — capability narration

- separate `exists`, `enabled`, `configured`, `verification_status`, `available_on_this_path`, `requires_approval`, and `authority_class`;
- do not model `authorized` as static capability metadata;
- ensure OpenClaw self-awareness exposes only tools available to that execution path.

#### B3 — memory governance

- ordinary GeneralChat must not silently create durable personal memory;
- define explicit/observed precedence and conflict rules;
- preserve provenance/confidence/non-authoritative status;
- preserve epistemic status when memory is consumed by reasoning.

#### B4 — reproducibility hygiene

- make `pyproject.toml` canonical for dependencies;
- resolve the `python-multipart` mismatch with `nova_backend/requirements.txt`;
- stop maintaining independent manual dependency pin lists.

### Wave C — proof and stabilization checkpoint

- choose one exact candidate commit;
- regenerate repaired runtime truth;
- run the strongest supported proof matrix per environment;
- run the semantic-contract regression matrix;
- rebenchmark Issue #227 against the current local inference stack;
- repair only reproduced defects;
- record immutable `validated_baseline_sha` only after required proof passes;
- reconstruct #335 on that exact baseline;
- harden post-token identity-failure cleanup and invalid callback consumption;
- rerun exact-head #335 verification;
- perform independent security/architecture review;
- make merge a separate decision.

## Post-Stabilization Order

Only after Wave C and a separate #335 decision:

```text
Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

A new connector/data source is not a Nova product feature merely because it can be called. The product test is whether Nova can connect trustworthy evidence to other state and reduce a real uncertainty.

## Permanent Boundaries

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
execution != verified outcome
memory != Operational Continuity
```

No control plane may silently increase authority available to another control plane.

## Explicitly Not Active

Do not begin:

```text
Google Tasks domain implementation
Gmail expansion
Google Calendar writes
Operational Continuity runtime
broad provider routing
large graph/memory infrastructure
predictive learning
multi-agent orchestration
broad browser/computer-use
expanded OpenClaw autonomy
autonomous business operation
broad SaaS productization
Protection Wall runtime expansion
```

## Backlog / Planning Issues

Issue #227 remains a current-hardware/model benchmark backlog item and must be re-evaluated in Wave C using the actual current model, context, latency, and hardware rather than May assumptions.

Other old planning/future issues are not active merely because they remain open.
