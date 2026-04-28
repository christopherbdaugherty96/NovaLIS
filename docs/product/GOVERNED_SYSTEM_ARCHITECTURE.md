# Governed System Architecture

This document explains Nova in product language.

## Short Version

Nova is not designed as:

```text
User -> AI -> Action
```

Nova is designed as:

```text
User -> Intelligence -> Governance -> Execution -> Trust Output
```

That middle layer is the point of the project.

## Layer 1: Intelligence

The model can interpret requests, summarize information, classify intent, draft content, and help the user think.

Intelligence can expand usefulness.
It should not automatically expand authority.

## Layer 2: Governance

Before real actions run, requests should pass through governed controls such as:

- capability allowlists
n- confirmation requirements
- policy checks
- network mediation
- execution limits
- logging / ledger rules

## Layer 3: Execution

Only approved capabilities should execute. Examples may include:

- local search
- read-oriented snapshots
- bounded device controls
- draft creation
- governed connectors

## Layer 4: Trust Output

Users should not have to guess what happened.
A mature governed system should show:

- detected intent
n- chosen capability
- whether confirmation was required
- what was blocked or allowed
- result summary
- receipt / history row

## Why This Matters

Many AI systems compete on raw autonomy.
Nova is exploring a different tradeoff:

More visible control, less hidden authority.

## Current Reality

Some backend trust surfaces and ledger data already exist.
The full Trust Review Card UI remains a priority gap.

Use generated runtime docs for exact live implementation truth.