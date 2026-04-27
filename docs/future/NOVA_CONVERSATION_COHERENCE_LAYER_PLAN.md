# Nova Conversation Coherence Layer Plan

Date: 2026-04-27

Status: Future implementation plan / safe usability improvement path

Purpose: define how Nova should become more coherent, context-aware, understandable, and reasonable without widening execution authority or rewriting the governed action spine.

This is a planning document, not current runtime truth. Exact runtime status remains governed by `docs/current_runtime/` and live code.

Related future-direction docs:

```text
docs/future/NOVA_GOVERNED_LEARNING_PLAN.md
docs/future/NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md
```

---

## Executive Summary

Nova's coherence should improve through the conversation/context layer first, not by immediately replacing the LLM or widening tool authority.

A stronger model can improve language quality, but Nova's biggest coherence gains should come from:

```text
intent classification
current task state awareness
paused/active blocker awareness
runtime-truth labeling
response mode selection
clarification behavior
answer templates
tests for different question types
```

Governed learning and background reasoning are related future directions, but they are tracked separately so this plan stays focused on conversation coherence.

Core rule:

> **A better LLM makes Nova sound smarter. A better coherence layer makes Nova understand what kind of help the user needs.**

Important safety rule:

> **The coherence layer may shape conversation. It must never grant execution authority.**

---

## Existing Surfaces To Preserve

Current code already has a real conversation layer. Do not replace it wholesale.

Important existing surfaces:

```text
nova_backend/src/conversation/conversation_router.py
nova_backend/src/conversation/conversation_decision.py
nova_backend/src/conversation/response_style_router.py
nova_backend/src/conversation/response_formatter.py
nova_backend/src/conversation/session_router.py
nova_backend/src/conversation/general_chat_runtime.py
nova_backend/src/websocket/session_handler.py
nova_backend/src/skills/general_chat.py
```

Relevant existing tests:

```text
nova_backend/tests/conversation/test_conversation_router.py
nova_backend/tests/conversation/test_response_style_router.py
nova_backend/tests/conversation/test_response_formatter.py
nova_backend/tests/conversation/test_session_router.py
nova_backend/tests/conversation/test_general_chat_runtime.py
```

Preserve current behavior unless a targeted test demonstrates the gap.

---

## Current Observed Strengths

The current conversation layer already includes:

```text
ConversationMode values: direct, casual, work, analysis, brainstorm, action, unknown
ConversationDecision dataclass
Deterministic pre-routing
Policy blocked phrase checks
Follow-up detection
Session mode overrides
Clarification prompts for vague actions
Reference resolution for “that/it” patterns
Input normalization for common typos and STT artifacts
ResponseStyle routing: direct, brainstorm, deep, casual
Response templates for bounded research and findings
```

This means the right next step is **incremental coherence hardening**, not a rewrite.

---

## Main Problem To Solve

Nova needs to better distinguish different kinds of user requests, especially project/status questions, implementation guidance, action requests, explanation requests, and paused/blocked work.

Examples that should route differently:

```text
What is Nova?
What is the current status?
What should Claude do next?
Open my documents folder.
Draft an email but do not send it.
Why did you do that?
Explain this like I am new.
Do a second pass.
Save this to memory.
Add this to docs.
Review the repo.
What is paused right now?
```

These should not all receive the same generic response style.

---

## Product Rule

Nova should feel:

> **Simple outside. Governed inside.**

For normal conversation, Nova should be warm and understandable.

At action boundaries, Nova must stay strict:

```text
sending
posting
deleting
submitting forms
booking appointments
changing records
payments
purchases
public actions
customer/business changes
sensitive data
```

---

## Proposed Coherence Layer

Add a small, testable layer around existing router decisions rather than replacing the router.

Suggested concept:

```text
ConversationRouter
→ ConversationDecision
→ CoherenceContext / TaskState overlay
→ ResponseMode selection
→ Response template / formatter
```

The new layer should answer:

```text
What kind of question is this?
What project/task state matters?
Is the requested area active, paused, blocked, or future-only?
Does the answer need runtime truth, repo lookup, or general explanation?
Should Nova ask a clarification question?
What should Nova explicitly not touch?
```

---

## Critical Boundary: Coherence Is Not Authority

The coherence layer must remain non-authorizing.

Allowed:

```text
choose a response template
label an answer as project status vs next-step advice
recognize paused work
explain current active focus
ask a clarification question
format a safer answer
route general-chat style
```

Not allowed:

```text
approve an action
bypass GovernorMediator
bypass ExecuteBoundary
bypass NetworkMediator
mark a capability signoff as passed
lock a capability
resume paused work
execute OpenClaw tasks
create Google/Shopify/ElevenLabs connector authority
change confirmation requirements
```

