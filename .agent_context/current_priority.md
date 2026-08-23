# Current Priority

## Wave B1 — Final Review Correction Gate — 2026-08-23

Current active lane:

```text
WAVE B1 — runtime-truth instrumentation only
SUBSTATE: bounded final-review corrections applied; exact-head rerun + regeneration required
PR: #356 OPEN / DRAFT
MERGE: NOT AUTHORIZED
```

Handoff anchors:

```text
branch: codex/b1-runtime-truth-instrumentation-20260820
A2 base: 060380f2e8c6437ff888773f0078647547ff4622
first published/proven B1 candidate: f44cb8b856345ddc573fe0cb56037104350ffeb4
source/test correction checkpoint: ecd4033928990c68663f2ef81b46236686043765
```

The A2 base is a planning/comparison checkpoint, not a validated baseline. `f44cb8b8...` completed the first exact-head proof, generated-artifact publication, and draft-PR opening. Final release review then found two bounded truth-integrity defects: active operational documents still described the pre-generation/no-PR state, and the fingerprint file count included one nonexistent allowlist path.

The fingerprint source/test correction is now applied. Later handoff-document commits may advance branch HEAD beyond `ecd403...`; verify and record the actual HEAD used for the corrective proof.

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

## Final-review findings being corrected

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
✓ active B1 documents are being synchronized to the correction/review state
```

Do not redesign B1. These changes are bounded truth-integrity corrections found by final review.

## Next action — exact-head corrective proof and regeneration

From a usable local checkout:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
```

Expected branch:

```text
codex/b1-runtime-truth-instrumentation-20260820
```

Run:

```bash
export PYTHONPATH=nova_backend
python -m ruff check nova_backend/src/audit/runtime_truth_instrumentation.py nova_backend/tests/test_runtime_truth_b1.py scripts/check_operational_truth_consistency.py
python -m pytest nova_backend/tests/test_runtime_truth_b1.py
python -m pytest nova_backend/tests/test_runtime_auditor.py nova_backend/tests/test_runtime_governance_docs.py
python scripts/check_operational_truth_consistency.py
python scripts/check_runtime_doc_drift.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "nova_backend"
```

Then mechanically regenerate:

```bash
python scripts/generate_runtime_docs.py
```

The generator also refreshes tracked `_MOCs/*`. That remains an incidental overlay refresh, not B1 publication output. For B1 stage only:

```bash
git add -- docs/current_runtime/CURRENT_RUNTIME_STATE.md docs/current_runtime/BYPASS_SURFACES.md docs/current_runtime/RUNTIME_FINGERPRINT.md
```

Do not stage `_MOCs/*`, and do not use `git add .`, `git add -A`, `git add --all`, or equivalent broad staging.

## Required generated-output inspection

Inspect:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/BYPASS_SURFACES.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
```

Acceptance conditions:

```text
CURRENT_RUNTIME_STATE.md
  - connections_api.py appears through KNOWN_DIRECT_NETWORK_EXCEPTION
  - no false "Discrepancies: None" while the requests-based exception is detected
  - universal NetworkMediator/Governor/ledger claims remain qualified
  - Phase 9 evidence names real active symbols
  - Runtime Surface Scope file count reflects existing fingerprinted files only

BYPASS_SURFACES.md
  - connections_api.py remains visible
  - classification = local_administrative_health_probe
  - wording states requests-scanner scope and does not claim universal network coverage

RUNTIME_FINGERPRINT.md
  - scope_version = behaviorally_active_v2
  - runtime_surface_file_count present
  - reported count equals the exact existing-file set consumed by the runtime-surface hash
  - source_families present
  - includes brain, connections, identity, memory, usage
```

After generation rerun:

```bash
python scripts/check_operational_truth_consistency.py
python scripts/check_runtime_doc_drift.py
```

Then:

```text
1. commit only the mechanically regenerated three runtime artifacts if changed
2. verify _MOCs/* remains excluded
3. exact compare A2 base -> corrected final B1 HEAD
4. verify no B2/B3/B4/Google/#335/Continuity/OpenClaw-authority/provider-routing leakage
5. review PR #356 at its new exact head
6. produce merge-readiness verdict
7. do not merge without separate owner authorization
```

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
B1 corrective proof/regeneration/final PR review/separate merge decision
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
