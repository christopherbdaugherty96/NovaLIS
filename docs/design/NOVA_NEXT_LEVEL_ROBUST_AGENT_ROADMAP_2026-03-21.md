# Nova Next-Level Robust Agent Roadmap
Date: 2026-03-21
Status: Planning packet only; cross-phase roadmap for making Nova feel more capable, more robust, and more useful without widening unsafe autonomy
Scope: Capture the major missing layers that would make Nova feel next-level while preserving governed safety, explicit control, and reviewability

## Purpose
This packet preserves a direct product question:

What is still missing that would make Nova feel stronger, more robust, more modern, and more competitive with newer agents while still staying safe?

This document is not runtime truth.
It is a roadmap packet for the structural layers that matter most after the current conversation, style, search, news, and local-project work.

## Honest Framing
The biggest gap is not "more AI magic."

The biggest gap is the operating system around the model:
- projects
- modes
- memory
- retrieval
- connectors
- tasks
- permissions
- evals
- context management

That is what increasingly separates:
- chatbot features
from
- robust agent products

## Product Signal From Recent Agent Systems
Across newer agent products, the pattern is consistent:
- project/workspace organization matters
- research and chat are treated as different modes
- connected sources matter
- memory is becoming more explicit and reviewable
- scheduled tasks are becoming normal
- evaluation and guardrails are becoming core infrastructure

Nova should learn from that pattern without copying the products directly.

The goal is not:
- imitate another assistant's personality

The goal is:
- build the missing agent-system layers that make Nova more useful and more reliable

## Core Missing Layers

### 1. Project And Workspace System
Nova needs a stronger project surface where a project can hold:
- a repo or folder
- notes
- saved memories
- linked sources
- reports
- trusted sites
- task history

This is one of the biggest upgrades from "chat with tools" to "working assistant."

### 2. Clear Mode Architecture
Nova should have clearer separation between:
- Chat
- Research
- Action
- Review / second opinion

This prevents every experience from collapsing into one mixed mode.
It keeps:
- chat smooth
- research deep
- action governed
- review explicit

### 3. Strong Explicit Memory System
Nova needs better:
- save this
- remember this
- memory list
- memory view
- memory edit/delete
- relevant memory use in context

This should remain explicit and governed, not hidden adaptive learning.

### 4. Better Research / Retrieval Answer Engine
Nova needs stronger:
- answer-first search
- grounded news summaries
- source reading before summary
- better follow-up handling after retrieval

The key pattern is:
- understand
- retrieve
- read
- reason
- answer
- show evidence on demand

### 5. Connector And App Layer
Nova should eventually connect to the tools people actually use for coding and writing.

The best first connector targets are common, practical tools and document surfaces:

Coding-oriented connections:
- local folders and repos
- GitHub
- VS Code workspaces
- Visual Studio solutions
- JetBrains project folders
- Cursor projects
- Markdown files
- plain text files

Writing-oriented connections:
- Notepad / plain text files
- Word documents (`.docx`)
- Google Docs
- Notion pages or exports
- Obsidian vaults
- OneNote exports or notes
- PDFs and reference documents

Important product rule:
- prefer source/file/workspace-level connections first
- do not start by trying to drive every app UI directly

For example:
- connecting to a Word document is better than pretending Nova should immediately remote-control Microsoft Word
- connecting to a VS Code workspace or repo is better than starting with broad IDE automation

### 6. Background Tasks And Schedules
Nova should eventually support visible, user-controlled recurring work such as:
- daily brief
- project check-ins
- scheduled summaries
- reminder-style reviews
- research refreshes

This should always stay:
- explicit
- user-created
- inspectable
- pausable
- deletable

### 7. Evaluation, Tracing, And Regression Infrastructure
This is one of the most important missing layers.

Nova needs stronger infrastructure for:
- replaying important prompts
- grading outcomes
- tracing tool paths
- measuring regression over time
- proving quality changes actually helped

Without this, Nova risks becoming broader without becoming more reliable.

### 8. Permission And Trust Center
Nova should have a clearer trust surface for:
- what sites can be searched
- what connectors are enabled
- what actions need approval
- what memories are active
- what background tasks exist
- what the current authority boundaries are

This would make Nova safer and easier to understand.

### 9. Context Management For Long-Running Work
Nova needs better systems for:
- keeping the right context alive
- dropping stale context
- carrying forward the active project state
- avoiding "forgot what we were doing" failures

This is different from long-term learning.
It is mostly about disciplined active context management.

### 10. Stronger External Reasoning Lane
Nova should eventually use stronger external reasoning providers in a governed way for:
- harder research
- second opinions
- deeper critique
- better long-form reasoning

