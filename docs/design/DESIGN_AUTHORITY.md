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
5. Product-truth packets may define the intended user-facing direction for Nova, but they still remain design-layer authority unless promoted into runtime truth artifacts.

Authoritative Runtime Sources:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/PROOFS/` (verified runtime proof artifacts)

Canonical Design Sets:
- Phase 3.5: `docs/design/Phase 3.5/`
- Phase 4: `docs/design/Phase 4/`
- Phase 4.2: `docs/design/Phase 4.2/`
- Phase 4.5: `docs/design/Phase 4.5/`
- Phase 5: `docs/design/Phase 5/`
- Phase 6: `docs/design/Phase 6/`
- Phase 7: `docs/design/Phase 7/`
- Phase 8: `docs/design/Phase 8/`
- Phase 8.5: `docs/design/Phase 8.5/`
- Phase 9: `docs/design/Phase 9/`
- Phase 10: `docs/design/Phase 10/`
- Phase 11: `docs/design/Phase 11/`

Root-level exceptions:
- `docs/design/README.md`
- `docs/design/DESIGN_AUTHORITY.md`

Special non-phase directories:
- `docs/design/IDEAS/`
- `docs/design/archive/`
- `docs/design/archive(phase 4)/`

Archival:
- Historical and superseded design artifacts belong in `docs/design/archive/`.
