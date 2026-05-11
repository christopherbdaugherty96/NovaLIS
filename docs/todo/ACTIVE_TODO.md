# Active TODO - Nova

## PRIORITY LOCK STATUS (2026-05-11)

No active priority lock.

Most recently completed workstream:

```text
Everyday UX Friction + Live Daily Workflow Testing
```

Status:

```text
CLOSED — PR #135–#140 merged / closeout doc PR #144 / 2026-05-11
Work-style enforcement lock: PR #145 merged / 2026-05-11
```

Final implementation PR #140 merged 2026-05-11. Final commit on main: `ae0fba5`.
Closeout doc: `docs/PROOFS/Everyday-UX/EVERYDAY_UX_FRICTION_CLOSEOUT_2026-05-11.md`

Prior completed workstream:

```text
Cap 16 governed_web_search certification lock
```

Status:

```text
LOCKED — P1–P5 passed / 60 tests / locked_date 2026-05-10
```

PR #134 merged 2026-05-10.

---

## Active TODO

None. No active priority lock.

Open follow-up issues (each needs own scoped investigation before becoming active):

- [ ] #141 — Search widget not surfacing in live WebSocket sessions
- [ ] #142 — RS-2 capability list truncation (may be context-length dependent)
- [ ] #143 — `"tell me more"` with prior context — session-state-aware test needed

---

## Queued / deferred

```text
ui/simplify-dashboard-core-navigation — needs own reviewed priority lock
Cap 64 P5 — paused until own lock
```

---

## Prior lock history (archive — 2026-05-07)

## Current Next TODO

Merge PR #135 if review passes, then begin:

```text
proof/everyday-ux-live-workflow-baseline
```

Run the 13 live workflow scenarios and record evidence. Do not make fixes in the baseline branch.

Current recovery result:

```text
blocked / setup-required
```

Browser Use/iab still fails before JavaScript execution in the Node REPL kernel asset setup layer:

```text
failed to write kernel assets: The system cannot find the path specified. (os error 3)
```

Current event replay result:

```text
deterministic replay proof added / 22 passed
```

Current non-search widget fuzzing result:

```text
deterministic contract verification added / 21 passed (51 passed expanded)
```

Proof infrastructure closeout result:

```text
substantially reduced / closeout-ready
closeout review: docs/status/PROOF_INFRASTRUCTURE_CLOSEOUT_REVIEW_2026-05-09.md
```

