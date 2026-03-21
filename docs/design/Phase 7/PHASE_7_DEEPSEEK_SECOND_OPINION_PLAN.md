# Phase 7 DeepSeek Second-Opinion Plan
Date: 2026-03-21
Status: Planning packet only; runtime not authorized
Scope: Governed DeepSeek-backed second-opinion reasoning inside the same Nova chat surface

## Why This Belongs In Phase 7
This request is about:
- external reasoning
- text-only audit/review support
- a second opinion inside the same chat box
- no new execution authority

That makes it a Phase-7 concern, not a Phase-8 execution concern and not a personality or learning feature.

DeepSeek in this design is:
- a governed external reasoning source
- a consultant
- a second-opinion provider
- never an execution authority

## Product Goal
Allow Nova to request a second opinion from DeepSeek for audit, review, critique, or verification style tasks while keeping the interaction inside the same Nova chat experience.

Desired product feel:
- the user stays in one chat box
- Nova remains the primary voice
- DeepSeek is used as a reference or second-opinion layer
- the user can see that a second opinion was used when it matters
- no separate "DeepSeek agent" personality takes over the interface

## Best Product Shape
The best version of this is not:
- Nova hands the chat over to DeepSeek
- DeepSeek becomes a second speaker with equal authority
- DeepSeek output is shown raw without Nova mediation

The best version is:
- Nova remains the assistant
- Nova asks DeepSeek for a bounded second opinion when requested or clearly appropriate
- Nova returns a single integrated response
- Nova can optionally expose a collapsible second-opinion section, provider note, or comparison detail

In other words:
- Nova speaks
- DeepSeek advises

## Recommended Use Cases
DeepSeek second-opinion mode is best for:
- code review
- architecture critique
- audit-style analysis
- "double check this" review requests
- counterargument or challenge requests
- second-pass explanation review
- structured quality checks on a draft answer

It is less ideal as the default for:
- every casual chat turn
- greetings
- basic utility questions
- simple local summaries
- frequent short back-and-forth conversation

The second-opinion lane should feel selective and high-value, not always-on.

## Recommended User Experience

### Same Chat Box
Keep everything inside the Nova chat box.

Nova should answer in one integrated message, for example:
- Nova's answer first
- then a short note like `Second opinion used: DeepSeek`
- then either:
  - a concise agreement/disagreement summary
  - or an expandable deeper review section

### Nova Stays The Main Voice
Nova should not suddenly switch tone or pretend to be DeepSeek.

Better:
- `My read is X. DeepSeek's second opinion mostly agrees, but it raised two concerns.`

Worse:
- `DeepSeek says: ...`
- raw pasted provider output
- full chat-speaker switching inside the same thread

### Optional Transparency
The user should be able to tell when a second opinion was used.
That can be lightweight:
- `Second opinion used: DeepSeek`
- `DeepSeek review note`
- `External reasoning cross-check`

But it should not dominate the conversation when the second opinion is only supporting context.

### Recommended UI Control
The best first user-facing control is a small button near the existing chat controls:
- near `Send`
- near `Mic`
- labeled simply: `DeepSeek`

This button should behave as a one-shot second-opinion trigger, not as a persistent mode switch.

That means:
- it does not permanently switch Nova into "DeepSeek mode"
- it does not create a second full assistant persona in the thread
- it simply asks DeepSeek to review the current exchange or recent bounded thread context

The clean mental model is:
- `Ask DeepSeek for a second opinion on this`

Not:
- `Switch this chat over to DeepSeek`

## Button Behavior Recommendation

### Best Stage-1 Behavior
When the `DeepSeek` button is clicked:
1. Nova stays in the same chat thread
2. the system collects a bounded recent conversation window
3. the system sends a second-opinion request to DeepSeek
4. DeepSeek returns a text-only advisory response
5. the UI renders a clearly labeled second-opinion message in the same thread

