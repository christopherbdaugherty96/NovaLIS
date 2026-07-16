# Proposed Priority Lock — Awareness Outcome Truth

Status: proposed — owner approval required before implementation

Date prepared: 2026-07-16

Base reviewed: `main` at `703c09bb1b1278130edaa26bc6644d61041457cd`

Owner: Christopher Daugherty

This is human-maintained priority guidance, not generated runtime truth.

Actual code, tests, generated runtime artifacts, and observed runtime behavior remain authoritative if they conflict with this document.

---

## Active Decision Requested

Approve one bounded corrective lane:

```text
An unavailable weather, news, or calendar source must not be recorded or described as a successful action.
```

This lane corrects outcome truth only. It does not expand capability, authority, provider access, automation, or UI scope.

---

## Why This Work Is P0

The current awareness skills can return `SkillResult(success=True)` while their own structured payload reports states such as:

- `not_configured`
- `not_connected`
- `unavailable`
- source or parse failure

The snapshot executors already contain separate success and failure branches. Because the three skills currently hardcode or preserve `success=True` on degraded paths, the failure branches are effectively unreachable for those conditions.

The false-success result propagates into action receipts and Trust presentation. A degraded awareness fetch can therefore be described as having "completed successfully" even though the user-visible widget correctly says the source was unavailable.

The defect is not missing status information. The honest source status already exists in `widget_data`. The defect is that the top-level success flag contradicts it.

---

## Objective

Make execution outcome truth consistent across:

```text
skill result
→ snapshot executor
→ ActionResult
→ receipt / ledger outcome
→ Trust presentation
→ awareness and morning brief rendering
```

An unavailable source must produce a failed action outcome while preserving the existing honest degraded widget and brief section.

---

## Governing Risk

Changing `SkillResult.success` can affect every consumer that branches on that field.

The primary regression risk is:

```text
A false positive is removed, but the degraded weather/news/calendar section disappears from the awareness or morning brief.
```

That outcome is not acceptable.

The required contract is:

1. `success=False` for a source that did not provide the requested data.
2. Existing degraded `widget_data`, status values, and user-facing messages remain available.
3. The snapshot executor enters its existing failure branch.
4. The UI and briefs still render the honest unavailable section.
5. Trust and receipts no longer describe the action as successful.

The flag correction is not complete until all five conditions are proven.

---

## Scope

### Files expected to change

- `nova_backend/src/skills/weather.py`
- `nova_backend/src/skills/news.py`
- `nova_backend/src/skills/calendar.py`
- focused tests required to prove the contract

### Files to inspect but not change unless a test proves a minimal correction is required

- `nova_backend/src/executors/info_snapshot_executor.py`
- receipt and ledger construction paths
- `nova_backend/src/personality/trust_presenter.py`
- awareness brief construction and rendering paths
- morning brief / RoutineGraph consumers of `SkillResult.success`

### Required degraded conditions

Weather:

- provider or configuration unavailable
- fetch failure
- parse or response failure that prevents usable weather data

News:

- no usable items because retrieval failed or sources are unavailable
- parse or feed failure that prevents usable news data

Calendar:

- not connected or not configured
- read or parse failure
- source unavailable

A legitimate empty state must be classified deliberately. For example, "connected calendar with no events today" is not automatically equivalent to "calendar source unavailable."

---

## Required Status Contract

The implementation must preserve the distinction between:

### Execution outcome

Did the skill obtain and process the requested source successfully?

```text
success=True
success=False
```

### Source state

What was true about the source?

Examples:

```text
available
not_configured
not_connected
unavailable
rate_limited
parse_failed
```

### Data state

What usable data was produced?

Examples:

```text
complete
partial
empty_valid
empty_degraded
```

PR 1 does not need to introduce a broad new shared schema unless required for correctness. It must, however, stop using `success=True` to represent unavailable source states.

---

## Implementation Requirements

1. Return `SkillResult(success=False)` when weather, news, or calendar cannot provide the requested source data.
2. Preserve the existing degraded `widget_data`, structured status, and user-facing message.
3. Do not replace useful source-specific states with a generic error.
4. Do not treat a valid empty result as an infrastructure failure without evidence.
5. Confirm the existing `ActionResult.failure()` branches receive the same safe widget payload.
6. Confirm receipts store a failed outcome.
7. Confirm Trust presentation does not use "completed successfully" for the degraded result.
8. Confirm awareness and morning briefs retain the unavailable section.
9. Keep successful paths unchanged.

