# Active TODO - Nova

**Updated:** 2026-05-03 (cost posture pass)
**Sprint goal:** Stage 6 — Routine surfaces. Context Pack and BrainTrace now live in prompt path.
**Authority note:** This file is the public task snapshot. Exact runtime truth still comes from generated runtime docs and code.

## Stepwise Execution Order

### Step 1 - Active proof closeout — DONE

- [x] Re-run Daily Brief + continuity proof — PASS (2026-05-02, all 4 proof docs updated)
- [x] Re-run Search Evidence Synthesis functional proof — PASS (source_backed/weak/snippet cases)
- [x] Conversation continuity fields proof — PASS (412 conversation tests, roundtrip verified)
- [x] Full suite — PASS (1877 passed, 4 skipped, exit 0)
- [ ] Capture a short public conversation/search demo (optional, not blocking memory loop)

### Step 2 - Update status after proof — DONE

- [x] Proof results recorded in `docs/demo_proof/daily_operating_baseline/`
- [x] TODO and status docs updated with proof outcome

### Step 3 - Memory loop implementation — DONE

- [x] Memory full loop - remember / review-list / update / forget / why-used, without silent autosave
- [x] Add memory receipts for create / update / forget / use
- [x] Prove memory is not used before confirmation
- [x] Prove forgotten memory is not reused
- [x] Prove memory never authorizes action
- [ ] Add Memory UX flows - remember / forget / review saved memory (post-Stage 5)

### Step 4 - Context Pack implementation — DONE

- [x] Implement Context Pack object with source labels, authority labels, budget limits,
      why-selected metadata, and stale/conflict warnings
- [x] Prove candidate items are not treated as confirmed
- [x] Prove runtime truth outranks memory
- [x] Prove Context Pack budgets are enforced

### Step 5 - Brain discipline and trace — DONE

- [x] Add mode contracts for brainstorm, repo-review, implementation, merge, planning, and action-review
- [x] Add safe BrainTrace fields without exposing private chain-of-thought
- [ ] Improve conversation follow-up/topic tracking for connector/governance topics (Stage 6)
- [ ] Tighten uncertainty wording for health/safety/current-evidence questions (Stage 6)

### Step 6 - Routine and workflow surfaces — ACTIVE SPRINT

- [x] Convert Daily Brief into RoutineGraph v0 — PR #93 2026-05-03; 60 tests; RoutineBlock,
      RoutineGraph, RoutineRun, RoutineReceipt frozen non-authorizing dataclasses;
      run_daily_brief_routine() wraps compose_daily_brief() with named blocks + receipt
- [x] Plan My Week routine — PR #98 2026-05-03; 52 tests; WeeklyPlan, PlanMyWeekProposal
      (approval_required=True), PlanApprovalRecord; two-phase runner: propose → record decision
- [ ] Capture UI/API proof demo for Plan My Week (proposal, approval boundary, approval record, receipt; no execution)
- [ ] Capture one business workflow demo: find 5 local businesses that need better websites, draft improvement notes, and create reviewable outreach drafts
- [ ] Define governed workflow workspace shell for everyday workflows, independent automation, and business-owner use cases
- [ ] Draft workflow object model and workflow template schema

## Current Priorities (ordered)

- [x] Convert Daily Brief into RoutineGraph v0 (PR #93, 2026-05-03)
- [x] Inject Context Pack and BrainTrace into live general_chat_runtime.py prompt assembly (PR #89, 2026-05-02)
- [ ] Re-run Daily Brief + continuity proof manually in the local UI/API
- [x] Plan My Week routine (PR #98, 2026-05-03)
- [ ] Continue doc/status cleanup where stale wording remains
- [x] Implement cost posture metadata — first free-first step (PR #99, 2026-05-03); metadata + visibility only, no enforcement
- [x] Plan Google read-only connector foundation — planning doc only; no OAuth, no runtime connector
- [ ] Prepare OpenClaw hardening pass: mandatory EnvelopeFactory, approval decisions, centralized execution guard, boundary detection, and receipts
- [ ] Fuller Trust Review Card / Trust Panel
- [ ] Windows installer VM validation
- [ ] README screenshot or GIF of governed action flow
- [ ] Dashboard home improvements
- [ ] Cap 65 P5 live signoff
- [ ] Waitlist activation

## Current Proof Queue

- [ ] Re-run conversation/search proof prompts after Search Evidence Synthesis merge
- [ ] Capture a short public conversation/search demo
- [ ] Capture Plan My Week UI/API proof (proposal → approval record → receipt; no execution)
- [ ] Capture one business workflow demo
- [ ] Run Cap 64 live signoff only after conversation/search proof is stable
- [ ] Run Cap 65 credential-backed proof only after Shopify env vars are available

## Important Principle

Current priorities favor:
- coherent everyday assistant behavior
- visible trust
- onboarding quality
- proof of value
- usability
- truthful readiness

Not raw feature count.

## Paused (do not start)

- Cap 64 P5 live signoff + lock
- Solo Business Assistant shell (Tier 2)
- Google OAuth connector runtime work
- Gmail/Calendar/Drive write or send capabilities
- OpenClaw broad automation
- OpenClaw browser/computer-use expansion until envelope issuance, approval decisions, execution guard, boundary detection, and receipts exist
- Voice / ElevenLabs expansion
- Auralis social content runtime integration before manual validation and Nova memory/context/routine foundations

## Recently Completed

- Google read-only connector foundation plan — planning only (no OAuth/runtime connector)
- Cost posture metadata — visibility only (no enforcement)
- Plan My Week routine — proposal + approval record + receipt (non-authorizing)
- RoutineGraph v0 — Daily Brief as first governed routine (non-authorizing)
- Stage 6 wiring — Context Pack and BrainTrace live in general_chat_runtime.py
- Stage 5 Brain discipline — mode contracts + BrainTrace
- Stage 4 Context Pack — bounded, labeled context bridge
- Stage 3 Memory loop — explicit, receipted memory system
