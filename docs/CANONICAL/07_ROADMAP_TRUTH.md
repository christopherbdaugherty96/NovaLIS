# 07 — Roadmap Truth

**Status: current ordering summary.**

This file does not redesign Nova's roadmap. It reconciles the current stabilization gate around the existing roadmap and points to the master ordering document.

## Ordering authority

- [`../future/NOVA_MASTER_ROADMAP_2026-07-05.md`](../future/NOVA_MASTER_ROADMAP_2026-07-05.md) remains the long-lived ordering authority.
- Issue #343 is the current detailed stabilization checkpoint/order.
- Lane-specific lock/spec documents remain scope authority for their lane.
- Explicit reviewed owner authorization remains required to activate implementation where the governing lane requires it.

Ordering and scope are distinct:

```text
roadmap / Issue #343 -> what comes before what
lane contract         -> what the lane may change
implementation/proof  -> what actually changed and was verified
```

## Current checkpoint — 2026-08-25

Wave C is COMPLETE / MERGED / VALIDATED. The current active lane is the documentation-only post-Wave-C truth-hygiene pass in draft PR #366. PR #335 reconstruction remains next but not authorized by this synchronization.

```text
A1 — COMPLETE / MERGED via #353
A2 — COMPLETE / MERGED via #355
B1 — COMPLETE / MERGED via #356
B2 — COMPLETE / MERGED via #358
B3 — COMPLETE / MERGED via #360
B4 — COMPLETE / MERGED via #362
C  — COMPLETE / MERGED / VALIDATED
#365 — MERGED post-Wave-C documentation sync
#366 — ACTIVE / DRAFT / documentation-current-truth only
#335 reconstruction — NEXT / NOT AUTHORIZED
```

Immutable runtime validation evidence:

```text
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

Post-Wave-C documentation provenance:

```text
PR #365 merge / PR #366 branch base: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
```

`d5b0dc66...` is durable provenance for PR #365 and this truth-hygiene branch base, not a forever-current `main` claim. Resolve current HEAD from Git/repository state when needed. `ec20a714...` remains the immutable Wave C validated baseline unless a separately warranted future validation package establishes another baseline.

First published/proven B1 candidate:

```text
f44cb8b856345ddc573fe0cb56037104350ffeb4
```

That candidate completed the first exact-head local proof, mechanical runtime-doc generation, artifact publication, and remote scope review. It remains historical evidence rather than a `validated_baseline_sha`; PR #356 later merged through the corrected final package recorded below.

Final release review then found two bounded B1 truth-integrity defects:

```text
P1 — active handoff surfaces still described the pre-generation/no-PR state
P2 — runtime_surface_file_count included one nonexistent ALLOWED_READ_PATHS entry
```

Both bounded defects were corrected. The corrected source proof passed, mechanical generation completed, and the generated artifacts were published at `e668ec0c09df6e0d304427431e95a26619a9f507`. PR #356 merged at reviewed head `381dbaeca73786f789cc6e68fd3b6bf193296041`; squash merge `969c369b453fffca0eb2b8dad65ff3f285df8fbc` completed B1. Post-B1 operational truth sync #357 then merged as `864ceba9747384b3bdca4a693dca938b3899864e`. B2 merged through PR #358 at reviewed head `b95039c2dc483ad330205de5dac8e3b3f94d8836`; squash merge `e84a9d55f8575c687765b1df19e8f794b180599b` completed B2. Post-B2 sync #359 established B3 base `b1dad94e08e2d01b1cd7f0cf43981cff80b0de2e`. B3 merged through PR #360 at reviewed head `3e8a68aa5d17712fbb2106f052e309a2f33e120e`; squash merge `8cc67213bd7e06e862d50bc2c1bf29d8ac72f064` completed B3. Post-B3 sync #361 established B4 base `bb99a5edbc9397d6b96b91fe0e9fe01bf57f9bd1`. B4 merged through PR #362 at reviewed head `7b70a91b3a294e829a36edac067da7e4b567774e`; squash merge `5c243a822f79ea09b0031124d4bafbf32d18842c` completed B4. Post-B4 sync #363 merged as `404689ef07f42480966c59ba30c07db5c4f101e1`, the Wave C initial candidate.

Wave C merged through PR #364 at reviewed head `786c048df6dc4ed8f3c8245c5b365d4296f342f4`. Its squash merge `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915` passed the complete non-hosted proof and is the immutable `validated_baseline_sha`. GitHub-hosted jobs remained `NOT EXECUTED` due to the account-billing restriction in Issue #354; the owner explicitly waived that evidence source without classifying it as PASS. PR #365 then merged documentation-only synchronization at `d5b0dc66...`; it did not change or extend the validated runtime evidence.

## Merged stabilization state

The following August truth/routing packages are already merged and are not pending roadmap items:

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session action/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit weather-location preservation / WebSocket repair
#345         brightness outcome truth
#346         turn-down-volume routing/wording
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
#365         post-Wave-C validated-baseline/evidence-waiver documentation sync
```

