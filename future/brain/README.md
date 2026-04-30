# Future Brain Extensions

This folder is the umbrella for future NovaLIS brain-adjacent planning that should stay separate from current runtime Brain documentation.

It exists to keep long-term learning, planning, governed execution, and domain workflows in one organized category without overstating current runtime capability.

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

Current runtime Brain documentation remains under `docs/brain/`.

Future, experimental, or not-yet-implemented brain extensions belong here.

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

---

## Subfolders

### `governed_desktop_runs/`

Defines task-scoped desktop, browser, scheduled, continuous, and OpenClaw run planning.

This is the future governed execution contract layer.

### `market_sandbox/`

Defines future market-research, paper-trading, thesis tracking, and governed learning loops.

This is a domain example of learning that feeds the brain without becoming financial authority.

### `youtubelis/`

Defines a future content-production workflow idea.

This is a domain example of using governed planning/execution for media workflows.

---

## Why One Umbrella Folder

The ideas are separate but related:

- governed desktop runs explain how Nova may act safely
- market sandbox explains how Nova may learn safely in a risky domain
- YouTubeLIS explains how Nova may coordinate a content workflow later

Keeping them under `future/brain/` makes the long-term architecture easier to follow.

---

## What Belongs Here

- future learning architecture
- future planning architecture
- future governed execution models
- future domain workflows that depend on Brain planning
- design docs that are not runtime truth

---

## What Does Not Belong Here

- generated runtime truth
- live capability counts
- current implementation claims
- Governor source code
- capability registry changes
- documents claiming unimplemented behavior as active

---

## Promotion Rule

A document or idea in this folder should only move into current docs or runtime implementation when:

- code exists
- tests exist
- runtime behavior is verified
- generated runtime truth reflects it
- claims are no longer future-only

Until then, this folder is a safe planning space.
