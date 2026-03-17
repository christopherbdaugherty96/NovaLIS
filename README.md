# NOVA
Nova is Governed personal agent over contained intelligence.
It is built to help with:
- research and explanation
- daily information snapshots
- screen and file understanding
- ongoing project continuity
- explicit governed memory
- bounded local computer help

Nova is not meant to be a hidden autonomous agent.
Its core principle is simple:

`Intelligence may expand. Authority may not expand without explicit unlock.`

## What Nova Feels Like

In everyday use, Nova is meant to feel like:
- a calm intelligence layer on your computer
- a system that can explain what you are looking at
- a system that can help you continue real work
- a system that can preserve important context without silent persistence

Examples of the kind of help Nova is designed to provide:
- explain a page, error, chart, or screen
- summarize current news and go deeper on a selected story
- show weather, calendar, and system summaries
- continue a project thread and surface blockers or next steps
- save an important decision into governed memory

## Read This First

If you want the plain-language explanation of the project, start here:

- `docs/reference/HUMAN_GUIDES/README.md`

That guide set explains:
- what Nova is
- how Nova works
- what Nova can do
- how voice, screen, context, continuity, and memory fit together
- what is live today vs what is still planned

## Runtime Authority

For all runtime behavior, capability status, and execution authority truth, see:

`docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Use these alongside it:
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

If any explanatory or historical document conflicts with runtime truth, `docs/current_runtime/CURRENT_RUNTIME_STATE.md` is authoritative.

## Documentation Map

Nova's docs are intentionally separated into different roles:

- Human guides:
  - `docs/reference/HUMAN_GUIDES/`
  - plain-language explanation for people

- Runtime truth:
  - `docs/current_runtime/`
  - generated and runtime-aligned operational truth

- Proof packets:
  - `docs/PROOFS/`
  - evidence for what has been implemented and verified

- Design docs:
  - `docs/design/`
  - design intent, future plans, and phase concepts

- Canonical governance:
  - `docs/canonical/`
  - constitutional and governance source material

## High-Level Project State

At a high level, Nova now has:
- active governed execution
- active cognitive/reporting systems
- active perception and screen explanation
- active project continuity surfaces
- active governed memory slices

That means Nova is already more than a chat interface.
It is becoming a workspace for understanding information, continuing work, and preserving important context under user control.

## Repository Orientation

Main surfaces:
- `nova_backend/src/`
- `nova_backend/tests/`
- `nova_backend/static/`
- `Nova-Frontend-Dashboard/`
- `docs/`

If you are reviewing or onboarding, a good order is:
1. `docs/reference/HUMAN_GUIDES/README.md`
2. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
3. `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
4. `nova_backend/src/brain_server.py`
5. `nova_backend/src/governor/`

## Safety Posture

Nova is designed around a few non-negotiable ideas:
- no hidden autonomy
- no background execution loops
- no silent authority expansion
- no direct execution from cognitive reasoning
- explicit user action for persistence and real-world effects

Nova is strongest when it is clear, inspectable, and helpful.
