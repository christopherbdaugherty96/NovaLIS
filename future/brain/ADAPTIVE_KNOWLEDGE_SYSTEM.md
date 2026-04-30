# Adaptive Knowledge System

This document defines how NovaLIS may become continuously informed about new tools, breakthroughs, agent systems, APIs, apps, and opportunities without becoming an uncontrolled self-changing system.

This is planning only. It does not change runtime behavior, active capabilities, generated runtime truth, or execution authority.

---

## Core Principle

> NovaLIS should adapt in knowledge first, planning second, and execution last.

Nova may learn about new things. Nova may not silently grant itself new authority, install tools, change workflows, or expand capabilities.

---

## What This System Is For

Nova should be able to stay aware of:

- AI breakthroughs
- robotics progress
- new apps and tools
- agent frameworks
- automation platforms
- video/content tools
- business opportunities
- API changes
- local-first AI tooling
- open-source projects
- workflow improvements relevant to the user

The goal is not to chase everything new.

The goal is to maintain a governed, useful, current knowledge layer around the user’s active projects.

---

## What This System Is Not

This is not:

- autonomous capability expansion
- autonomous software installation
- hidden self-improvement
- automatic workflow mutation
- automatic trading, publishing, purchasing, or account action
- permission to use new third-party tools without review

---

## System Flow

```text
Signal Intake
→ Signal Filtering
→ Knowledge Map
→ Relevance Scoring
→ Evaluation Pass
→ Suggestion
→ User Approval
→ Planning Integration
→ Optional Capability Proposal
```

Execution remains separate and governed.

---

## Layer 1 — Signal Intake

Signal intake discovers new information.

Possible sources:

- approved RSS feeds
- GitHub repositories/releases
- official product blogs
- AI research announcements
- tool changelogs
- curated news sources
- user-provided links
- saved project sources
- existing Nova docs

Signal intake may collect and summarize.

Signal intake must not execute.

---

## Layer 2 — Signal Filtering

Most signals should be ignored.

Each signal should be filtered by:

```text
- Is it real or hype?
- Is it recent?
- Is it from a reliable source?
- Is it relevant to a user project?
- Is it actionable?
- Is it safe?
- Does it require account access, payment, or installation?
- Does it conflict with Nova governance?
```

Possible outcomes:

```text
IGNORE
TRACK
SUMMARIZE
EVALUATE
SUGGEST
BLOCK
```

---

## Layer 3 — Knowledge Map

Accepted signals should become structured knowledge, not random memory.

Example topics:

```text
AI video generation
AI agents
robotics
local models
OpenClaw / computer-use systems
YouTubeLIS workflow
market sandbox tooling
small-business automation
real-estate automation
Nova runtime architecture
```

A topic record may include:

```text
TopicKnowledge
- topic_id
- name
- summary
- recent_updates
- known_tools
- useful_sources
- risks
- relevance_to_projects
- last_reviewed_at
- confidence
```

---

## Layer 4 — Relevance Scoring

Nova should prioritize what matters to the user.

A signal is higher priority when it:

- improves an active workflow
- reduces cost or manual effort
- increases reliability
- improves privacy/local-first behavior
- aligns with governed execution
- helps Nova’s current P1 work
- helps YouTubeLIS, Market Sandbox, or business workflows

A signal is lower priority when it:

- is hype-heavy
- requires broad permissions
- requires paid accounts without clear ROI
- conflicts with local-first goals
- would encourage premature capability expansion

---

## Layer 5 — Evaluation Pass

Before Nova recommends using a new tool or method, it should evaluate:

```text
What does it do?
What permissions does it need?
What data leaves the local machine?
Does it require login or payment?
Does it support export/receipts?
Can it run locally?
Can it be used read-only first?
What could go wrong?
Does it fit Nova’s governance model?
```

Evaluation should produce an explicit recommendation:

```text
REJECT
WATCH
USE_MANUALLY
TEST_IN_SANDBOX
PROPOSE_CAPABILITY
```

---

## Layer 6 — Suggestion Layer

Nova may suggest high-value updates to the user.

Example:

```text
I found a new AI video tool that may help YouTubeLIS. It appears useful for generating scene b-roll, but it requires account login and paid credits. I recommend manual testing only, not capability integration.
```

Suggestion does not equal approval.

---

## Layer 7 — User Approval

Before a signal changes how Nova works, the user must approve.

Approval may allow:

- tracking a source
- evaluating a tool
- adding a manual workflow note
- testing in a sandbox
- drafting a capability proposal

Approval does not automatically allow:

- installation
- credential entry
- account mutation
- paid usage
- publishing
- trading
- new capability activation

---

## Layer 8 — Planning Integration

Approved knowledge can influence planning.

Examples:

- Nova may suggest a better YouTubeLIS workflow.
- Nova may update a tool comparison table.
- Nova may warn that a method is outdated.
- Nova may propose a safer alternative.

Planning integration must not increase execution authority.

---

## Layer 9 — Optional Capability Proposal

A new tool or workflow may eventually become a formal capability only if it passes the promotion path.

Required before capability proposal:

- clear use case
- governance model
- permission profile
- expected receipts
- failure modes
- tests
- no existing capability already covers it

Capability proposal does not equal implementation.

---

## Relationship to Existing Future Brain Docs

This document connects to:

- `future/brain/SIGNAL_REGISTRY.md`
- `future/brain/CONTEXT_ASSEMBLER.md`
- `future/brain/DOMAIN_PERMISSION_PROFILES.md`
- `future/brain/PROMOTION_PATH.md`
- `future/brain/FINAL_POLISH_RULES.md`
- `docs/product/TRUST_FLOW.md`

This system provides current knowledge. The other systems decide how knowledge is filtered, surfaced, governed, and eventually promoted.

---

## Relationship to YouTubeLIS

For YouTubeLIS, this system helps Nova stay aware of:

- AI video tools
- ElevenLabs alternatives
- editing tools
- stock/footage sources
- robotics demos
- AI race updates
- job-impact stories
- public interest trends

Nova may use this to suggest content angles and workflow improvements.

Nova may not use it to auto-publish or auto-operate accounts.

---

## Relationship to Market Sandbox

For Market Sandbox, this system may track:

- market data tooling
- financial news source quality
- trading-bot research
- risk-model ideas
- paper-trading methods

Nova may use this to improve research and paper simulation.

Nova may not use it to enable real trading authority.

---

## Relationship to Nova Runtime Development

For Nova itself, this system may track:

- local model improvements
- agent framework changes
- OpenClaw updates
- Python package changes
- browser automation safety patterns
- privacy/local-first infrastructure

Nova may recommend updates or experiments.

Nova may not silently modify its own architecture.

---

## Safety Rules

Nova must not:

- auto-install a discovered tool
- auto-create an account
- auto-enter credentials
- auto-spend credits
- auto-change a workflow
- auto-register a new capability
- auto-expand permission
- treat popularity as proof
- treat novelty as value

---

## First Safe Implementation Target

Start with a read-only weekly knowledge review:

```text
1. Read approved sources.
2. Summarize relevant updates.
3. Score relevance to active projects.
4. Suggest only the top few.
5. Ask whether to evaluate any.
6. Store approved notes only.
```

No installation.
No execution.
No workflow mutation.
No capability expansion.

---

## Current Status

Planning only.

Do not claim NovaLIS has a live Adaptive Knowledge System until code, tests, UI/receipt behavior, and generated runtime truth support it.
