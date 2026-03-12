# Runtime Truth Addendum (Docs-Only Corrections)
Date: 2026-03-12
Status: Active
Scope: Clarifies known documentation/auditor blind spots without changing runtime code.

## Purpose
This addendum records known mismatches where generated/runtime-audit docs can be misleading due to auditor logic limitations.

Use with:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## Correction 1: Calendar integration status
Generated runtime docs may report calendar integration as "not implemented" due to brittle detector logic.

Current code-path evidence indicates calendar flow exists in:
- skill registration path
- governor route path
- brain server handling
- dashboard widget handling

Interpretation rule:
- Treat "calendar not implemented" in generated output as an auditor false negative until detector logic is updated.

## Correction 2: Phase-5 status row
Generated runtime docs may show `Phase 5 | DESIGN` while runtime/fingerprint indicate Build Phase 5 and active capability 61.

Interpretation rule:
- Use fingerprint + capability activation + proof packet as authoritative runtime phase signal.
- Treat static phase-table wording in generated output as non-authoritative if it conflicts with runtime markers.

## Correction 3: BYPASS scan scope
`BYPASS_SURFACES.md` can under-report direct `requests` usage outside approved surfaces if the auditor allowlist/scope is incomplete.

Interpretation rule:
- Use BYPASS report as partial signal, not as exhaustive proof.
- Cross-check with source search when assessing network-surface compliance.

## Governance Decision Rule
When conflicts appear between generated status text and runtime code/proofs:
1. Runtime code + tests + fingerprint win.
2. Generated status text is treated as advisory until auditor logic is corrected.
3. Document the divergence in this addendum and in phase proof packets.

## Related References
- `docs/README.md`
- `docs/canonical/CANONICAL_DOCUMENT_MAP.md`
- `docs/current_runtime/RUNTIME_DOC_UPDATE_PROOF_2026-03-12.md`
- `docs/PROOFS/Phase-5/PHASE_5_PROOF_PACKET_INDEX.md`
- `docs/PROOFS/Phase-5/PHASE_5_CUMULATIVE_IMPLEMENTATION_STATE_2026-03-12.md`
