# Active TODO — Nova

Last reviewed: 2026-08-23.

This file is the current actionable task inventory. Historical lane detail belongs in Git history and dated proof/strategy artifacts, not in the active queue.

## Active Now

### Wave B2 — authorization gate

Current state:

```text
current main: 969c369b453fffca0eb2b8dad65ff3f285df8fbc
B1 / PR #356: COMPLETE / MERGED
B2: NEXT / NOT YET IMPLEMENTATION-AUTHORIZED
B3: BLOCKED
B4: BLOCKED
Wave C: BLOCKED
```

Wave A1, A2, and B1 are already merged:

```text
#353  A1 operational truth synchronization
       merge: f25c798c7cb488495a343068463e9214cab0a763

#355  A2 strategy reconciliation
       merge: 060380f2e8c6437ff888773f0078647547ff4622

#356  B1 runtime-truth instrumentation
       reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
       squash merge/current main: 969c369b453fffca0eb2b8dad65ff3f285df8fbc
```

Do not reopen B1 without concrete new evidence. Do not implement B2 without separate reviewed owner authorization.

### Completed B1 source/truth work

- [x] Reproduce the requests-based network discrepancy inconsistency: `BYPASS_SURFACES.md` detects `connections_api.py` while the main discrepancy set can report none.
- [x] Identify `nova_backend/src/api/connections_api.py` as the known requests-based path.
- [x] Preserve classification `local_administrative_health_probe` pending explicit disposition.
- [x] Add discrepancy representation for known and unclassified requests-based network paths.
- [x] Replace Phase 9 retired-placeholder evidence with live import/symbol checks.
- [x] Expand runtime fingerprint scope over behaviorally active source families, including `usage`.
- [x] Qualify generated NetworkMediator/Governor/ledger and network-scan wording to measured scope.
- [x] Add focused B1 regression coverage and generator-entrypoint integration coverage.
- [x] Add `scripts/check_operational_truth_consistency.py` separately from `check_runtime_doc_drift.py`.
- [x] Include `docs/CANONICAL/00_INDEX.md` in active-lane consistency checking with stale-index regression.
- [x] Synchronize A1/A2/B1 operational truth surfaces and Issue #343 checkpoint.
- [x] Complete first exact-head local proof pass.
- [x] Mechanically generate and review the first B1 runtime artifacts.
- [x] Commit only the three intended runtime artifacts; exclude `_MOCs/*`.
- [x] Open draft PR #356.
- [x] Complete final remote exact-head/scope review of `f44cb8b8...`.
- [x] Final release review identified one P1 operational-doc substate defect and one P2 fingerprint-count defect.
- [x] Correct fingerprint scope so the exact hashed/count set contains existing files only.
- [x] Add focused regression asserting all fingerprinted paths exist and missing allowlist entries are excluded.
- [x] Synchronize active B1 handoff documents to the correction/review state.
- [x] Verify corrected branch/head/clean working state.
- [x] Rerun Ruff on the B1 correction surfaces.
- [x] Rerun 13 focused B1 tests.
- [x] Rerun 29 runtime-auditor/governance-doc tests.
- [x] Run operational consistency and runtime-doc drift before generation.
- [x] Mechanically regenerate the bounded runtime artifacts.
- [x] Inspect `CURRENT_RUNTIME_STATE.md`, `BYPASS_SURFACES.md`, and `RUNTIME_FINGERPRINT.md`.
- [x] Verify `runtime_surface_file_count` equals 230 existing files in the exact hash set.
- [x] Rerun operational consistency and runtime-doc drift after generation.
- [x] Commit corrected generated artifacts at `e668ec0c09df6e0d304427431e95a26619a9f507`.
- [x] Exclude `_MOCs/*`.
- [x] Review the exact A2-base to corrected-B1 diff; 14 paths, `+1,887/-447`, clean.
- [x] Complete final PR #356 review / evidence assessment.
- [x] Merge PR #356 at reviewed head `381dbaeca73786f789cc6e68fd3b6bf193296041`.
- [x] Verify squash merge/current main `969c369b453fffca0eb2b8dad65ff3f285df8fbc`.

### Current B2 gate

```text
[ ] separate reviewed owner authorization for B2 implementation
```

Generated runtime artifacts must not be edited manually.

Completed generated-output acceptance:

```text
CURRENT_RUNTIME_STATE.md
  - KNOWN_DIRECT_NETWORK_EXCEPTION includes connections_api.py
  - no false Discrepancies: None
  - Phase 9 names live active symbols
  - NetworkMediator/Governor/ledger wording is qualified
  - Runtime Surface Scope count reflects existing fingerprinted files only

BYPASS_SURFACES.md
  - connections_api.py remains visible
  - local_administrative_health_probe visible
  - requests-scanner scope explicit
  - no universal network-coverage claim

RUNTIME_FINGERPRINT.md
  - scope_version: behaviorally_active_v2
  - runtime_surface_file_count = 230 existing files
  - runtime_surface_hash = c5cadfeff5db3e22fea0f1c2efeb05016765c20bb7cd24e33ad758361fd9acd9
  - runtime_fingerprint_hash = 9c0d4ee90572e3356811436bc490de13fb82fc1393c63aa5774b36fd05154f34
  - source_families present
  - brain / connections / identity / memory / usage included
```

B1 does not change the actual `connections_api.py` network behavior. Reporting the exception does not approve or mediate it.

## Already Merged — Not Active TODOs

Do not recreate or reopen these as pending implementation:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session action/outcome history
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
#356         Wave B1 runtime-truth instrumentation
```

Merged implementation is not universal live-proof coverage.

## Open but Deferred

### PR #335 — Google Workspace Foundation

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
```

PR #335 remains deferred; do not modify, mark ready, or merge it before it is reconstructed/reconciled onto the exact Wave C validated baseline.

### Issue #354 — zero-step GitHub Actions infrastructure

```text
STATUS: infrastructure/open
IMPACT: hosted workflows currently provide no trustworthy behavioral evidence
NEEDED BEFORE: Wave C validated-baseline proof relies on hosted CI
```

Keep #354 separate from B2 capability-narration work unless infrastructure diagnosis is explicitly selected.

### Front-door README truth cleanup

`README.md` still contains stale sequencing/current-status language. This is separate documentation debt. Do not rewrite README inside this post-B1 sync or B2 without separate scope.

## Current Next Lane and Blocked Work

### Wave B2 — capability narration

**NEXT / NOT YET IMPLEMENTATION-AUTHORIZED.** Preserve the established scope only:

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
- run semantic-contract regression;
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
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
```

No control plane may silently increase authority available to another control plane.

## Explicitly Not Active

Do not begin from this post-B1 synchronization:

```text
B2 capability-narration implementation
B3 memory-governance behavior
B4 dependency/reproducibility repair
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
README/front-door rewrite
```

Issue #227 remains a Wave C current-hardware/model benchmark item. Old planning/future issues are not active merely because they remain open.
