# Runtime Documentation Update Proof
Date: 2026-03-12
Status: Active
Scope: Proof that Nova still generates and updates runtime documentation artifacts.

## Claim
Nova still creates and updates runtime documents, but via explicit generation/verification flows (script and CI), not autonomous background mutation during normal chat runtime.

## Runtime Generation Mechanism (Code Evidence)
Primary generator script:
- `scripts/generate_runtime_docs.py`

Generator entrypoint behavior:
- imports `write_current_runtime_state_snapshot` from `nova_backend/src/audit/runtime_auditor.py`
- executes runtime audit render and writes `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Companion document writer:
- `nova_backend/src/audit/runtime_auditor.py`
- `write_current_runtime_state_snapshot(...)` writes `CURRENT_RUNTIME_STATE.md` and calls `write_runtime_governance_docs(...)`
- `write_runtime_governance_docs(...)` writes:
  - `GOVERNANCE_MATRIX.md`
  - `GOVERNANCE_MATRIX_TREE.md`
  - `SKILL_SURFACE_MAP.md`
  - `BYPASS_SURFACES.md`
  - `RUNTIME_FINGERPRINT.md`

## CI Enforcement Evidence
Runtime docs are enforced in CI and cannot drift silently:

1. `.github/workflows/runtime-docs.yml`
   - runs `python scripts/generate_runtime_docs.py`
   - fails on diff for generated runtime docs
   - runs `python scripts/check_runtime_doc_drift.py`

2. `.github/workflows/phase-3.5-verification.yml`
   - runs `python scripts/generate_runtime_docs.py`
   - fails on diff for generated runtime docs
   - runs `python scripts/check_frontend_mirror_sync.py`

3. `.github/workflows/governance-check.yml`
   - runs `python3 scripts/check_runtime_doc_drift.py`

## Local Verification Snapshot (2026-03-12)
Executed commands:
- `python scripts/generate_runtime_docs.py`
- `python scripts/check_runtime_doc_drift.py`
- `python scripts/check_frontend_mirror_sync.py`

Observed outputs:
- `Generated runtime docs: C:\Nova-Project\docs\current_runtime\CURRENT_RUNTIME_STATE.md`
- `Runtime documentation drift check passed.`
- `Frontend mirror check passed.`

Observed write times after generation:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` -> `2026-03-12 00:49:15` (America/New_York)
- `docs/current_runtime/RUNTIME_FINGERPRINT.md` -> `2026-03-12 00:49:15` (America/New_York)

## Authority and Interpretation
Runtime documentation authority remains:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md`

This proof artifact confirms update mechanics and enforcement, but does not replace the authority hierarchy above.

## Relationship to Known Auditor Blind Spots
Generated runtime docs can still contain wording-level mismatches when auditor logic is incomplete (for example, calendar detection and phase-row wording). Those interpretation rules are tracked in:
- `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md`

