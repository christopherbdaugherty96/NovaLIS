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

The consolidated August Product/Platform strategy is merged as strategy-only guidance through PR #355. Strategy does not override current runtime truth, operational ordering, lane scope, or authority.

## Read Order

Current post-#405 override (2026-09-03):

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
verified main at sync start: df2df490083511f480b653c0960fbe7a6e6abfe8
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
NEXT: separate owner authorization decision for corruption-safe readers
THEN: if authorized, corruption-safe readers
THEN: bounded product-translation/readiness pass
THEN: clean Windows operator proof
THEN: frozen-SHA full beta acceptance
THEN: private-beta candidacy/distribution decision
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This
override supersedes older current-order language below; historical evidence remains
valid for the revisions and scope it actually covered.

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

## Post-Wave-C Current Development State — 2026-08-25

Post-Wave-C documentation closeout is COMPLETE. PR #366 is MERGED truth-hygiene provenance and PR #378 is the MERGED narration/front-door package. Wave C is COMPLETE / MERGED / VALIDATED. Issue #388 is COMPLETE and its truth-checker prerequisite is SATISFIED; Issue #368 is the next bounded technical lane, then Issue #387 performs the docs-only master-roadmap sync. PR #335 remains pending a separate owner decision and is not authorized.

Wave A1, A2, B1, B2, B3, and B4 are complete:

```text
#353  Wave A1 operational truth synchronization — MERGED
       merge: f25c798c7cb488495a343068463e9214cab0a763

#355  Wave A2 strategy reconciliation — MERGED
       merge: 060380f2e8c6437ff888773f0078647547ff4622

#356  Wave B1 runtime-truth instrumentation — MERGED
       reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
       squash merge: 969c369b453fffca0eb2b8dad65ff3f285df8fbc

#357  Post-B1 operational truth synchronization — MERGED
       merge: 864ceba9747384b3bdca4a693dca938b3899864e

#358  Wave B2 capability narration truth — MERGED
       reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
       squash merge: e84a9d55f8575c687765b1df19e8f794b180599b
#359  Post-B2 operational truth sync — MERGED
       merge/current B3 base: b1dad94e08e2d01b1cd7f0cf43981cff80b0de2e

#360  Wave B3 memory governance — MERGED
       reviewed head: 3e8a68aa5d17712fbb2106f052e309a2f33e120e
       squash merge: 8cc67213bd7e06e862d50bc2c1bf29d8ac72f064

#361  Post-B3 operational truth synchronization — MERGED
       merge/B4 base: bb99a5edbc9397d6b96b91fe0e9fe01bf57f9bd1

#362  Wave B4 reproducibility hygiene — MERGED
       reviewed head: 7b70a91b3a294e829a36edac067da7e4b567774e
       squash merge: 5c243a822f79ea09b0031124d4bafbf32d18842c

#363  Post-B4 operational truth synchronization — MERGED
       merge / Wave C initial candidate:
       404689ef07f42480966c59ba30c07db5c4f101e1

#364  Wave C validation and reproduced-defect repairs — MERGED
       reviewed head:
       786c048df6dc4ed8f3c8245c5b365d4296f342f4
       squash merge / validated_baseline_sha:
       ec20a7146f7d6d55b8983cb7d6d3918d5fad9915

#365  Post-Wave-C validated-baseline/evidence-waiver documentation sync — MERGED
       merge / PR #366 branch base:
       d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c

#366  Post-Wave-C truth-hygiene contract package — MERGED
       squash merge:
       4ddd46ad0c3e3c5db55e006680f4a426956581c1

#378  Post-Wave-C narration/front-door closeout package — MERGED / VERIFIED
       squash merge:
       67c3d8fd10e013eef466769cd4c8d96f75d27845
```

Current planning state:

