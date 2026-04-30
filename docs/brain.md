# Nova Brain

This document is the canonical overview of Nova's Brain architecture.

For detailed specs, see [`docs/brain/`](brain/README.md).

## Core Principle

Nova's Brain is not the authority.

The Brain may reason, clarify, rank environments, prepare plans, suggest fallbacks, and explain boundaries.

Execution still passes through the Governor.

```text
Let intelligence reason.
Let the Governor authorize.
Let receipts prove.
```

## What The Brain Is

The Brain is the reasoning layer between conversation and execution.

It helps Nova answer:

1. What is the user trying to accomplish?
2. Is the request clear enough?
3. What does Nova know?
4. What does Nova not know?
5. What memory or context is needed?
6. What environment is required?
7. What authority tier applies?
8. Which capability would handle the task?
9. Is confirmation required?
10. What proof should exist afterward?
11. What is the next safe step?

The Brain is designed to make Nova more helpful and adaptive without turning intelligence into unchecked authority.

## Current Runtime Status

Current live Brain behavior:

- Task Clarifier is implemented for tested ambiguous/high-boundary prompts.
- Task Understanding / Simple Task Mode / Task Envelope exist as planning-only scaffolds.
- General-chat fallback can carry a planning-only Task Understanding preview for task-like requests.
- RunManager exists as an in-memory planning-only scaffold for run continuity state.
- General-chat fallback can create a session-local planning Run Preview for task-like requests.
- EnvironmentRequest schema exists as read-only scaffold.
- Static Capability Contract catalog exists for Cap 16, Cap 64, Cap 65, and Cap 63.
- Brain live-test proof exists under `docs/demo_proof/brain_live_test/`.

Still future / not fully live:

- full Task Environment Router
- live Capability Contract lookup in runtime routing/Governor
- Dry Run / Plan Preview API
- Brain Trace UI
- Co-Work page
- persistent RunManager storage
- RunManager execution integration
- persistent Run Preview history
- project context engine
- suggestion buffer runtime
- full OpenClaw environment planning
- full small-model runtime stack: Context Assembler, Model Router, Intention Parser, Search Synthesis, Sandbox Boundary Enforcer, and Persona Filter

## Brain Loop

```text
Task Intake
→ Task Understanding
→ Task Clarifier
→ Working Memory
→ Environment Reasoner
→ Authority Question
→ Plan Builder
→ Dry Run / Preview
→ Governor Gate
→ Execution
→ Proof
→ Reflection
```

## Task Clarifier

The first live Brain behavior is the Task Clarifier.

It pauses before Nova implies action when a prompt is ambiguous, underspecified, account-related, browser-related, or outside current capability.

Examples:

```text
User: Find contractors and draft an email.
Nova: What city or service area should I search in?
```

```text
User: Log into my account and change my settings.
Nova: That requires a personal account/browser/account-write environment and cannot proceed without explicit governed capability, confirmation, and proof.
```

```text
User: Change a Shopify product price.
Nova: Current Shopify support is read-only reporting/intelligence. Nova will not write to Shopify through the current Cap 65 path.
```

Task Clarifier is intentionally narrow and deterministic. It does not execute tools, call the Governor, or replace full Brain routing.

## Task Environment Router

The Task Environment Router is the planned middle layer between conversation and governed execution.

It answers:

```text
For this task, what environment does Nova need to enter?
What authority is required?
Which capability would grant access?
What confirmation is needed?
What proof should exist afterward?
```

A future Task Environment Router should produce structured output including:

```text
task_type
required_environments
environment_options
authority_required
capability_needed
confirmation_required
setup_required
proof_required
allowed_status
confidence
risk_level
blocker
fallback_ladder
next_safe_step
```

## Runtime Brain Stack

The full practical Brain should not depend on one giant local model.

It should use a governed runtime stack around smaller models:

```text
Task Clarifier
→ Context Assembler
→ Model Router / Tier Manager
→ local or approved reasoning model
→ Intention Parser
→ Tool Bridge
→ Sandbox Boundary Enforcer
→ Capability Contract Check
→ Governor
→ Execution Boundary
→ Receipts / Proof
→ Persona / Identity Filter
```

This stack is documented in [`docs/brain/NOVA_BRAIN_RUNTIME_ARCHITECTURE.md`](brain/NOVA_BRAIN_RUNTIME_ARCHITECTURE.md).

## EnvironmentRequest

