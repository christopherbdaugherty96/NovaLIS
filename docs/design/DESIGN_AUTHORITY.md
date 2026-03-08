# DESIGN AUTHORITY

Status: ACTIVE
Scope: All files under `docs/design/`

Design documents describe intended architecture.

Operational behavior is defined exclusively by:
- `CURRENT_RUNTIME_STATE.md`
- `RUNTIME_FINGERPRINT.md`
- Verified runtime proofs

Interpretation Rules:
1. If design intent conflicts with runtime truth, runtime truth wins.
2. Design docs may propose future behavior but do not authorize runtime behavior.
3. Governance and phase claims in design docs are directional unless reflected in runtime truth artifacts.
4. Deprecated design docs must contain a deprecation banner pointing to the canonical design file.

Authoritative Runtime Sources:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/PROOFS/` (verified runtime proof artifacts)

Canonical Design Sets:
- Phase 4: `docs/design/Phase 4/`
- Phase 4.2: `docs/design/Phase 4.2/`
- Phase 4.5: `docs/design/Phase 4.5/`

Archival:
- Historical and superseded design artifacts belong in `docs/design/archive/`.
