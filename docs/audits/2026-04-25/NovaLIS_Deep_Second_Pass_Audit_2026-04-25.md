# NovaLIS Deep Second-Pass Audit

**Date:** 2026-04-25
**Type:** Code-grounded read-only audit
**Authority:** Snapshot only. Runtime truth docs and Now.md are authoritative for live status.
**Scope:** Source code, registry, trust module, test coverage, installer, OpenClaw hardening, hot-path growth.

---

## 1. Executive Summary

The prior audits were accurate but soft on two findings that are now confirmed as the most critical gaps:

1. **All 27 capabilities have zero completed verification phases.** The framework is real and well-designed. The execution is entirely pending.
2. **The trust module is a stub.** 122 lines across two files. No panel, no UI surface, no action receipt system.

Everything else — governance spine, registry, executor architecture, test suite, OpenClaw — is real and solid. The delta between "technically real" and "product-ready" is concentrated in these two items and the installer validation blockage.

---

## 2. Hot-Path Monolith Growth

| File | Prior Audit (2026-04-15) | Current | Direction |
|---|---:|---:|---|
| `nova_backend/src/brain_server.py` | 3,571 lines | **3,624 lines** | Growing |
| `nova_backend/src/websocket/session_handler.py` | 3,821 lines | **3,930 lines** | Growing |

Both files are actively accreting. The DEEP_CODE_AUDIT.md correctly deferred extraction to Tier 3 — that discipline is holding — but the files are not stable. Each sprint that adds routes or intent handlers to these files increases future refactor cost.

**No action required now.** Document as a watch metric: if either file crosses 4,500 lines before Tier 3 begins, refactor cost will increase substantially.

---

## 3. Governance Registry — Confirmed Real, One Design Flag

All 27 capabilities have complete governance fields in `nova_backend/src/config/registry.json`: `risk_level`, `authority_class`, `requires_confirmation`, `reversible`, `external_effect`. This is verified.

Three `persistent_change` capabilities run without `requires_confirmation`:

| ID | Capability | authority_class | req_confirm |
|---|---|---|---|
| 52 | story_tracker_update | persistent_change | False |
| 58 | screen_capture | persistent_change | False |
| 61 | memory_governance | persistent_change | False |

These are deliberate design choices — all three write to local state only, no external effect, and are reversible. The choice is defensible. It should be explicitly stated in a design note so future reviewers do not flag it as an oversight.

Additionally: `openclaw_execute` (cap 63) has `external_effect=True` and `requires_confirmation=False`. The description says it runs read-only templates, so the external effect is read-only outbound. This also should be stated explicitly.

---

## 4. Capability Verification — Most Critical Finding

From `docs/capability_verification/STATUS.md` (updated 2026-04-18):

> Every one of the 27 active capabilities shows: P1 pending, P2 pending, P3 pending, P4 pending, P5 pending, Lock open.

The only exception is cap 64 (`send_email_draft`), confirmed in Now.md as "implemented through P4, pending live checklist and signoff."

**This means:** The test suite (`tests/governance/`, `tests/executors/`, phase test folders) exercises governance boundaries and routing, but no individual capability has been formally certified through the six-phase framework. Registry status says `active`; verification status says `entirely unverified`.

This is the gap that would prevent claiming any capability is production-ready.

**Recommended priority order for first verification pass:**
1. Cap 64 (`send_email_draft`) — closest to locked, unblock now
2. Cap 32 (`os_diagnostics`) — read-only, low risk, good smoke test
3. Cap 16 (`governed_web_search`) — highest user-visibility
4. Cap 61 (`memory_governance`) — high strategic value, persistent_change without confirmation worth P5 human sign-off

---

## 5. Trust Module — Thin Stub

`nova_backend/src/trust/` contains three files, 122 total lines:

- `__init__.py` — 4 lines
- `trust_contract.py` — 39 lines: normalizes a status dict (mode, failure_state, last_external_call, data_egress, consecutive_failures)
- `failure_ladder.py` — 79 lines

There is no trust panel, no action receipt system, no UI surface. The runtime truth doc correctly lists "Trust Panel system" as not implemented. The prior audit noted this; this pass confirms it is more foundational than implied — the trust module itself barely exists. The gap is not "the UI isn't done"; the gap is that the data model and backend for a trust surface have not been built.

**Impact:** Any action that runs shows no user-facing record of what happened. For a "governed" system, this is the largest UX credibility gap.

---

## 6. OpenClaw Hardening — Accurate Progress

Per Now.md, Steps 1–7 of the OpenClaw governance hardening are complete:

- `envelope_factory.py` — stateless constructor with authority snapshot
- `envelope_store.py` — file-backed lifecycle store with TTL and single-use enforcement
- `models.py` — `OpenClawProposedAction`, `ActionType`, `ApprovalState`
- Dashboard Run Permit card in `dashboard-control-center.js`
- Approval endpoint at `/api/openclaw/approve-action`
- Feature-flagged at all three entry points behind `NOVA_FEATURE_ENVELOPE_FACTORY`