---

## Required Tests

### Skill-level negative tests

For each of weather, news, and calendar:

```text
unavailable source
→ SkillResult.success is False
→ existing widget_data.status is preserved
→ existing degraded message is preserved
```

### Executor-level tests

For each snapshot executor:

```text
degraded SkillResult
→ existing ActionResult.failure() branch is used
→ external_effect remains False
→ safe widget payload is preserved
```

### Receipt and Trust test

```text
degraded awareness action
→ receipt success is False
→ Trust output does not say "completed successfully"
→ Trust output remains understandable and non-alarming
```

### Brief-level regression test

At least one unavailable source must still appear in the awareness or morning brief as a visible degraded section.

Required assertion:

```text
The section is shown as unavailable or not connected; it is not silently omitted.
```

### Successful-path regression tests

Existing successful weather, news, and calendar responses must continue to:

- return `success=True`
- render their current widgets
- enter `ActionResult.ok()`
- preserve current routing and user-visible content

---

## Definition of Done

This lane is complete only when all of the following are true:

- unavailable weather returns `SkillResult.success=False`
- unavailable news returns `SkillResult.success=False`
- unavailable calendar returns `SkillResult.success=False`
- each snapshot executor enters its existing failure branch
- degraded widget payloads remain visible
- receipts record failure
- Trust no longer describes the degraded action as successful
- at least one brief-level test proves the unavailable section remains visible
- existing successful behavior remains green
- no capability, provider, routing, or UI expansion occurs

---

## Explicitly Out of Scope

Do not include:

- generated runtime discrepancy repair
- `BYPASS_SURFACES.md` or runtime-auditor changes
- NetworkMediator or provider health-check refactoring
- NewsAPI or provider-registry cleanup
- OpenAI model-label cleanup
- bridge hardening
- persistent-state quarantine work
- GoalStore persistence repair
- packaging or wheel work
- STT or TTS changes
- UI layout or navigation changes
- new capabilities
- connector expansion
- autonomous execution
- external writes

Those are separate lanes with separate proofs.

---

## Planned Sequence After This Lane

```text
PR 1 — Awareness outcome truth
PR 2 — Generated discrepancy reconciliation
PR 3 — Shared corruption-detection and quarantine foundation
Follow-ups — apply corruption-safe loading store by store
```

PR 3 is a foundation lane, not one large multi-store patch. The shared mechanism should land first, followed by bounded store-specific adoption in authority order.

---

## Preserved Governance Boundaries

This work:

- adds no authority
- adds no new executor
- adds no network destination
- adds no background execution
- changes no confirmation requirement
- changes no capability registration
- changes no external-effect classification
- performs no provider or connector expansion

The intended result is narrower and more truthful outcome reporting.

---

## Codex Handoff

### Objective

Correct false-success awareness outcomes without removing degraded user-visible information.

### Required first action

Trace all consumers of `SkillResult.success` for the three skills before changing the flag. Identify any consumer that drops degraded sections when `success=False`.

### Change boundary

Prefer changes in the three skill files and focused tests. Modify a downstream consumer only if a failing regression test proves that preserving the degraded widget requires a minimal correction.

### Required validation

Run the smallest focused suites first, followed by the relevant awareness, executor, receipt/Trust, and brief regression suites.

### Stop conditions

Stop and report rather than expanding scope if:

- a shared result-contract redesign appears necessary
- the change requires provider or routing changes
- the brief cannot preserve degraded sections without broad restructuring
- unrelated existing failures prevent trustworthy validation

### Required return format

```text
- Summary:
- Root cause confirmed:
- Files changed:
- Behavior changed:
- Degraded widget preservation:
- Receipt / Trust result:
- Brief regression result:
- Tests run:
- Test results:
- Existing failures or blockers:
- Governance impact:
- Scope deviations:
- Recommended next action:
- ChatGPT second pass:
```

---

## Review Gate

Implementation must not merge based only on green unit tests.

Second-pass review must confirm:

1. failure semantics are honest
2. valid empty states were not misclassified
3. degraded widgets remain visible
4. Trust wording matches the receipt
5. no unrelated architecture was changed
6. the generated discrepancy lane remains separate

---

## Owner Approval

```text
[ ] Approved as the next implementation lane
[ ] Keep proposed; do not implement yet
[ ] Revise scope before implementation
```
