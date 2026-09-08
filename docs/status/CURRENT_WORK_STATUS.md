# Nova Current Work Status

Last reviewed: 2026-09-03.

## Current post-#405 beta-readiness status

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
verified main at sync start: df2df490083511f480b653c0960fbe7a6e6abfe8
#397 through #405: COMPLETE / MERGED
NEXT: #406 governed-memory ID collision correctness
THEN: #408 durability/state-ownership decision
THEN: evidence-authorized durability implementation
THEN: bounded product-translation/readiness pass
THEN: clean Windows operator proof
THEN: frozen-SHA full beta acceptance
THEN: private-beta candidacy/distribution decision
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This
current block supersedes older ordering language below.

## Current post-#394 status

```text
#388 COMPLETE
#368 COMPLETE
#387 COMPLETE / DOCS-ONLY
#393 COMPLETE / EXACT-HEAD PROOF POLICY
#394 GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
main at reconciliation start: 691a397d14e93c1e0607a73de2ab54b9bbfc3cc2

PR #335: OPEN / DRAFT / UNMERGED / UNTOUCHED
PR #335 implementation path: SUPERSEDED BY MERGED PR #394

NEXT AUTHORIZED INPUT: Google identity-only live proof
FUTURE, NOT YET AUTHORIZED: Google Tasks READ -> minimal Continuity -> owner daily-use proof
```

No new capability, Google domain-data access, external write, or authority expansion is active.
The remainder of this document is retained as historical evidence; where its older current/next
language conflicts with this block, this block wins.

## Historical pre-#394 work status

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
TRUTH-HYGIENE PROVENANCE: PR #366 MERGED
NARRATION/FRONT-DOOR PACKAGE: PR #378 MERGED
POST_CLOSEOUT_NARRATION_MERGE_SHA: 67c3d8fd10e013eef466769cd4c8d96f75d27845
VALIDATED_BASELINE_SHA: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
WAVE C: COMPLETE / MERGED / VALIDATED
PR #364 REVIEWED HEAD: 786c048df6dc4ed8f3c8245c5b365d4296f342f4
B1: COMPLETE / MERGED via PR #356
B2: COMPLETE / MERGED via PR #358
B3: COMPLETE / MERGED via PR #360
B4: COMPLETE / MERGED via PR #362
#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368: COMPLETE
#387: COMPLETE / DOCS-ONLY
#393: COMPLETE / EXACT-HEAD PROOF POLICY
#394: GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
PR #335 IMPLEMENTATION PATH: SUPERSEDED BY MERGED PR #394
PR #335 STATE: OPEN / DRAFT / UNMERGED
```

B1 is complete and merged. PR #356's reviewed head was `381dbaec...`; its generated-artifact evidence commit remains `e668ec0c...`; its squash merge was `969c369b...`. Post-B1 operational truth sync #357 merged as `864ceba9...`. B2 then merged through PR #358 at reviewed head `b95039c2...`; its squash merge was `e84a9d55...`. Post-B2 sync #359 merged as `b1dad94e...`. B3 merged through PR #360 at reviewed head `3e8a68aa...`; its squash merge was `8cc67213...`. Post-B3 sync #361 established B4 base `bb99a5ed...`. B4 merged through PR #362 at reviewed head `7b70a91b...`; squash merge `5c243a82...` completed B4. Post-B4 sync #363 established `404689ef...` as the Wave C initial candidate. Wave C merged through PR #364 and established `ec20a714...` as the immutable validated runtime baseline. PR #365, PR #366, and PR #378 later advanced `main` with documentation/truth synchronization only. None established a new runtime validated baseline; PR #378's squash merge `67c3d8fd...` is post-closeout narration provenance, not a replacement for `validated_baseline_sha`.

## Completed Gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622

Wave B1 first exact-head proof/publication pass
  candidate: f44cb8b856345ddc573fe0cb56037104350ffeb4
  PR #356 first publication occurred (historical)
  local Ruff / focused tests / auditor-governance tests / consistency / drift: PASS
  hosted behavioral proof: NOT EXECUTED because Issue #354 jobs ran zero steps

Wave B1 corrected proof/publication pass
  corrected source proof: PASS
  generated artifacts: e668ec0c09df6e0d304427431e95a26619a9f507
  Ruff: PASS
  focused B1 tests: 13 PASS
  auditor/governance tests: 29 PASS
  operational consistency + runtime-doc drift: PASS before/after generation
  exact A2-to-B1 diff: CLEAN
  _MOCs: excluded

Wave B1 merge
  PR #356: MERGED
  reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
  squash merge: 969c369b453fffca0eb2b8dad65ff3f285df8fbc

Wave B2 merge
  PR #358: MERGED
  reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
  squash merge: e84a9d55f8575c687765b1df19e8f794b180599b

Wave B3 merge
  PR #360: MERGED
  reviewed head: 3e8a68aa5d17712fbb2106f052e309a2f33e120e
  squash merge: 8cc67213bd7e06e862d50bc2c1bf29d8ac72f064

Post-B3 operational truth synchronization
  PR #361: MERGED
  merge/B4 base: bb99a5edbc9397d6b96b91fe0e9fe01bf57f9bd1

Wave B4 merge
  PR #362: MERGED
  reviewed head: 7b70a91b3a294e829a36edac067da7e4b567774e
  squash merge: 5c243a822f79ea09b0031124d4bafbf32d18842c

Post-B4 operational truth synchronization
  PR #363: MERGED
  merge/Wave C initial candidate: 404689ef07f42480966c59ba30c07db5c4f101e1

Wave C validated baseline
  PR #364: MERGED
  reviewed head: 786c048df6dc4ed8f3c8245c5b365d4296f342f4
  squash merge/validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
  exact-baseline non-hosted proof: PASS
  hosted Actions: NOT EXECUTED / owner-waived as mandatory Wave C exit evidence

Post-Wave-C documentation synchronization
  PR #365: MERGED
  merge/#366 branch base: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
  runtime baseline change: NONE

Post-Wave-C truth-hygiene contract
  PR #366: MERGED
  squash merge: 4ddd46ad0c3e3c5db55e006680f4a426956581c1
  runtime baseline change: NONE

Post-Wave-C narration/front-door closeout
  PR #378: MERGED / VERIFIED ON MAIN
  squash merge: 67c3d8fd10e013eef466769cd4c8d96f75d27845
  runtime baseline change: NONE
```

