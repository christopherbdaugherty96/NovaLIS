# Active TODO - Nova

## PRIORITY LOCK STATUS (2026-05-07)

Refer to: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-06_WEB_NEWS_PROOF_STRESS_TEST.md`

Updated: 2026-05-07 after PR #121 added deterministic Web/News stress fixtures for contradictory reporting, duplicate/prior-state topic maps, and split-topic headline comparison.

Current active workstream:

```text
Governed Web / News / Reporting + UI / Commands Proof + Stress Test
```

This lock permits only proof scaffolding, proof artifacts, simulations, stress-test prompts, and audit work for existing governed information/reporting and visible UI/command surfaces.

This is not an automation-expansion lock.

PR #119 improved proof-library coverage.

PR #121 reduced the contradiction and duplicate/split-topic proof gaps with deterministic tests and proof evidence, but it did not close the active proof/stress-test lock.

---

## Current Next TODO

Build the next proof/stress-test pass for remaining governed web/news/reporting truthfulness gaps.

Highest-priority remaining proof gaps:

- stale-cache/provider-failure fixtures
- source-credibility matrix fixtures
- freshness labeling
- confidence lowering under weak/old/untrusted sources
- rapid-click / double-submit UI behavior
- malformed-widget payload behavior
- Browser Use screenshot/click-path proof after runtime asset setup is fixed
- broader visual UI/button coverage beyond command-path evidence

Recommended next branch:

```text
proof/stale-provider-credibility-fixtures
```

Expected proof outcome is truthful behavior, not guaranteed success.

Required proof focus retained from the active lock:

- governed web search
- browser/article open behavior
- headline summaries
- headline cluster comparison
- multi-source reports
- intelligence briefs
- topic maps
- story tracking
- dashboard buttons/widgets
- command entry flows
- degraded/error states
- confirmation prompts
- blocked-action behavior
- setup-required states
- truthful UI state labels: working, blocked, setup-required, degraded, offline, unsupported
- voice/media/system controls
- analysis/memory/document surfaces

Required stress-test focus retained from the active lock:

- malformed feeds
- conflicting narratives
- stale caches
- duplicate stories
- fake/low-credibility sources
- governance bypass attempts
- hallucinated attribution
- topic-map instability
- network failure paths
- rapid repeated button presses
- stale WebSocket state
- malformed widget payloads
- blocked-action coercion attempts
- degraded-state rendering
- prompt injection from article content

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

- Governed Web / News / Reporting + UI / Commands Proof + Stress Test

Completed under current lock:

- proof package scaffolds created
- Web/News proof library index created
- case-level proof files created for governed web search, open website/article behavior, headline summaries, multi-source reporting/intelligence brief, topic map/story tracker, and governance/adversarial/degraded behavior
- seeded adversarial prompt suite created
- master UI/button/command verification matrix created
- generator-consistent MOC/runtime-doc refresh completed after proof docs were added
- contradictory reporting fixture added and verified
- duplicate/prior-state topic-map fixture added and verified
- split-topic headline comparison fixture added and verified

Still open under current lock:

- stale-cache/provider-failure fixtures
- source-credibility matrix fixtures
- freshness labeling and confidence lowering under weak/old/untrusted sources
- timeline-drift fixtures
- rapid-click/double-submit proof
- malformed-widget proof
- Browser Use screenshot/click-path proof after asset setup is fixed
- broader visual UI/button proof beyond command-path evidence
- final lock closeout review

Paused prior lock:

- Trust Review Card MVP / Visible Non-Action Receipt Surface

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
- Trust Review Card implementation while paused

---

**Historical baseline below is retained for completed-context only. Work outside the active Web/News/Reporting + UI/Commands proof/stress-test lock requires a new reviewed priority lock.**
