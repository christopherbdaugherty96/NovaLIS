# Active TODO — Nova

Last reviewed: 2026-08-20.

This file is the current actionable task inventory. Historical lane detail belongs in Git history and dated proof/strategy artifacts, not in the active queue.

## Active Now

### Wave B1 — runtime-truth instrumentation

Current branch:

```text
codex/b1-runtime-truth-instrumentation-20260820
base: 060380f2e8c6437ff888773f0078647547ff4622
```

Wave A1 and A2 are already merged:

```text
#353  A1 operational truth synchronization
       merge: f25c798c7cb488495a343068463e9214cab0a763

#355  A2 strategy reconciliation
       merge: 060380f2e8c6437ff888773f0078647547ff4622
```

B1 checklist:

- [x] Reproduce the direct-network discrepancy inconsistency: `BYPASS_SURFACES.md` detects `connections_api.py` while the main discrepancy set can report none.
- [x] Identify the known direct-network path as `nova_backend/src/api/connections_api.py`.
- [x] Preserve its classification as a local administrative health probe pending explicit disposition.
- [x] Add generated discrepancy representation for known and unclassified direct-network paths.
- [x] Replace Phase 9 retired-placeholder evidence with live import/symbol checks against active modules.
- [x] Expand runtime fingerprint scope over behaviorally active source families without broadening the direct-network scan allowlist.
- [x] Qualify generated NetworkMediator/Governor/ledger invariants to the scope actually measured.
- [x] Add focused B1 regression coverage.
- [x] Add `scripts/check_operational_truth_consistency.py` separately from `check_runtime_doc_drift.py`.
- [x] Synchronize active operational surfaces to B1.
- [ ] Regenerate the mechanically derived runtime truth documents on the B1 head.
- [ ] Run the strongest locally available focused/runtime-doc/structural proof package.
- [ ] Review the exact B1 diff for scope and generated-truth consistency.
- [ ] Open a draft B1 PR; no merge is authorized merely by this checklist.

B1 does not change the actual `connections_api.py` network behavior. The generated truth must expose the exception without pretending it is mediated or silently approving it.

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
#353         Wave A1 operational truth synchronization
#355         Wave A2 strategy reconciliation
```

A merged package may still have bounded live-proof limits. That does not make the implementation itself pending again.

## Open but Deferred

### PR #335 — Google Workspace Foundation

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
```

Do not modify, mark ready, or merge #335 during B1. It must later be reconstructed/reconciled onto the exact Wave C validated baseline.

### Issue #354 — zero-step GitHub Actions infrastructure

```text
STATUS: infrastructure/open
IMPACT: hosted workflows currently provide no trustworthy behavioral evidence
NEEDED BEFORE: Wave C validated-baseline proof
```

Keep this issue separate from B1 content/runtime semantics unless infrastructure diagnosis is explicitly selected.

## Ordered After B1

### Wave B2 — capability narration

- separate `exists`, `enabled`, `configured`, `verification_status`, `available_on_this_path`, `requires_approval`, and `authority_class`;
- do not model `authorized` as static capability metadata;
- ensure OpenClaw self-awareness exposes only tools available to that execution path.

### Wave B3 — memory governance

- ordinary GeneralChat must not silently create durable personal memory;
- define explicit/observed precedence and conflict rules;
- preserve provenance/confidence/non-authoritative status;
- preserve epistemic status when memory is consumed by reasoning.

### Wave B4 — reproducibility hygiene

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
B2 capability narration inside B1
B3 memory-governance behavior inside B1
B4 dependency/reproducibility repair inside B1
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
