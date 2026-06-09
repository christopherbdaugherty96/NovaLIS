# Findings Report - 2026-06-08

Status: Draft findings report
Date: 2026-06-08
Source: Local repo inspection and operating-model package creation
Reason: Record robust gaps and decisions found during implementation

## Findings

1. The operating model is valuable only if it separates context, truth,
   authority, and execution.
2. Obsidian is appropriate as a context and coordination layer.
3. Obsidian must not become an authority or execution layer.
4. AI outputs must remain proposals until reviewed.
5. Business needs must pass through proposal and review before becoming Nova
   implementation scope.
6. GitHub implementation truth does not automatically authorize execution.
7. Runtime docs, receipts, logs, and code outrank drafts and planning notes.
8. The current accepted Nova implementation lane remains Second Brain Slice 1
   and is limited to schema/parser/wikilink/vault lint/no-mutation tests.

## Implementation Decision

This package was placed under:

```text
docs/Future/ai_ecosystem_operating_model/
```

Reason:
The package is useful and reviewable, but it is not the repo's current active
implementation priority and should not masquerade as live Nova runtime policy.
