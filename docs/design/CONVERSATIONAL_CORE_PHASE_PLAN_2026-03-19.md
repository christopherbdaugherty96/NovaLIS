# Conversational Core Phase Plan
Date: 2026-03-19
Status: Planning packet only; post-Phase-6 conversational build plan grounded in current `main`
Scope: Improve Nova's in-session conversational fluidity without widening execution authority, routing power, or trust claims

## Core Rule
Presentation can adapt. Authority cannot.

That is the governing sentence for this whole effort.

Nova may become better at:
- holding the thread of a conversation
- adjusting phrasing, tone, and depth
- resolving bounded follow-ups
- asking short clarifications when needed

Nova may not become better at:
- inferring hidden execution intent
- guessing commands from vague chat
- widening authority boundaries
- bypassing confirmation or governed routing

## Why This Packet Exists
The recent conversation-fluidity work on `main` established a real base:
- bounded recent-turn carryover
- conversational initiative in replies
- ordinal follow-up handling
- rolling long-session summary
- vague option-reference handling
- rewrite/clarify follow-ups

That work is useful and user-visible, but it was shipped as a series of bounded slices.

This packet turns those slices into a single named program:
- define the next target architecture
- define safe scope boundaries
- define build order
- define proof expectations

This packet does not replace runtime truth.
It defines the next conversational design direction to build against.

## Current Grounded Baseline
As of March 19, 2026, `main` already includes the following conversation checkpoint:
- `426e829` `polish: surface conversational initiative in chat replies`
- `9916409` `polish: improve ordinal followup references in chat`
- `604ac73` `polish: add rolling summary for longer chat sessions`
- `8712e57` `polish: resolve vague option references in chat`
- `a2751af` `polish: improve rewrite followups in chat`

Current grounded conversation files:
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/conversation/response_formatter.py`
- `nova_backend/src/conversation/conversation_router.py`
- `nova_backend/src/brain_server.py`

Current grounded proof files:
- `nova_backend/tests/conversation/test_general_chat_tone.py`
- `nova_backend/tests/conversation/test_conversation_router.py`
- `nova_backend/tests/conversation/test_personality_interface_agent.py`
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`
- `nova_backend/tests/phase45/test_brain_server_tone_commands.py`
- `nova_backend/tests/test_tierb_conversation.py`

## Goal
Make Nova feel more fluid, coherent, and adaptive within a bounded session while preserving governed execution discipline.

In plain language, this means Nova should get better at:
- understanding what the user is still talking about
- adapting how it explains something
- recognizing rewrite and follow-up intent
- asking one short clarification when needed

It should not become a broader authority surface.

## Architectural Scope

### 1. Session Context Object
Maintain a conversation-scoped context object for the local chat lane only.

This object should represent:
- `topic`
- `user_goal`
- `open_question`
- `active_options`
- `latest_recommendation`
- `rewrite_target`
- `presentation_preference`

This is not long-term memory.
It is not cross-session learning.
It is not a governed action planner.

#### Session Context Rules
- bounded to the active session only
- used only for non-authorizing local conversation handling
- never treated as durable memory
- never used to trigger governed actions implicitly
- must degrade safely when context is weak or absent

### 2. Adaptive Presentation Layer
Allow Nova to shape responses more intelligently by presentation mode while preserving the same routing and authority rules.

Presentation dimensions:
- concise <-> detailed
- plain-language <-> technical
- direct <-> exploratory
- practical <-> reflective

Presentation shaping should affect:
- wording
- structure
- amount of detail
- whether a reply invites a useful next turn

Presentation shaping should not affect:
- capability routing
- confirmation requirements
- authority boundaries
- trust claims

### 3. Reference Resolution
Expand follow-up handling only when references can be anchored cleanly.

Target follow-up classes:
- ordinal references
  - `the first one`
  - `go with the second`
- vague option references
  - `that one`
  - `the calmer option`
- rewrite/explanation references
  - `what do you mean by that`
  - `say that simpler`
  - `reword that`
- bounded comparative semantic modifiers
  - `the safer version`
  - `the simpler one`
  - `that approach instead`