The proof infrastructure chain (PRs #129–#131) is classified as substantially reduced.
Browser Use visual capture remains blocked/setup-required. Deeper widget fuzzing is
deferred as low-urgency follow-up.

Carried-forward proof gaps:

- Browser Use screenshot/click-path proof after runtime asset setup is fixed
- broader visual UI/button coverage beyond command-path evidence
- policy widget deep field fuzzing (deferred / low-urgency)
- voice/audio status widget field fuzzing (deferred / low-urgency)
- workspace/thread widget field fuzzing (deferred / low-urgency)
- timeline-drift fixtures (deferred / low-urgency)

Recommended next branch:

```text
proof/browser-use-visual-capture-recovery (when setup is repaired)
or no new proof infrastructure until visual capture is unblocked
```

Reason:

Deterministic proof infrastructure is substantially reduced. Remaining open items
are either blocked at the Browser Use setup layer or low-urgency deferred follow-ups.
No new proof infrastructure branches are needed until visual capture is unblocked.

Browser Use proof-infrastructure follow-up remains:

- repair screenshot/click-path proof capture only
- capture visual evidence for existing UI surfaces if Browser Use runtime capture works
- keep Browser Use screenshot/click-path proof explicitly blocked if runtime capture remains unavailable
- no browser/computer-use capability expansion
- no autonomous browsing
- no execution authority
- no OpenClaw expansion
- no new capabilities
- no external writes

Completed Trust Review Card MVP pass:

- propagates existing `request_understanding_review_card` payloads into general-chat WebSocket responses
- renders deterministic display-only card rows in chat
- adds tests proving no action buttons, dispatch handlers, confirmation acceptance, capability calls, Governor calls, OpenClaw calls, or state mutation from rendering
- closeout review classifies PR #127 as merged / display-only / non-authorizing / follow-ups tracked

Current completed audit/proof outcomes:

- generated runtime docs changed only through the generator path
- runtime truth changes remained code-grounded and generator-consistent
- proof-only OpenClaw artifacts were not inflated into runtime authority
- raw proof evidence and screenshot folders are excluded from generated runtime/reference topical MOCs where appropriate
- runtime truth audit merged in PR #110
- Trust Review Card MVP lock selected in PR #112 and later paused by user request
- Web/News/Reporting + UI/Commands proof/stress-test lock created in PR #114
- Web/News proof library, case-level proof files, adversarial prompt suite, and master UI/button/command matrix merged in PR #119
- PR #119 organized already-captured raw evidence into reviewer-readable proof cases and refreshed generated MOCs/runtime-doc indexes through the generator path
- PR #121 added deterministic stress fixtures for contradictory reporting, duplicate/prior-state topic-map behavior, and split-topic headline comparison
- PR #121 recorded `24 passed` for `nova_backend/tests/executors/test_news_intelligence_executor.py`
- PR #121 recorded `23 passed` for the adjacent web search / search synthesis / story tracker slice
- the stale/provider/credibility fixture pass added deterministic search evidence/web search tests for stale timestamps, malformed provider payloads, degraded provider status, and weak/untrusted source signals
- the stale/provider/credibility fixture pass recorded `24 passed` for the search evidence/web search slice and `28 passed` for the adjacent news/story slice
- the dashboard stale/degraded rendering pass added visible search widget rendering for provider status, freshness status, source credibility rows, and empty degraded search state
- the dashboard stale/degraded rendering pass recorded `4 passed`, `24 passed`, `2 passed`, and JS syntax checks for the focused rendering branch
- the malformed widget / rapid-submit proof pass added an unsupported dashboard-message fallback and contract proof for overlapping send blocks, single-use send binding, turn-id filtering, assistant-text de-dupe, and pending confirmation isolation
- the malformed widget / rapid-submit proof pass recorded `25 passed` and JS syntax checks for served/mirrored dashboard files
- the Web/News/UI proof lock closeout review classified the lock as qualified closed and carried Browser Use screenshot/click-path proof forward as visual proof infrastructure debt
- the Trust Review Card MVP closeout review accepted PR #127 as a display-only non-action receipt surface and kept Browser Use screenshot/click-path proof as separate proof-infrastructure debt
- the Browser Use visual capture recovery attempt recorded `blocked / setup-required` because Node REPL fails before JavaScript execution with `failed to write kernel assets`; no screenshot or click-path proof was captured or faked
- the dashboard event replay harness recorded `22 passed` for deterministic replay and adjacent dashboard contract checks, plus JS syntax checks for served/mirrored dashboard files
- the non-search widget fuzzing pass recorded `21 passed` for focused malformed/degraded payload contract verification and `51 passed` for the expanded suite including prior harness and adjacent checks
- the proof infrastructure closeout review classifies the full deterministic proof chain (PRs #129–#131) as substantially reduced and closeout-ready; Browser Use visual proof is carried forward as separate proof debt; deeper widget fuzzing is deferred as low-urgency follow-up

Do not broaden OpenClaw or start product/runtime expansion outside the active reviewed priority lock.

References:

- `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`
- `docs/status/OPENCLAW_PRIORITY_LOCK_CLOSEOUT_2026-05-06.md`
- `docs/PROOFS/Web-News-Reporting/README.md`
- `docs/PROOFS/Web-News-Reporting/PROOF_LIBRARY_INDEX.md`
- `docs/PROOFS/Web-News-Reporting/adversarial_tests/PROMPT_SUITE_2026-05-07.md`
- `docs/PROOFS/UI-Commands/README.md`
- `docs/PROOFS/UI-Commands/MASTER_UI_VERIFICATION_MATRIX_2026-05-07.md`

## Lock Progress

Current active lock:

- Trust Review Card MVP / Visible Non-Action Receipt Surface

Most recently completed lock:

- Governed Web / News / Reporting + UI / Commands Proof + Stress Test: qualified closed

Completed under the qualified-closed Web/News/UI proof lock:

- proof package scaffolds created
- Web/News proof library index created
- case-level proof files created for governed web search, open website/article behavior, headline summaries, multi-source reporting/intelligence brief, topic map/story tracker, and governance/adversarial/degraded behavior
- seeded adversarial prompt suite created
- master UI/button/command verification matrix created
- generator-consistent MOC/runtime-doc refresh completed after proof docs were added
- contradictory reporting fixture added and verified
- duplicate/prior-state topic-map fixture added and verified
- split-topic headline comparison fixture added and verified
- stale-cache/provider-failure fixture coverage added and verified
- source-credibility matrix fixture coverage added and verified
- freshness labeling and confidence lowering under weak/old/untrusted source signals added and verified
- dashboard-rendered stale/degraded search evidence state added and verified
- malformed/degraded search widget empty-state rendering added and verified
- unsupported dashboard/WebSocket message fallback added and verified
- rapid-click/double-submit contract guard coverage added and verified
- dashboard event replay harness added and verified
- non-search widget malformed/degraded payload fuzzing added and verified
- proof infrastructure closeout review written and accepted

Carried-forward proof debt:

- timeline-drift fixtures
- Browser Use screenshot/click-path proof after asset setup is fixed
- broader visual UI/button proof beyond command-path evidence
- deeper widget-specific malformed payload fixtures beyond search/unsupported-message coverage
- final lock closeout review added

Resumed prior lock:

- Trust Review Card MVP / Visible Non-Action Receipt Surface: merged / display-only / non-authorizing / follow-ups tracked

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
- Trust Review Card implementation outside the narrow resumed MVP/non-action receipt scope

---

**Historical baseline below is retained for completed-context only. Work outside the resumed Trust Review Card MVP / Visible Non-Action Receipt Surface scope requires a new reviewed priority lock.**
