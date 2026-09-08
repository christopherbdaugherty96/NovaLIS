# Current Priority

## Post-#405 beta-readiness truth — 2026-09-03

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
verified main at sync start: df2df490083511f480b653c0960fbe7a6e6abfe8

#397 through #405: COMPLETE / MERGED
daily operating loop: STABLE
startup health truth: VERIFIED
Home activity usefulness: LIVE-ACCEPTED BEFORE/AFTER RESTART

NEXT: #406 governed-memory ID collision correctness
THEN: #408 durability/state-ownership decision
THEN: evidence-authorized durability implementation
THEN: bounded product-translation/readiness pass
THEN: clean Windows operator proof
THEN: frozen-SHA full beta acceptance
THEN: private-beta candidacy/distribution decision
```

Keep #406 bounded to deterministic unique memory identity, collision regression
coverage, unambiguous ID-addressed mutation, and explicit handling of existing
duplicate persisted IDs. It does not authorize a memory redesign.

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. Intelligence remains separate from authority. This truth sync
does not grant new execution authority. Older priority text below is historical
wherever it conflicts with this block.

## Post-#394 truth — 2026-08-28

```text
#388: COMPLETE
#368: COMPLETE
#387: COMPLETE / DOCS-ONLY
#393: COMPLETE / EXACT-HEAD PROOF POLICY
#394: GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
verified repository head at sync start: 691a397d14e93c1e0607a73de2ab54b9bbfc3cc2

Historical PR #335: OPEN / DRAFT / UNMERGED / UNTOUCHED
Implementation path: SUPERSEDED BY MERGED PR #394
Use #335 as historical reference only; do not reconstruct or merge it.

NEXT AUTHORIZED INPUT: Google identity-only live proof against the merged #394 foundation.
LATER, SEPARATELY AUTHORIZED: Google Tasks READ -> minimal Continuity -> owner daily-use proof.
```

The identity proof is proof-only: connect, confirm account identity and exact scopes, verify
encrypted credential storage and status, exercise refresh/reconnect/revoke/disconnect, and check
that tokens never leak. It adds no capability and authorizes no Google domain-data access.
Google Tasks READ, Continuity implementation, Gmail, Google writes, external writes, and broader
authority remain unstarted and require their own reviewed authorization.

## Historical pre-#394 handoff (superseded by the block above)

## Post-Wave-C Documentation Closeout — COMPLETE — 2026-08-25

Current planning lane:

```text
B2: COMPLETE / MERGED
B3: COMPLETE / MERGED
B4: COMPLETE / MERGED
WAVE C: COMPLETE / MERGED / VALIDATED
POST-WAVE-C DOCUMENTATION CLOSEOUT: COMPLETE
truth-hygiene provenance: PR #366 MERGED
narration/front-door package: PR #378 MERGED
#388: COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
#368: COMPLETE
#387: COMPLETE / DOCS-ONLY
PR #335 implementation path: SUPERSEDED BY MERGED PR #394
PR #335 state: OPEN / DRAFT / UNMERGED
post_wave_c_sync_sha: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
post_closeout_narration_merge_sha: 67c3d8fd10e013eef466769cd4c8d96f75d27845
validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
```

Handoff anchors:

```text
Wave C initial candidate: 404689ef07f42480966c59ba30c07db5c4f101e1
B1 reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
B1 generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
B1 PR #356: MERGED
B2 reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
B2 PR #358: MERGED
B2 squash merge: e84a9d55f8575c687765b1df19e8f794b180599b
post-B2 sync #359 merge: b1dad94e08e2d01b1cd7f0cf43981cff80b0de2e
B3 reviewed head: 3e8a68aa5d17712fbb2106f052e309a2f33e120e
B3 PR #360: MERGED
B3 squash merge: 8cc67213bd7e06e862d50bc2c1bf29d8ac72f064
post-B3 sync #361 merge: bb99a5edbc9397d6b96b91fe0e9fe01bf57f9bd1
B4 reviewed head: 7b70a91b3a294e829a36edac067da7e4b567774e
B4 PR #362: MERGED
B4 squash merge: 5c243a822f79ea09b0031124d4bafbf32d18842c
post-B4 sync #363 merge: 404689ef07f42480966c59ba30c07db5c4f101e1
Wave C PR #364: MERGED
PR #364 reviewed head: 786c048df6dc4ed8f3c8245c5b365d4296f342f4
PR #364 squash merge / validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
PR #365 documentation sync / PR #366 branch base: d5b0dc66259274076b8b7e1a8501bc8fee6b2e2c
PR #366: MERGED / post-Wave-C truth-hygiene contract package
PR #366 squash merge: 4ddd46ad0c3e3c5db55e006680f4a426956581c1
PR #378 reviewed head: 84222288335c399c1ffa73186858e8ba84e9a64a
PR #378: MERGED / narration-front-door closeout package
PR #378 squash merge: 67c3d8fd10e013eef466769cd4c8d96f75d27845
```

B1 through B4 and Wave C are complete and merged. Their proof, generated truth, operational synchronization, and review records remain evidence only for the revisions and environments actually exercised. The complete Wave C non-hosted proof passed on exact validated baseline `ec20a714...`; the owner waived GitHub-hosted Actions as a required evidence source while preserving their `NOT EXECUTED` classification. PR #365, PR #366, and PR #378 later advanced `main` with documentation/truth synchronization only and did not establish a new runtime validated baseline.

## Completed gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622

Wave B1 — MERGED via PR #356
  reviewed head: 381dbaeca73786f789cc6e68fd3b6bf193296041
  squash merge: 969c369b453fffca0eb2b8dad65ff3f285df8fbc
  proof / generated truth / operational truth / final review: COMPLETE

Wave B2 — MERGED via PR #358
  reviewed head: b95039c2dc483ad330205de5dac8e3b3f94d8836
  squash merge: e84a9d55f8575c687765b1df19e8f794b180599b
  capability narration projection / consumer migration / review: COMPLETE

Wave B3 — MERGED via PR #360
  reviewed head: 3e8a68aa5d17712fbb2106f052e309a2f33e120e
  squash merge: 8cc67213bd7e06e862d50bc2c1bf29d8ac72f064
  bounded memory truth / provenance / review: COMPLETE

Wave B4 — MERGED via PR #362
  reviewed head: 7b70a91b3a294e829a36edac067da7e4b567774e
  squash merge: 5c243a822f79ea09b0031124d4bafbf32d18842c
  canonical dependency truth / compatibility projection / install proof: COMPLETE
```

