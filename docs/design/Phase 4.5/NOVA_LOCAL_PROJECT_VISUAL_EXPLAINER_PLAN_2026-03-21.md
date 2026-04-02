# Nova Local Project Visual Explainer Plan
Date: 2026-03-26
Status: Stage 1 now live; later stages still planned
Scope: Add a human-friendly visual structure map on top of Nova's local project summary and architecture report capabilities without changing authority or execution behavior

## Purpose
This packet captures a high-value UX layer:

Nova should not only summarize a codebase in words.
Nova should also be able to show the structure of a codebase in a way a human can quickly understand.

In plain English, the goal is:
- take a folder of code
- turn it into a visual map of the system

## Why This Matters
Nova already has:
- local project understanding
- codebase summary
- architecture report

The next useful step was:
- make the structure easier to see

That means helping a user understand:
- what parts exist
- how they connect
- what each part does

This is one of the highest-value UX upgrades because it turns codebase understanding into something more visual and more accessible.

## Current Live State
Stage 1 is now live on `main`.

That means Nova can now:
- produce a text-based Structure Map
- expose that Structure Map in chat
- surface the Structure Map on the new Workspace page
- keep the view read-only and grounded in local structure

Examples:
- `show structure map`
- `show repo map`
- `visualize this repo`
- `visualize this project`

## Best Product Framing
The right framing is not:
- generic diagram generator

The right framing is:
- visual codebase explainer layer

This sits on top of:
- repo summary
- module detection
- folder scanning
- architecture report signals

## Implementation Order

### Stage 1 - Text-Based Structure Map
Status:
- live

What it does now:
- gives the user an immediate readable system map
- provides plain-English labels for major parts
- works in chat and on the Workspace page
- avoids frontend graph complexity while still being useful

Why this was the right first step:
- immediate payoff
- readable in chat
- aligned with the current architecture
- useful to non-technical users right away

### Stage 2 - Structured Diagram Data
Status:
- planned

Goal:
- output diagram-ready structured data so the frontend can render a richer visual map later

Best shape:
- nodes
- edges
- node roles/types
- labels and descriptions

Suggested branch:
- `codex/local-project-visualization-stage2-structured-graph`

### Stage 3 - Actual Visual Graph UI
Status:
- planned

Goal:
- show an interactive system map in the UI

Possible features:
- clickable nodes
- hover explanations
- zoom and pan
- expand/collapse by folder or subsystem

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

That keeps the map useful instead of becoming a folder dump.

## Boundaries
This remains:
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

## Success Condition
Nova can explain a codebase visually enough that a user can quickly understand:
- the main parts
- how they connect
- what each part does

And the first version works without needing a full interactive UI.

## Recommended Product Rule
The anchor rule for this feature should be:

Show the structure, explain the meaning, and stay read-only.
