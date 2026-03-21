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

### Mode B - Suggested Second Opinion
Nova suggests it, but the user still chooses.

Examples:
- `I can answer directly, or I can get a second opinion from DeepSeek first.`
- `This looks like a review-heavy question. Want a second opinion pass?`

This is a good later slice.

### Mode C - Silent Background Cross-Check
Nova uses DeepSeek automatically behind the scenes for some review-heavy cases.

This should come much later, if ever.
It adds latency, cost, and product complexity.
It also risks making the system feel inconsistent unless extremely well bounded.

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

### Stage 2 - Structured Comparison Surface
Goal:
- let Nova summarize agreement and disagreement more clearly

Good outputs:
- where DeepSeek agrees
- where DeepSeek raises concern
- what is still uncertain

### Stage 3 - Suggested Second Opinion
Goal:
- let Nova suggest a second-opinion pass in high-value review contexts

Still keep it user-controlled.

## Best Technical Recommendation
The strongest implementation pattern is:

1. user asks Nova something
2. Nova decides whether this is a normal answer or a second-opinion task
3. if second opinion is requested, Nova creates a bounded external reasoning request
4. DeepSeek returns structured review text only
5. Nova synthesizes the result into one final chat reply
6. the UI stays single-threaded and single-speaker from the user's perspective

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
