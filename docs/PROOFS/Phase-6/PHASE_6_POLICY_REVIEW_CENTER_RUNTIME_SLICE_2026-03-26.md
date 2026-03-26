# Phase-6 Policy Review Center Runtime Slice
Date: 2026-03-26
Status: Implemented runtime slice
Scope: User-facing review surface for disabled policy drafts, simulations, and one-shot review runs

## Purpose
This slice makes the Phase-6 delegated-policy foundation visible to normal users.

It does not enable automation.

It adds a product surface where users can:
- inspect disabled policy drafts
- review draft envelope limits
- run simulations
- inspect one-shot manual review runs

## What Landed
- dedicated `Policies` page in the dashboard
- policy overview widget hydration
- selected draft detail panel
- simulation result panel
- one-shot manual run result panel
- starter draft actions for:
  - weekday calendar snapshot
  - daily weather snapshot
- cross-links from Trust and Settings into Policies
- policy page route commands:
  - `policy center`
  - `policy review`
  - `open policies`

## Important Bug Fix Included
This slice also fixes a real command-path issue:
- policy command regexes now match the punctuation-trimmed command text

That means:
- `policy show <id>`
- `policy simulate <id>`
- `policy run <id> once`
- `policy delete <id> confirm`

continue to work even when the session router normalizes a user sentence with trailing punctuation.

## Runtime Shape
Nova can now:
- create disabled policy drafts
- show them in a dedicated Policy Review Center
- simulate them through the Governor executor gate
- manually run safe ones once
- keep the whole flow visible and inspectable for non-technical users

Nova still cannot:
- run policy triggers in the background
- enable stored policies for autonomous execution
- quietly widen delegation rules
- bypass the Governor to make policy execution easier

## Core Files
- `nova_backend/src/brain_server.py`
- `nova_backend/src/audit/runtime_auditor.py`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/index.html`
- `nova_backend/static/style.phase1.css`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/style.phase1.css`

## Tests Added Or Expanded
- `nova_backend/tests/phase45/test_dashboard_policy_center_widget.py`
- `nova_backend/tests/phase45/test_policy_center_surface.py`
- existing `nova_backend/tests/phase6/*` foundation suites retained

## Verification
- focused policy page + Phase-6 bundle: `25 passed`
- focused affected conversation bundle: `5 passed`
- broader regression bundle: passed in follow-up validation
- dashboard syntax check: passed
- frontend mirror sync check: passed
- runtime documentation drift check: passed

## Why This Matters
Before this slice, Phase-6 policy foundations existed mostly through chat commands and backend proofs.

Now they are also visible as a product surface:
- clearer to inspect
- easier to trust
- easier to explain to non-technical users

## Correct Interpretation
This slice means:
- Phase 6 is now active in runtime as a review-only delegated-policy layer

It does not mean:
- autonomous policy execution is live
- background triggers are enabled
- Nova has moved beyond its invocation-bound trust model