The LLM may help phrase the answer, but deterministic code and governed capability paths must control action authority.

---

## Add Task State Awareness

Nova should maintain or load a small current task state object.

Example:

```json
{
  "active_focus": [
    "Cap 64 P5 live signoff and lock",
    "Windows installer/bootstrap validation",
    "trust/action-history dashboard proof"
  ],
  "paused": [
    "Auralis / website merger work",
    "Shopify / Cap 65 P5 live work"
  ],
  "future_only": [
    "Google connector implementation",
    "ElevenLabs implementation",
    "broad OpenClaw hands-layer work"
  ],
  "truth_mode": "repo_grounded_when_exact_status_matters",
  "default_answer_style": "current_truth_gap_next_action"
}
```

This should not grant execution authority. It only helps answer coherently.

Do not make this task-state object a replacement for generated runtime truth. It is a conversation helper only.

Recommended source options, from safest to most dynamic:

```text
1. Small Python module with conservative constants and tests.
2. Small JSON config under config/ with strict schema and tests.
3. Later: generated task-state artifact derived from roadmap/backlog docs.
```

Avoid initially:

```text
runtime Markdown scraping from BackLog.md or Now.md
LLM-generated task state without review
hidden background updates
state that changes capability authority
```

---

## Add Runtime-Truth Labels

Nova should label project facts internally as:

```text
CURRENT_RUNTIME_TRUTH
IMPLEMENTED_BUT_UNVERIFIED
PLANNED
PAUSED
BLOCKED
DEFERRED
IDEA_ONLY
```

This prevents future plans from being described as current implementation.

Example:

Bad:

```text
Nova has Google connectors.
```

Good:

```text
Google connector onboarding is planned, not current runtime truth. The accepted future plan is identity-first Google Sign-In, then read-only Calendar before Gmail/Drive writes.
```

Runtime-truth labels should affect explanation wording only. They must not be treated as permission gates for real actions.

---

## Add More Intent Families

The existing router already has broad intent families. Add additional test-backed intent labels only where useful.

Candidate added categories:

```text
PROJECT_STATUS
NEXT_STEP_ADVICE
DOC_OR_REPO_REVIEW
IMPLEMENTATION_GUIDANCE
MEMORY_SAVE_REQUEST
DOC_UPDATE_REQUEST
PAUSED_WORK_REFERENCE
RUNTIME_TRUTH_CHECK
TROUBLESHOOTING
CAPABILITY_SIGNOFF
```

Durable learning/correction behavior belongs in `NOVA_GOVERNED_LEARNING_PLAN.md`; this plan only needs to distinguish when a user appears to be asking for memory, docs, status, action, or explanation.

These do not all need to become new `ConversationMode` enum values. Many can be sublabels or metadata under existing modes.

Recommended approach:

```text
Keep ConversationMode stable.
Add optional metadata or a lightweight classification helper.
Use tests to confirm output behavior.
```

Possible shape:

```text
ConversationMode remains: direct / casual / work / analysis / brainstorm / action / unknown
Coherence intent adds: project_status / next_step_advice / paused_work_reference / capability_signoff
```

---

## Response Templates To Add

### Project Status

```text
Current truth:
What is done:
What is blocked/paused:
Next best action:
```

### Claude/Codex Direction

```text
Best ROI task:
Why this task:
What to avoid:
Success criteria:
```

### Paused Work

```text
Status: paused
Preserve:
Do not touch:
Unpause condition:
Active replacement focus:
```

### Capability Signoff

```text
Capability:
Current phase:
Evidence:
Blocker:
Do not certify unless:
Next command/manual action:
```

### Explanation

```text
Plain-English explanation:
Why it matters:
Example:
What to improve first:
```

### Governed Action

```text
Requested action:
Risk level:
Approval needed:
What will happen:
What will not happen:
Receipt/log expectation:
```

---

## Clarification Policy

Nova should ask a clarification only when needed for safety, scope, or usefulness.

Ask clarification for:

```text
ambiguous action target
unclear file/folder/reference
conflicting active vs paused scope
possible real-world mutation
missing credentials/environment
unclear user intent between docs vs memory vs code
```

Do not ask clarification when a safe default is obvious.

Example:

```text
User: “review current status”
Default: summarize current active/paused/blocker state.
```

---

## Paused Work Awareness

Current paused areas should be recognized by the coherence layer:

```text
Auralis / website merger work — paused
Shopify / Cap 65 P5 live work — paused
```

If user asks about a paused area, Nova should say it is paused and ask whether the owner wants to unpause before doing new work.

If user asks for a general Nova next step, Nova should not recommend paused work.

