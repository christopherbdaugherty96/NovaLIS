# Memory Layers

Nova memory is context, not authority.

Memory can help Nova understand a task, but it cannot authorize execution.

## Layers

- Session context
- Working memory
- Core user memory
- Project memory
- Topic/story memory
- Archival memory
- Conversation search
- Suggestion buffer
- Receipts / ledger
- Runtime truth
- Future docs

## Working Memory

Working Memory tracks the active task:

- current goal
- known facts
- unknowns
- active project
- current environment
- blocker
- next decision

## Suggestion Buffer

The Suggestion Buffer stores candidate suggestions, not actions.

Example:

```text
Pattern noticed: user often asks for Shopify summary, then an email draft.
Suggestion: offer to prepare the summary and hold an email draft plan for review.
```

Rules:

- suggestions do not execute
- suggestions do not authorize actions
- suggestions are dismissible
- suggestions should be inspectable and deletable

## Active Garbage Collection

Long tasks need resource control.

The brain should eventually be able to move stale Working Memory into Archival Memory to avoid context collapse.

This should be visible and reversible where practical.

## Receipts Are Separate

Receipts and ledger events are proof, not personal memory.

They may inform reflection, but they must not become hidden permission.