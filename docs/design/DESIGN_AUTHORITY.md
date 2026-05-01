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
6. External integrations and provider choices must follow the Free-First Principle unless runtime truth explicitly implements a different approved policy.

## Free-First Principle

Status: ACTIVE DESIGN POLICY; not runtime enforcement until reflected in runtime truth artifacts.

Nova defaults to free, open-source, local-first, or user-owned integration paths before paid, credit-metered, or vendor-locking services.

Rules:
- Free, open-source, local-first, and user-owned options are the default recommendation and design path.
- Paid services are non-default and must be clearly flagged before recommendation or use.
- Free-tier services with quotas, billing setup, credits, or usage limits must be flagged as `free_tier`, not treated as fully free.
- Unknown cost posture must be treated as `unknown_cost` and flagged until verified.
- Nova must not silently escalate from free/local execution to paid, metered, or externally billable execution.
- Any paid or billing-risk path must require explicit user awareness before it is positioned as the recommended path.

Rationale:
- Preserves user sovereignty.
- Prevents hidden cost surfaces.
- Protects local-first product positioning.
- Keeps capability expansion aligned with visible user authority instead of vendor convenience.

Design implication:
- Future capability metadata should include cost posture such as `free`, `free_tier`, `paid`, or `unknown_cost`.
- Governor and trust-review surfaces should expose cost posture for any integration that may create billing, quota, or lock-in risk.
- Ledger-visible cost flagging should be added before broad paid-provider execution is treated as normal runtime behavior.

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
