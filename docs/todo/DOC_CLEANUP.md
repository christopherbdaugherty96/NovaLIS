# Doc Cleanup — Nova

**Updated:** 2026-07-05
**Purpose:** Documentation maintenance tasks. Not implementation work.

---

## Open

### SECURITY.md — fill PGP placeholder

`SECURITY.md` contains `PGP-PUBKEY-PLACEHOLDER` and no response SLA.
Fix: fill in PGP key or remove placeholder; add "We aim to respond within
14 days."

### Phase 4.5 status conflict — NEEDS HUMAN DECISION

- `NovaLIS-Governance/STATUS.md` (repo root, outside `docs/`) shows Phase 4.5 = **ACTIVE**
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` (generated) shows Phase 4.5 = **PARTIAL**

Not auto-fixed: the stale file is outside `docs/` and is runtime-adjacent governance state that
Codex may edit. Generated runtime truth (PARTIAL) is authoritative; someone with runtime context
should reconcile `NovaLIS-Governance/STATUS.md`.

### Cap 65 lock status conflict — RESOLVED BY EVIDENCE (2026-07-09)

The disagreement was never two competing truths: mechanical lock truth
(`nova_backend/src/config/capability_locks.json` + `python scripts/certify_capability.py status`)
records Cap 65 as P1-P5 LOCKED (2026-05-22, read-only), matching `CURRENT_WORK_STATUS.md`.
The dissenting docs (`WHAT_WORKS_TODAY.md` reviewed 2026-05-04, `SHOPIFY_SETUP_TODO.md`)
simply predated the lock. No human call was needed — the certify script answers it.
Both stale docs synced in the 2026-07-09 capability lock-truth sync PR.

### Archive folder headers — DONE (2026-07-08)

Solved at folder level rather than per-file: `docs/archive/README.md` declares the whole tree
non-authoritative, and the two `docs/design/archive*` folders carry their own banners plus a
CANONICAL pointer. Per-file headers on all 39 legacy files were intentionally not added — a
folder README covers it (see cleanup rule D).

### Canonical reading-order doc — DONE (2026-07-08)

Superseded by a richer solution: `docs/CANONICAL/` now holds an index plus seven truth
files (project / runtime / governance / capability / frontend-backend / test-proof / roadmap)
and an archive policy, each pointing to real source docs and tests. `docs/INDEX.md` links to
`docs/CANONICAL/00_INDEX.md`.

### Post-PR-4 docs review queue

Four follow-up docs passes on 2026-07-05 found no sequence-changing plan
outside `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`. The next work remains
C1 Auralis Today after the post-PR-4 current-truth sync lands.

Keep these tidy items together in the docs cleanup PR unless a smaller PR is
clearly safer:

- Add roadmap pointers to `docs/INDEX.md`, `docs/FULL_DOCUMENTATION_MAP.md`,
  `docs/future/README.md`, and `docs/todo/README.md`.
- ~~Update or retire stale `docs/todo/SHOPIFY_SETUP_TODO.md`~~ — DONE 2026-07-09:
  superseded banner states Cap 65 locked; file kept as historical setup procedure.
- Delete or deprecation-banner `docs/design/ui_backend_contract.md`; it is
  boilerplate example API content, not a real UI/backend contract.
- Banner or rename `docs/Audit BackLog(active)/New-Audit-and-Issues.md` as
  stale audit input. Some findings are obsolete, but still-valid robustness
  items include monolith risk, frontend modularity, env docs, CSP/security
  headers, and docs hygiene.
- Cite `docs/planning/NOVA_JOB_WORKFLOW_PLAN.md` and
  `docs/product/AURALIS_INTERFACE_PLAN.md` as future Nova Jobs / Auralis job
  surface substrate.
- Cite connector/security references under the relevant horizon items:
  `docs/security/NOVA_INTEGRATION_THREAT_MODEL_2026-04-28.md`,
  `docs/future/NOVA_CONNECTOR_RISK_CLASSIFICATION_TABLE_2026-04-28.md`, and
  `docs/future/NOVA_CONNECTOR_REGISTRY_PLAN_2026-04-27.md`.
- Cite `docs/nova-conversation-response-contract.md` as acceptance-criteria
  input for PR 5/6 and Lane D response-quality work.
- Cite `docs/simulations/APPROVAL_GATE_WORKFLOW_SIMULATIONS.md` and
  `docs/simulations/ECOSYSTEM_SIMULATION_MATRIX.md` as approval lifecycle and
  proof-ratchet substrate.
- Add Free-First Principle to the master roadmap doctrine list, sourced from
  `docs/design/DESIGN_AUTHORITY.md`.
- Add B2/H2/D15 substrate citations found during review:
  `docs/design/Phase 10/Firewall & Ledger Specification.txt`,
  `docs/design/Phase 10/# Autonomy Tiers & Evolution.txt`,
  `docs/design/MEMORY_SYSTEM_REFERENCE.md`,
  `docs/design/brain/PERSONAL_PERSONALITY_LAYER.md`, and
  `docs/brain/BRAIN_TRACE_UI_SPEC.md`.
