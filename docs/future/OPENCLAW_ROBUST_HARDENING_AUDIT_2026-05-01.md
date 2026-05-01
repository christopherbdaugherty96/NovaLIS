# OpenClaw Robust Hardening Audit — 2026-05-01

Status: audit and implementation recommendations; not generated runtime truth
Scope: OpenClaw robustness, authority alignment, envelope enforcement, approval gates, receipts, and future browser/computer-use readiness

This document records the final deeper-pass audit of OpenClaw after the 2026-05-01 branch/workstream alignment pass.

Generated runtime truth, code, tests, and proof artifacts win if they conflict with this note.

---

## Bottom Line

OpenClaw should not become more autonomous first.

OpenClaw should become more subordinate, inspectable, and run-based.

The correct target is:

```text
OpenClaw as Nova's governed hands layer:
bounded run -> visible plan -> explicit scope -> step execution -> boundary pauses -> receipts -> cleanup
```

The next work is not broad browser automation.

The next work is to make every OpenClaw path impossible to run unless it has:

- Task Envelope
- Run context
- Governor / capability path where appropriate
- step limits
- domain and tool budgets
- real approval gate
- pause/cancel behavior
- receipts
- cleanup

---

## Current Implemented Truth

OpenClaw is already partially implemented and constrained.

Current implemented surfaces include:

- Cap 63 `openclaw_execute` executor for named home-agent template runs.
- OpenClaw runtime code under `nova_backend/src/openclaw/`.
- Task envelopes with tools, allowed hostnames, steps, duration, network/file/byte budgets.
- Strict manual preflight for a narrow foundation of read-oriented tools.
- Scheduler gates for home-agent settings, scheduler settings, delivery policy, suppression, and daily limits.
- EnvelopeFactory as a future canonical envelope issuer, currently feature-flagged.
- Agent API endpoints for status, template runs, schedules, cancel, delivery dismissal, freeform goal runs, and action approval.
- Goal-run tests for freeform goal execution, cancellation, failure, terminal events, and per-tool budget reset.

Current status remains constrained:

- OpenClaw is not broad autonomy.
- Full Run-based OpenClaw execution is not finished.
- Personal browser control is not a safe default.
- Browser/computer-use expansion should not start until envelope issuance, approval, and receipt gaps are closed.

---

## Strong Existing Foundations

### 1. TaskEnvelope exists

`TaskEnvelope` already carries allowed tools, allowed hostnames, max steps, max duration, max network calls, max files touched, max bytes read, max bytes written, trigger source, delivery mode, metadata, and URL/hostname allow checks.

This is the right base for bounded OpenClaw execution.

### 2. Strict manual preflight exists

The strict manual foundation currently allows a narrow set of tools:

```text
calendar
news
project_read
schedules
summarize
weather
```

It also caps steps, duration, network calls, local files, bytes read, bytes written, and trigger labels.

The current strict foundation disallows writes by setting the write budget to zero.

### 3. Scheduler has meaningful gates

The scheduler checks settings, due templates, delivery policy, delivery suppression, claim-before-run behavior, max scheduled runs per day, and ledger events.

This is not an unbounded hidden loop.

### 4. EnvelopeFactory exists

EnvelopeFactory is the right direction: channel-aware, trigger-aware, settings-aware, feature-flag-aware, and able to emit issuance metadata.

However, it is still transitional and not mandatory.

### 5. Goal-run tests exist

The freeform `run_goal()` path is tested for structured result, execution memory, terminal events, cancellation, failure, and per-tool budget reset.

That is useful, but it also proves the freeform goal path is real enough to require stricter gating.

---

## Key Risks

## Critical Risk 1 — EnvelopeFactory is still optional

EnvelopeFactory is described as the sole authorized constructor of TaskEnvelopes, but it is currently gated by `NOVA_FEATURE_ENVELOPE_FACTORY`.

When the feature flag is false, legacy direct construction can still remain in effect.

That creates two authority paths:

```text
Path A: EnvelopeFactory-issued, stored, ledger-visible envelope
Path B: legacy direct construction
```

Nova should not keep two OpenClaw authority paths.

### Recommendation

Make EnvelopeFactory mandatory for all OpenClaw execution.

Rule:

```text
No EnvelopeFactory-issued envelope = no OpenClaw run.
```

