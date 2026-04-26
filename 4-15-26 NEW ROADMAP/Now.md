# NOW.md - Current Sprint (Week 1-4)

**Sprint Goal:** Non-developer installs and runs Nova in 5 minutes.

**Status:** INSTALLER PAUSED - cap 64 is implemented through P4, while installer validation and cap 64 live signoff remain open. Installer will be validated when returning to Tier 1 close-out.  
**Start Date:** 2026-04-15  
**Target End:** 2026-05-13 (4 weeks)

---

## Current Reality

- Cap 64: implemented through P4, pending live checklist, signoff, and lock closure
- Installer: compiled and published, but clean Windows VM validation is still blocked on the current bootstrap failure
- CI: workflow exists, but GitHub Actions is blocked by account billing lock
- Landing page: deployed, but Formspree waitlist activation is still pending
- Immediate priority: cap 64 signoff, installer VM validation, waitlist activation, and demo-ready README assets
- Follow-up hardening that should not interrupt this close-out path is tracked in [BackLog.md](BackLog.md)

---

## Active Blockers

- Cap 64 live checklist is not yet complete
- Clean Windows VM installer validation is paused pending `C:\Program Files\Nova\bootstrap.log` review
- GitHub Actions billing lock is preventing CI verification and README badges
- Formspree endpoint has not been activated for the waitlist flow

---

## This Week

- [ ] Run the cap 64 live checklist end-to-end → sign off → lock (first locked capability) — checklist at `docs/capability_verification/live_checklists/cap_64_send_email_draft.md`
- [ ] Inspect `C:\Program Files\Nova\bootstrap.log` on the target VM (requires clean Windows VM install run)
- [ ] Complete clean Windows VM installer validation
- [x] Trust receipt backend — `GET /api/trust/receipts` live; reads ledger, returns last N governed action events
- [ ] Activate Formspree for the landing page waitlist
- [ ] Add a screenshot or demo GIF to README
- [ ] Add CI badges after the GitHub billing issue is resolved
- [x] Cap 65 P3 integration tests — 16 tests, all pass
- [x] Cap 65 P4 API tests — 10 tests, all pass (includes trust receipt endpoint smoke)
- [x] Windows CI job added to `.github/workflows/ci.yml`
- [x] `scripts/verify_windows.ps1` — local Windows verification script (use when billing-locked)

---

## Progress Update (2026-04-21)

### Done

- `runtime_root()` now walks up to find `src/` by landmark instead of using `parents[1]` — all stores (memory, patterns, policies, connections, etc.) now resolve to the same directory regardless of call depth; `persistent_state.py` utility added
- `start_nova.bat` simplified to delegate entirely to `start_daemon.py`; `start_daemon.py` now owns health-check logic
- Startup contract test updated to validate `start_daemon.py` directly
- Mailto test assertions corrected for RFC 6068 (@ literal in recipients)
- Gitignore now covers PID files, model hash, and `nova.log`
- Dashboard chat/news JS reworked for cleaner report widget rendering
- Social content operator design doc created (`docs/future/NOVA_SOCIAL_CONTENT_OPERATOR_DESIGN_2026-04-21.md`) — caps 77–82, four-pass reviewed, Pydantic models validated, governance spine wired, YouTube quota noted (10k units/day = ~6 uploads/day free tier)
- OpenClaw governance hardening plan finalized (`docs/future/NOVA_OPENCLAW_GOVERNANCE_HARDENING_2026-04-21.md`) — four-phase plan: EnvelopeFactory, approval gate, authority headers, run trace
- `NovaLIS-Governance/STATUS.md` updated: Phase 8+9 marked ACTIVE, cap count corrected to 26 (later updated to 27 with cap 65), next-layer posture updated
- OpenClaw governance hardening Steps 1–7 complete (EnvelopeFactory, EnvelopeStore, approval endpoint, Run Permit UI, feature-flagged wiring at all three entry points; bug fixes: null-template guard in scheduler, orphan-envelope prevention)
- Cap 65 (shopify_intelligence_report) wired end-to-end: executor, routing, topology override, registry, capability_locks, connector_packages, P1+P2 tests (51 passing); HttpShopifyConnector implemented with GraphQL Admin API calls routed through NetworkMediator; bootstrapped at startup from env vars
- Docs updated: NovaLIS-Governance/STATUS.md, Now.md, docs/capability_verification/STATUS.md — all reflect 27 active caps

### Issues

- `C:\Program Files\Nova\bootstrap.log` is not available from this machine, so the original VM failure point is still unknown
- Cap 64 live signoff remains manual and still requires a configured mail client plus trust-page verification

### Needs Second Pass

- Re-run the Windows installer on the clean VM and capture the improved bootstrap/startup diagnostics
- Retrieve and inspect `C:\Program Files\Nova\bootstrap.log` from the VM after the next installer run
- Complete the cap 64 live checklist and signoff on a machine with Nova running and a configured mail client

---

## Progress Update (2026-04-18)

### Done

