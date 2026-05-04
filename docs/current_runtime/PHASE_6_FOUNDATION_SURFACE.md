# Phase-6 Foundation Surface
Updated: 2026-03-14
Status: Present in code, but not an active delegated-runtime unlock

> **Context note (2026-05-04):** This document was written in March 2026 and describes the *atomic
> policy validation / draft storage* slice that was labeled "Phase 6" at that time. Current Stage 6
> work (2026-05-03) is different — it covers RoutineGraph v0, Plan My Week routine, and cost posture
> metadata. See `docs/status/CURRENT_WORK_STATUS.md` and `RUNTIME_CAPABILITY_REFERENCE.md` for the
> current Stage 6 truth. This file remains accurate for the atomic-policy foundation surface it
> describes, but it does not represent the full current Stage 6 scope.

## What Exists
Nova now has the first real Phase-6 foundation code in the repository:
- atomic policy validation in the Governor
- disabled-by-default atomic policy draft storage
- capability topology metadata for delegated-policy enforcement
- a Governor-side policy executor gate for simulation and manual review runs
- explicit draft-policy commands for create, show, list, delete, simulate, and `run once`
- Operator Health Surface with deterministic system-reason visibility
- a live "What Nova Can Do Right Now" capability panel driven from the enabled registry surface
- a ledger-backed Trust / Review surface for recent runtime activity and blocked conditions
- a dropdown-based dashboard header control strip for workspace, controls, and quick actions
- a simplified Home page focused on health, trust, discovery, threads, and a compact personal layer
- a dedicated Memory page for governed-memory inspection
- a stronger News page with source-grounded brief entry, article-summary actions, topic search, and broader political category pages
- a more polished orthogonal-review presentation and deeper natural-language detection for deep-analysis requests

## What Does Not Exist Yet
The following are still **not** active:
- trigger monitoring
- background policy evaluation
- enabled delegated trigger runtime
- enabled autonomous action from stored policies

## Correct Runtime Interpretation
For the current repository state:
- Phase 5 remains the active closed trust-facing runtime package
- Phase-6 foundation code now exists
- manual delegated policy review is now live through simulation and one-shot Governor-routed runs
- delegated trigger execution is still not live

## Why This Matters
This slice starts Phase 6 at the lawful boundary:
- define and validate policy first
- classify delegated capability authority before widening execution
- allow simulation and one-shot review runs before any trigger runtime exists
- execute nothing automatically yet
- expose runtime state and blocked conditions clearly before deeper delegated infrastructure is added
- expose live discoverability from the current capability surface rather than static help copy
- expose recent runtime behavior through the ledger before delegated execution expands

That preserves Nova's current constitutional model while preparing the next phase safely.
