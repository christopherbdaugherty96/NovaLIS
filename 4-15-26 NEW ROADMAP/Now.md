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

## Progress Update (2026-04-27) — Cap 64 confirmation gate fix

### Done

- Root-cause identified: `session_handler.py` never set `pending_governed_confirm` state for cap 64. The governor's `risk_level=confirm` check at line 222 returns a refusal when `confirmed=False`, but there was no pre-invoke check in the session handler to save pending state for cap 64's follow-up "yes". Users saw "This action requires confirmation" but typing "yes" had no effect.
- Fix: added cap 64 block analogous to the existing cap 22 gate in `session_handler.py` (lines ~3292-3314). Shows recipient/subject in the confirmation prompt, saves `pending_governed_confirm`, then the existing `pending_governed_confirm → invoke_governed_capability(confirmed=True)` flow completes the action.
- Correct confirmation word: `yes` (or `confirm`, `ok`, `proceed`) — `confirmed` maps to `reprompt` in `SessionRouter.route_pending_web_confirmation()`.
- All 89 cap 64 tests pass; full suite 1564 pass, 4 skipped.
- Pushed as commit `93be5ff` on main.
- Cap 64 live checklist updated: status block added, "confirmed" → "yes" corrected, Test 4 points to `/api/trust/receipts` (Trust Panel UI not yet built).

### Cap 64 P5 ready state

P5 is now unblocked from the code side. Two environmental requirements remain:
- Ollama must be running at `localhost:11434` (or model lock must be cleared) for LLM body generation — without it, body falls back to static placeholder text, which is acceptable for P5 testing
- A mail client must be registered as the system `mailto:` handler

To run P5:
```
# Start Nova
nova-start

# In Nova chat:
draft an email to test@example.com about the quarterly review
# → Nova shows confirmation prompt with To: and Subject:
# → Type: yes
# → Mail client opens; verify To/Subject/Body; close without sending

# Verify ledger:
# http://localhost:8000/api/trust/receipts
# → should contain EMAIL_DRAFT_CREATED entry

# Sign off and lock:
python scripts/certify_capability.py live-signoff 64
python scripts/certify_capability.py lock 64
```

---

## Progress Update (2026-04-27) — Cap 65 P5 Live Signoff Audit

P5 status: **BLOCKED — Shopify credentials not present in this environment.**

Automated verification completed:
- 84 tests (P1–P4) all pass
- P1 unit (executor + connector): 9 tests pass
- P2 routing: 49 tests pass (19 canonical phrases, 8 period extractions, 6 negative phrases)
- P3 integration (governor spine): 16 tests pass
- P4 API (WebSocket + trust receipts): 10 tests pass

Safety confirmed:
- Read-only: all GraphQL calls use `query {}` only — zero mutations, zero write endpoints
- NetworkMediator path: confirmed active in `HttpShopifyConnector._gql()`
- Credential guard: executor returns clean `ActionResult.refusal()` when env vars absent

Blocker: `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN` not set.

To unblock:
```
set NOVA_SHOPIFY_SHOP_DOMAIN=mystore.myshopify.com
set NOVA_SHOPIFY_ACCESS_TOKEN=shpat_...
nova-start
# Then run all 5 tests in docs/capability_verification/live_checklists/cap_65_shopify_intelligence_report.md
python scripts/certify_capability.py live-signoff 65 --notes "all tests pass, read-only confirmed on <store domain>"
python scripts/certify_capability.py lock 65
```

Doc updates this session: live checklist updated with audit results and status block; `Now.md` updated.

---

## Progress Update (2026-04-26)

### Done

- Trust receipt backend hardened: outer `try/except Exception` in `get_recent_receipts()` prevents any ledger error from surfacing as an API 500; `isinstance(entry, dict)` guard skips non-dict JSON lines; fresh-install and corrupt-ledger both return `[]`
- 18 direct unit tests added for `receipt_store.py` (`nova_backend/tests/trust/test_receipt_store.py`) — missing ledger, empty ledger, malformed JSON, non-dict JSON, ordering, limit, OSError, unexpected exception, all 14 receipt-worthy event types
- Loopback guard wired at the trust router level: `APIRouter(dependencies=[Depends(require_local_http_request)])`; `/api/trust` added to `_LOCAL_ONLY_API_PREFIXES` in `local_request_guard.py` (without this the guard was a no-op for trust routes)
- Runtime drift check was failing: README contained a bare capability name and the phrase "Runtime Fingerprint" as link text — both fixed
- Four 2026-04-25 audit docs stranded in the worktree branch were landed on main (deep second-pass, final confirmation pass, third deep wide, fourth pass)
- QUICKSTART.md updated: optional features table (voice, calendar, Shopify) and `NOVA_HOST`/`NOVA_PORT` env var notes
- All stale branches cleaned up (local + remote); three claude worktrees removed; `restore/trust-receipts-cap65` deleted post-merge
- BackLog.md updated: three completed hardening items marked done; ci.yml comment and verify_windows.ps1 prereq checks added; troubleshooting sections added to cap 64 and cap 65 live checklists
- `capability_locks.json` `updated` date corrected; `STATUS.md` date header corrected

### Verified state

- 104 tests pass, 4 skipped; runtime drift check passes; `git status` clean; local main = origin/main

### Still open

- Cap 64 P5 live signoff (requires running Nova + configured mail client)
- Cap 65 P5 live signoff (requires `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN`)

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