- Local diagnostic pass completed for installer support surfaces
- `python scripts/fetch_models.py` succeeds locally
- `python scripts/start_daemon.py --no-browser` succeeds locally
- `installer/windows/nova_bootstrap.ps1` now fails fast on venv, pip install, and Nova startup errors instead of silently continuing
- `scripts/start_daemon.py` now reports when the Nova process exits before the health check succeeds
- `installer/windows/nova_setup.iss` now runs bootstrap with `-NoLaunch`, so the installer owns the single post-install launch path instead of competing with the bootstrap script

### Issues

- `C:\Program Files\Nova\bootstrap.log` is not available from this machine, so the original VM failure point is still unknown
- Cap 64 live signoff remains manual and still requires a configured mail client plus trust-page verification

### Needs Second Pass

- Re-run the Windows installer on the clean VM and capture the improved bootstrap/startup diagnostics
- Retrieve and inspect `C:\Program Files\Nova\bootstrap.log` from the VM after the next installer run
- Complete the cap 64 live checklist and signoff on a machine with Nova running and a configured mail client

---

## Active Tasks

### Cap 64

- Implemented through P4
- Routing, executor, governance dispatch, and tests are landed
- Full suite was green at implementation time
- Remaining: live checklist, live signoff, and lock closure in `docs/capability_verification/STATUS.md`

### Installer

- Windows installer is built and published
- Clean Windows VM validation is paused at the current bootstrap failure
- Resume from `C:\Program Files\Nova\bootstrap.log`
- macOS packaging stays deferred until Windows validation is complete

### README / Packaging

- README and core intro/architecture docs are rewritten
- Remaining: screenshot or demo GIF, CI badges after billing unlock, and GitHub repo metadata cleanup

### UI / First-Use Flow

- Initial simplification work is landed
- Remaining: verify the install -> launch -> first successful action path feels clear and demo-ready

### Packaging / CI

- `pyproject.toml`, entry point, and CI workflow are landed
- Remaining: verify `pip install -e .` from a clean venv and run CI once GitHub billing is unblocked

### Landing Page / Waitlist

- Landing page is live and linked from README
- Remaining: activate the Formspree endpoint and decide later whether public hosting needs a dedicated domain

---

### Cap 65 (shopify_intelligence_report)

- P1, P2, P3, P4 certified (P3 16 tests, P4 10 tests — all pass as of 2026-04-25)
- Remaining: P5 live sign-off — checklist at `docs/capability_verification/live_checklists/cap_65_shopify_intelligence_report.md`
- Requires `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN` for live test
- Run P5 after cap 64 is locked

### Trust Backend (minimum viable action receipt)

- `src/trust/receipt_store.py` — reads ledger tail, filters for receipt-worthy events, returns structured list
- `GET /api/trust/receipts` — returns last N receipts as JSON; `GET /api/trust/receipts/summary` for badge
- Next: add a dashboard card that pulls from `/api/trust/receipts` and renders the last 5 actions
- The Trust Panel (full inline confirmation surface) remains future work

### OpenClaw Governance Hardening (Steps 1–4, zero behavioral impact)

Design doc: `docs/future/NOVA_OPENCLAW_GOVERNANCE_HARDENING_2026-04-21.md`

These steps have zero behavioral impact and can run in parallel with the cap 64 / installer work.
Steps 5+ (approval endpoint, robust_executor.py changes) must NOT begin until steps 1–4 are merged and verified.
Shopify Tier 4 (write caps) must NOT be activated until steps 1–7 are complete.

- [x] Step 0: Design doc complete and reviewed
- [x] Step 1a: `nova_backend/src/openclaw/models.py` — `OpenClawProposedAction`, `ActionType`, `ApprovalState`, `UserVisibleCategory`
- [x] Step 1b: Hardening event types added to `nova_backend/src/ledger/event_types.py` — `RUN_ISSUED`, `DEPRECATED_DIRECT_RUN`, `ACTION_PROPOSED`, `ACTION_APPROVED`, `ACTION_DENIED`, `ACTION_PENDING`, `AUTHORITY_DIVERGENCE`
- [x] Step 2: `nova_backend/src/openclaw/envelope_factory.py` — stateless constructor, authority snapshot, feature-flagged
- [x] Step 3: `nova_backend/src/openclaw/envelope_store.py` — file-backed lifecycle store, TTL, status machine, single-use enforcement
- [x] Step 4: Run Permit card in `dashboard-control-center.js` — Authority lane, domain chips, budget chips
- [x] Steps 5–6: EnvelopeFactory wired at all three entry points (manual API, scheduler, bridge comment) behind `NOVA_FEATURE_ENVELOPE_FACTORY` flag; orphan-prevention pre-check added
- [x] Step 7: `/api/openclaw/approve-action` passthrough endpoint added
- **Next**: Monitor `OPENCLAW_DEPRECATED_DIRECT_RUN` ledger counts, then flip `NOVA_FEATURE_ENVELOPE_FACTORY=true`

---

## Notes

- Do not start refactoring `brain_server.py` or `session_handler.py`. That is Tier 3 work.
- Docker fallback is allowed only if the native installer path is blocked; it does not replace the Tier 1 goal.
- Test every task completion on a clean Windows VM.
- OpenClaw hardening Steps 5+ are blocked until Steps 1–4 show zero divergence in logs.

---

*This document is active. Update weekly. Move completed tasks to `CHANGELOG.md` and delete them from this file.*
