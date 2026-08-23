# Nova Current Work Status

Last reviewed: 2026-08-23.

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
WAVE B1 — runtime-truth instrumentation
STATUS: FINAL REVIEW CORRECTIONS IN PROGRESS; MERGE NOT AUTHORIZED
BRANCH: codex/b1-runtime-truth-instrumentation-20260820
POST-A2 BASE: 060380f2e8c6437ff888773f0078647547ff4622
PUBLISHED CANDIDATE: f44cb8b856345ddc573fe0cb56037104350ffeb4
DRAFT PR: #356 — OPEN / DRAFT
CORRECTION CHECKPOINT: ecd4033928990c68663f2ef81b46236686043765
```

The A2 base is a planning/comparison checkpoint, not a validated baseline. `f44cb8b8...` completed the first full B1 proof/publication pass and opened draft PR #356. Final release review then found two bounded truth-integrity defects: stale operational substate language and a fingerprint file-count set that included one nonexistent allowlist path. The source/test correction is now applied; later documentation commits may advance branch HEAD beyond `ecd403...`.

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
```

## B1 Current Substate

Final release review found:

```text
P1  active B1 handoff surfaces still described the pre-generation/no-PR state
P2  runtime_surface_file_count counted one nonexistent ALLOWED_READ_PATHS entry
```

Bounded correction already applied at source/test level:

```text
✓ fingerprinted runtime-surface set now requires path.exists()
✓ runtime_surface_file_count therefore describes existing files in the exact hash set
✓ focused regression requires every fingerprinted path to exist
✓ missing ALLOWED_READ_PATHS entries are excluded from the fingerprinted set
```

The generated runtime artifacts committed at `f44cb8b8...` were valid for that earlier source state but are now stale relative to the fingerprint correction. They must be mechanically regenerated on the corrected exact head. Manual edits remain forbidden.

## Remaining B1 Gate

From a usable local checkout of the corrected branch HEAD:

```bash
export PYTHONPATH=nova_backend
python -m ruff check nova_backend/src/audit/runtime_truth_instrumentation.py nova_backend/tests/test_runtime_truth_b1.py scripts/check_operational_truth_consistency.py
python -m pytest nova_backend/tests/test_runtime_truth_b1.py
python -m pytest nova_backend/tests/test_runtime_auditor.py nova_backend/tests/test_runtime_governance_docs.py
python scripts/check_operational_truth_consistency.py
python scripts/check_runtime_doc_drift.py
python scripts/generate_runtime_docs.py
```

Windows PowerShell environment equivalent:

```powershell
$env:PYTHONPATH = "nova_backend"
```

The generator also refreshes tracked `_MOCs/*`. That remains outside B1 publication scope. Stage only:

```bash
git add -- docs/current_runtime/CURRENT_RUNTIME_STATE.md docs/current_runtime/BYPASS_SURFACES.md docs/current_runtime/RUNTIME_FINGERPRINT.md
```

Do not use broad staging and do not publish `_MOCs/*` in B1.

After generation inspect:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/BYPASS_SURFACES.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
```

Required acceptance now includes:

```text
CURRENT_RUNTIME_STATE.md
  KNOWN_DIRECT_NETWORK_EXCEPTION visible for connections_api.py
  no false Discrepancies: None
  qualified NetworkMediator/Governor/ledger wording
  Phase 9 evidence references live active symbols
  Runtime Surface Scope file count reflects existing fingerprinted files only

BYPASS_SURFACES.md
  connections_api.py remains visible
  local_administrative_health_probe classification visible
  requests-scanner scope is explicit
  no universal network-coverage claim

RUNTIME_FINGERPRINT.md
  scope_version: behaviorally_active_v2
  runtime_surface_file_count present and equal to existing files in the exact hashed set
  source_families present
  brain/connections/identity/memory/usage included
```

Then rerun:

```bash
python scripts/check_operational_truth_consistency.py
python scripts/check_runtime_doc_drift.py
```

Finally perform an exact A2-base → corrected final-B1 diff review and reassess draft PR #356. Merge remains a separate decision and is not authorized by a clean rerun.

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
B1 bounded correction -> exact-head rerun -> regeneration -> final PR #356 review -> separate merge decision
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
