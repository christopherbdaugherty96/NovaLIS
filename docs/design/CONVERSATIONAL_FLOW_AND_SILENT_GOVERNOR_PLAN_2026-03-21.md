# Conversational Flow And Silent Governor Plan
Date: 2026-03-21
Status: Planning packet only; next bounded conversational direction after current `main`
Scope: Make Nova feel more fluid, context-aware, and natural in conversation while keeping Governor-mediated authority strict and mostly silent unless approval or execution boundaries matter

## Core Rule
Conversation should feel fluid. Authority should stay governed.

More specifically:

The governor should be quiet during normal conversation and visible only when:
- approval is required
- execution is requested
- a real-world effect is about to happen
- a trust-significant boundary or failure must be surfaced honestly

That is the governing sentence for this packet.

## Why This Packet Exists
Nova now has a much stronger baseline on `main`:
- bounded session conversation context
- adaptive presentation shaping
- bounded reference resolution
- short clarification discipline
- speech and input naturalness improvements
- stronger local project/codebase summary paths

That means the next quality gap is no longer basic continuity alone.
It is the feel of the conversation layer itself.

The user goal is clear:
- Nova should follow the flow of conversation intuitively
- Nova should ask better clarifying questions
- Nova should preserve topic context more naturally
- the Governor should not feel like it is intruding on normal chat

This does not mean authority should loosen.
It means authority should be enforced mostly behind the scenes until the user reaches a point where execution, approval, or a trust boundary actually matters.

## Goal
Make Nova feel more like a steady reasoning partner in normal conversation without making it more autonomous, less governed, or more willing to infer actions.

In plain language:
- Nova should keep up with the thread
- Nova should ask short, useful clarifications
- Nova should summarize ongoing context better
- Nova should not surface approval/governor framing unless it is actually relevant

## Silent Governor Principle

### What Should Be Silent
For normal conversation turns, Nova should not lead with:
- permission language
- authority disclaimers
- action-governance framing
- capability defensiveness

Examples of turns where the Governor should stay silent:
- explanation requests
- follow-up questions
- rewrite requests
- comparisons
- brainstorming
- local project/codebase summaries
- topic continuity and session recap

### What Should Still Be Visible
The Governor must still surface clearly when:
- a governed action needs approval
- a capability is unavailable for execution
- a boundary prevents a requested action
- a failure affects trust or system effect truth

Good examples:
- `Open C:\Nova-Project? This action needs confirmation.`
- `I recognized the action, but this runtime can't execute it right now.`

Bad examples:
- surfacing execution-boundary language during harmless discussion
- acting guarded and formal during ordinary chat
- making casual conversation feel like a policy review

## Context Awareness Focus
Nova should become better at carrying the active conversational thread.

Target context elements:
- current topic
- user goal
- active target
- unresolved question
- active options or recommendation
- current project/repo when clearly in scope
- current explanation/rewrite target

Desired result:
- less reset-heavy interaction
- fewer literal misunderstandings
- smoother follow-ups
- better continuation of local project discussion

This remains:
- session-scoped
- bounded
- non-authorizing
- not durable memory

## Clarification Discipline
When Nova is uncertain, it should ask one short targeted question instead of:
- guessing
- falling into a generic misunderstanding bucket
- surfacing unnecessary policy language

Good clarification examples:
- `Do you mean the current repo or a different local folder?`
- `Do you want a summary of the codebase or an architecture report?`
- `Are you asking me to explain it, or to open it?`

Bad clarification examples:
- long self-justifying explanations
- open-ended wandering questions
- early authority disclaimers when no action is being taken

## Session Summarization Focus
Nova should get better at holding and surfacing the current thread without overwhelming the user.

Useful session-summary behavior:
- keep a lightweight view of what the user is working on
- preserve the current objective and unresolved question
- help continue a session naturally after a few turns
- support better repo/project continuity

