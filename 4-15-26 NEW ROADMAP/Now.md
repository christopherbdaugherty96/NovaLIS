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

---

## Active Blockers

- Cap 64 live checklist is not yet complete
- Clean Windows VM installer validation is paused pending `C:\Program Files\Nova\bootstrap.log` review
- GitHub Actions billing lock is preventing CI verification and README badges
- Formspree endpoint has not been activated for the waitlist flow

---

## This Week

- [ ] Run the cap 64 live checklist end-to-end
- [ ] Inspect `C:\Program Files\Nova\bootstrap.log`
- [ ] Complete clean Windows VM installer validation
- [ ] Activate Formspree for the landing page waitlist
- [ ] Add a screenshot or demo GIF to README
- [ ] Add CI badges after the GitHub billing issue is resolved

---

## Progress Update (2026-04-18)

### Done

- Local diagnostic pass completed for installer support surfaces
- `python scripts/fetch_models.py` succeeds locally
- `python scripts/start_daemon.py --no-browser` succeeds locally
- `installer/windows/nova_bootstrap.ps1` now fails fast on venv, pip install, and Nova startup errors instead of silently continuing
- `scripts/start_daemon.py` now reports when the Nova process exits before the health check succeeds

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

## Notes

- Do not start refactoring `brain_server.py` or `session_handler.py`. That is Tier 3 work.
- Docker fallback is allowed only if the native installer path is blocked; it does not replace the Tier 1 goal.
- Test every task completion on a clean Windows VM.

---

*This document is active. Update weekly. Move completed tasks to `CHANGELOG.md` and delete them from this file.*
