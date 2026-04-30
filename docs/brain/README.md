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
- Brain runtime architecture for small/medium local models
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
- Task Understanding / Simple Task Mode / Task Envelope planning-only scaffold
- conversation fallback helper can attach a planning-only Task Understanding preview for task-like requests
- planning-only in-memory RunManager scaffold for run creation, listing, pause/cancel, and focus tracking
- conversation fallback helper can create a session-local planning Run Preview for task-like requests
- read-only EnvironmentRequest schema scaffold
- static Capability Contract catalog for Cap 16, Cap 64, Cap 65, and Cap 63
- Brain live proof package under `docs/demo_proof/brain_live_test/`

Not fully implemented yet:

- full Task Environment Router
- runtime/live Capability Contract lookup
- Dry Run / Plan Preview API
- full runtime routing for Task Understanding / Simple Task Mode / Task Envelope
- persistent RunManager storage
- RunManager integration with dashboard / Co-Work page
- persistent Run Preview history
- Brain Trace UI
- Co-Work page
- project context engine
- suggestion buffer runtime
- full OpenClaw environment planning
- full model router / context assembler / intention parser stack

## OpenClaw Boundary

OpenClaw is documented as a governed execution environment, not a second brain or autonomous agent.

The current model requires future OpenClaw work to pass through:

```text
Brain → Run System → Governor → CapabilityRegistry → ExecuteBoundary → OpenClaw → Ledger
```

Key constraints are defined in [`OPENCLAW_ENVIRONMENT_MODEL.md`](OPENCLAW_ENVIRONMENT_MODEL.md), including:

- no direct chat-to-OpenClaw path
- Run and task-envelope requirement
- step-based execution
- domain/navigation scope
- approval granularity
- boundary detection
- interruption handling
- duplicate-action protection
- concurrency limits
- cleanup/session closure
- screenshot/evidence hygiene
- tests proving blocked actions pause instead of execute

These are governance expectations for future implementation. They do not mean full Run-based OpenClaw execution is live today.

## What This Package Does Not Do

This package does not implement runtime autonomy.

It does not add new execution paths.
It does not bypass the Governor.
It does not change Cap 64, Cap 65, OpenClaw, Shopify, or email behavior.
It does not mark conceptual plans as implemented runtime features.

Current runtime truth still comes from generated runtime docs and code.

## Recommended Reading Order

1. [`NOVA_BRAIN_MODEL.md`](NOVA_BRAIN_MODEL.md)
2. [`NOVA_BRAIN_RUNTIME_ARCHITECTURE.md`](NOVA_BRAIN_RUNTIME_ARCHITECTURE.md)
3. [`TASK_ENVIRONMENT_ROUTER.md`](TASK_ENVIRONMENT_ROUTER.md)
4. [`ENVIRONMENT_CATALOG.md`](ENVIRONMENT_CATALOG.md)
5. [`AUTHORITY_PLANE.md`](AUTHORITY_PLANE.md)
6. [`BRAIN_TRACE_UI_SPEC.md`](BRAIN_TRACE_UI_SPEC.md)
7. [`MEMORY_LAYERS.md`](MEMORY_LAYERS.md)
8. [`PROJECT_CONTEXTS.md`](PROJECT_CONTEXTS.md)
9. [`OPENCLAW_ENVIRONMENT_MODEL.md`](OPENCLAW_ENVIRONMENT_MODEL.md)
10. [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md)
