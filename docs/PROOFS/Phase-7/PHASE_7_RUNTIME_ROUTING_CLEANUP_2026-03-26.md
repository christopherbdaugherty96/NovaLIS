# Phase 7 Runtime Routing Cleanup
Date: 2026-03-26
Status: Completed and verified

## Purpose
Reduce architectural drift in the live runtime entrypoint by:
- removing the direct `SkillRegistry` dependency from `brain_server.py`
- removing the inert `confirmation_gate` branch from the live websocket path
- isolating the bounded general-chat fallback into a focused helper module

## What changed
Runtime code:
- `nova_backend/src/brain_server.py`
- `nova_backend/src/conversation/general_chat_runtime.py`

Focused regression coverage:
- `nova_backend/tests/conversation/test_general_chat_runtime.py`
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`

## Implementation summary
The websocket runtime now:
- instantiates a dedicated general-chat fallback helper instead of the broad Phase-3.5 `SkillRegistry`
- routes pending escalation confirmation through `general_chat_runtime.py`
- uses a bounded general-chat fallback helper for advisory chat after governed routing returns no capability match
- no longer checks the passive `confirmation_gate` in the live websocket loop

## Behavioral outcome
This change does not widen authority.

It keeps the same product behavior where Nova can still:
- answer ordinary conversational turns
- use bounded relevant-memory context in fallback chat
- ask whether the user wants deeper analysis
- return a deeper answer when the user confirms

But it removes the misleading appearance that the live runtime still depends on a broader legacy skill stack for that path.

## Small quality improvement included
If a user confirms deeper analysis and that deeper pass is unavailable, Nova now returns an honest message:
- `Deep analysis is unavailable right now, so I kept the brief version.`

This replaces the older misleading prompt that asked the user to answer `yes/no/cancel` even though the pending state had already been cleared.

## Verification
Focused bundle run from `nova_backend/`:

```text
python -m pytest tests\conversation\test_general_chat_runtime.py tests\phase45\test_brain_server_basic_conversation.py -k "pending_escalation_confirmation or hello_uses_deterministic_local_response or what_can_you_do_with_question_mark_stays_on_capability_path or general_chat_receives_relevant_explicit_memory_context or followup_chat_uses_recent_conversation_context or brain_server_carries_structured_conversation_context_between_chat_turns or voice_general_chat_auto_speaks_generated_answer" -q
```

Result:
- `7 passed`

Quick compile validation:

```text
python -m py_compile nova_backend/src/brain_server.py nova_backend/src/conversation/general_chat_runtime.py nova_backend/tests/conversation/test_general_chat_runtime.py nova_backend/tests/phase45/test_brain_server_basic_conversation.py
```

Result:
- passed

## Current truth after this slice
- `brain_server.py` is still too large and should still be decomposed further
- the legacy `SkillRegistry` module still exists on disk, but it is no longer part of the live websocket hot path
- the passive `confirmation_gate` module still exists on disk, but it is no longer consulted by the live websocket runtime
- Nova's bounded conversational fallback is now more explicit, smaller, and easier to audit
