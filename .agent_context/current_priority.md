# Current Priority

## Wave B1 — Final PR Review Gate — 2026-08-23

Current active lane:

```text
WAVE B1 — runtime-truth instrumentation only
SUBSTATE: corrective proof and generation complete; final PR review / merge decision
PR: #356 OPEN / DRAFT
MERGE: NOT AUTHORIZED
```

Handoff anchors:

```text
branch: codex/b1-runtime-truth-instrumentation-20260820
A2 base: 060380f2e8c6437ff888773f0078647547ff4622
first published/proven B1 candidate: f44cb8b856345ddc573fe0cb56037104350ffeb4
final corrected artifact commit: e668ec0c09df6e0d304427431e95a26619a9f507
```

The A2 base is a planning/comparison checkpoint, not a validated baseline. `f44cb8b8...` completed the first exact-head proof, generated-artifact publication, and draft-PR opening. Final release review then found two bounded truth-integrity defects: active operational documents still described the pre-generation/no-PR state, and the fingerprint file count included one nonexistent allowlist path.

Both bounded defects are corrected. Corrected proof passed, mechanical generation completed, the corrected artifacts were published at `e668ec0c...`, and the exact A2-to-B1 diff is clean. A later docs-only synchronization commit may advance branch HEAD; `e668ec0c...` remains the generated-artifact evidence commit.

## Completed gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622

Wave B1 first publication pass
  exact-head local proof: PASS on 3ec075fc...
  generated artifacts committed: f44cb8b856345ddc573fe0cb56037104350ffeb4
  draft PR #356: OPEN
  final remote scope review: CLEAN before final-release review
```

Hosted GitHub Actions on PR #356 remain zero-step failures tracked by Issue #354. They are infrastructure evidence only: neither behavioral PASS nor B1 behavioral FAIL.

## Corrected final-review findings

```text
P1  active B1 handoff docs described pre-generation / no-PR state
P2  fingerprint runtime_surface_file_count included one nonexistent ALLOWED_READ_PATHS entry
```

Applied correction:

```text
✓ _fingerprinted_runtime_surface_paths() now includes existing paths only
✓ runtime_surface_file_count therefore counts existing files in the exact hash set
✓ focused regression asserts every fingerprinted path exists
✓ missing allowlist entries are excluded from the fingerprinted set
✓ active B1 documents are synchronized to the correction/review state
```

Do not redesign B1. These changes are bounded truth-integrity corrections found by final review.

## Current action — final PR review and separate merge decision

Corrective evidence is complete:

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

The only remaining B1 gate is final PR #356 evidence assessment followed by a separate owner-authorized merge decision. Do not regenerate, redesign B1, or begin a downstream lane.

## Google Foundation / CI state

PR #335 remains:

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
Foundation/auth/identity only
```

Do not modify or merge #335 during B1.

Issue #354 remains:

```text
infrastructure/open
zero-step hosted Actions
not behavioral pass/fail evidence
required before Wave C relies on hosted CI
```

## Ordered sequence after B1

```text
B1 final PR review / separate merge decision
-> B2 capability narration
-> B3 memory governance
-> B4 reproducibility hygiene
-> Wave C proof / semantic-contract stabilization / validated baseline
-> reconstruct #335 onto exact validated baseline
-> independent #335 review + separate merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> evidence-based Operational Continuity warrant
```

B2/B3/B4 remain blocked until B1 is separately merged.

## Scope lock

Do not start or modify inside B1:

```text
capability narration semantics (B2)
GeneralChat durable-memory semantics (B3)
dependency-source truth (B4)
network behavior / NetworkMediator wiring
capability registry
OAuth / #335
Google domain-data access
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
README/front-door rewrite
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
