# Nova Local Project Visual Explainer Plan
Date: 2026-03-21
Status: Planning packet only; current product-improvement roadmap for a visual codebase explanation layer
Scope: Add a human-friendly visual structure map on top of Nova's local project summary and architecture report capabilities without changing authority or execution behavior

## Purpose
This packet captures a high-value next UX layer:

Nova should not only summarize a codebase in words.
Nova should also be able to show the structure of a codebase in a way a human can quickly understand.

In plain English, the goal is:
- take a folder of code
- turn it into a visual map of the system

This is not runtime truth.
It is a product and design roadmap for a visual codebase explainer layer.

## Why This Matters
Nova already has:
- local project understanding
- codebase summary
- architecture report

The next useful step is:
- make the structure easier to see

That means helping a user understand:
- what parts exist
- how they connect
- what each part does

This is one of the highest-value UX upgrades because it turns codebase understanding into something more visual and more accessible.

## Best Product Recommendation
The right framing is not:
- generic diagram generator

The right framing is:
- visual codebase explainer layer

This should sit on top of:
- repo summary
- module detection
- folder scanning
- architecture report signals

## Best Implementation Order

### Stage 1 - Text-Based Structure Map
Goal:
- give the user an immediate, readable system map with no frontend complexity

Best shape:
- tree-style output in chat or report form
- plain-English labels for major parts
- grouped by important modules/folders

Example shape:

```text
Nova System Overview

├── brain_server.py
│   └── Entry point (API + routing)

├── governor/
│   ├── governor.py
│   │   └── Execution control and permissions
│   └── capability_registry.py
│       └── What Nova can do

├── executors/
│   ├── web_search_executor.py
│   ├── local_project_executor.py
│   └── system_control_executor.py
│       └── Actions Nova can perform

├── skills/
│   └── general_chat.py
│       └── Conversation and reasoning

├── audit/
│   └── runtime_auditor.py
│       └── Trust and reporting
```

Why this is the best first step:
- immediate payoff
- no heavy frontend work
- readable in chat
- aligned with current architecture

Suggested branch:
- `codex/local-project-visualization-stage1-structure-map`

### Stage 2 - Structured Diagram Data
Goal:
- output diagram-ready structured data so the frontend can render a visual map later

Best shape:
- nodes
- edges
- node roles/types
- labels and descriptions

Example shape:

```json
{
  "nodes": [
    {"id": "brain_server", "type": "entry", "label": "Brain Server"},
    {"id": "governor", "type": "control", "label": "Governor"},
    {"id": "executors", "type": "actions", "label": "Executors"},
    {"id": "skills", "type": "conversation", "label": "Skills"}
  ],
  "edges": [
    ["brain_server", "governor"],
    ["governor", "executors"],
    ["brain_server", "skills"]
  ]
}
```

Why this is the right second step:
- keeps the backend/frontend contract clean
- avoids hardwiring presentation too early
- enables multiple visual renderers later

Suggested branch:
- `codex/local-project-visualization-stage2-structured-graph`

### Stage 3 - Actual Visual Graph UI
Goal:
- show an interactive system map in the UI

Likely technologies:
- Mermaid
- React Flow
- D3

Possible features:
- clickable nodes
- hover explanations
- zoom and pan
- expand/collapse by folder or subsystem

This is the polish layer, not the first move.

Suggested branch:
- `codex/local-project-visualization-stage3-graph-ui`

## What Nova Should Explain
The visual layer should not only show structure.
It should show meaning.

Each node should ideally include:
- what it is
- what it does
- how important it is
- whether it appears active

Example:

```text
Governor
- Role: Controls execution
- Type: Critical
- Authority: High
- Status: Active
```

That makes the visual map more than a folder dump.

## Boundaries
This should remain:
- read-only
- explanatory
- grounded in inspected codebase structure

It should not:
- execute code
- modify files
- infer behavior beyond the inspected evidence
- claim certainty beyond what Nova actually inspected

## Placement
This belongs in the current product and local-project improvement track.

It is not:
- a Phase 7 reasoning-provider item
- a Phase 8 execution item
- a learning/adaptation item

It is a human-understanding and UX layer on top of the existing local project summary work.

## Likely Inputs
This should build on:
- local codebase summary
- local architecture report
- repo/folder scan data
- folder/module role detection

Likely surfaces:
- `nova_backend/src/brain_server.py`
- local project summary helpers
- local architecture report helpers
- later, dashboard/UI rendering surfaces

## Success Condition
Nova can explain a codebase visually enough that a user can quickly understand:
- the main parts
- how they connect
- what each part does

And the first version works without needing a full interactive UI.

## Recommended Product Rule
The anchor rule for this feature should be:

Show the structure, explain the meaning, and stay read-only.
