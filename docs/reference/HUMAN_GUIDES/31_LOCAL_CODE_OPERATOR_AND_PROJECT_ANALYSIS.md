# Local Code Operator And Project Analysis
Updated: 2026-04-13

## Purpose
This guide explains the next coding-focused direction for Nova in plain language.

The short version is:
- Nova is moving toward a stronger project-review and code-change workflow
- it should do that through OpenClaw and local Gemma
- it should stay governed and local-first

## What People Usually Want
When people ask for a stronger coding mode, they usually mean:
- summarize this project
- tell me what it does
- find the biggest gaps
- recommend the safest improvements
- make the changes for me

That is a reasonable goal.

But the safe way to build it is not:
- "let the model change anything in the repo whenever it wants"

The safe way is:
- inspect first
- propose second
- apply only with approval
- verify after

## The Mental Model
Think of the future coding workflow like this:
- Nova is still the one you talk to
- OpenClaw is the worker lane underneath
- Gemma is the default local reasoning brain

That means:
- Nova stays calm and user-facing
- OpenClaw does the bounded work
- Gemma handles the everyday reasoning locally when possible

## What Exists Already
Nova already has a few useful local project features:
- repo summary
- project overview
- local architecture report
- structure map

Those are helpful, but they do not yet feel like one unified coding operator workflow.

## What Is Being Added First
The first step is a read-only Agent page workflow for project analysis.

That first step should let Nova:
- inspect the current workspace
- summarize what the project is
- point out the main surfaces
- recommend the next safest steps

Important truth:
- this first step is read-only
- it is not code writing yet
- it is not silent automation

## Why Read-Only Comes First
This order matters because it prevents a lot of regressions.

If Nova can understand a project well first, then later write steps become:
- clearer
- easier to review
- easier to stop
- less likely to break things

## What Comes After That
The next layers should be:
1. patch proposal
2. approval-gated apply
3. verify and repair

That means the future coding flow should eventually become:
- understand
- propose
- approve
- apply
- verify

## Local-First Cost Model
The intended model is:
- local Gemma first
- deterministic local fallback if needed
- optional cloud reasoning only if explicitly turned on later

So the goal is not "no limits by magic."

The real goal is:
- no required cloud bill for everyday project analysis and small coding help
- metered cloud usage only when explicitly enabled and actually worth it

## Best Honest Description
Nova is not yet a full autonomous coding agent.

The next strong useful step is:
- a governed local code operator that starts with read-only project analysis

That is the right foundation for later patching work.