Paused recognition should not delete, move, rewrite, or expand paused docs/code. It only changes answer selection and guardrail messaging.

---

## What Not To Do

Do not use this work to:

```text
change GovernorMediator authority rules
change ExecuteBoundary behavior
change NetworkMediator policy
add new Google connector implementation
add ElevenLabs implementation
expand OpenClaw hands authority
resume Auralis/Shopify work
rewrite brain_server.py or session_handler.py broadly
replace the conversation router wholesale
implement governed learning storage
implement background reasoning jobs
```

This is a usability/context improvement only.

---

## Suggested Implementation Sequence

### Step 1 — Add tests first

Add tests for the user-request types Nova currently handles poorly.

Candidate tests:

```text
project status question returns status-shaped metadata/style
next-step question returns priority/ROI-shaped metadata/style
paused Auralis request is recognized as paused
paused Shopify request is recognized as paused
memory-save request is not treated as repo-doc request
repo-doc request is not treated as memory-save request
capability signoff request uses capability-signoff template
vague action still clarifies
simple explanation stays plain-language
```

### Step 2 — Add a lightweight task-state source

Add a small source of current task-state facts.

Options:

```text
static config file under docs or config
small Python module with conservative defaults
runtime-generated state later
```

Do not make it authoritative over generated runtime docs.

### Step 3 — Add coherence classification metadata

Do not explode `ConversationMode` unless necessary.

Preferred:

```text
existing mode remains: direct/work/analysis/action/etc.
new metadata adds: project_status, next_step_advice, paused_work_reference, etc.
```

### Step 4 — Add response template selection

Use the classification metadata to choose clearer formatting.

### Step 5 — Wire only into general-chat/project-status paths

Do not alter governed action routing first.

Scope for first implementation:

```text
project/status questions
next-step/Claude-direction questions
paused-work questions
memory-save vs docs-update disambiguation
capability-signoff status explanations
```

Explicitly out of scope for first implementation:

```text
governed action execution changes
OpenClaw run behavior
Google connector logic
ElevenLabs voice logic
Shopify live testing
Auralis merger planning
governed learning persistence
background reasoning jobs
```

### Step 6 — Add regression tests

Prevent future drift.

---

## Test Cases To Require

Minimum test matrix:

```text
“What is Nova’s current status?” → project/status shaped answer
“What should I have Claude do next?” → ROI/next-step shaped answer
“Resume Shopify” → notes Shopify is paused unless explicit unpause is given
“Put a pause on Shopify” → paused-work path, no deletion
“Save this to memory” → memory/save intent, not GitHub docs
“Add this to docs” → docs/update intent, not memory-only
“Draft an email” → action/capability path, not generic chat
“Explain why Nova is incoherent” → explanation path
“Do a second pass” → continuation/follow-up path
```

Add negative tests:

```text
Conversation coherence must not mark Cap 64 P5 passed.
Conversation coherence must not mark Cap 65 P5 passed.
Conversation coherence must not issue OpenClaw envelopes.
Conversation coherence must not call Google/Shopify/ElevenLabs connectors.
Conversation coherence must not change capability locks.
Conversation coherence must not persist governed-learning memories by itself.
Conversation coherence must not start background reasoning jobs by itself.
```

---

## Done Means

This work is done only when:

```text
existing conversation tests still pass
new coherence tests pass
no governed action authority is widened
paused Auralis and paused Shopify are respected
Nova can distinguish memory-save vs repo-doc requests
Nova can answer status/next-step questions in a consistent structure
Nova can explain future plans without overstating current runtime truth
negative tests prove no capability signoff/lock/action execution occurs
negative tests prove no learning persistence or background reasoning starts from coherence alone
```

---

## Recommended Claude Task After Cap 64

After Cap 64 P5 live signoff and lock, assign Claude:

```text
Implement the Conversation Coherence Layer as an incremental router/response improvement. Preserve existing ConversationMode behavior. Add tests first. Add paused/active task-state awareness. Add status/next-step/signoff/paused-work templates. Do not touch GovernorMediator, ExecuteBoundary, NetworkMediator, OpenClaw authority, Google connectors, ElevenLabs, Auralis, Shopify live work, governed learning persistence, or background reasoning jobs.
```

---

## Final Recommendation

The LLM matters, but Nova's next coherence upgrade should be architectural:

> **Improve the conversation/context layer before swapping model providers.**

Best near-term order:

```text
1. Cap 64 P5 live signoff and lock
2. Trust/action-history dashboard proof
3. Conversation Coherence Layer
4. Governed Learning
5. Background Reasoning, Not Background Automation
6. OpenClawMediator / Business Follow-Up Brief
7. Model/provider upgrades
```