Recommended label for the returned card:
- `DeepSeek second opinion`
- or `Second opinion: DeepSeek`

This keeps the experience:
- simple
- understandable
- review-friendly
- same-thread

### What It Should Review
The button should review the most relevant recent exchange, not the full chat by default.

Best default review target:
- the last user message
- the last Nova response
- plus a bounded recent window of context

If there is no meaningful prior Nova answer yet, then it should review:
- the latest user request
- the recent bounded context needed to understand it

## Recommended Context Window
Do not send the full conversation by default.

Recommended bounded context:
- last user message
- last Nova reply
- last 4 to 8 turns of recent chat
- current local project/repo target when clearly in scope
- current task type if known

Good task-type examples:
- explanation
- review
- architecture
- debugging
- summary
- contradiction check

Why this is better:
- lower latency
- lower cost
- less noise
- lower chance of context confusion
- easier auditing

### If The User Wants Broader Review Later
That can become a later slice, for example:
- review last answer
- review current thread
- challenge Nova's answer
- architecture second opinion

But this should be a later enhancement, not the first version.

## Best Architectural Recommendation

### 1. Make It A Mode, Not A New Personality
Treat this as a reasoning mode or audit mode, not as a second assistant identity.

Good conceptual model:
- `Nova + second opinion`

Bad conceptual model:
- `Nova vs DeepSeek`

### 2. Make The Capability Provider-Neutral
Even if DeepSeek is the first provider you want to use, the capability should stay provider-neutral.

Recommended direction:
- capability meaning = external second-opinion reasoning
- provider selection = config or policy

That avoids baking vendor naming into the permanent capability contract.

Good examples:
- `llm_reasoning_external`
- `llm_second_opinion`

Less good:
- hard-coding the capability contract around one vendor forever

### 3. Use Structured Second-Opinion Output
Do not ask DeepSeek for a vague blob if the goal is review.

Better contract:
- `agreement_level`
- `main_findings`
- `risks_or_gaps`
- `counterpoints`
- `confidence_note`
- `recommended_follow_up`

This gives Nova something stable to summarize.

### 3.5. Use A Structured Prompt Contract
Do not send the recent conversation to DeepSeek with a vague instruction like:
- `continue this chat`

That creates weak, inconsistent second-opinion behavior.

Instead, send a bounded prompt like:
- review Nova's last answer
- answer the user's last message as a second opinion
- identify agreement, concerns, gaps, or stronger framing
- remain in text-only reasoning mode
- do not execute
- do not infer authority
- do not present as the primary assistant

The prompt contract should make DeepSeek's role explicit:
- consultant
- reviewer
- second-opinion source

Not:
- acting assistant
- planner with authority
- hidden system governor

### 4. Keep Nova As The Synthesizer
Nova should synthesize the second opinion into the final user-facing answer.

That means:
- Nova reads the user request
- Nova frames a bounded review task for DeepSeek
- DeepSeek returns structured reasoning only
- Nova summarizes the result in Nova's voice
- Nova optionally exposes deeper provider detail if the user wants it

### 5. Use It Selectively
Best activation patterns:
- explicit user ask
  - `give me a second opinion`
  - `double check this`
  - `audit this answer`
  - `have DeepSeek review this`
- or explicit high-value review surfaces
  - architecture review
  - code review
  - contradiction check
  - quality verification

Do not make it automatically run on every chat turn by default.

## Recommended Interaction Modes

### Mode A - Explicit Second Opinion
User asks for it directly.

Examples:
- `give me a second opinion on this`
- `have DeepSeek review this answer`
- `double check the architecture critique`

This should be the first implementation slice.

This mode should also include the explicit `DeepSeek` button as a UI trigger for the same bounded review behavior.

### Mode B - Suggested Second Opinion
Nova suggests it, but the user still chooses.

Examples:
- `I can answer directly, or I can get a second opinion from DeepSeek first.`
- `This looks like a review-heavy question. Want a second opinion pass?`