Transition-safe behavior:

```text
If NOVA_FEATURE_ENVELOPE_FACTORY is false:
- manual template run: blocked
- scheduler run: blocked
- bridge run: blocked
- freeform goal run: blocked or preview-only
```

`OPENCLAW_DEPRECATED_DIRECT_RUN` may remain as a migration/error event, but it should not permit execution.

---

## Critical Risk 2 — Freeform goal execution is too agent-like

The `/api/openclaw/agent/goal` path accepts a freeform goal and calls `openclaw_agent_runner.run_goal(...)`.

The thinking loop can then reason about the goal, select tools, extract parameters, execute tools, decide whether to continue, and synthesize an answer.

Even with a 10-step cap, that is still LLM-selected tool execution.

This path must become subordinate to a Run Preview and Task Envelope before it expands.

### Recommendation

Demote freeform goal execution to preview-only until it is envelope-issued and approved.

Future flow:

```text
Freeform goal
-> TaskUnderstanding
-> Run Preview
-> proposed TaskEnvelope
-> user-visible scope
-> Governor / capability approval
-> envelope-filtered execution
```

Immediate safe behavior:

```text
Disable /api/openclaw/agent/goal for non-test use,
or restrict it to strict-preflight, read-only, envelope-issued tools only.
```

---

## Critical Risk 3 — approve-action currently auto-allows

The `/api/openclaw/approve-action` endpoint is a passthrough placeholder.

It logs proposed and approved action events, then returns `allow` / `auto_allowed`.

That is not a real approval system.

### Recommendation

Replace auto-allow with risk-aware decisions:

| Action class | Default decision |
|---|---|
| Read public page inside envelope | allow |
| Read local file inside envelope | allow if within budget |
| Off-domain navigation | pause or block |
| Login / credential field | block or pause |
| Submit / send / post | pause + explicit approval |
| Upload / download | pause + explicit approval |
| Purchase / checkout | block by default |
| Delete / archive / account mutation | block by default |
| Personal browser use | block by default |
| Unknown action | block |

---

## Critical Risk 4 — Scheduler can continue through deprecated direct-run path

The scheduler uses EnvelopeFactory when the feature flag is enabled.

If the flag is disabled, it logs `OPENCLAW_DEPRECATED_DIRECT_RUN` and can continue through legacy execution.

Scheduled execution should be stricter than manual execution, not looser.

### Recommendation

Change behavior to:

```text
EnvelopeFactory disabled
-> record OPENCLAW_ENVELOPE_REQUIRED
-> do not run
```

---

## High Risk 5 — Envelope enforcement must be centralized

TaskEnvelope contains URL/hostname checks and budgets, but robust OpenClaw should not rely on scattered enforcement.

Every tool call should pass one mandatory guard.

### Recommendation

Add a centralized execution guard:

```text
OpenClawExecutionGuard.check_before_tool_call(...)
OpenClawExecutionGuard.check_before_network(...)
OpenClawExecutionGuard.check_before_file(...)
OpenClawExecutionGuard.check_before_action(...)
```

The guard should enforce tool allowlist, hostname allowlist, step budget, duration budget, network budget, file budget, byte budget, write budget, and blocked action classes.

---

## High Risk 6 — Receipts are too coarse for future browser/computer use

Current ledger events are useful, but future browser/computer-use needs step-level and boundary-level receipts.

### Recommendation

Add receipt events:

```text
OPENCLAW_RUN_PREVIEW_CREATED
OPENCLAW_ENVELOPE_ISSUED
OPENCLAW_RUN_STARTED
OPENCLAW_STEP_STARTED
OPENCLAW_ACTION_PROPOSED
OPENCLAW_ACTION_ALLOWED
OPENCLAW_ACTION_PAUSED
OPENCLAW_ACTION_BLOCKED
OPENCLAW_BOUNDARY_DETECTED
OPENCLAW_STEP_COMPLETED
OPENCLAW_RUN_CANCEL_REQUESTED
OPENCLAW_RUN_CANCELLED
OPENCLAW_RUN_FAILED
OPENCLAW_RUN_COMPLETED
OPENCLAW_SESSION_CLEANED_UP
```

Receipt payload should include run id, envelope id, step id, template id or goal hash, tool name, action type, target hostname / URL when safe, decision, reason, budget snapshot, and timestamp.

