# Active TODO — Nova

Last reviewed: 2026-09-20.

This file is the current actionable task inventory. Historical lane detail belongs in Git history and dated proof/strategy artifacts, not in the active queue.

## Active Now — post-#405 correctness and beta-readiness

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
verified main after Lane 5A rollback/restore proof: 868de9d92c701834f1c4fba422ab9c47a01ea33f
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
COMPLETE: durability implementation lane 2 - corruption-safe readers (PR #416; main `80e1c86f`)
COMPLETE: durability implementation lane 3 - maintenance locking + mutation quiescence (PR #419; main `2bfe202e`)
COMPLETE: durability implementation lane 4 - versioned snapshot + manifest (PR #421; main `4e32b501`)
FRESH-MAIN CLOSEOUT: PASS (314 focused durability/operational-truth tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: #409 release integrity / repository control (PR #423; main `aa39515f`)
COMPLETE: #410 private-beta freeze criteria (PR #410; main `3ad3f544`)
AUTHORIZED / ACTIVE: Lane 5A recovery construction (owner authorization; base main `3ad3f544`)
COMPLETE: Lane 5A step 1 - inactive recovery candidate migration (PR #424; main `298b7731`)
MIGRATION PROOF: PASS (173 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 2 - recovery candidate validation (PR #426; main `9de640cd`)
VALIDATION PROOF: PASS (184 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 3 - controlled recovery activation (PR #427; main `678dda6c`)
ACTIVATION PROOF: PASS (192 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A authority-foundation correction (PR #428; main `3a3e9d33`)
AUTHORITY FOUNDATION PROOF: PASS (201 durability tests passed; 1 expected Windows POSIX-FIFO skip)
RECOVERY AUTHORITY MODEL: dual-slot highest-valid-generation selection
COMPLETE: Lane 5A step 4 - rollback/restore proof (PR #430; main `868de9d9`)
ROLLBACK/RESTORE PROOF: PASS (208 durability tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: beta user-facing truth pass (PR #433; main `ad64048e`)
COMPLETE: rollback/restore operational-truth checker contract (PR #436; main `0003a2e`)
FRESH-MAIN PROOF: PASS (39 focused checker-contract tests; Ruff; operational-truth consistency; runtime structural smoke)
COMPLETE: first Synthetic Beta Cohort v1 (PR #438; test-only evidence, not product acceptance)
COMPLETE: connected-user cohort test-spec correction (PR #439; main `486ad3dddc3f75412085b968c28561ab57e25686`)
CONFIRMED P1 BEFORE BETA ACCEPTANCE: the local-only boundary is unsafe if `NOVA_HOST` accepts a non-loopback bind; repair and fresh proof are required before any Windows acceptance run.
NEXT REQUIRED ENGINEERING: bounded local-boundary P1 repair (no remote mode or authority expansion)
THEN: fresh-main security and truth proof
THEN: installer supply-chain and privacy/Data-Out/secrets audit
THEN: build a new exact Windows candidate artifact; the prior artifact is historical only
THEN: clean Windows operator proof against that exact artifact
THEN: freeze exact candidate identity
THEN: rerun #434 and remaining acceptance checks against that frozen candidate
THEN: owner acceptance/distribution decision
THEN: 3 real non-developer users
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. Older
active-order language below is historical wherever it conflicts with this block.

## Historical active queue

### Post-Wave-C documentation closeout — COMPLETE

Current state:

```text
Wave C initial candidate: 404689ef07f42480966c59ba30c07db5c4f101e1
B1 / PR #356: COMPLETE / MERGED
B2 / PR #358: COMPLETE / MERGED
B3 / PR #360: COMPLETE / MERGED
B4 / PR #362: COMPLETE / MERGED
Wave C: COMPLETE / MERGED / VALIDATED
PR #364: MERGED
PR #364 reviewed head: 786c048df6dc4ed8f3c8245c5b365d4296f342f4
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
PR #365 merge / PR #366 branch base: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
PR #366 truth-hygiene package: MERGED
PR #366 squash merge: 4ddd46ad0c3e3c5db55e006680f4a426956581c1
PR #378 narration/front-door package: MERGED / VERIFIED
PR #378 squash merge: 67c3d8fd10e013eef466769cd4c8d96f75d27845
documentation closeout: COMPLETE
#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368: NEXT BOUNDED TECHNICAL LANE
#387: AFTER #368 / DOCS-ONLY
PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED
PR #335 state: OPEN / DRAFT / UNMERGED
```

Wave A1, A2, B1, B2, B3, B4, and Wave C are already merged:

```text
#353  A1 operational truth synchronization
       merge: f25c798c7cb488495a343068463e9214cab0a763

#355  A2 strategy reconciliation
       merge: 060380f2e8c6437ff888773f0078647547ff4622

#356  B1 runtime-truth instrumentation
       reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
       squash merge: 969c369b453fffca0eb2b8dad65ff3f285df8fbc

#357  post-B1 operational truth synchronization
       merge: 864ceba9747384b3bdca4a693dca938b3899864e

#358  B2 capability narration truth
       reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
       squash merge: e84a9d55f8575c687765b1df19e8f794b180599b

#359  post-B2 operational truth synchronization
       merge/current B3 base: b1dad94e08e2d01b1cd7f0cf43981cff80b0de2e

#360  B3 memory governance
       reviewed head: 3e8a68aa5d17712fbb2106f052e309a2f33e120e
       squash merge: 8cc67213bd7e06e862d50bc2c1bf29d8ac72f064

#361  post-B3 operational truth synchronization
       merge/B4 base: bb99a5edbc9397d6b96b91fe0e9fe01bf57f9bd1

#362  B4 reproducibility hygiene
       reviewed head: 7b70a91b3a294e829a36edac067da7e4b567774e
       squash merge: 5c243a822f79ea09b0031124d4bafbf32d18842c

#363  post-B4 operational truth synchronization
       merge/Wave C initial candidate:
       404689ef07f42480966c59ba30c07db5c4f101e1

#364  Wave C validation and reproduced-defect repairs
       reviewed head: 786c048df6dc4ed8f3c8245c5b365d4296f342f4
       squash merge/validated_baseline_sha:
       ec20a7146f7d6d55b8983cb7d6d3918d5fad9915

#365  post-Wave-C validated-baseline/evidence-waiver documentation sync
       merge/PR #366 branch base:
       d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
       runtime validated-baseline change: NONE

#366  post-Wave-C truth-hygiene contract package
       squash merge:
       4ddd46ad0c3e3c5db55e006680f4a426956581c1
       runtime validated-baseline change: NONE

#378  consolidated narration/front-door documentation package
       reviewed head:
       84222288335c399c1ffa73186858e8ba84e9a64a
       squash merge:
       67c3d8fd10e013eef466769cd4c8d96f75d27845
       runtime validated-baseline change: NONE
```

Do not reopen B1 through B4 or Wave C without concrete new evidence. The Wave C exit proof passed on exact validated baseline `ec20a714...` under the explicit owner evidence waiver; do not reinterpret waived hosted jobs as PASS. PRs #365, #366, and #378 are later documentation/truth provenance, not new runtime validated baselines.

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
- [x] Verify B1 squash merge `969c369b453fffca0eb2b8dad65ff3f285df8fbc`.

### Completed B2 lane

```text
[x] separate reviewed owner authorization for B2 implementation
[x] implement one shared seven-field capability-truth projection
[x] migrate the five authorized narration consumers
[x] complete focused local proof and exact base-to-candidate diff review
[x] complete remote exact-head PR review and separate merge decision
[x] merge PR #358 at reviewed head `b95039c2dc483ad330205de5dac8e3b3f94d8836`
[x] verify B2 squash merge `e84a9d55f8575c687765b1df19e8f794b180599b`
```

### Completed B3 lane

```text
[x] complete the bounded memory-governance implementation
[x] prove ordinary GeneralChat does not silently create authoritative durable memory
[x] preserve explicit/observed provenance, precedence, conflict, supersession, and promotion semantics
[x] keep superseded history out of current-memory results
[x] complete focused automated and live proof
[x] merge PR #360 at reviewed head `3e8a68aa5d17712fbb2106f052e309a2f33e120e`
[x] verify B3 squash merge `8cc67213bd7e06e862d50bc2c1bf29d8ac72f064`
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
#358         Wave B2 capability narration truth
#360         Wave B3 memory governance
#362         Wave B4 reproducibility hygiene
#364         Wave C validation / validated baseline
#365         post-Wave-C baseline/evidence-waiver documentation sync
#366         post-Wave-C truth-hygiene contract package
#378         consolidated narration/front-door documentation package
```

Merged implementation is not universal live-proof coverage.

## Open but Deferred

### PR #335 — Google Workspace Foundation

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED
```

The documentation-closeout prerequisite is complete. PR #335 still remains deferred because reconstruction/reconciliation requires a later separate owner decision. If authorized later, reconstruction remains pinned to exact Wave C validated baseline `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`; do not substitute a later documentation-only `main` revision.

### Issue #354 — zero-step GitHub Actions infrastructure

```text
STATUS: infrastructure/open
IMPACT: hosted workflows currently provide no trustworthy behavioral evidence
CAUSE: external GitHub account billing / Actions spending restriction
WAVE C DISPOSITION: owner-waived as a mandatory exit evidence source
```

Keep #354 separate from Nova runtime truth. Its jobs remain `NOT EXECUTED`, not PASS or behavioral FAIL; the owner waiver removed it as a Wave C exit dependency without fixing the account restriction.

## Completed Documentation Closeout

README, START_HERE, historical-guide lifecycle, and Brain/operating-model narration cleanup were consolidated and merged through PR #378. The post-Wave-C truth-hygiene contract was merged through PR #366. This completion state does not authorize runtime or #335 work.

## Current Ordered Work and Blocked Work

### #388 complete; #368 next; then #387

```text
#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368: NEXT BOUNDED TECHNICAL LANE
#387: AFTER #368 / DOCS-ONLY
PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED
```

Documentation closeout and Issue #388 are complete, but no Google engineering lane becomes active automatically. After the bounded #368 and #387 sequence, the owner may separately decide whether to authorize #335 reconstruction/reconciliation against exact validated baseline `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`.

Until a later separate owner decision grants authorization, do not create or modify the #335 reconstruction branch, implement Google Foundation changes, or treat #335 as an active capability lane.

### Wave B2 — capability narration

**COMPLETE / MERGED via PR #358.** The established projection keeps these distinctions:

- separate `exists`, `enabled`, `configured`, `verification_status`, `available_on_this_path`, `requires_approval`, and `authority_class`;
- do not model `authorized` as static capability metadata;
- ensure OpenClaw self-awareness exposes only tools available to that execution path.

### Wave B3 — memory governance

**COMPLETE / MERGED via PR #360.** The bounded memory truth/provenance scope established:

- ordinary GeneralChat does not silently create durable personal memory;
- explicit/observed precedence and conflict rules are defined;
- provenance/confidence/non-authoritative status is preserved;
- epistemic status is preserved when memory is consumed by reasoning.

### Wave B4 — reproducibility hygiene

**COMPLETE / MERGED via PR #362.** The bounded dependency-truth scope established:

- make `pyproject.toml` canonical for dependencies;
- resolve the `python-multipart` mismatch with `nova_backend/requirements.txt`;
- stop maintaining independent manual dependency pin lists.

### Wave C — proof and stabilization checkpoint

**COMPLETE / MERGED / VALIDATED.** Exit evidence:

- choose one exact candidate commit;
- regenerate repaired runtime truth;
- run the strongest supported proof matrix per environment;
- run semantic-contract regression;
- rebenchmark Issue #227 against the current local inference stack;
- repair only reproduced defects;
- immutable `validated_baseline_sha`: `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`;

### Post-Wave-C / Google Foundation reconciliation — deferred

**PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED.** Issue #388 is complete; Issues #368 and #387 precede this decision. A later owner decision is still required before any branch or implementation change:

- reconstruct #335 on the exact validated baseline only after an authorizing owner decision;
- harden post-token identity-failure cleanup and invalid callback consumption;
- rerun exact-head #335 verification;
- perform independent security/architecture review;
- make merge a separate decision.

## Post-Stabilization Order

Only after a separate #335 reconstruction decision and the subsequent separately reviewed/merged work:

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

Do not begin outside the next separately authorized lane:

```text
B3 memory architecture beyond the completed truth/provenance repair
B4 dependency modernization, unrelated upgrades, or packaging redesign beyond completed B4
Wave C reopening, capability expansion, or repairs without reproduced evidence
PR #335 reconstruction/reconciliation without separate owner authorization
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

Issue #227's Wave C current-hardware/model revalidation is historical evidence from the completed Wave C package. Old planning/future issues are not active merely because they remain open.