This is a good later slice.

This is still Phase 7, but it should come after the button-triggered explicit flow is stable.

### Mode C - Silent Background Cross-Check
Nova uses DeepSeek automatically behind the scenes for some review-heavy cases.

This should come much later, if ever.
It adds latency, cost, and product complexity.
It also risks making the system feel inconsistent unless extremely well bounded.

If this ever exists, it should be treated as a late Phase-7 or later experiment, not the initial product shape.

## Guardrails
The following should be non-negotiable:
- DeepSeek remains text reasoning only
- DeepSeek never gets execution authority
- DeepSeek never becomes a second governor
- DeepSeek output is sanitized before reuse
- DeepSeek output is treated as advisory, not authoritative
- Nova remains responsible for the final user-facing response

## Recommended Implementation Order

### Stage 1 - Explicit Second-Opinion Review
Goal:
- allow the user to explicitly ask for a DeepSeek-backed review or second opinion

Best scope:
- code review
- architecture critique
- answer audit
- contradiction check

Product shape:
- same Nova chat box
- Nova is primary voice
- lightweight `Second opinion used: DeepSeek` indicator
- explicit `DeepSeek` button near `Send` and `Mic`
- bounded recent-context review, not full-thread by default
- one labeled second-opinion response card in the same thread

### Stage 2 - Structured Comparison Surface
Goal:
- let Nova summarize agreement and disagreement more clearly

Good outputs:
- where DeepSeek agrees
- where DeepSeek raises concern
- what is still uncertain
- optional expandable comparison detail

This is still Phase 7.

### Stage 3 - Suggested Second Opinion
Goal:
- let Nova suggest a second-opinion pass in high-value review contexts

Still keep it user-controlled.

This is also still Phase 7, but later than the explicit button-triggered flow.

### Stage 4 - Optional Review Variants
Goal:
- support richer explicit review controls without changing the one-thread experience

Examples:
- `Review last answer`
- `Review this thread`
- `Challenge Nova's answer`
- `Architecture second opinion`

This is a later enhancement inside the same Phase-7 reasoning lane.

## Cross-Phase Placement

### Phase 7
Belongs here:
- explicit `DeepSeek` button
- bounded recent-thread review
- same-chat-box second-opinion response
- structured review output
- Nova-as-synthesizer behavior

### Phase 8
Does not belong here initially:
- execution tied to DeepSeek output
- any action authority derived from second-opinion reasoning

Phase 8 should only care about this feature insofar as:
- execution remains separate
- approval remains explicit
- DeepSeek output never becomes execution authority

### Phase 9 And Later
Potential later placement:
- the same second-opinion surface across multiple clients
- cross-device coherence for second-opinion history
- more advanced provider selection across node clients

### Much Later
Still not recommended early:
- always-on hidden background DeepSeek review
- silent adaptive use without user understanding
- provider-driven personality drift

## Best Technical Recommendation
The strongest implementation pattern is:

1. user asks Nova something
2. the user either explicitly asks for a second opinion or clicks the `DeepSeek` button
3. Nova decides whether this is a normal answer or a second-opinion task
4. if second opinion is requested, Nova creates a bounded external reasoning request from recent context
5. DeepSeek returns structured review text only
6. Nova synthesizes the result into one final chat reply or labeled second-opinion card
7. the UI stays single-threaded and single-speaker from the user's perspective

That preserves product coherence.

## What To Avoid
Do not:
- stream raw DeepSeek output directly as if it were Nova
- give DeepSeek equal speaker presence in the chat thread
- make it always-on by default
- let it affect execution or authority decisions directly
- let it silently rewrite the trust model

## One-Sentence Recommendation
The best way to use your DeepSeek API is as a governed, structured, optional second-opinion reasoning layer inside Nova's existing chat experience, with Nova remaining the main voice and DeepSeek serving as an auditable advisory reference.
