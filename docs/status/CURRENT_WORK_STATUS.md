# Nova Current Work Status

Last reviewed: 2026-08-23.

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
WAVE B1 — runtime-truth instrumentation
STATUS: CORRECTIVE PROOF / GENERATION COMPLETE; FINAL PR REVIEW / MERGE DECISION
BRANCH: codex/b1-runtime-truth-instrumentation-20260820
POST-A2 BASE: 060380f2e8c6437ff888773f0078647547ff4622
FINAL CORRECTED ARTIFACT COMMIT: e668ec0c09df6e0d304427431e95a26619a9f507
DRAFT PR: #356 — OPEN / DRAFT
MERGE: NOT AUTHORIZED
```

The A2 base is a planning/comparison checkpoint, not a validated baseline. `f44cb8b8...` completed the first B1 publication pass. Final release review then found two bounded truth-integrity defects. Both are corrected, the corrected artifacts were published at `e668ec0c...`, and the exact A2-to-B1 diff review is clean. A later docs-only synchronization commit may advance branch HEAD; `e668ec0c...` remains the generated-artifact evidence commit.

## Completed Gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622

Wave B1 first exact-head proof/publication pass
  candidate: f44cb8b856345ddc573fe0cb56037104350ffeb4
  draft PR #356 opened
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
```

## B1 Current Substate

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

## Remaining B1 Gate

```text
[ ] final PR #356 review / evidence assessment
[ ] separate owner-authorized merge decision
```

Hosted CI remains NOT EXECUTED because the Issue #354 jobs contain zero steps. That result is neither behavioral PASS nor behavioral FAIL. No known B1 code blocker remains.

## Scope Lock

B1 does not change:

```text
network behavior / connections_api.py wiring
capability narration semantics (B2)
GeneralChat persistence behavior (B3)
dependency-source truth (B4)
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

Do not modify or merge #335 during B1.

Issue #354 remains:

```text
infrastructure/open
zero-step hosted GitHub Actions
not behavioral pass/fail evidence
must be resolved before Wave C relies on hosted CI
```

## Current Ordering

```text
B1 final PR #356 review -> separate merge decision
-> B2 capability narration
-> B3 memory governance
-> B4 reproducibility hygiene
-> Wave C semantic/proof stabilization and validated baseline
-> reconstruct #335 onto exact validated baseline
-> independent security/architecture review
-> separate #335 merge decision
-> Google identity-only live proof
-> Google Tasks READ / first real provider-backed Google evidence vertical
-> evidence-based Continuity warrant
```

B2/B3/B4 remain blocked.

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
