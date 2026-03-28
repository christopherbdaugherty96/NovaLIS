# Phase-4.5 Onboarding And Setup Readiness Refresh
Date: 2026-03-28
Scope: First-run onboarding, in-product setup guidance, and readiness visibility
Classification: Governance-safe UX refinement (no authority expansion)

## What Changed

1. Intro page now carries a live setup-readiness checklist
- Added a current-device readiness panel for:
  - runtime connection
  - local model route
  - setup mode
  - voice check
  - optional provider keys
  - optional remote bridge
  - optional home-agent surfaces
- Added a dynamic "next step" line so the product tells the user what to do next instead of making them infer it.

2. Settings page now mirrors the onboarding checklist
- Added a Setup Checklist panel that uses the same runtime truth as the Intro page.
- The Settings page now explains readiness, not just configuration choices.

3. Startup and recovery help now lives inside Nova
- Added an Intro-page recovery panel for users stuck on `Connecting`.
- The UI now explicitly shows:
  - `start_nova.bat` / `stop_nova.bat`
  - `./start_nova.sh` / `./stop_nova.sh`
- This reduces the need to leave the product just to recover a local-first setup issue.

4. First-run guidance is more actionable
- The first-run modal now includes a current readiness summary.
- It also includes a direct path to Connection Status so users can review runtime readiness immediately.

## Safety Invariants Preserved

- No new authority surface was added.
- No hidden automation was introduced.
- No new background behavior was added.
- The onboarding surfaces remain read-only guidance and page-routing helpers.
- Runtime truth still comes from the live settings, trust, websocket, and agent-status paths rather than hard-coded fake readiness.

## Files Touched

Frontend runtime:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/style.phase1.css`

Focused regression coverage:
- `nova_backend/tests/phase45/test_dashboard_onboarding_widget.py`
- `nova_backend/tests/phase45/test_dashboard_trust_center_widget.py`

Human guides:
- `docs/reference/HUMAN_GUIDES/01_START_HERE.md`
- `docs/reference/HUMAN_GUIDES/07_CURRENT_STATE.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
- `docs/reference/HUMAN_GUIDES/26_LOCAL_SETUP_AND_STARTUP.md`

## Verification

Focused validation after patch:
- `python -m pytest C:\Nova-Project\nova_backend\tests\phase45\test_dashboard_onboarding_widget.py C:\Nova-Project\nova_backend\tests\phase45\test_dashboard_trust_center_widget.py -q`
  - Result: `6 passed`
- `node --check nova_backend/static/dashboard.js`
- `node --check Nova-Frontend-Dashboard/dashboard.js`
- `python scripts/check_frontend_mirror_sync.py`
  - Result: passed

## Outcome

Nova's onboarding now does a better job of answering the first practical user questions inside the product itself:
- Am I connected?
- Is local mode ready?
- What is required right now?
- What is optional later?
- What should I do next?
- How do I recover if the local runtime is not connecting?

This is a UX and setup-trust improvement, not a capability-authority expansion.
