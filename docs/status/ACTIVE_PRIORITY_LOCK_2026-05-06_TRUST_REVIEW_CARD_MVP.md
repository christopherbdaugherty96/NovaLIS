# Active Priority Lock - 2026-05-06 Trust Review Card MVP

Status: active / MVP implementation in progress.

Resumed after qualified closeout: `docs/status/WEB_NEWS_UI_PROOF_LOCK_CLOSEOUT_REVIEW_2026-05-07.md`

This is human-maintained priority guidance, not generated runtime truth.

Generated runtime docs and actual code remain authoritative if they conflict with this lock.

---

## Active Workstream

```text
Trust Review Card MVP / Visible Non-Action Receipt Surface
```

---

## Resume Context

The user requested a pause on current work to create a proof folder and stress-test plan for the governed web/news/reporting capability family:

- governed web search
- governed browser/article opening
- headline summaries
- headline cluster comparison
- structured multi-source reports
- compact intelligence briefs
- story tracking over time
- topic maps of headline themes

The Web/News/Reporting + UI/Commands proof/stress-test lock is now qualified closed. Browser Use screenshot/click-path proof, high-frequency browser event replay, broader visual UI proof, deeper widget-specific fuzzing, and timeline-drift fixtures are carried forward as proof debt.

Trust Review Card MVP may resume as a narrow deterministic visibility surface.

---

## Original Purpose

Create the first visible trust/review surface for the planning-only and read-only governance work completed in the prior OpenClaw proof chain.

This lock exists to connect the current backend governance/proof infrastructure to a visible user-facing review surface without expanding authority.

The target is a minimal read-only review/trust card surface.

This is not an automation-expansion lock.

## MVP Principle

```text
derive, don't invent
```

The Trust Review Card must be an inspectability surface over existing state. It must not become a planner, router, executor, workflow engine, or LLM-generated trust narration surface.

---

## Allowed Scope

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

---

## Still Not Approved

- no OpenClaw execution
- no direct Cap 63 shortcut use
- no browser/computer-use
- no filesystem writes
- no external writes
- no email/calendar/Shopify/account actions
- no autonomous workflow execution
- no Google connector runtime work
- no capability registry expansion
- no workflow automation expansion
- no scheduler expansion
- no installer work

---

## Resume Rule

This lock has resumed after the Web/News/UI proof lock qualified closeout. Keep implementation narrow and display-only.
