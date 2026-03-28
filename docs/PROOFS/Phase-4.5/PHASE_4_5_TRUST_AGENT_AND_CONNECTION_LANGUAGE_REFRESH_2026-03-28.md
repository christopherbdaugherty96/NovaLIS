# Phase 4.5 Trust, Agent, and Connection Language Refresh
Date: 2026-03-28
Status: Focused frontend wording refresh

## Purpose
This packet records the user-language refresh across the Trust, Agent, and Settings surfaces.

The goal of this pass was not to add new authority or new runtime behaviors.
The goal was to make the existing surfaces answer the questions a normal user actually has:

- what happened
- what was blocked
- what is ready now
- what is optional
- what still needs setup
- what is intentionally later

## Files Updated
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/tests/phase45/test_dashboard_trust_center_widget.py`
- `docs/reference/HUMAN_GUIDES/07_CURRENT_STATE.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
- `docs/reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md`

## What Changed
### Trust page
- hero and section copy now lead with:
  - what Nova did
  - what it refused
  - what left the device
  - what may need attention
- empty states now explain what the user should expect to appear there

### Agent page
- OpenClaw is now described more clearly as Nova's worker layer
- summaries distinguish:
  - manual runs available now
  - scheduling paused in Settings
  - optional weather/calendar sources
  - setup items that are still missing
- runtime labels were shifted from internal terminology toward user language

### Settings connections section
- wording now distinguishes:
  - what is visible now
  - what can be configured today
  - what still requires manual env or connector setup
- connection summary now explains that manual setup is still the current truth

## Verification
Executed from `nova_backend`:

- `python -m pytest tests/phase45/test_dashboard_trust_center_widget.py tests/phase45/test_dashboard_onboarding_widget.py -q`
- `node --check static/dashboard.js`
- `node --check ../Nova-Frontend-Dashboard/dashboard.js`
- `python ..\\scripts\\check_frontend_mirror_sync.py`

## Result
- Focused Phase 4.5 UI bundle passed
- Dashboard syntax checks passed for both runtime and mirror copies
- Frontend mirror sync check passed

## Runtime Truth Boundary
This refresh changes language and guidance only.

It does not:
- widen execution authority
- widen OpenClaw autonomy
- change reasoning-lane authority
- change connector implementation status

It makes the live frontend more legible and more honest for normal users.