This was verified against the actual file list in `nova_backend/src/openclaw/` (26 files, 5,630 lines). The architecture is real.

**Remaining step:** Flip `NOVA_FEATURE_ENVELOPE_FACTORY=true` after confirming `OPENCLAW_DEPRECATED_DIRECT_RUN` ledger count is zero. Do not flip until cap 64 and installer are resolved — avoid parallel scope creep.

---

## 7. Installer State

`installer/windows/` contains:
- `nova_setup.iss` — Inno Setup script
- `nova_bootstrap.ps1` — bootstrap PowerShell script

Now.md states: "installer compiled and published, clean Windows VM validation is paused pending `C:\Program Files\Nova\bootstrap.log` review." The bootstrap log is not accessible from this machine.

`nova_backend/src/brain_server.py:3605` confirms `def main()` exists — the entry point is wired.

**The installer exists. Validation is blocked, not unstarted.** The specific failure point is unknown without the bootstrap log. No new installer work should be done until the log is read on the target machine.

---

## 8. Frontend Duplication — Still Present

`Nova-Frontend-Dashboard/` (top-level) and `nova_backend/static/` both exist. The DEEP_CODE_AUDIT.md flagged this as a drift risk. It remains unresolved. Changes to the dashboard must still be made in two places, or one version drifts.

This is Tier 3 scope per the roadmap. No action now — but the drift is accumulating with each dashboard change.

---

## 9. What Is Solid

- **Governance spine:** GovernorMediator → Governor → CapabilityRegistry → SingleActionQueue → LedgerWriter → ExecuteBoundary — confirmed real, tested, phase-locked.
- **Registry governance fields:** All 27 capabilities have complete authority model fields. Fail-closed behavior verified in tests.
- **Test suite:** `tests/governance/` has 24+ tests covering network bypass, background execution, ledger enforcement, mediator enforcement, cognitive layer contracts. These are structural correctness tests.
- **Runtime truth generation:** `scripts/generate_runtime_docs.py` generates CURRENT_RUNTIME_STATE.md with "Manual edits: NOT PERMITTED" guard. Confirmed.
- **main() entry point:** Confirmed at brain_server.py:3605. `nova-start` CLI entry is wired.
- **OpenClaw hardening:** Steps 1–7 complete, feature-flagged, not yet activated.
- **Roadmap discipline:** Now.md is honest, specific, and actively maintained. Blockers are named. Tier 3 work is explicitly blocked.

---

## 10. Verified Risk Register (Updated)

| Risk | Severity | Status | Recommended Control |
|---|---|---|---|
| All 27 capabilities unverified | **Critical** | Open | Complete cap 64 first; then run P1–P4 for caps 32, 16, 61 in sequence |
| Trust module is a stub | **Critical** | Open | Build trust backend before calling any capability "governed" in public materials |
| Installer validation blocked | **High** | Blocked on VM | Read bootstrap.log on target machine; do not rebuild installer before diagnosing |
| Hot-path monolith growth | **Medium** | Watch | Track line count per sprint; hold Tier 3 extraction until Tier 1 ships |
| Frontend duplication | **Medium** | Deferred (Tier 3) | No action until Tier 1 complete |
| persistent_change without confirmation | **Low** | Design choice | Add explicit design note to capability registry or architecture doc |
| openclaw_execute external_effect without confirm | **Low** | Design choice | Add explicit note that external effect is read-only outbound |
| GitHub Actions billing lock | **Medium** | External | Resolve billing; CI is written and ready |

---

## 11. Recommended Immediate Actions (Ordered)

1. **Cap 64 live checklist** — run the checklist at `docs/capability_verification/live_checklists/cap_64_send_email_draft.md`, sign off, lock. This is the only unblocked item that produces a locked capability.
2. **Bootstrap log** — access the target VM, read `C:\Program Files\Nova\bootstrap.log`, identify the failure point. Nothing else unblocks the installer.
3. **Trust backend design** — before shipping any capability as "governed" externally, define and build the minimum trust surface: what did Nova do, when, and what was the outcome. Does not need to be a full panel — an action receipt log accessible from the dashboard is sufficient to unblock launch credibility.
4. **Capability maturity labels** — apply labels from `docs/product/CAPABILITY_MATURITY.md` to the registry JSON or a companion maturity doc. This separates "registry active" from "user-ready."
5. **Design notes for persistent_change without confirmation** — add one paragraph to architecture docs explaining the explicit design rationale. Prevents future reviewers from flagging as oversight.

---

## 12. Final Verdict

NovaLIS is structurally real and architecturally coherent. The governance spine, registry, executor pattern, and test suite are all confirmed. The OpenClaw hardening is well-executed and appropriately gated.

The gaps are concentrated and specific:
- Zero capabilities are verified through the certification framework.
- The trust surface does not exist beyond a 39-line normalizer.
- The installer is blocked on a log file on a specific machine.

None of these are hidden problems. All three are named in Now.md and runtime truth docs. The project's own documentation is honest about its state. The next milestone — one locked capability, one readable trust receipt, one validated install — would materially change what can be claimed publicly.
