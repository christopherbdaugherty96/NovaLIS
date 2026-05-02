# Context Pack Specification

Status: planning.

This document defines the planned Context Pack layer for Nova. It is not implemented runtime behavior.

## Purpose

Context Pack is the bounded bridge between Memory/Learning/Search/Project state and the Brain.

The Brain should not scan all memory, all docs, all learning items, or all search results directly.

## Core rule

```text
No Context Pack means no durable memory or learning influence on Brain.
```

## Responsibilities

Context Pack should:

- select relevant context
- label every source
- preserve authority levels
- enforce budgets
- surface stale/conflict warnings
- explain why context was selected
- prevent memory/learning overload

## Non-responsibilities

Context Pack must not:

- authorize action
- execute tools
- promote memory
- confirm learning
- override runtime truth
- silently hide conflicts

## Inputs

Future inputs may include:

- current user message
- session continuity
- active project
- confirmed memories
- candidate memory prompts
- confirmed learning items
- learning health warnings
- project capsule
- search evidence summary
- runtime truth summary
- receipts
- calendar/weather summaries

## Output shape

```json
{
  "project": "novalis",
  "mode": "repo-review",
  "sources": [],
  "project_capsule": {},
  "confirmed_memories": [],
  "confirmed_learning": [],
  "open_loops": [],
  "search_evidence": {},
  "runtime_truth": {},
  "warnings": [],
  "budget": {},
  "why_selected": []
}
```

## Source labels

Use stable source labels:

- `runtime_truth`
- `current_conversation`
- `session_continuity`
- `confirmed_memory`
- `candidate_memory`
- `confirmed_learning`
- `candidate_learning`
- `project_capsule`
- `search_evidence`
- `receipt`
- `calendar_summary`
- `weather_summary`
- `assumption`

## Authority labels

Use stable authority labels:

- `runtime_truth`
- `current_instruction`
- `confirmed_project_memory`
- `confirmed_personal_memory`
- `confirmed_learning`
- `candidate_memory`
- `candidate_learning`
- `scratchpad`
- `assumption`

## Budget defaults

Suggested first budget:

- max 1 project capsule
- max 5 confirmed memories
- max 3 confirmed learning items
- max 3 open loops
- max 2 candidate prompts
- max 2 stale/conflict warnings
- max 1 search evidence summary

## Warning types

- `stale_memory`
- `stale_learning`
- `conflicting_sources`
- `runtime_truth_unknown`
- `weak_search_evidence`
- `unclear_scope`
- `budget_exceeded`

## Brain use rule

Brain may use Context Pack to:

- improve recommendations
- understand project state
- identify open loops
- explain why memory was used
- detect uncertainty
- prepare candidate memory/learning proposals

Brain may not use Context Pack to:

- authorize action
- bypass Governor
- treat candidate memory as fact
- treat planning docs as runtime truth

## Proof requirements

Before claiming Context Pack is implemented, prove:

- budgets are enforced
- source labels are present
- stale/conflict warnings are surfaced
- candidate items are not treated as confirmed
- runtime truth outranks memory
- forgotten memory is not selected
- Brain can explain why context was selected
