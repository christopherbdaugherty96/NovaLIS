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

Between conversation, local capability signoff, and OpenClaw, the active best ROI is:

```text
RequestUnderstanding trust/action-history visibility first.
```

Why:

```text
Nova now has a tested RequestUnderstanding foundation and prompt integration. The next product gap is visibility: the user should be able to see what Nova understood, what Nova thinks it can/cannot do, the safe next step, and what Nova must not do before any broader hands-layer work.
```

---

## Current Verification State

Latest handoff:

```text
4-15-26 NEW ROADMAP/HANDOFF_2026-04-27_REQUEST_UNDERSTANDING_LIVE_VERIFICATION.md
```

Current truth:

```text
RequestUnderstanding code path is implemented and test-proven.
RequestUnderstanding formatter and prompt assembly are test-proven.
General-chat prompt integration exists.
Live runtime was updated and partially verified.
Live free-form LLM behavior is not fully verified because of Ollama speed and some routing bypasses.
Trust/action-history visibility is not implemented yet.
```

Known limitations:

```text
gemma4:e4b was too slow for some live free-form prompts
some prompts can bypass general chat before RequestUnderstanding sees them
DeepSeek / ALLOW_ANALYSIS_ONLY path does not yet receive the RequestUnderstanding block
```

---

## Active Next Task

```text
Build the minimal RequestUnderstanding trust/action-history review card.
```

Purpose:

```text
Make Nova's understanding and boundary visible even when the LLM is slow, inconsistent, or bypassed by routing.
```

Implemented foundation:

```text
nova_backend/src/conversation/request_understanding.py
nova_backend/src/conversation/request_understanding_formatter.py
nova_backend/tests/conversation/test_request_understanding.py
nova_backend/tests/conversation/test_request_understanding_formatter.py
docs/future/NOVA_REQUEST_UNDERSTANDING_CONTRACT.md
docs/future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md
4-15-26 NEW ROADMAP/HANDOFF_2026-04-27_EMAIL_PAUSED_CONVERSATION_NEXT.md
4-15-26 NEW ROADMAP/HANDOFF_2026-04-27_REQUEST_UNDERSTANDING_LIVE_VERIFICATION.md
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
local capability signoff matrix
```

The local capability signoff matrix comes after the RequestUnderstanding trust/action-history card.

---

## Success Criteria For Next Work

Nova should surface a visible, non-authorizing review artifact with fields such as:

```text
understood_goal
request_type
capability_status
confidence
safe_next_step
must_not_do
authority_effect
result / not executed
```

Tests must prove:

```text
RequestUnderstanding does not execute capabilities.
RequestUnderstanding does not approve actions.
RequestUnderstanding does not change capability locks.
RequestUnderstanding does not call OpenClaw or connectors.
The review card is visible but non-authorizing.
```

---

## Current Order After This Task

```text
1. Build RequestUnderstanding trust/action-history review card.
2. Re-run live conversation checks when a faster local model, longer timeout, or stable provider lane is available.
3. Fix narrow RequestUnderstanding routing bypasses, starting with paused-scope thread-continuation cases.
4. Start local capability signoff matrix.
5. Add OpenClawMediator skeleton only after conversation visibility and local capability limits are clearer.
6. Revisit Google connector/email direction before unpausing Cap 64 P5.
```

---

## Final Rule

> Conversation first, visibility next, hands later.

Nova should make understanding and boundaries visible before OpenClaw or broader local capability work is expanded.