Issue #354 remains open as a separate account/billing infrastructure issue. Its zero-step jobs are neither behavioral PASS nor behavioral FAIL. The owner waived hosted execution as a mandatory Wave C exit source; the issue is not Nova runtime evidence.

## B1 completed evidence

```text
Ruff: PASS
focused B1 tests: 13 PASS
auditor/governance tests: 29 PASS
operational consistency: PASS before/after generation
runtime-doc drift: PASS before/after generation
scope_version: behaviorally_active_v2
runtime_surface_file_count: 230 existing files
runtime_surface_hash: c5cadfeff5db3e22fea0f1c2efeb05016765c20bb7cd24e33ad758361fd9acd9
runtime_fingerprint_hash: 9c0d4ee90572e3356811436bc490de13fb82fc1393c63aa5774b36fd05154f34
generated-artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
_MOCs: excluded
exact A2-to-B1 diff: CLEAN
```

## Historical action — Issue #368 bounded technical lane (complete)

This historical section records the pre-#394 decision boundary. Issues #368 and #387 are now complete, and merged PR #394 superseded PR #335 as the implementation path.

This state transition does not authorize runtime, generated-artifact, capability, OAuth/Google, #335, Google domain-data, OpenClaw-authority, provider-routing, external-write, or Operational Continuity changes.

The merged B2 projection preserves these distinct fields:

```text
exists
enabled
configured
verification_status
available_on_this_path
requires_approval
authority_class
```

`authorized` remains request-specific, not static capability metadata. Connection, capability, OAuth scope, and Nova authority remain distinct.

B3 is complete: ordinary chat no longer silently creates authoritative personal memory; explicit and observed memory remain distinct; provenance, confidence, conflict, supersession, and promotion semantics remain visible. Superseded history is not current memory.

B4 is complete: `pyproject.toml` is canonical dependency truth; requirements-style compatibility surfaces are mechanically checked; the historical `python-multipart` mismatch is resolved; and the supported install path was proven on the reviewed B4 revision. Do not reopen or redesign packaging without new evidence.

Wave C is complete. Exact validated-baseline proof passed and `validated_baseline_sha` is `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915`. PR #365, #366, and #378 are later documentation/truth provenance and are not new runtime validated baselines. Documentation closeout is complete at this revision, but #335 reconstruction still requires a later separate owner decision.

## Google Foundation / CI state

PR #335 remains:

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Do not modify, reconstruct, rebase, or merge historical PR #335; merged PR #394 supersedes that implementation path.

Issue #354 remains:

```text
infrastructure/open
zero-step hosted Actions
not behavioral pass/fail evidence
external account/billing limitation
owner-waived as mandatory Wave C exit evidence
```

## Ordered sequence

```text
B1 COMPLETE / MERGED
-> B2 capability narration / COMPLETE / MERGED
-> B3 memory governance / COMPLETE / MERGED
-> B4 reproducibility hygiene / COMPLETE / MERGED
-> Wave C proof / semantic-contract stabilization / COMPLETE / MERGED / VALIDATED
-> post-Wave-C truth-hygiene provenance / PR #366 / COMPLETE / MERGED
-> narration/front-door closeout package / PR #378 / COMPLETE / MERGED
-> post-Wave-C documentation closeout / COMPLETE
-> #388 / COMPLETE / TRUTH-CHECKER PREREQUISITE SATISFIED
-> #368 / COMPLETE
-> #387 / COMPLETE / DOCS-ONLY
-> #393 / COMPLETE / EXACT-HEAD PROOF POLICY
-> #394 / GOOGLE WORKSPACE FOUNDATION COMPLETE / MERGED
-> historical PR #335 implementation path / SUPERSEDED BY MERGED PR #394
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

B1 through B4, Wave C, the post-Wave-C documentation closeout, Issues #388/#368/#387, the #393 proof policy, and the #394 Google Workspace Foundation are complete. Historical PR #335 is not a current lane and must not be reconstructed.

## Scope lock

Wave C authorization and the bounded documentation-closeout work are complete and closed at this revision. This completion sync does not authorize broader post-Wave-C work. Do not reopen Wave C or begin the next substantive engineering lane without separate authorization:

```text
memory architecture beyond the completed B3 truth/provenance repair
dependency modernization, unrelated upgrades, or packaging redesign beyond completed B4
Wave C reopening, capability expansion, or repairs without reproduced evidence
network behavior / NetworkMediator wiring
capability registry
OAuth / #335
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
README/front-door rewrite outside separately reviewed documentation closeout
_MOCs publication / Obsidian overlay refresh
```

## Permanent truth boundaries

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
request acceptance != verified effect
memory != Operational Continuity
current HEAD != immutable validated baseline
```

Generated evidence is authoritative only for what its generator mechanically measures. Tests prove only the revision/environment/scope actually exercised. A proof PASS on `f44cb8b8...` does not automatically prove a later corrective head.
