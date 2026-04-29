# Nova Brain Architecture

This folder expands the canonical `docs/brain.md` note into a more detailed architecture package.

Nova's brain is not the authority.

The Governor remains the authority boundary for execution.

Reasoning may explore, clarify, plan, rank environments, prepare dry runs, and propose fallback paths. Execution still requires the existing governed runtime path.

Core rule:

```text
Let intelligence reason.
Let the Governor authorize.
Let receipts prove.
```

## What This Package Defines

- The Nova Brain model
- Task clarification before planning
- Task Environment Router behavior
- environment catalog and trust tiers
- Authority Plane concepts
- capability contracts
- fallback ladders
- dry-run / plan-preview behavior
- Brain Trace UI concepts
- memory layers and project contexts
- OpenClaw as an environment, not the brain
- implementation roadmap

## What This Package Does Not Do

This package does not implement runtime autonomy.

It does not add new execution paths.
It does not bypass the Governor.
It does not change Cap 64, Cap 65, OpenClaw, Shopify, or email behavior.
It does not mark conceptual plans as implemented runtime features.

Current runtime truth still comes from generated runtime docs and code.