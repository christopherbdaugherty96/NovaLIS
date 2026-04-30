# Future Brain Promotion Path

This document defines how a future Brain-related idea graduates from planning into current NovaLIS runtime work.

It is a control document for preventing documentation drift, premature claims, and unsafe promotion of unimplemented behavior.

---

## Core Rule

> Future Brain ideas do not become current truth until code, tests, runtime behavior, and generated runtime truth all agree.

A concept may be useful, but usefulness is not implementation.

---

## Promotion Ladder

```text
Idea
→ future planning doc
→ implementation design
→ schema / contract
→ dry-run prototype
→ tests
→ trust / review surface
→ governed runtime integration
→ generated runtime truth update
→ current docs update
```

---

## Stage 0 — Idea Capture

Purpose:

- preserve the idea
- mark it as future-only
- avoid losing direction

Required:

- clear status: planning only
- no runtime claims
- no capability claims
- no implication of current execution support

Example location:

```text
future/brain/<domain>/
```

---

## Stage 1 — Design Spec

Purpose:

- define architecture
- define boundaries
- define governance assumptions

Required:

- relationship to current NovaLIS architecture
- allowed / blocked behavior
- failure modes
- open questions
- promotion risks

---

## Stage 2 — Contract / Schema

Purpose:

- make the idea machine-readable or implementation-ready

Possible artifacts:

- envelope schema
- learning record schema
- domain permission profile
- signal registry definition
- action contract

Required:

- fail-closed defaults
- explicit required fields
- validation rules
- unknown-state handling

---

## Stage 3 — Dry Run Prototype

Purpose:

- prove planning without real execution

Allowed:

- simulate plan
- show risk
- show required approvals
- generate receipt preview

Blocked:

- real desktop control
- real browser action
- account mutation
- financial action
- publishing

---

## Stage 4 — Tests

Purpose:

- prove the design fails safely

Required test classes:

- valid path
- missing fields
- blocked action
- scope violation
- timeout
- user cancellation
- uncertainty
- retry limit
- receipt generation

---

## Stage 5 — Trust Surface

Purpose:

- make governance visible to the user

Required:

- intent summary
- plan preview
- allowed actions
- blocked actions
- risk tier
- approval state
- stop condition
- result / receipt

---

## Stage 6 — Runtime Integration

Purpose:

- connect the feature through the governed NovaLIS path

Required:

- GovernorMediator path respected
- CapabilityRegistry respected
- ExecuteBoundary respected
- LedgerWriter receipt emitted
- NetworkMediator used for outbound HTTP where relevant
- no side execution path

---

## Stage 7 — Runtime Truth Update

Purpose:

- make generated runtime docs reflect reality

Required:

- generated runtime docs updated by generator
- no manual truth edits
- implementation status reflected accurately
- gaps still listed

---

## Stage 8 — Current Docs Update

Purpose:

- move from future docs to current user-facing docs only when real

Required:

- current docs do not overstate
- future docs link to promoted implementation
- old future claims are retired or marked superseded

---

## Anti-Patterns

Do not promote because:

- the idea sounds useful
- docs exist
- a demo prompt worked once
- a model can describe the workflow
- the user wants it soon
- a future folder exists

---

## Promotion Checklist

Before marking anything current:

```text
[ ] code exists
[ ] tests exist
[ ] runtime path is governed
[ ] user approval behavior is defined
[ ] receipts/logging exist
[ ] failure modes are tested
[ ] runtime truth generator reflects it
[ ] current docs match runtime truth
```

---

## Current Status

This document governs promotion discipline for future Brain work.

It does not promote any current future folder by itself.