- Refresh product/reference docs that still name old top-level pages such as
  Agent, Activity, Rules, Workspace, or Trust without the current
  Settings -> Advanced relationship. Specific stale line:
  `docs/product/WHAT_WORKS_TODAY.md` lists the pre-PR-4 page set and omits
  Goals; `docs/product/KNOWN_LIMITATIONS.md` says "Trust page" without the
  Settings -> Advanced location.

### Claude review-pass additions (2026-07-05)

Delta from the four-pass docs review not already listed above. Fold into the
same tidy PR:

- NEEDS HUMAN DECISION. `branches_safe_to_delete.txt` is at the repo root (outside `docs/`) and
  deleting it is a non-docs file removal — left for a human to delete. Content does appear fully
  stale (the listed branches are gone).
- DONE (2026-07-08). Archived the three April-dated audit strays at `docs/`
  root to `docs/archive/audits-2026-04/`
  (`AUDIT_ACTION_PLAN_2026-04-28.md`, `SANITY_AUDIT_2026-04-28.md`,
  `SECOND_PASS_OVERVIEW_2026-04-28.md`) and the two orphaned capability spec
  `.txt` files to `docs/archive/` (Governed Web Intelligence / Governed
  Webpage Launch). `FULL_DOCUMENTATION_MAP.md` reference updated.
- NEEDS HUMAN DECISION (2026-07-08). Folding the two `docs/design/archive*`
  folders into top-level `docs/archive/` conflicts with the Phase 6 archive
  audit, which ratified keeping them in place, and would rot ~14
  cross-references across 7 design docs. Instead, both folders now carry
  archived banners + a CANONICAL pointer, and `docs/archive/README.md` notes
  their existence. Physical fold deferred to a human call.
- SUPERSEDED / false premise (2026-07-08). `docs/integrations/` is NOT empty
  (contains `youtubelis/`) and `docs/architecture/` is cited as a doc layer by
  `docs/README.md` and `docs/future/repo_improvement_action_plan.md`. Do not
  fold either. Left in place.
- DONE (2026-07-08). Moved `docs/tools/check_quarantine.ps1` to
  `scripts/check_quarantine.ps1`. (`docs/tools/youtubelis.md` stays — it is a
  real doc, not a misfiled script.)
- SUPERSEDED / false premise (2026-07-08). The
  `docs/archive/phase 3/NovaLIS-Governance(older)/OLD_VISION.md_files/`
  directory is NOT empty — it holds three stray `.css` export assets. Deleting
  a non-empty directory is beyond an exact-duplicate removal, so it is left for
  a human. The security-sensitive JWT HTML is confirmed already gone; only
  harmless CSS remains.
- Proof systems: do NOT merge `PROOFS/`, `demo_proof/`, and
  `capability_verification/` — different genres. Add one cross-linking
  paragraph to each README instead.
- Naming reconciliation (record, don't "fix"): `PROOFS/Trust-Panel/` has a
  `trust_panel_mvp_live_2026-05-14.png` while runtime gaps list "Trust Panel
  not implemented." Both true — the trust *page* MVP was proven; the full
  Trust *Panel* concept (Phase 4.5) remains open. Not a discrepancy.
- Memory-store truth for B7 / C1 (from
  `docs/design/MEMORY_SYSTEM_REFERENCE.md`): `NovaSelfMemoryStore` has dead
  writes and `quick_corrections` has no consumer. Do not build C1 seeds on
  either; B7 schema work should revive or formally retire them. C1 seeds map
  onto the existing `GovernedMemoryStore` schema (lock tier + tags), no
  schema change needed.

---

## Resolved

| Item | Resolved |
|------|---------|
| README.md capability count | Updated to 27 — 2026-04-21 |
| TODO.md stale content | Replaced with pointer to Now.md — 2026-04-27 |
| docs/INDEX.md scope vs. actual file count | Known gap; not blocking |