```text
Wave B2 — capability narration: COMPLETE / MERGED
Wave B3 — memory governance: COMPLETE / MERGED
B4: COMPLETE / MERGED
Wave C: COMPLETE / MERGED / VALIDATED
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
truth-hygiene provenance: PR #366 MERGED
narration/front-door package: PR #378 MERGED / VERIFIED
#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368: NEXT BOUNDED TECHNICAL LANE
#387: AFTER #368 / DOCS-ONLY
PR #335 reconstruction: PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED
PR #335 state: OPEN / DRAFT / UNMERGED
post_wave_c_sync_sha: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
post_closeout_narration_merge_sha: 67c3d8fd10e013eef466769cd4c8d96f75d27845
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

`post_wave_c_sync_sha` and `post_closeout_narration_merge_sha` are durable documentation provenance, not replacements for the immutable runtime-validated baseline and not forever-current `main` claims. Resolve current HEAD from Git/repository state when that distinction matters.

B1 through B4 are complete and merged. Their proof and review records remain historical evidence for the revisions and environments actually exercised.

### Immediate worker instruction

The post-Wave-C documentation closeout and Issue #388 truth-checker prerequisite are complete. The next bounded technical lane is Issue #368; Issue #387 follows #368 as docs-only synchronization. Do not treat that ordering as authorization for #335. PR #335 reconstruction is pending a separate owner decision and remains not authorized against exact validated baseline `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`. Do not begin OAuth/Google, #335, Google domain-data, OpenClaw-authority, provider-routing, external-write, or Operational Continuity implementation work from this state.

B3's bounded memory-governance contract is complete: ordinary chat does not silently create authoritative durable personal memory; explicit and observed memory remain distinct; provenance, confidence, conflict, supersession, and promotion semantics remain visible; superseded history is not current memory.

B4 is complete: `pyproject.toml` is canonical dependency truth; `nova_backend/requirements.txt` is a mechanically checked compatibility projection; the historical `python-multipart` mismatch is resolved; and supported installation was proven on the reviewed B4 revision. Do not reopen packaging without concrete new evidence.

Wave C is complete and merged. The complete non-hosted proof passed on exact validated baseline `ec20a714...`: source Ruff, 20 adversarial tests, 289 certification tests with five expected skips, 4,294 backend tests with five expected skips, structural/truth/dependency checks, and live `nova-start` smoke. GitHub-hosted jobs remained `NOT EXECUTED` because of the account-billing restriction in Issue #354. The owner explicitly waived that evidence source as a Wave C exit requirement; it is not recorded as PASS. PR #365, PR #366, and PR #378 later advanced repository `main` with documentation/truth synchronization only; none established a new runtime validated baseline.

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

Do not merge or extend PR #335 in its historical state. Reconstructing it on the exact validated baseline requires a later authorizing owner decision; documentation closeout completion does not provide that authorization.

## Current Ordered Gate

```text
Wave B2 — capability narration / COMPLETE / MERGED
-> Wave B3 — memory governance / COMPLETE / MERGED
-> Wave B4 — reproducibility hygiene / COMPLETE / MERGED
-> Wave C — proof / validated-baseline checkpoint / COMPLETE / MERGED / VALIDATED
-> post-Wave-C documentation closeout / COMPLETE
   truth-hygiene provenance: PR #366 MERGED
   narration/front-door package: PR #378 MERGED / VERIFIED
-> #388 / COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
-> #368 / NEXT BOUNDED TECHNICAL LANE
-> #387 / AFTER #368 / DOCS-ONLY
-> PR #335 reconstruction / PENDING SEPARATE OWNER DECISION / NOT AUTHORIZED
-> separate #335 review/merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

Issue #343 remains the detailed stabilization ordering record.

Issue #354 separately tracks the zero-step GitHub Actions account/billing failure. That infrastructure state is not behavioral test evidence. The owner waived it as a mandatory Wave C exit source without reclassifying it as PASS.

## Completed Wave B1 Boundary

B1 changed only what was required to make generated/runtime truth instrumentation accurately describe what it measures:

- runtime-auditor instrumentation;
- requests-based network discrepancy/classification reporting;
- Phase 9 implementation evidence checks;
- runtime fingerprint scope;
- generated runtime truth outputs required by those changes;
- focused tests;
- a separate operational-truth consistency checker;
- minimal current-status synchronization needed to name B1 and its proof/review substate accurately.

The B1 publication and bounded P1/P2 correction passes are complete and merged. Do not reopen B1 without concrete new evidence.

B1 does **not** authorize:

```text
network behavior changes
moving connections_api.py behind NetworkMediator
capability narration repair (B2)
GeneralChat memory/persistence repair (B3)
dependency-source cleanup (B4)
capability registry or authority changes
OAuth or PR #335 implementation
Google domain-data access
Operational Continuity runtime
OpenClaw authority expansion
provider routing
external-write behavior
README/front-door rewrite
```

The known requests-based network checkpoint finding remains:

```text
nova_backend/src/api/connections_api.py
classification: local_administrative_health_probe
status: detected outside NetworkMediator; explicitly reported pending disposition
```

B1 makes that fact visible in discrepancy/runtime truth. It does not silently treat the path as mediated and does not fix the network path itself. The scanner is requests-based and does not prove absence of every possible network mechanism.

## B1 Completed Evidence

Corrective evidence is complete:

```text
Ruff: PASS
focused B1 tests: 13 PASS
auditor/governance tests: 29 PASS
operational consistency: PASS before/after generation
runtime-doc drift: PASS before/after generation
scope: behaviorally_active_v2
existing-file fingerprint count: 230
runtime surface hash: c5cadfeff5db3e22fea0f1c2efeb05016765c20bb7cd24e33ad758361fd9acd9
runtime fingerprint hash: 9c0d4ee90572e3356811436bc490de13fb82fc1393c63aa5774b36fd05154f34
generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
exact A2-to-B1 diff: CLEAN
_MOCs: excluded
```

Hosted CI did not execute because the Issue #354 jobs contain zero steps. That is infrastructure evidence only: neither behavioral PASS nor behavioral FAIL.

PR #356 merged as `969c369b453fffca0eb2b8dad65ff3f285df8fbc`; post-B1 sync #357 merged as `864ceba9747384b3bdca4a693dca938b3899864e`; B2 merged through PR #358 as `e84a9d55f8575c687765b1df19e8f794b180599b`; post-B2 sync #359 established the B3 base `b1dad94e08e2d01b1cd7f0cf43981cff80b0de2e`. B3 merged through PR #360 at reviewed head `3e8a68aa5d17712fbb2106f052e309a2f33e120e`; squash merge `8cc67213bd7e06e862d50bc2c1bf29d8ac72f064` completed B3. Post-B3 sync #361 established B4 base `bb99a5edbc9397d6b96b91fe0e9fe01bf57f9bd1`. B4 merged through PR #362 at reviewed head `7b70a91b3a294e829a36edac067da7e4b567774e`; squash merge `5c243a822f79ea09b0031124d4bafbf32d18842c` completed B4. Post-B4 sync #363 merged as `404689ef07f42480966c59ba30c07db5c4f101e1`, the Wave C initial candidate. Wave C merged through PR #364; `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915` is the immutable `validated_baseline_sha`. PR #365, PR #366, and PR #378 subsequently advanced documentation/truth state only. #388 is complete and its truth-checker prerequisite is satisfied; #368 is next, and #387 follows #368. PR #335 reconstruction remains pending a separate owner decision and is not authorized; Google domain work and Operational Continuity runtime remain blocked.

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
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
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

Do not infer that a generated PASS proves behavior the generator does not measure. Do not infer that a historical proof packet is current proof. Do not mark unexecuted test definitions as passing evidence. Do not call a candidate baseline validated until the required Wave C proof package has completed. Do not treat the PASS on `f44cb8b8...` as proof of a later corrected branch head.

## Continuity Boundary

Operational Continuity remains strategically accepted but implementation-inactive.

Continuity may preserve/reconcile/project state, but it may never:

- authorize;
- execute;
- change permission;
- manufacture commitments;
- silently reopen decisions;
- convert learned behavior into authority.

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
- reopen B2, B3, B4, or Wave C without concrete new evidence, or start #335 reconstruction, Google domain work, or Continuity runtime without a later authorizing owner decision;
- manually edit generated runtime artifacts;
- publish `_MOCs/*` as part of B1 without separate review/authorization;
- direct work from a stale `current`, `next`, or `active` statement without checking the current truth surfaces first.

## Repo Truth Rule

Code is authoritative for implemented behavior. Tests and proof artifacts are evidence for the revisions/environments/scopes they actually cover. Generated runtime surfaces are authoritative for the exact mechanically measured claims they report. Hand-maintained operational docs establish current ordering and interpretation, but may go stale and must be reconciled when the repository changes.