Reference resolution must remain:
- session-scoped
- bounded to visible prior conversational material
- conservative when anchors are weak

### 4. Clarification Layer
When a follow-up is too weak to resolve safely, Nova should ask one short clarification instead of pretending it knows.

Good clarification behavior:
- brief
- specific
- anchored to visible options when possible

Examples:
- `Do you mean the first option or the calmer option?`
- `Do you want a rewrite or a decision?`
- `Do you want the shorter version or the simpler version?`

Bad clarification behavior:
- open-ended wandering questions
- authority guesses
- verbose self-explanations

### 5. Hard Boundary
No conversational improvement may:
- trigger governed actions implicitly
- lower the threshold for command inference
- change confirmation semantics
- widen permissions
- bypass Governor-mediated execution

## Safe Build Order

### Stage 1 - Session Context Object
Goal:
- make the local chat lane track the conversation thread more explicitly

Tasks:
- formalize the session-scoped conversation object
- separate short-window context from rolled summary
- persist latest recommendation and rewrite target for chat only
- keep this out of governed action routing

Primary files:
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/brain_server.py`

### Stage 2 - Adaptive Presentation
Goal:
- improve phrasing and depth control without changing authority

Tasks:
- make tone/depth preference more explicit inside the conversation lane
- preserve deterministic behavior for short social interactions
- avoid theatrical or over-personalized styling

Primary files:
- `nova_backend/src/conversation/response_formatter.py`
- `nova_backend/src/personality/interface_agent.py`
- `nova_backend/src/skills/general_chat.py`

### Stage 3 - Broader Semantic Reference Handling
Goal:
- extend bounded follow-up understanding beyond ordinals and rewrite prompts

Tasks:
- handle safe modifier-style references
- prefer anchored option/recommendation resolution
- add fallback clarification when confidence is weak

Primary files:
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/conversation/conversation_router.py`

### Stage 4 - Clarification Discipline
Goal:
- make Nova ask better short clarifications in ambiguous conversational cases

Tasks:
- distinguish:
  - rewrite request
  - decision request
  - option reference
  - command-like request
- add short clarification templates for weakly anchored follow-ups

Primary files:
- `nova_backend/src/conversation/conversation_router.py`
- `nova_backend/src/conversation/response_formatter.py`
- `nova_backend/src/brain_server.py`

### Stage 5 - Evaluate Before Broadening
Goal:
- stop and assess whether Nova feels materially better before attempting broader semantic inference

Evaluation questions:
- does Nova hold the thread better?
- does Nova rewrite the right part of the answer?
- does Nova avoid fake confidence?
- does Nova remain governed and non-authorizing in ambiguous cases?

## Proof Rule For Every Slice
Every conversational-core slice should end with:
- one focused unit-level proof
- one live WebSocket/session proof when applicable
- no authority regression
- restored runtime artifacts before commit
- a clean branch checkpoint

Recommended proof surfaces:
- `nova_backend/tests/conversation/test_general_chat_tone.py`
- `nova_backend/tests/conversation/test_conversation_router.py`
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`
- `nova_backend/tests/conversation/test_personality_interface_agent.py`
- `nova_backend/tests/test_tierb_conversation.py`

## Definition Of Done For This Program
This conversational-core program is in a good stopping state when:
- Nova can hold bounded session context over short and medium chat threads
- Nova can adapt presentation without changing authority
- Nova can resolve common follow-ups conservatively and truthfully
- Nova asks short clarifications instead of over-guessing
- conversation improvements remain fully separated from governed action execution

It does not require:
- long-term memory
- autonomous conversation steering
- implied command execution
- “human-like” simulation

## Explicit Non-Goals
This program does not include:
- external-provider conversational expansion
- broader authority changes
- autonomous follow-up behavior
- cross-session learning
- emotion simulation
- “assistant persona” theatrics

## Practical Next Slice
If coding continues from this packet, the next best bounded slice is:
- strengthen the explicit session context object for local chat only

After that:
- adaptive presentation shaping
- broader semantic modifier handling
- short clarification prompts for ambiguous follow-ups

That order should be preserved unless a more urgent truth gap appears in live use.
