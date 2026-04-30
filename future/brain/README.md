# Future Brain Extensions

This folder is the umbrella for future NovaLIS brain-adjacent planning that should stay separate from current runtime Brain documentation.

It keeps long-term learning, planning, governed execution, and domain workflow ideas in one organized category without overstating current runtime capability.

---

## Current Boundary

This folder is planning only.

It does not change:

- current Brain runtime behavior
- Governor
- CapabilityRegistry
- generated runtime truth
- OpenClaw execution path
- memory governance
- active capabilities

Current runtime Brain documentation remains under:

```text
docs/brain/
```

Future, experimental, or not-yet-implemented brain extensions belong here.

---

## Source-of-Truth Rule

This umbrella currently uses reference folders instead of moving the original docs.

Current source-of-truth locations:

```text
future/governed_desktop_runs/
future/market_sandbox/
future/youtubelis/
```

Reference locations under this umbrella:

```text
future/brain/governed_desktop_runs/
future/brain/market_sandbox/
```

This avoids broken links and preserves history while making the long-term brain category easier to navigate.

---

## Core Principle

> Learning and planning may feed the brain. They do not grant authority.

NovaLIS should keep this separation:

```text
Brain proposes.
Governance decides.
Execution stays bounded.
Memory remains inspectable.
```

The brain may use approved context, learning records, plans, and summaries. It may not grant itself execution authority, expand permissions, or bypass the Governor.

---

## Concept Map

```text
future/brain/
  governed_desktop_runs/  → how future Brain planning may become governed action
  market_sandbox/         → how future Brain learning may work in a risky domain
  youtubelis/             → how future Brain planning may support content workflows later
```

---

## Subfolders

### `governed_desktop_runs/`

Defines task-scoped desktop, browser, scheduled, continuous, and OpenClaw run planning.

This is the future governed execution contract layer.

Relationship to Brain:

- Brain proposes task plans.
- Governed run envelopes constrain action.
- Governor remains the authority.
- Execution remains logged and interruptible.

### `market_sandbox/`

Defines future market-research, paper-trading, thesis tracking, and governed learning loops.

This is a domain example of learning that feeds the brain without becoming financial authority.

Relationship to Brain:

- Brain analyzes data and lessons.
- Market learning records remain structured and inspectable.
- Strategy changes require user approval.
- Learning never grants trading authority.

### `youtubelis/`

Defines a future content-production workflow idea.

This is a domain example of using governed planning/execution for media workflows.

Relationship to Brain:

- Brain may help plan scripts, workflows, and asset steps.
- Publishing remains separate and high-risk.
- Workflow execution should depend on governed desktop runs if implemented later.

---

## Why One Umbrella Folder

The ideas are separate but related:

- governed desktop runs explain how Nova may act safely
- market sandbox explains how Nova may learn safely in a risky domain
- YouTubeLIS explains how Nova may coordinate a content workflow later

Keeping them visible under `future/brain/` makes the long-term architecture easier to follow without mixing future plans into current runtime docs.

---

## What Belongs Here

- future learning architecture
- future planning architecture
- future governed execution models
- future domain workflows that depend on Brain planning
- design docs that are not runtime truth
- cross-links between future Brain-related ideas

---

## What Does Not Belong Here

- generated runtime truth
- live capability counts
- current implementation claims
- Governor source code
- capability registry changes
- documents claiming unimplemented behavior as active
- financial, publishing, or desktop execution claims that are not implemented

---

## Promotion Rule

A document or idea in this folder should only move into current docs or runtime implementation when:

- code exists
- tests exist
- runtime behavior is verified
- generated runtime truth reflects it
- claims are no longer future-only

Until then, this folder is a safe planning space.

---

## Migration Rule

Do not delete or move the original source folders until:

1. references are checked,
2. duplicate docs are reconciled,
3. README links are updated,
4. history-sensitive docs are preserved,
5. the new structure is clearly marked as the source of truth.

For now, this folder is the umbrella/navigation layer.
