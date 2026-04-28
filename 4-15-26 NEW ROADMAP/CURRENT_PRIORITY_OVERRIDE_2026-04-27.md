# Current Priority Override — Conversation Focus

Date: 2026-04-27

Status: Active owner priority override

This file supersedes older `Now.md` and `BackLog.md` priority language where those files still list Cap 64 live signoff as the next active task.

---

## Current Owner Direction

Email / Cap 64 P5 live signoff is paused for now.

Reason:

```text
Email should wait until Google connectors are designed/implemented enough that the email path can align with the future Gmail/Google connector model.
```

Do not delete or revert Cap 64 work. Preserve:

```text
Cap 64 implementation
Cap 64 confirmation-gate fix
Cap 64 tests
Cap 64 checklist updates
Cap 64 P1-P4 evidence
```

But do not actively run:

```text
Cap 64 P5 live checklist
Cap 64 live signoff
Cap 64 P6 lock
mail-client live testing
standalone email expansion outside Google connector alignment
```

---

## Current Best ROI

Between conversation and OpenClaw, the active best ROI is:

```text
Conversation / RequestUnderstanding integration first.
```

Why:

```text
OpenClaw is the hands layer. Nova should first become better at understanding the user's request, explaining capability boundaries, and surfacing safe next steps before expanding the hands layer.
```

---

## Active Next Task

```text
Wire RequestUnderstanding into general-chat response wording and/or trust/action-history review cards in a non-authorizing way.
```

Implemented foundation:

```text
nova_backend/src/conversation/request_understanding.py
nova_backend/tests/conversation/test_request_understanding.py
docs/future/NOVA_REQUEST_UNDERSTANDING_CONTRACT.md
docs/future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md
4-15-26 NEW ROADMAP/HANDOFF_2026-04-27_EMAIL_PAUSED_CONVERSATION_NEXT.md
```

---

## Explicitly Not Active

Do not start or continue:

```text
Cap 64 P5/P6
Cap 65 / Shopify
Auralis / website merger
Google connector implementation
ElevenLabs implementation
broad OpenClaw hands-layer execution
background reasoning jobs
governed learning persistence
CRM/SaaS packaging
```

---

## Success Criteria For Next Work

Nova should begin producing clearer user-facing boundary language, for example:

```text
I understand you want to draft an email.
Current capability: draft-only.
Safe next step: prepare a draft for review.
I will not send it automatically.
```

or:

```text
I understand you want background work.
Current capability: reasoning/proposal only.
Safe next step: prepare a review card.
I will not send, post, delete, book, buy, or execute OpenClaw actions in the background.
```

Tests must prove:

```text
RequestUnderstanding does not execute capabilities.
RequestUnderstanding does not approve actions.
RequestUnderstanding does not change capability locks.
RequestUnderstanding does not call OpenClaw or connectors.
```

---

## Final Rule

> Conversation first, hands later.

Nova should understand and explain boundaries before OpenClaw is expanded.
