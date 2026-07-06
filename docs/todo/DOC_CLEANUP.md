# Doc Cleanup — Nova

**Updated:** 2026-07-05
**Purpose:** Documentation maintenance tasks. Not implementation work.

---

## Open

### SECURITY.md — fill PGP placeholder

`SECURITY.md` contains `PGP-PUBKEY-PLACEHOLDER` and no response SLA.
Fix: fill in PGP key or remove placeholder; add "We aim to respond within
14 days."

### Phase 4.5 status conflict

- `NovaLIS-Governance/STATUS.md` shows Phase 4.5 = **ACTIVE**
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` shows Phase 4.5 = **PARTIAL**

Verify which is correct; update the stale doc.

### Archive folder headers

Docs in `docs/archive/` are not clearly marked as non-authoritative.
Fix: add `> ARCHIVED — do not use for implementation decisions.` header
to each.

### Canonical reading-order doc

No root-level pointer tells new readers which 5 docs to read first.
Fix: create `docs/CANONICAL.md` — 10 lines listing the 5 authoritative
sources with one-line descriptions.

### Post-PR-4 docs review queue

Four follow-up docs passes on 2026-07-05 found no sequence-changing plan
outside `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`. The next work remains
C1 Auralis Today after the post-PR-4 current-truth sync lands.

Keep these tidy items together in the docs cleanup PR unless a smaller PR is
clearly safer:

- Add roadmap pointers to `docs/INDEX.md`, `docs/FULL_DOCUMENTATION_MAP.md`,
  `docs/future/README.md`, and `docs/todo/README.md`.
- Update or retire stale `docs/todo/SHOPIFY_SETUP_TODO.md`; it still describes
  Cap 65 P5 as blocked even though current repo truth says Cap 65 is locked
  read-only.
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

- Delete repo-root `branches_safe_to_delete.txt` — all seven listed branches
  were already deleted; the file is fully stale.
- Archive the three April-dated audit strays at `docs/` root:
  `AUDIT_ACTION_PLAN_2026-04-28.md`, `SANITY_AUDIT_2026-04-28.md`,
  `SECOND_PASS_OVERVIEW_2026-04-28.md`; and the two orphaned capability
  spec `.txt` files at `docs/` root (Governed Web Intelligence / Governed
  Webpage Launch).
- Fold the two archives *inside* `docs/design/` (`archive/` and
  `archive(phase 4)/`) into top-level `docs/archive/`.
- Fold only genuinely empty/orphan singleton folders (`integrations/` empty,
  `architecture/` one README) into `reference/`. Do NOT fold folders now
  cited as substrate above (`planning/`, `simulations/`, `security/`,
  `business/`).
- Move `docs/tools/check_quarantine.ps1` to `scripts/` (a script misfiled
  under docs).
- Delete the empty `docs/archive/phase 3/NovaLIS-Governance(older)/
  OLD_VISION.md_files/` directory. Security note: the JWT-bearing HTML export
  is fully gone from the working tree; combined with the clean gitleaks
  history scan, that exposure is closed end to end.
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