Merged implementation is not identical to universal product readiness or unlimited live-proof scope. Capability verification must remain evidence-specific.

## Google Workspace Foundation state

PR #335 remains:

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

It must not be merged in its historical branch state. After PR #366 truth hygiene is reviewed and a separate owner authorization is given, #335 may be reconstructed/reconciled against exact validated baseline `ec20a714...`, then undergo exact-head proof and independent review before a separate merge decision.

## Current stabilization gate

The roadmap itself remains intact. The current gate is:

```text
WAVE A — truth reconciliation
  A1 operational truth synchronization              COMPLETE
  A2 strategy reconciliation                        COMPLETE

WAVE B — truth-integrity repairs
  B1 runtime-truth instrumentation                  COMPLETE / MERGED
  B2 capability narration                           COMPLETE / MERGED
  B3 memory governance                              COMPLETE / MERGED
  B4 reproducibility hygiene                        COMPLETE / MERGED

WAVE C — proof and stabilization checkpoint         COMPLETE / MERGED / VALIDATED
  exact candidate baseline
  repaired runtime-truth regeneration
  supported proof matrix
  semantic-contract regression
  current local-inference benchmark / Issue #227
  reproduced-defect-only fixes
  immutable validated baseline

POST-WAVE-C — truth hygiene                         ACTIVE / DRAFT #366
  separate current HEAD/provenance from validated baseline
  reconcile active operational/roadmap surfaces
  no runtime, generated-runtime, authority, or Google implementation changes

POST-WAVE-C — Google Foundation reconciliation      NEXT / NOT AUTHORIZED
  reconstruct #335
  OAuth hardening cases
  exact-head #335 verification
  independent security/architecture review
  separate merge decision
```

After truth hygiene and only after a separate #335 merge decision:

