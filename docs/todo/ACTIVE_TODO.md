# Active TODO - Nova

## ACTIVE PRIORITY LOCK (2026-05-04)

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-04.md`

Updated: 2026-05-06 after PR #106 merged.

Only active path:

```text
RequestUnderstanding trust/action-history review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
```

All other work is paused. If a task does not advance one of these four steps, it is paused.

---

## Current Next TODO

Build the first read-only OpenClaw workflow proof.

Purpose:

- prove one narrow workflow through the reviewed OpenClawMediator boundary
- use safe caller-provided sample/local input only
- require explicit allowed input scope
- produce a read-only proof artifact and receipt/non-action statement
- keep browser/computer-use, filesystem writes, external writes, direct Cap 63 shortcut use, and workflow automation blocked

Do not broaden OpenClaw beyond this proof path.

Branch/proof targets:

- `nova_backend/src/openclaw/read_only_workflow_proof.py`
- `docs/demo_proof/2026-05-06_first_read_only_openclaw_workflow/`

## Lock Progress

- Step 1 foundation complete:
  - planning-task preview runtime handoff proof merged in PR #103
  - RequestUnderstanding review-card payload contract merged in PR #104
- Step 1 remaining optional/future work:
  - minimal visible read-only UI card render
  - real receipt/action-history integration beyond `history_status: "not_available"`
- Step 2 complete:
  - local capability signoff matrix merged in PR #105
- Step 3 complete:
  - OpenClawMediator skeleton merged in PR #106
- Step 4 is now the recommended next work item:
  - first read-only OpenClaw workflow proof

---

**Historical baseline below is retained for completed-context only. It is not the active sprint while the priority lock is in force.**

**Updated:** 2026-05-03 (cost posture pass)
**Previous sprint goal:** Stage 6 — Routine surfaces. Context Pack and BrainTrace now live in prompt path.
**Authority note:** This file is the public task snapshot. Exact runtime truth still comes from generated runtime docs and code.

## Completed Baseline Before Priority Lock

- Active proof closeout — PASS (Daily Brief, Search Evidence Synthesis, conversation continuity, prior full-suite proof)
- Stage 3 Memory Loop — explicit remember / review-list / update / forget / why-used with receipts
- Stage 4 Context Pack — bounded labeled context bridge with proof package
- Stage 5 Brain discipline and BrainTrace — non-authorizing trace without private chain-of-thought exposure
- Stage 6 RoutineGraph v0 — Daily Brief routine surface, non-authorizing
- Plan My Week routine — proposal + approval record + receipt, non-authorizing
- Cost posture metadata — visibility only, no runtime enforcement
- Google read-only connector foundation plan — planning only, no OAuth/runtime connector

## Paused While Priority Lock Is Active

- Plan My Week UI/API proof capture
- business workflow demos
- governed workflow workspace shell
- workflow object model or workflow template schema
- Google OAuth connector runtime work
- Gmail/Calendar/Drive/Contacts runtime connector work
- Gmail/Calendar/Drive write or send capabilities
- Cap 64 P5 live signoff + lock
- Cap 65 P5 live signoff + lock
- Shopify write operations
- OpenClaw broad automation
- OpenClaw browser/computer-use expansion
- OpenClaw scheduled external actions
- Voice / ElevenLabs expansion
- dashboard polish not directly required for the review card or signoff matrix
- README screenshots/GIFs
- waitlist activation
- one-click installer work
- Auralis social content runtime integration
- YouTubeLIS runtime integration
- free-first runtime enforcement beyond existing metadata unless directly required by signoff safety
- general doc cleanup unless it directly supports this lock