Do not log credentials, OAuth tokens, private message contents, payment details, full sensitive screenshots, or unrelated private account data.

---

## High Risk 7 — Browser boundary detection is not ready for expansion

Before browser/computer-use expansion, OpenClaw needs a boundary detector.

Boundary classes:

```text
login
credential field
submit / send / post
checkout / payment
delete / archive
upload / download
file picker
permission prompt
CAPTCHA
off-domain navigation
personal data exposure
private account page
browser extension / install prompt
```

Default behavior:

```text
pause -> summarize boundary -> ask user for direction
```

---

## Recommended Hardening Order

### Phase 0 — Freeze expansion

Do not add browser-use actions, personal browser control, account login, form submission, uploads/downloads, publishing, client outreach, purchases, or background multi-app chains until Phases 1–4 are complete.

### Phase 1 — Mandatory EnvelopeFactory

Patch targets:

```text
nova_backend/src/openclaw/envelope_factory.py
nova_backend/src/openclaw/envelope_store.py
nova_backend/src/openclaw/task_envelope.py
nova_backend/src/openclaw/strict_preflight.py
nova_backend/src/openclaw/agent_runner.py
nova_backend/src/openclaw/agent_scheduler.py
nova_backend/src/api/openclaw_agent_api.py
nova_backend/src/executors/openclaw_execute_executor.py
```

Required behavior:

- every OpenClaw run must have an EnvelopeFactory-issued envelope
- missing envelope fails closed
- expired envelope fails closed
- channel/trigger mismatch fails closed
- direct `TaskEnvelope.from_template()` execution path is removed from production execution
- legacy direct-run event may be logged but cannot permit execution

### Phase 2 — Freeform goal preview gate

Replace direct freeform execution with:

```text
POST /api/openclaw/agent/goal-preview
-> returns proposed run, tools, scope, blocked actions, budgets, proof required

POST /api/openclaw/agent/goal/{preview_id}/run
-> requires accepted preview
-> issues envelope
-> executes within envelope
```

Until this exists, keep freeform goal execution blocked or strict read-only envelope-only.

### Phase 3 — Real approval gate

Replace action auto-allow with `allow`, `pause_for_user`, or `block`.

### Phase 4 — Central execution guard

Add one mandatory enforcement point for tool permission, URL/domain permission, step budget, duration budget, network budget, file budget, byte budget, write budget, and blocked action classes.

### Phase 5 — Boundary detector

Add boundary classification before browser/computer-use actions are permitted.

### Phase 6 — Run/step receipts

Add step-level and boundary-level proof events.

### Phase 7 — Operator UI

Minimum UI:

- active run
- current step
- next planned action
- allowed tools
- allowed domains
- blocked actions
- budget used
- time remaining
- pause
- cancel
- approve / deny pending action
- receipts
- cleanup state

### Phase 8 — First safe browser slice

Only after Phases 1–7:

```text
approved read-only isolated browser
-> specific URLs or domains only
-> open/read public pages
-> summarize
-> stop
-> receipt
```

Do not start with personal browser, logins, forms, uploads, publishing, checkout, messaging, client outreach, or multi-app chains.

---

## Risk Ranking

| Rank | Risk | Severity | Recommendation |
|---|---|---|---|
| 1 | EnvelopeFactory optional | Critical | Make mandatory before expansion. |
| 2 | Freeform goal runs LLM-selected tools | Critical | Disable or preview-gate until envelope-issued. |
| 3 | approve-action auto-allows | Critical | Replace with allow/pause/block. |
| 4 | Scheduler can run deprecated direct path | Critical | Fail closed when envelope factory is unavailable. |
| 5 | Enforcement may be scattered | High | Add centralized execution guard. |
| 6 | Receipts too coarse | High | Add run/step/boundary/cleanup receipts. |
| 7 | Personal-browser boundary not runtime-hard | High | Block by default. |
| 8 | Goal path lacks visible Run Preview | High | Add preview/approval workflow. |
| 9 | Strict preflight is narrow but not generalized | Medium | Generalize after mandatory envelope path. |
| 10 | Cost posture missing from runtime metadata | Medium | Add after free-first metadata work begins. |
| 11 | UI lacks full active-run control | Medium | Add before browser expansion. |
| 12 | Some docs may sound more implemented than runtime | Low | Keep status docs grounded. |

