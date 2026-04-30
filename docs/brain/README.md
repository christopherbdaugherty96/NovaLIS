# Nova Brain Architecture

This folder contains the detailed Brain architecture package.

For the concise canonical overview, start with [`docs/brain.md`](../brain.md).

For the product-level framing, see [`docs/product/NOVA_OPERATING_MODEL.md`](../product/NOVA_OPERATING_MODEL.md).

## Core Rule

Nova's Brain is not the authority.

The Brain may reason, clarify, rank environments, prepare dry runs, and propose fallback paths.

Execution still requires the existing governed runtime path.

```text
Let intelligence reason.
Let the Governor authorize.
Let receipts prove.
```

## What This Package Defines

- Nova Brain model
- Task clarification before planning
- Task Environment Router behavior
- environment catalog and authority tiers
- Authority Plane concepts
- capability contract model
- fallback ladders
- dry-run / plan-preview behavior
- Brain Trace UI concepts
- memory layers and project contexts
- OpenClaw as an environment, not the brain
- implementation roadmap

## Current Runtime Status

Implemented today:

- Task Clarifier for tested ambiguity/boundary prompt classes
- read-only EnvironmentRequest schema scaffold
- Brain live proof package under `docs/demo_proof/brain_live_test/`

Not fully implemented yet:

- full Task Environment Router
- live Capability Contract lookup
- Dry Run / Plan Preview API
- Brain Trace UI
- project context engine
- suggestion buffer runtime
- full OpenClaw environment planning

## What This Package Does Not Do

This package does not implement runtime autonomy.

It does not add new execution paths.
It does not bypass the Governor.
It does not change Cap 64, Cap 65, OpenClaw, Shopify, or email behavior.
It does not mark conceptual plans as implemented runtime features.

Current runtime truth still comes from generated runtime docs and code.

## Recommended Reading Order

1. [`NOVA_BRAIN_MODEL.md`](NOVA_BRAIN_MODEL.md)
2. [`TASK_ENVIRONMENT_ROUTER.md`](TASK_ENVIRONMENT_ROUTER.md)
3. [`ENVIRONMENT_CATALOG.md`](ENVIRONMENT_CATALOG.md)
4. [`AUTHORITY_PLANE.md`](AUTHORITY_PLANE.md)
5. [`BRAIN_TRACE_UI_SPEC.md`](BRAIN_TRACE_UI_SPEC.md)
6. [`MEMORY_LAYERS.md`](MEMORY_LAYERS.md)
7. [`PROJECT_CONTEXTS.md`](PROJECT_CONTEXTS.md)
8. [`OPENCLAW_ENVIRONMENT_MODEL.md`](OPENCLAW_ENVIRONMENT_MODEL.md)
9. [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md)