`nova_backend/src/brain/environment_request.py` defines the first read-only schema scaffold for Brain planning objects.

It is not live routing.

It is the structured vocabulary future Brain layers can use for environment requests, dry runs, trace events, and capability planning.

## Capability Contracts

Capability Contracts are per-capability definitions of what a capability can and cannot do.

Current status: schema plus a static catalog exists. Runtime routing and the Governor do not yet use live contract lookup.

A contract should define:

```text
capability_id
name
environment
authority_tier
can
cannot
required_setup
confirmation_required
expected_receipts
fallbacks
known_failure_modes
```

Priority contracts:

- Cap 16 — governed web search
- Cap 64 — send email draft
- Cap 65 — Shopify intelligence report
- Cap 63 — OpenClaw execute

Capability Contracts should make Nova's Brain smarter without widening authority.

## Dry Run / Plan Preview

Dry Run / Plan Preview is planned, not currently live as a full API.

A dry run should show:

```text
planned steps
environments to enter
capabilities involved
confirmation points
expected receipts
fallback ladder
what Nova will not do
```

A dry run is non-executing.

It lets the user inspect a plan before the Governor is asked to authorize any action.

## Brain Trace

Brain Trace is planned operational metadata, not hidden chain-of-thought.

A future trace should show:

```text
task received
clarification checked
environment need detected
capability contract consulted
dry run generated
governor decision
execution result
receipt created
fallback used if needed
```

The purpose is inspectability, not exposing private reasoning.

## Memory Boundary

Memory can improve understanding.

Memory cannot authorize action.

A remembered preference does not give Nova permission to send, buy, publish, delete, edit, or trigger external systems.

Governed actions still require capability checks, confirmation when needed, and receipts.

## OpenClaw Boundary

OpenClaw is an environment, not the Brain.

Nova may eventually plan for an isolated OpenClaw browser environment, but execution still requires the governed OpenClaw capability path.

Personal browser sessions are higher-risk environments and must remain distinct from isolated browser automation.

## Detailed Specs

Use these files for implementation guidance:

- [`docs/brain/README.md`](brain/README.md)
- [`docs/brain/NOVA_BRAIN_MODEL.md`](brain/NOVA_BRAIN_MODEL.md)
- [`docs/brain/NOVA_BRAIN_RUNTIME_ARCHITECTURE.md`](brain/NOVA_BRAIN_RUNTIME_ARCHITECTURE.md)
- [`docs/brain/TASK_ENVIRONMENT_ROUTER.md`](brain/TASK_ENVIRONMENT_ROUTER.md)
- [`docs/brain/ENVIRONMENT_CATALOG.md`](brain/ENVIRONMENT_CATALOG.md)
- [`docs/brain/AUTHORITY_PLANE.md`](brain/AUTHORITY_PLANE.md)
- [`docs/brain/BRAIN_TRACE_UI_SPEC.md`](brain/BRAIN_TRACE_UI_SPEC.md)
- [`docs/brain/MEMORY_LAYERS.md`](brain/MEMORY_LAYERS.md)
- [`docs/brain/PROJECT_CONTEXTS.md`](brain/PROJECT_CONTEXTS.md)
- [`docs/brain/OPENCLAW_ENVIRONMENT_MODEL.md`](brain/OPENCLAW_ENVIRONMENT_MODEL.md)
- [`docs/brain/IMPLEMENTATION_ROADMAP.md`](brain/IMPLEMENTATION_ROADMAP.md)

## Current Priority

Cap 16 search reliability remains the active P1 blocker.

The Brain can clarify and prepare structure, but current-evidence tasks still depend on a reliable governed search lane.

Best next implementation order:

```text
1. Fix Cap 16 search reliability.
2. Add live/static Capability Contracts.
3. Add Context Assembler and Intention Parser scaffolds.
4. Add Search Synthesis for evidence handling.
5. Add Sandbox Boundary Enforcer.
6. Implement read-only Dry Run / Plan Preview.
7. Add Brain Trace metadata/UI.
8. Add OpenClaw environment planning.
9. Expand project contexts and suggestion buffer.
```

## Final Framing

Nova's Brain exists to make Nova more intelligent before action.

It should help Nova understand the task, identify the environment, state the authority boundary, prepare the plan, and show the expected proof.

It should not turn reasoning into permission.

```text
Let intelligence reason.
Let the Governor authorize.
Let receipts prove.
```
