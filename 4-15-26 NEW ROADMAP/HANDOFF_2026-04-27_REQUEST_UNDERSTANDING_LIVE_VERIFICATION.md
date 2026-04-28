# Handoff — RequestUnderstanding Live Verification Status

Date: 2026-04-27

Status: Verification documented / next step identified

---

## Current Truth

The RequestUnderstanding conversation integration is implemented and test-proven, but live LLM behavior is only partially verified.

Implemented and verified by tests:

```text
RequestUnderstanding contract
RequestUnderstanding formatter
General-chat runtime skill_state injection
GeneralChatSkill system prompt assembly
Selective boundary block behavior
No boundary block for general/explanation/casual cases
```

The current best next implementation remains:

```text
Trust/action-history review card for RequestUnderstanding.
```

---

## What Was Verified

Claude pulled latest `origin/main`, restarted Nova from updated code, confirmed Nova/Ollama reachability, corrected the WebSocket test payload key to `text`, and ran the conversation test suite.

Reported passing tests:

```text
25/25 request_understanding_formatter tests
341/341 full conversation tests
41/41 targeted conversation tests
```

Confirmed code path:

```text
build_request_understanding(...)
→ format_request_understanding_block(...)
→ skill_state["request_understanding_prompt_block"]
→ GeneralChatSkill._run_local_model(...)
→ GeneralChatSkill._build_system_prompt(...)
```

Confirmed safety:

```text
authority_effect = "none"
No GovernorMediator changes
No ExecuteBoundary changes
No NetworkMediator changes
No capability locks/signoffs changed
No OpenClaw execution added
No connector behavior added
No memory persistence added
No background jobs added
```

---

## Live Verification Results

### Passed Live

```text
Prompt: hey
Result: normal canned social response
Status: PASS
Meaning: casual/social path is not polluted with RequestUnderstanding boundary boilerplate
```

```text
Prompt: draft an email to test@example.com about quarterly review
Result: Cap 64 confirmation gate appeared with recipient/subject and "Nova never sends automatically" framing
Status: PASS as boundary/confirmation evidence
Meaning: updated runtime loaded the newer Cap 64 confirmation behavior
```

Important note: Cap 64 P5 live signoff remains paused. This email prompt was used only as a boundary/confirmation check, not as P5 certification.

---

## Partially Verified / Blocked

```text
Prompt: what should I work on next
Status: BLOCKED_OLLAMA
Reason: gemma4:e4b response was too slow for live timeout
```

```text
Prompt: what is the status of Shopify work
Status: BLOCKED_OLLAMA
Reason: gemma4:e4b response was too slow for live timeout
```

```text
Prompt: analyze the repo in the background while I am away
Status: PARTIAL_PASS / ROUTED_REFUSAL
Reason: router intercepted before free-form LLM boundary response; runtime refused execution safely
Meaning: safe behavior observed, but not full RequestUnderstanding-shaped LLM proof
```

---

## Known Limitations

### 1. Slow local model path

`gemma4:e4b` was too slow for the live timeout on free-form LLM-dependent prompts.

This is not a RequestUnderstanding code failure.

### 2. Routing bypasses

Some phrases are intercepted before `run_general_chat_fallback(...)` and therefore do not reach the RequestUnderstanding prompt block.

Known example:

```text
continue Shopify
```

This is intercepted by the project-thread continuation route before general chat fallback. If the named thread does not exist, Nova may respond with a thread-not-found message instead of the paused-scope boundary.

Future narrow fix:

```text
If project-thread continuation cannot find a thread and the requested name matches a paused scope, return a paused-scope boundary response instead of generic thread-not-found.
```

Do not fix this before the main live conversation path is stable unless explicitly assigned.

### 3. Deep-analysis path gap

The common local-model path receives RequestUnderstanding boundary context. The DeepSeek / `ALLOW_ANALYSIS_ONLY` path does not yet receive the block.

This is accepted for now to avoid broad prompt/refactor work.

---

## Current Priority Remains

Email / Cap 64 P5 live signoff remains paused until Google connector direction is ready.

Do not work on:

```text
Cap 64 P5/P6
Cap 65 / Shopify
Auralis / website merger
Google connector implementation
ElevenLabs implementation
OpenClaw execution / hands-layer expansion
background reasoning jobs
governed learning persistence
CRM/SaaS packaging
```

---

## Recommended Next Step

Build the minimal RequestUnderstanding trust/action-history review card.

Purpose:

```text
Make Nova's understanding and boundary visible even when the LLM is slow, inconsistent, or bypassed by routing.
```

Card fields should include:

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

The card must remain non-authorizing.

It should not:

```text
execute capabilities
approve actions
change locks/signoffs
call OpenClaw
call connectors
persist memories
start background jobs
resume paused work
```

---

## Success Criteria For Next Work

A user or developer should be able to see:

```text
What Nova understood
What Nova thought it could/could not do
What Nova said the safe next step was
What Nova was explicitly forbidden from doing
Whether anything actually executed
What did not happen
```

This makes the loop visible:

```text
User asks
→ Nova understands
→ Nova states boundary
→ Nova proposes safe next step
→ user approves if needed
→ governed execution path acts if allowed
→ trust/action history records what happened and what did not happen
```

---

## Final Rule

> RequestUnderstanding is verified enough to move to visibility, not authority.

The next step is to show the boundary clearly in trust/action-history, not to expand OpenClaw or local actions yet.