This should stay:
- explicit
- bounded
- advisory
- clearly separated from execution authority

## Recommended Connector Strategy

### Best First Connector Rule
Start with:
- read-only sources
- file-level access
- workspace-level access

Only later move toward:
- app-level control
- document editing actions
- cross-app automation

### Best Connector Rollout Order

#### Stage A - Read-Only Local And Cloud Sources
Good first targets:
- local folders
- repos
- markdown files
- plain text files
- Word documents
- PDFs
- GitHub repos
- Google Docs
- Notion exports/pages
- Obsidian vaults

#### Stage B - Project-Aware Source Connectors
Next, make those sources project-aware:
- this project uses these docs
- this repo uses these notes
- this writing workspace uses these references

#### Stage C - Governed App Actions
Only later, and only under approval, consider:
- open this doc
- open this workspace
- create a new note
- insert reviewed text into a document

That belongs with stronger execution governance, not with casual chat.

## Phase Placement Map

### Current Product Track
These belong in the current bounded product and conversation program:
- stronger project/workspace system
- clearer mode architecture
- stronger explicit memory UX
- better research/retrieval answer engine
- connector planning with read-only source-first integrations
- evaluation/tracing/regression infrastructure
- better context management for long-running work
- trust-center design surfaces

Why they belong here:
- they improve usefulness and reliability now
- they do not require unsafe autonomy
- they can be built in bounded slices

### Phase 7 - Governed External Reasoning
These belong in Phase 7:
- stronger external reasoning lane
- deeper provider-backed research support
- second-opinion review
- harder synthesis and ambiguity handling

Why they belong in Phase 7:
- they are reasoning-quality upgrades
- they remain text-first
- they do not add execution authority

### Phase 8 - Governed Execution And Connectors
These belong in Phase 8:
- action-aware mode discipline once execution expands
- governed app actions
- approval-gated connector actions
- explicit scheduled actions or multi-step workflows with real-world effects
- stronger permission surfaces tied to actual execution

Why they belong in Phase 8:
- they touch real-world effect pathways
- they require stronger approval and trust loops

Important boundary:
- read-only source connections can begin earlier
- app control and write actions belong here

### Phase 9 - Node-Scale Coherence
These belong in Phase 9:
- cross-client project continuity
- connector coherence across interfaces
- stable memory behavior across clients
- shared task visibility across Nova surfaces
- one trust model across device and client boundaries

Why they belong in Phase 9:
- they are node-level, not just one-local-surface improvements

### Phase 10 And Later - Reviewable Learning
Only much later should Nova consider:
- adaptive source weighting
- reviewable preference learning
- durable project-style adaptation
- learned retrieval prioritization
- long-term personalization beyond explicit memory

This should happen only with:
- auditability
- rollback
- diffability
- approval
- undoability

## What To Prioritize First
If the goal is "next-level, robust, but safe," the best order is:

1. evaluation / trace / regression infrastructure
2. project and workspace system
3. stronger explicit memory plus contextual retrieval
4. answer-first search/news/research implementation
5. clear mode architecture
6. read-only source connectors for common coding/writing tools
7. permission and trust center
8. governed background tasks and schedules
9. stronger external reasoning lane

## What Not To Do Yet
Do not prioritize:
- hidden personality learning
- broad autonomous behavior
- always-on background reasoning without clear user control
- app-control sprawl before trust surfaces exist
- connector writes before read-only source flows are strong
- broad multi-agent complexity without evals and traces

## Suggested Future Branch Families

Current product lane:
- `codex/agent-os-stage1-project-workspaces`
- `codex/agent-os-stage2-mode-architecture`
- `codex/agent-os-stage3-evals-and-traces`
- `codex/connector-stage1-readonly-sources`
- `codex/context-stage1-active-work-continuity`
- `codex/trust-center-stage1-visible-controls`

Memory lane:
- `codex/memory-stage1-save-remember-flow`
- `codex/memory-stage2-management-ui`
- `codex/memory-stage3-context-retrieval`

Reasoning lane:
- `codex/news-ui-stage1-inline-card-summary`
- `codex/websearch-stage1-answer-first-ui`
- `codex/phase7-second-opinion-stage1-explicit-review`

Execution/connectors lane:
- `codex/phase8-connector-actions-stage1-governed-opens`
- `codex/phase8-task-center-stage1-visible-schedules`

## Recommended Product Rule
The anchor rule for this roadmap should be:

Build the systems around Nova that make it more capable and reliable, while keeping authority explicit, reviewable, and governed.