```text
Google identity-only live proof
-> Google Tasks READ / first real provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

## Wave A1 — completed gate

A1 synchronized active operational/canonical truth against the already-merged August stabilization work and corrected the three-control-plane/current-truth doctrine.

A1 changed documentation/current-truth surfaces only. It did not authorize later runtime lanes.

## Wave A2 — completed strategy reconciliation

A2 separately reconciled the consolidated August Product/Platform strategy against the truthful operational baseline while keeping strategy and current-state documentation distinct.

The durable strategy package is:

```text
NOVA_PRODUCT_PLATFORM_DIRECTION_2026-08-17.md
NOVA_PRODUCT_VALIDATION_PROTOCOL_2026-08-17.md
NOVA_STRATEGIC_DOCUMENT_STATUS_INDEX_2026-08-17.md
```

The governed-protection-wall concept remains long-term security/digital-sovereignty reference material. It does not silently become present roadmap authority or replace Nova's current product identity.

## Wave B — truth-integrity repairs

Wave B is intentionally split into focused PRs rather than one broad stabilization branch.

### B1 — runtime-truth instrumentation

**Complete / merged via PR #356.**

B1 source/truth-harness work covers:

```text
requests-based network discrepancy visibility
connections_api.py explicit local_administrative_health_probe classification
Phase 9 live import/symbol evidence
behaviorally_active_v2 fingerprint coverage
existing-file exact hash/count path-set semantics
qualified generated invariants/network wording
operational-truth consistency checker
canonical-index lane checking + regression
generator-entrypoint integration regression
```

Corrected final evidence:

```text
local Ruff / focused B1 tests / auditor-governance tests: PASS
operational consistency + runtime-doc drift: PASS before/after generation
focused B1 tests: 13 PASS
auditor/governance tests: 29 PASS
generated-output review: PASS
generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
scope_version: behaviorally_active_v2
runtime_surface_file_count: 230 existing files
runtime_surface_hash: c5cadfeff5db3e22fea0f1c2efeb05016765c20bb7cd24e33ad758361fd9acd9
runtime_fingerprint_hash: 9c0d4ee90572e3356811436bc490de13fb82fc1393c63aa5774b36fd05154f34
_MOCs excluded
PR #356 merged at reviewed head 381dbaeca73786f789cc6e68fd3b6bf193296041
squash merge: 969c369b453fffca0eb2b8dad65ff3f285df8fbc
hosted behavioral proof: NOT EXECUTED because Issue #354 jobs ran zero steps
```

The P1/P2 defects above are corrected and B1 is closed. Its evidence remains historical evidence for the merged B1 package.

Do not manually edit or regenerate the generated runtime artifacts without a concrete new generator defect. `e668ec0c...` remains the final B1 generated-artifact evidence commit.

### B2 — capability narration

**Complete / merged via PR #358.**

The merged B2 package implements only the established non-authorizing narration projection and its reviewed consumers.

Separate:

```text
exists
enabled
configured
verification_status
available_on_this_path
requires_approval
authority_class
```

`authorized` is request-specific and must not be static capability metadata.

### B3 — memory governance

**Complete / merged via PR #360.**

B3 repaired ordinary GeneralChat persistence boundaries and explicit-vs-observed precedence/provenance while preserving confidence, conflict, supersession, promotion, and non-authoritative observed state. Ordinary chat does not silently create authoritative durable personal memory; superseded history is not current memory. The completed lane does not authorize new memory architecture, Continuity, authority, capabilities, or autonomous learning.

### B4 — reproducibility hygiene

**Complete / merged via PR #362.**

B4 established `pyproject.toml` as canonical dependency truth, made `nova_backend/requirements.txt` a mechanically checked compatibility projection, resolved the historical `python-multipart` declaration mismatch, and proved the supported install path on the reviewed B4 revision. This historical completion does not authorize dependency modernization, packaging redesign, runtime behavior changes, or Wave C.

## Wave C — validated-baseline checkpoint

**Complete / merged / validated.**

Wave C turned the initial candidate into a validated baseline after reproduced repairs merged and the complete non-hosted proof passed on exact validated baseline `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`. The owner waived GitHub-hosted execution as a mandatory exit source because Issue #354 is an external account/billing restriction; those zero-step jobs remain `NOT EXECUTED`, not PASS.

Important distinction:

```text
current HEAD != candidate baseline != validated baseline
```

The validated baseline is immutable evidence for a verification package. It is not expected to remain current HEAD forever.

Wave C also re-evaluated Issue #227 using current model/context/hardware/latency evidence rather than May assumptions.

Only reproduced failures were repaired. Acceptance failure must be classified before root cause is assigned.

## Issue #354 — hosted CI infrastructure

Issue #354 remains:

```text
external account/billing infrastructure/open
zero-step hosted GitHub Actions / NOT EXECUTED
not behavioral pass/fail evidence
owner-waived as mandatory Wave C exit evidence
```

This is separate from Nova content/runtime semantics. The owner waiver removed it as a Wave C exit dependency without resolving the account restriction or upgrading hosted jobs to PASS.

## Operational Continuity strategic ordering

Operational Continuity remains **strategically accepted / inactive / not implementation-authorized**.

It is the future product model for persistent reconciled state around Awareness, Decision, Authority, Execution, and Outcome. It is not a sixth authority system.

A future Continuity slice requires its own:

- evidence-based warrant;
- exact scope;
- persistence/provenance contract;
- authority/non-authority boundaries;
- tests;
- implementation authorization;
- fresh-main proof.

Continuity may never:

- authorize;
- execute;
- change permission;
- manufacture commitments;
- silently reopen decisions;
- convert learned behavior into authority.

## Google permanent boundary

```text
Google capability != Google authorization != Nova authority
connected != evidence collected != action permitted
```

OAuth proves provider permission/technical eligibility, not Nova authorization for an exact action.

Google evidence/actions must reuse Nova's provenance, request-acceptance, effect-verification, and outcome distinctions rather than introduce a second success model.

## Deferred until separate post-Wave-C authorization

Do not begin:

```text
Google Tasks domain work
Gmail expansion
Google Calendar writes
Operational Continuity runtime
broad multi-provider routing
large graph/memory infrastructure
predictive learning
multi-agent orchestration
broad browser/computer-use
expanded OpenClaw autonomy
autonomous business operation
broad SaaS productization
Protection Wall runtime expansion
```

README/front-door sequencing cleanup is separate documentation debt and must not be folded into PR #366 unless separately scoped.

## Historical context

The seven-morning observation threshold, grounded brief/category routing, Commitment Truth, Local Action Outcome Truth, Semantic Substrate Slice 1, and the August 12 acceptance-derived P1 repairs are historical inputs to the current state. Their old `current` or `next` wording is superseded by the gate above.

Historical records remain evidence of what was decided or proven at their date. Do not use their old current-main SHAs or pending-work language to select today's work.