This should not become:
- hidden persistence
- automatic long-term memory
- a broad user-profile layer

## Conversational Freedom Boundary
Nova may become more fluid in:
- explanation
- comparison
- summarization
- rewriting
- brainstorming
- local project/codebase discussion

Nova may not become freer in:
- hidden action inference
- executing from vague conversational phrasing
- bypassing approval
- widening command interpretation without explicit proof and review

This is the core product balance:
- freer conversation
- unchanged authority

## Architectural Direction
The right layering is:

1. Conversation interpretation decides what kind of conversational turn this is
2. Context/session state helps keep the active thread coherent
3. The Governor checks silently in the background when action capability matters
4. The user only sees the Governor when approval, denial, or trust-significant execution truth matters

That means the Governor becomes quieter in normal conversation, not weaker.

## Safe Build Order

### Stage 1 - Silent Governor Conversation Contract
Goal:
- define when the Governor should stay invisible during harmless conversational turns

Tasks:
- identify conversation-only lanes that should not surface authority framing
- define when approval/boundary language is actually required
- reduce generic boundary intrusions in non-action chat

Primary files:
- `nova_backend/src/brain_server.py`
- `nova_backend/src/governor/governor.py`
- `nova_backend/src/conversation/response_formatter.py`

### Stage 2 - Deeper Context Continuity
Goal:
- improve how Nova keeps track of the current topic, target, and unresolved question

Tasks:
- strengthen session-thread carryover
- preserve active local project/repo focus when clearly in scope
- improve current-target continuity for summaries, explanations, and rewrites

Primary files:
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/working_context/`

### Stage 3 - Better Clarification Prompts
Goal:
- make ambiguity recovery feel short, natural, and useful

Tasks:
- improve clarification templates
- reduce generic fallback responses
- distinguish local project clarification from generic topic clarification

Primary files:
- `nova_backend/src/conversation/conversation_router.py`
- `nova_backend/src/conversation/response_formatter.py`
- `nova_backend/src/skills/general_chat.py`

### Stage 4 - Ongoing Session Summary Discipline
Goal:
- help Nova continue longer conversations without feeling reset-heavy

Tasks:
- improve lightweight current-session summary use
- support better thread continuation after several turns
- preserve project-oriented context more deliberately

Primary files:
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/working_context/`
- `nova_backend/src/memory/` (only if bounded and still session-scoped for this slice)

### Stage 5 - Evaluate Before Broadening
Goal:
- stop and assess whether the conversation now feels materially smoother before any broader reasoning work

Evaluation questions:
- does Nova follow the active topic more naturally?
- does Nova ask better short clarifications?
- does conversation feel less interrupted by visible governance?
- do approval and execution boundaries still appear clearly when needed?
- does Nova remain just as strict on action authority?

## Proof Rule
Every slice in this program should end with:
- focused conversational tests
- at least one real session or websocket proof when applicable
- explicit no-authority-drift validation
- restored runtime artifact files before commit
- a clean checkpoint

Recommended proof surfaces:
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`
- `nova_backend/tests/conversation/test_general_chat_tone.py`
- `nova_backend/tests/conversation/test_conversation_router.py`
- `nova_backend/tests/conversation/test_response_formatter.py`
- `nova_backend/tests/test_governor_execution_timeout.py`

## Non-Goals
This packet does not authorize:
- personality learning
- adaptive personality drift
- hidden execution inference
- background autonomous behavior
- long-term memory expansion
- broader command looseness

## Definition Of Done
This packet reaches a good stopping point when:
- normal conversation feels smoother and less brittle
- topic and project continuity are stronger
- clarification prompts are shorter and more helpful
- the Governor feels quieter during ordinary discussion
- approval and trust-significant execution boundaries still surface clearly when necessary

## One-Sentence Summary
Nova should feel more conversationally natural by keeping context better and asking smarter clarifications, while the Governor stays mostly invisible until approval, execution, or real trust boundaries truly matter.
