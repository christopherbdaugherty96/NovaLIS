# Handoff — Email Paused, Conversation Coherence Next

Date: 2026-04-27

Status: Owner priority change

---

## Owner Direction

Email / Cap 64 live signoff is paused for now.

Reason:

```text
Email should wait until Google connectors are designed/implemented enough that the email path can align with the future Gmail/Google connector model.
```

Do not delete or revert Cap 64 work. Preserve the confirmation-gate fix, tests, checklist updates, and existing P1-P4 implementation. Cap 64 remains useful as the draft-only proof pattern, but P5 live signoff and P6 lock are no longer the active next task.

---

## Current Paused Scope

Paused until explicit owner unpause:

```text
Cap 64 P5 live checklist
Cap 64 live signoff
Cap 64 P6 lock
mail-client live testing
new email/send/draft expansion outside the Google connector plan
```

Allowed while paused:

```text
preserve Cap 64 implementation and tests
reference Cap 64 as the draft-only safety pattern
use Cap 64 lessons for request-understanding and trust/action-history design
keep existing checklist/status docs intact
```

Blocked while paused:

```text
asking owner to configure mail client for Cap 64 P5
running live mailto P5 testing
locking Cap 64
expanding standalone email work before Google connector alignment
adding automatic email sending
```

---

## Best ROI Decision

Between conversation coherence and OpenClaw, the best ROI is:

```text
Conversation / Request Understanding integration first.
```

Why:

```text
OpenClaw is the hands layer. It should not be expanded until Nova reliably understands the user request, explains can/cannot/must-not-do boundaries, and can surface the result in trust/action-history.

Conversation coherence improves every future feature: OpenClaw, Google connectors, background reasoning, governed learning, email drafting, and everyday assistant use.
```

---

## New Active Focus

Recommended next focus:

```text
RequestUnderstanding integration into general-chat response wording and trust/action-history review cards.
```

Implemented foundation already exists:

```text
nova_backend/src/conversation/request_understanding.py
nova_backend/tests/conversation/test_request_understanding.py
docs/future/NOVA_REQUEST_UNDERSTANDING_CONTRACT.md
docs/future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md
```

The next implementation should be narrow and non-authorizing:

```text
Use RequestUnderstanding to make Nova say what it understood, what it can do, what it cannot do, the safe next step, and what it must not do.
```

---

## What Not To Do Next

Do not work on:

```text
Cap 64 P5 live signoff or lock
Cap 65 / Shopify
Auralis / website merger
Google connector implementation yet
ElevenLabs implementation
broad OpenClaw hands-layer execution
background reasoning jobs
governed learning persistence
CRM/SaaS packaging
```

---

## Recommended Claude/Codex Task

Use this as the next task theme:

```text
Wire the existing RequestUnderstanding contract into Nova's general-chat response path and/or trust/action-history review surfaces in a non-authorizing way. Add tests first. Do not change GovernorMediator, ExecuteBoundary, NetworkMediator, OpenClaw execution, email execution, Google connectors, Shopify, or Auralis. The goal is clearer user-facing boundary language, not new action authority.
```

---

## Success Criteria

This next step is successful when Nova can visibly answer requests like:

```text
I understand you want to draft an email.
Current capability: draft-only.
Safe next step: prepare a draft for review.
I will not send it automatically.
```

or:

```text
I understand you want me to work in the background.
Current capability: reasoning/proposal only.
Safe next step: prepare a review card.
I will not send, post, delete, book, buy, or execute OpenClaw actions in the background.
```

And tests prove:

```text
RequestUnderstanding does not execute capabilities.
RequestUnderstanding does not approve actions.
RequestUnderstanding does not change capability locks.
RequestUnderstanding does not call OpenClaw or connectors.
```

---

## Final Rule

> Conversation first, hands later.

Nova should understand and explain boundaries before OpenClaw is allowed to act more broadly.
