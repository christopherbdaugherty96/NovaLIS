# Runtime Truth Addendum (Docs-Only Corrections)
Date: 2026-03-13
Status: Active
Scope: Clarifies any remaining documentation or auditor blind spots without changing runtime code.

## Purpose
This addendum records only active mismatches where generated runtime docs may still under-report or misclassify live behavior.

Use with:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## Resolved on 2026-03-13
- Calendar integration detection in generated runtime docs now matches the live governed path.
- Phase-5 status in generated runtime docs now reflects active runtime slices instead of a hardcoded design-only row.

## Remaining Correction: BYPASS scan scope
`BYPASS_SURFACES.md` can under-report direct `requests` usage outside approved surfaces if the auditor allowlist or scan scope is incomplete.

Interpretation rule:
- Use the BYPASS report as a partial signal, not as exhaustive proof.
- Cross-check with source search when assessing network-surface compliance.

## Governance Decision Rule
When conflicts appear between generated status text and runtime code/proofs:
1. Runtime code, tests, and fingerprint win.
2. Generated status text is treated as advisory only when an active blind spot is documented here.
3. Document the divergence in this addendum and in phase proof packets.

## Related References
- `docs/README.md`
- `docs/canonical/CANONICAL_DOCUMENT_MAP.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_DOC_UPDATE_PROOF_2026-03-12.md`
- `docs/PROOFS/Phase-5/PHASE_5_PROOF_PACKET_INDEX.md`
- `docs/PROOFS/Phase-5/PHASE_5_CUMULATIVE_IMPLEMENTATION_STATE_2026-03-12.md`
