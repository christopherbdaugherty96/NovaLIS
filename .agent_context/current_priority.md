# Current Priority

## Wave B1 — Mechanical Proof Gate — 2026-08-20

Current active lane:

```text
WAVE B1 — runtime-truth instrumentation only
SUBSTATE: source/truth corrections complete; mechanical proof required
```

Exact branch checkpoint for the next session:

```text
branch: codex/b1-runtime-truth-instrumentation-20260820
A2 base: 060380f2e8c6437ff888773f0078647547ff4622
B1 head: b43a3989527e1c20892694b307351948a6129727
```

The A2 base is a planning/comparison checkpoint, not a validated baseline. The B1 head is the current proof candidate only; do not call it validated.

## Completed gates

```text
Wave A1 — operational truth synchronization
  MERGED via PR #353
  merge: f25c798c7cb488495a343068463e9214cab0a763

Wave A2 — strategy reconciliation
  MERGED via PR #355
  merge/current main: 060380f2e8c6437ff888773f0078647547ff4622
```

B1 source-level work now includes:

```text
✓ stable-auditor instrumentation path
✓ requests-based network discrepancy/classification reporting
✓ connections_api.py local_administrative_health_probe classification
✓ Phase 9 live import/symbol evidence
✓ behaviorally_active_v2 fingerprint scope incl. usage
✓ exact fingerprint hash/count path set
✓ qualified generated invariants/network-scan wording
✓ operational truth consistency checker
✓ canonical-index lane participation + stale-index regression
✓ generator-entrypoint integration test added
✓ Issue #343 checkpoint synced
```

Third-pass review found no new scope leakage and no further code-design correction justified before execution.

## Branch freeze for proof

Treat `b43a3989527e1c20892694b307351948a6129727` as frozen for the mechanical proof pass.

Do **not** make additional B1 implementation changes unless the proof/generation pass reproduces a concrete defect.

The checked-in generated runtime artifacts are intentionally still pre-B1. Do not hand-edit them.

## Next action — execute, generate, inspect

From a usable local checkout of the exact B1 head:

```bash
export PYTHONPATH=nova_backend
python -m pytest nova_backend/tests/test_runtime_truth_b1.py
python -m pytest nova_backend/tests/test_runtime_auditor.py nova_backend/tests/test_runtime_governance_docs.py
python scripts/check_operational_truth_consistency.py
python scripts/check_runtime_doc_drift.py
python scripts/generate_runtime_docs.py
```

If the environment is Windows PowerShell, set the equivalent environment variable before pytest:

```powershell
$env:PYTHONPATH = "nova_backend"
```

After generation, rerun the consistency/drift checks if useful for final proof capture.

## Required generated-output inspection

Inspect mechanically generated:

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
  - universal NetworkMediator/Governor/ledger claims are qualified
  - Phase 9 evidence names real active symbols

BYPASS_SURFACES.md
  - connections_api.py remains visible
  - classification = local_administrative_health_probe
  - wording states requests-scanner scope and does not claim universal network coverage

RUNTIME_FINGERPRINT.md
  - scope_version = behaviorally_active_v2
  - runtime_surface_file_count present
  - source_families present
  - includes brain, connections, identity, memory, usage
  - count derives from the exact set consumed by the runtime-surface hash
```

## Final B1 gate after generation

Only after successful execution and generated-output inspection:

```text
1. exact compare: A2 base 060380f... -> final B1 head
2. verify no B2/B3/B4/Google/#335/Continuity/OpenClaw-authority/provider-routing leakage
3. verify generated files changed only through the generator
4. record actual test/check results without inflating their scope
5. only then open a DRAFT B1 PR
```

No B1 PR should exist before this gate completes.

## Current known generated-artifact contradiction

Until `scripts/generate_runtime_docs.py` is actually run on the B1 head, checked-in generated truth remains pre-B1 and still contains the known contradiction:

```text
CURRENT_RUNTIME_STATE.md -> universal network invariant + Discrepancies: None
BYPASS_SURFACES.md       -> connections_api.py detected outside NetworkMediator
RUNTIME_FINGERPRINT.md   -> pre-B1 fingerprint fields only
```

This is an expected pending proof condition, not authorization to manually edit those files.

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
B1 proof/generation/review/merge decision
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

B2/B3/B4 remain blocked until B1 receives its own completed proof/review and merge decision.

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
```

README sequencing drift is recorded separately and must not be folded into B1.

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

Generated evidence is authoritative only for what its generator mechanically measures. Tests prove only the revision/environment/scope actually exercised.
