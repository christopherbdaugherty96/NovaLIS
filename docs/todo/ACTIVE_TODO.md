# Active TODO - Nova

## PRIORITY LOCK STATUS (2026-05-06)

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_TRUST_REVIEW_CARD_MVP.md`

Updated: 2026-05-06 after Trust Review Card MVP lock selection.

Current active workstream:

```text
Trust Review Card MVP / Visible Non-Action Receipt Surface
```

This lock permits only a visible, read-only trust/review card surface and related non-action receipt display/proof work.

This is not an automation-expansion lock.

---

## Current Next TODO

Implement the active Trust Review Card MVP priority lock.

Allowed implementation scope:

- render a minimal read-only RequestUnderstanding review card in the UI
- render non-action / non-authorizing status fields clearly
- render receipt fields such as:
  - what happened
  - what did not happen
  - blocked actions
  - history unavailable / not available states
- add tests proving the trust card cannot imply execution occurred
- improve trust wording clarity where needed
- regenerate runtime docs through the generator path if runtime truth changes
- audit wording for OpenClaw overstatement or authority drift

Current completed audit outcomes:

- generated runtime docs changed only through the generator path
- runtime truth changes remained code-grounded and generator-consistent
- proof-only OpenClaw artifacts were not inflated into runtime authority
- raw proof evidence and screenshot folders are excluded from generated runtime/reference topical MOCs
- runtime truth audit merged in PR #110
- Trust Review Card MVP lock selected in PR #112

Do not broaden OpenClaw or start product/runtime expansion outside the active reviewed priority lock.

References:

- `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_TRUST_REVIEW_CARD_MVP.md`
- `docs/status/OPENCLAW_PRIORITY_LOCK_CLOSEOUT_2026-05-06.md`

## Lock Progress

Current active lock:

- Trust Review Card MVP / Visible Non-Action Receipt Surface

Planned lock targets:

- minimal visible read-only UI trust/review card render
- receipt/non-action rendering
- history unavailable / not available state rendering
- trust wording clarity pass
- tests proving the UI cannot imply execution
- audit for authority drift after implementation

Completed runtime truth audit lock:

- Step 1 complete:
  - runtime truth regeneration / audit after OpenClaw proof chain merged in PR #110

Completed previous lock:

- Step 1 foundation complete:
  - planning-task preview runtime handoff proof merged in PR #103
  - RequestUnderstanding review-card payload contract merged in PR #104
- Step 2 complete:
  - local capability signoff matrix merged in PR #105
  - authority-boundary clarification merged in PR #112
- Step 3 complete:
  - OpenClawMediator skeleton merged in PR #106
- Step 4 complete:
  - first read-only OpenClaw workflow proof merged in PR #107

## Still Not Approved

- broad OpenClaw automation
- browser/computer-use expansion
- external writes
- email/calendar/Shopify/account actions
- direct Cap 63 shortcut use
- autonomous workflow execution
- Google connector expansion
- claiming OpenClaw has full governed hands
- capability registry expansion outside reviewed lock scope
- workflow automation expansion
- scheduler expansion
- installer work

---

**Historical baseline below is retained for completed-context only. Work outside the active Trust Review Card MVP lock requires a new reviewed priority lock.**

**Updated:** 2026-05-03 (cost posture pass)
**Previous sprint goal:** Stage 6 - Routine surfaces. Context Pack and BrainTrace now live in prompt path.
**Authority note:** This file is the public task snapshot. Exact runtime truth still comes from generated runtime docs and code.

## Completed Baseline Before Priority Lock

- Active proof closeout - PASS (Daily Brief, Search Evidence Synthesis, conversation continuity, prior full-suite proof)
- Stage 3 Memory Loop - explicit remember / review-list / update / forget / why-used with receipts
- Stage 4 Context Pack - bounded labeled context bridge with proof package
- Stage 5 Brain discipline and BrainTrace - non-authorizing trace without private chain-of-thought exposure
- Stage 6 RoutineGraph v0 - Daily Brief routine surface, non-authorizing
- Plan My Week routine - proposal + approval record + receipt, non-authorizing
- Cost posture metadata - visibility only, no runtime enforcement
- Google read-only connector foundation plan - planning only, no OAuth/runtime connector

## Previously Paused During The Completed Priority Lock

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