---

## Required Tests

Minimum test additions:

```text
manual run blocked without envelope
scheduler run blocked without envelope
freeform goal blocked or envelope-required
EnvelopeFactory disabled means no OpenClaw execution
legacy direct-run path logs but does not execute
envelope issued and stored before successful run
trigger/channel mismatch blocked
expired envelope blocked
direct TaskEnvelope.from_template path not used outside factory-backed code
read-only in-envelope action allowed
off-domain action paused or blocked
submit action paused
login action blocked
payment action blocked
unknown action blocked
cancel leaves no active run
failure emits failed receipt
cleanup emits receipt
```

Validation command set:

```bash
python -m pytest nova_backend/tests/openclaw -q
python -m pytest nova_backend/tests/test_openclaw_agent_api.py -q
python -m pytest nova_backend/tests/governance -q
python scripts/check_runtime_doc_drift.py
git diff --check
```

---

## Next Claude / Codex Prompt

```text
OpenClaw hardening pass: make envelope issuance mandatory and block legacy direct-run paths.

Scope:
- Do not add new OpenClaw capabilities.
- Do not add browser control.
- Do not add personal browser use.
- Do not add write actions.
- Do not change generated runtime docs manually.

Goal:
Close the transition gap where OpenClaw can run without an EnvelopeFactory-issued envelope.

Files to inspect/update:
- nova_backend/src/openclaw/envelope_factory.py
- nova_backend/src/openclaw/envelope_store.py
- nova_backend/src/openclaw/task_envelope.py
- nova_backend/src/openclaw/strict_preflight.py
- nova_backend/src/openclaw/agent_runner.py
- nova_backend/src/openclaw/agent_scheduler.py
- nova_backend/src/api/openclaw_agent_api.py
- nova_backend/src/executors/openclaw_execute_executor.py
- nova_backend/tests/openclaw/
- nova_backend/tests/test_openclaw_agent_api.py

Required behavior:
1. All OpenClaw runs must have an EnvelopeFactory-issued envelope.
2. If EnvelopeFactory feature flag is off, OpenClaw execution must fail closed, not run through deprecated direct construction.
3. Manual template runs must register an envelope before runner execution.
4. Scheduler runs must register an envelope before runner execution.
5. Freeform goal runs must either be blocked until goal-preview/envelope flow exists, or require EnvelopeFactory issuance with strict read-only tool limits.
6. Deprecated direct-run events may be logged, but must not permit execution.
7. No generated runtime docs manually edited.

Tests to add/update:
- manual run blocked without envelope
- scheduler run blocked without envelope
- freeform goal blocked or envelope-required
- EnvelopeFactory disabled means no OpenClaw execution
- envelope issued and stored before successful run
- trigger/channel mismatch blocked
- expired envelope blocked if expiration is enforced by store
- no direct TaskEnvelope.from_template path outside factory-backed code
- existing strict preflight tests still pass

Validation:
python -m pytest nova_backend/tests/openclaw -q
python -m pytest nova_backend/tests/test_openclaw_agent_api.py -q
python -m pytest nova_backend/tests/governance -q
python scripts/check_runtime_doc_drift.py
git diff --check

Final report:
- implemented changes
- tests run and exact results
- remaining risks
- no-overclaim statement
```

---

## Do Not Overstate

Do not claim any of the following until code, tests, generated runtime truth, and proof artifacts agree:

- full Run-based OpenClaw execution is complete
- browser/computer-use automation is product-ready
- personal browser control is safe by default
- freeform goals are fully governed
- approve-action is a real approval gate
- scheduler is fully envelope-issued
- OpenClaw can safely submit forms, publish, upload, purchase, or message
- OpenClaw is broad autonomy

---

## Final Recommendation

Do OpenClaw hardening in this order:

```text
1. Mandatory EnvelopeFactory.
2. Disable or restrict freeform goal execution.
3. Replace auto-allow approval.
4. Add centralized execution guard.
5. Add boundary detector.
6. Add run/step receipts.
7. Add visible active-run approval UI.
8. Only then implement read-only isolated browser slice.
```

The strongest product move is to make OpenClaw feel powerful because it is controlled, not because it is loose.
