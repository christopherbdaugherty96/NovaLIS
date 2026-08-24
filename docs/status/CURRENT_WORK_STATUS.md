# Nova Current Work Status

Last reviewed: 2026-08-24.

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
WAVE C — proof / validated-baseline checkpoint
STATUS: COMPLETE / MERGED / VALIDATED
INITIAL CANDIDATE: 404689ef07f42480966c59ba30c07db5c4f101e1
PR #364: MERGED
REVIEWED HEAD: 786c048df6dc4ed8f3c8245c5b365d4296f342f4
CURRENT MAIN / VALIDATED_BASELINE_SHA: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
B1: COMPLETE / MERGED via PR #356
B2: COMPLETE / MERGED via PR #358
B3: COMPLETE / MERGED via PR #360
B4: COMPLETE / MERGED via PR #362
```

B1 is complete and merged. PR #356's reviewed head was `381dbaec...`; its generated-artifact evidence commit remains `e668ec0c...`; its squash merge was `969c369b...`. Post-B1 operational truth sync #357 merged as `864ceba9...`. B2 then merged through PR #358 at reviewed head `b95039c2...`; its squash merge was `e84a9d55...`. Post-B2 sync #359 merged as `b1dad94e...`. B3 merged through PR #360 at reviewed head `3e8a68aa...`; its squash merge was `8cc67213...`. Post-B3 sync #361 established B4 base `bb99a5ed...`. B4 merged through PR #362 at reviewed head `7b70a91b...`; squash merge `5c243a82...` completed B4. Post-B4 sync #363 established `404689ef...` as the Wave C initial candidate. Wave C merged through PR #364; `ec20a714...` is current `main` and the validated baseline. Earlier evidence remains revision- and environment-specific historical evidence.

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
  squash merge/current main/validated_baseline_sha: ec20a7146f7d6d55b8983cb7d6d3918d5fad9915
  exact-main non-hosted proof: PASS
  hosted Actions: NOT EXECUTED / owner-waived as mandatory Wave C exit evidence
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

B1 does not change:

```text
network behavior / connections_api.py wiring
capability narration semantics (B2)
GeneralChat persistence behavior (B3)
dependency-source truth beyond completed B4
capability registry
OAuth / PR #335 implementation
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
README/front-door rewrite
```

README sequencing drift is separate documentation debt and must not be folded into B1.

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

Do not modify or merge #335 before a separate reconstruction authorization.

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
B1 COMPLETE / MERGED
-> B2 capability narration / COMPLETE / MERGED
-> B3 memory governance / COMPLETE / MERGED
-> B4 reproducibility hygiene / COMPLETE / MERGED
-> Wave C semantic/proof stabilization and validated baseline / COMPLETE / MERGED / VALIDATED
-> reconstruct #335 onto exact validated baseline / NEXT / NOT AUTHORIZED
-> independent security/architecture review
-> separate #335 merge decision
-> Google identity-only live proof
-> Google Tasks READ / first real provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

B1 through B4 and Wave C are complete and merged. `ec20a7146f7d6d55b8983cb7d6d3918d5fad9915` is the validated baseline. #335 reconstruction is next but not implementation-authorized.

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
