# Trust Proof Plan

Last reviewed: 2026-04-28

## Purpose

Nova's current highest-leverage gap is proof visibility.

The goal of this document is to convert governance from something explained in docs into something a first-time user can immediately see and understand.

This is not a new feature roadmap. It is a trust and product proof roadmap.

---

## Core Goal

Convert this:

> Nova says it is governed.

Into this:

> I can see Nova is governed.

---

## Priority 1: Trust Review Card

Build a visible review surface for governed actions.

Recommended fields:

- User request
- Interpreted intent
- Capability used
- Risk level
- Approval required
- Decision (allowed / blocked / needs clarification)
- Result
- Receipt ID

Example:

```text
Request: Draft an email to John about tomorrow
Intent: Email drafting
Capability: send_email_draft
Risk: Low
Approval: No
Decision: Allowed
Result: Draft created
Receipt: #A1042
```

Why it matters:

- makes governance visible
- proves bounded execution
- increases trust quickly
- differentiates Nova from opaque assistants

---

## Priority 2: Screenshot Pack

Create and add screenshots to README.

Recommended screenshots:

1. Main dashboard
2. Trust Review Card
3. Runtime truth panel
4. Everyday use example
5. Blocked or confirmation-gated action

---

## Priority 3: Demo Video

Create a short 60-90 second walkthrough.

Suggested flow:

1. Open Nova
2. Ask for a summary
3. Ask for a draft action
4. Show Trust Review Card
5. Show block or confirmation flow
6. Show result / receipt

---

## Priority 4: README Proof Section

Add a top-level proof section with screenshots and short explanation.

Suggested message:

Nova is designed to make real actions visible and reviewable.

Every governed action should make clear:

- what was requested
- what Nova interpreted
- what capability would act
- whether approval is required
- whether it was allowed or blocked
- final result
- receipt trail

---

## Suggested Supporting Docs

- SEE_IT_WORK.md
- TRUST_MODEL.md
- DEMO_SCRIPT.md

---

## Brutal Truth

Without visible proof, visitors must imagine Nova's value.

With visible proof, they understand it in seconds.

That is the current highest ROI path.
