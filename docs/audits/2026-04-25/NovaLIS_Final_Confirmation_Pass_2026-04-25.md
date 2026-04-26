# NovaLIS Final Confirmation Pass

**Date:** 2026-04-25
**Type:** Claim-by-claim verification of the deep second-pass audit
**Method:** Every key claim verified directly against source files or config JSON.
**Authority:** Snapshot. Runtime truth docs and Now.md are authoritative for live status.

---

## Correction First

The deep second-pass audit stated:

> "All 27 capabilities have zero completed verification phases."

**This was wrong.** The actual state from `nova_backend/src/config/capability_locks.json`:

| ID | Capability | P1 | P2 | P3 | P4 | P5 | Locked |
|---|---|---|---|---|---|---|---|
| 64 | send_email_draft | **pass** | **pass** | **pass** | **pass** | pending | False |
| 65 | shopify_intelligence_report | **pass** | **pass** | pending | pending | pending | False |
| 16–63 (25 caps) | all others | pending | pending | pending | pending | pending | False |

Corrected statement:
- 25 capabilities are zero-phase-verified.
- Cap 64 is P1–P4 complete, P5 pending — one live sign-off from being lockable.
- Cap 65 is P1–P2 complete, P3–P5 pending.
- Zero capabilities are locked.

Everything else in the audit holds.

---

## Claim-by-Claim Verification

### Brain server: 3,624 lines
**Confirmed.** `wc -l nova_backend/src/brain_server.py` = 3,624.

### Session handler: 3,930 lines
**Confirmed.** `wc -l nova_backend/src/websocket/session_handler.py` = 3,930.

### Trust module: 122 lines total
**Confirmed.** `trust_contract.py` = 39 lines, `failure_ladder.py` = 79 lines, `__init__.py` = 4 lines. Total = 122.

`trust_contract.py` normalizes a status dict with five fields (mode, last_external_call, data_egress, failure_state, consecutive_failures). No panel, no action receipt, no ledger integration.

### Registry has 27 capabilities, all governance fields populated
**Confirmed.** `capability_locks.json` and `registry.json` cross-checked. All 27 entries have `risk_level`, `authority_class`, `requires_confirmation`, `reversible`, `external_effect`. No missing fields.

### persistent_change without requires_confirmation
**Confirmed.** Three capabilities:

| ID | Capability | Notes |
|---|---|---|
| 52 | story_tracker_update | local write, reversible, no external effect |
| 58 | screen_capture | local write, reversible, no external effect |
| 61 | memory_governance | local write, reversible, no external effect |

All three are local-only and reversible. Deliberate design choice, not oversight.

### external_effect without requires_confirmation
**Confirmed — and audit undercounted.** Two capabilities, not one:

| ID | Capability | authority_class | Notes |
|---|---|---|---|
| 63 | openclaw_execute | read_only_network | external effect = outbound read only |
| 65 | shopify_intelligence_report | read_only_network | external effect = outbound read only |

Both are read-only outbound. Deliberate design. The audit only named cap 63; cap 65 should also be noted.

### OpenClaw hardening Steps 1–7 complete
**Confirmed.** Verified against actual files:

| Artifact | File | Lines | Status |
|---|---|---:|---|
| Models | `src/openclaw/models.py` | 74 | Exists |
| EnvelopeFactory | `src/openclaw/envelope_factory.py` | 243 | Exists, feature-flagged at line 26 |
| EnvelopeStore | `src/openclaw/envelope_store.py` | 342 | Exists |
| Approve endpoint | `src/api/openclaw_agent_api.py:460` | — | `POST /api/openclaw/approve-action` confirmed |
| Run Permit card | `static/dashboard-control-center.js:3353` | — | Comment confirms authority lane, domain chips, budget chips |
| Ledger event types | `src/ledger/event_types.py` | — | `OPENCLAW_RUN_ISSUED` and `OPENCLAW_DEPRECATED_DIRECT_RUN` confirmed |

Feature flag `NOVA_FEATURE_ENVELOPE_FACTORY` wired in `envelope_factory.py`, `envelope_store.py`, `models.py`, `openclaw_agent_api.py`, and `agent_scheduler.py`. All entry points confirmed.

### Approval endpoint at /api/openclaw/approve-action
**Confirmed.** `src/api/openclaw_agent_api.py:460`.

### Confirmation flow is wired in session_handler, not ConfirmationGate class
**Confirmed.** `session_handler.py` uses `pending_governed_confirm` state at lines 233, 690–707, 966, 3263, 3278, 3299. The `ConfirmationGate` class in `src/gates/confirmation_gate.py` explicitly documents it is not on the active WebSocket path.

### Registry phase = 8
**Confirmed.** `registry.json` top-level `"phase": "8"`.

### main() entry point in brain_server.py
**Confirmed.** `brain_server.py:3605`.

### Installer files exist
**Confirmed.** `installer/windows/nova_setup.iss` and `installer/windows/nova_bootstrap.ps1` both present.

### Frontend duplication still present
**Confirmed.** `Nova-Frontend-Dashboard/` (top-level) and `nova_backend/static/` both exist and contain dashboard JS.

---

## Summary of Confirmed Risk State

| Risk | Severity | Confirmed |
|---|---|---|
| 25 capabilities zero-phase-verified | Critical | Yes |
| Cap 64 one step from locked (P5 pending) | Actionable | Yes |
| Trust module is a 122-line stub with no panel or receipt | Critical | Yes |
| Installer blocked on bootstrap.log | High | Yes — log not accessible from this machine |
| Hot-path monolith growth | Medium | Yes — both files growing each sprint |
| Frontend duplication | Medium (Tier 3 deferred) | Yes |
| persistent_change without confirmation (3 caps) | Low — design choice | Yes |
| external_effect without confirmation (caps 63, 65) | Low — read-only outbound | Yes — audit missed cap 65 |

---

## What Is Unconditionally Solid

These claims from prior audits are all confirmed against actual code:

- **Governance spine is real** — GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, LedgerWriter all present as named files with real implementation.
- **Confirmation gate on cap 22 and cap 64** — `requires_confirmation=True` in registry, `pending_governed_confirm` flow in session_handler confirmed.
- **Fail-closed execute boundary** — `GOVERNED_ACTIONS_ENABLED = True`; if False, execution is blocked by default.
- **Runtime truth generation** — `scripts/generate_runtime_docs.py` confirmed present. `CURRENT_RUNTIME_STATE.md` marked "Manual edits: NOT PERMITTED."
- **OpenClaw hardening is feature-flagged, not yet behavioral** — confirmed via flag wiring at all entry points.
- **Capability certification framework is real and well-designed** — `scripts/certify_capability.py`, `capability_locks.json` schema, phase descriptions, regression guard all confirmed.

---

## Recommended Next Actions (Unchanged, Ordered)

1. **Cap 64 P5 live sign-off** — run `docs/capability_verification/live_checklists/cap_64_send_email_draft.md`, then `python scripts/certify_capability.py live-signoff 64`, then `lock 64`. This produces the first locked capability.
2. **Bootstrap log** — read `C:\Program Files\Nova\bootstrap.log` on the target VM. Nothing else unblocks installer.
3. **Trust receipt minimum** — before any public "governed" claim, build a minimal action receipt: what ran, when, outcome. The backend for this does not exist yet.
4. **Document persistent_change and external_effect design choices** — one paragraph in architecture docs to prevent future reviewer confusion.
5. **Cap 65 P3–P5** — cap 65 is closer than most; completing it gives a second locked capability at low marginal cost.