## B1 Completed Evidence

Final release review found and the bounded correction closed:

```text
P1  active B1 handoff surfaces still described the pre-generation/no-PR state
P2  runtime_surface_file_count counted one nonexistent ALLOWED_READ_PATHS entry
```

Completed correction and evidence:

```text
✓ fingerprinted runtime-surface set now requires path.exists()
✓ runtime_surface_file_count therefore describes existing files in the exact hash set
✓ focused regression requires every fingerprinted path to exist
✓ missing ALLOWED_READ_PATHS entries are excluded from the fingerprinted set
✓ corrected generation uses behaviorally_active_v2 over 230 existing files
✓ runtime_surface_hash = c5cadfeff5db3e22fea0f1c2efeb05016765c20bb7cd24e33ad758361fd9acd9
✓ runtime_fingerprint_hash = 9c0d4ee90572e3356811436bc490de13fb82fc1393c63aa5774b36fd05154f34
```

The generated runtime artifacts were mechanically regenerated on the corrected source state. `CURRENT_RUNTIME_STATE.md` and `RUNTIME_FINGERPRINT.md` changed; `BYPASS_SURFACES.md` regenerated identically. The artifact commit is `e668ec0c...`. Manual edits remain forbidden.

## Completed B2 Lane

```text
B2 — capability narration
status — COMPLETE / MERGED via PR #358
result — shared seven-field non-authorizing truth projection and reviewed consumer migration
```

Hosted CI remains governed by Issue #354: its zero-step jobs are neither behavioral PASS nor behavioral FAIL. The issue remains open as an external account/billing limitation. The owner waived this evidence source for Wave C without marking it PASS.

## Completed B3 Lane

```text
B3 — memory governance
status — COMPLETE / MERGED via PR #360
result — ordinary chat does not silently create authoritative durable memory; explicit/observed provenance and precedence remain visible; superseded history is not current memory
```

Historical B3 evidence remains valid for the reviewed revision and environment. Do not reopen or redesign B3 without concrete new evidence.

## Completed B4 Lane

```text
B4 — reproducibility hygiene
status — COMPLETE / MERGED via PR #362
result — pyproject.toml is canonical dependency truth; requirements surfaces are mechanically checked compatibility projections; the historical python-multipart mismatch is resolved
```

Historical B4 proof remains valid for the reviewed revision and environment. Do not reopen packaging or dependency-source design without concrete new evidence.

## Scope Lock

The completed post-Wave-C documentation closeout did not change:

```text
runtime behavior
network behavior / connections_api.py wiring
capability narration semantics
GeneralChat persistence behavior
dependency-source truth
capability registry
OAuth / PR #335 implementation
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
generated runtime artifacts
```

PR #366 and PR #378 completed bounded truth/narration synchronization only. Their merge does not widen authority or activate the next engineering lane.

## PR #335 / Issue #354

PR #335 remains:

```text
OPEN
DRAFT
UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Documentation closeout, Issues #388/#368/#387, the #393 proof policy, and the merged #394 Google Workspace Foundation are complete. Historical PR #335 is superseded as an implementation path.

Issue #354 remains:

```text
infrastructure/open
zero-step hosted GitHub Actions
not behavioral pass/fail evidence
external account/billing limitation
owner-waived as mandatory Wave C exit evidence
```

## Current Ordering

```text
A1 / A2 / B1 / B2 / B3 / B4 / Wave C        COMPLETE
post-Wave-C truth-hygiene / PR #366             COMPLETE / MERGED
post-Wave-C narration/front-door / PR #378      COMPLETE / MERGED / VERIFIED
post-Wave-C documentation closeout              COMPLETE
#388                                             COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368                                             COMPLETE
#387                                             COMPLETE / DOCS-ONLY
#393                                             COMPLETE / EXACT-HEAD PROOF POLICY
#394                                             GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
PR #335 implementation path                      SUPERSEDED BY MERGED PR #394
```

Historical PR #335 must not be reconstructed or merged; PR #394 is the merged implementation path. Google identity-only live proof is next. Google Tasks READ and any evidence-based Operational Continuity warrant remain later, separately authorized steps.

`ec20a7146f7d6d55b8983cb7d6d3918d5fad9915` remains the immutable validated runtime baseline. PR #366 and PR #378 are later documentation/truth provenance and do not establish a new runtime validation baseline or authorize #335 reconstruction.

## Permanent Truth Boundaries

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
```

Generated evidence is authoritative only for what the generator actually measures. Historical or unexecuted test definitions are not current proof. A previously passing candidate does not automatically prove a later corrective head.
