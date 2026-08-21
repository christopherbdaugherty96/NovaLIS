# Nova Current Work Status

Last reviewed: 2026-08-20.

This is a hand-maintained operational status surface. It is not generated runtime truth.

For exact runtime implementation facts, use code plus the generated runtime surfaces that mechanically measure the relevant claim. For ordering, use this file together with `DAILY_COMMAND_CENTER.md`, `.agent_context/current_priority.md`, `docs/CANONICAL/07_ROADMAP_TRUTH.md`, and Issue #343.

## Current Development Lane

```text
WAVE B1 — runtime-truth instrumentation
STATUS: SOURCE/TRUTH CORRECTIONS COMPLETE; MECHANICAL PROOF REQUIRED
BRANCH: codex/b1-runtime-truth-instrumentation-20260820
POST-A2 BASE: 060380f2e8c6437ff888773f0078647547ff4622
IMPLEMENTATION CHECKPOINT: b43a3989527e1c20892694b307351948a6129727
PR: NONE — CORRECTLY WITHHELD
```

The A2 base is a planning/comparison checkpoint, not a validated baseline. `b43a398...` is the accepted B1 implementation/truth-harness checkpoint; later handoff-only documentation commits may advance branch HEAD. Verify `git rev-parse HEAD` before executing proof and record that exact revision with results.

## Completed Gates

```text
Wave A1 — MERGED via PR #353
  f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — MERGED via PR #355
  060380f2e8c6437ff888773f0078647547ff4622
```

## B1 Current Substate

B1 code/truth-harness design has completed three static review passes. No further code-design correction is justified before execution unless proof reproduces a concrete defect.

Completed B1 source-level work:

```text
✓ stable existing-auditor instrumentation path
✓ requests-based network findings enter discrepancy state
✓ connections_api.py classified local_administrative_health_probe
✓ unclassified requests-based paths hard-fail
✓ Phase 9 active evidence uses live imports/symbols
✓ behaviorally_active_v2 fingerprint scope
✓ source families include brain/connections/identity/memory/usage
✓ runtime_surface_file_count uses exact hashed path set
✓ generated invariant/network wording qualified to measured scope
✓ separate operational-truth consistency checker
✓ docs/CANONICAL/00_INDEX.md participates in lane consistency
✓ stale canonical-index regression added
✓ generator-entrypoint integration regression added
✓ Issue #343 synchronized to A1/A2 complete, B1 active
```

Branch posture now:

```text
FREEZE B1 IMPLEMENTATION FOR PROOF
Do not add more code unless execution reveals a reproduced defect.
```

## Remaining B1 Gate

The checked-in generated runtime docs are still pre-B1. This is the remaining material gate.

From a usable local checkout of current branch HEAD:

```bash
export PYTHONPATH=nova_backend
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

After generation inspect:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/BYPASS_SURFACES.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
```

Required acceptance:

```text
CURRENT_RUNTIME_STATE.md
  KNOWN_DIRECT_NETWORK_EXCEPTION visible for connections_api.py
  no false Discrepancies: None
  qualified NetworkMediator/Governor/ledger wording
  Phase 9 evidence references live active symbols

BYPASS_SURFACES.md
  connections_api.py remains visible
  local_administrative_health_probe classification visible
  requests-scanner scope is explicit
  no universal network-coverage claim

RUNTIME_FINGERPRINT.md
  scope_version: behaviorally_active_v2
  runtime_surface_file_count present
  source_families present
  brain/connections/identity/memory/usage included
```

Then perform exact A2-base → final-B1 diff review and open a **draft** B1 PR only if the proof/output gate is clean.

## Known Pre-Generation Contradiction

Until the generator is actually run, checked-in generated artifacts still contain the known pre-B1 contradiction:

```text
CURRENT_RUNTIME_STATE.md
  -> universal NetworkMediator/Governor/ledger claims
  -> Runtime Truth Discrepancies: None

BYPASS_SURFACES.md
  -> nova_backend/src/api/connections_api.py detected outside NetworkMediator

RUNTIME_FINGERPRINT.md
  -> pre-B1 fingerprint fields only
```

Do not manually edit those generated artifacts.

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
B1 mechanical proof / generation / review / merge decision
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

Generated evidence is authoritative only for what the generator actually measures. Historical or unexecuted test definitions are not current proof.
