# Future Brain Architecture Map

This document maps how future Brain-related planning folders connect without claiming current runtime behavior.

This is planning only. Current runtime truth remains generated under `docs/current_runtime/` and current Brain documentation remains under `docs/brain/`.

---

## Core Separation

```text
Brain = planning, reasoning, context, learning summaries
Governance = permission, authority, policy, approval
Execution = bounded capability/action path
Ledger = audit and receipts
Memory = explicit inspectable records
```

The Brain may prepare and explain. It does not grant itself authority.

---

## Future Brain Flow

```text
User intent
→ Brain context assembly
→ Task / domain understanding
→ Environment request or domain plan
→ Capability / contract awareness
→ Governed plan preview
→ User approval when required
→ Governor / capability path
→ Bounded execution
→ Ledger receipt
→ Structured memory / learning record
→ Future Brain context
```

---

## Folder Relationship

```text
future/brain/
├── README.md
├── ARCHITECTURE_MAP.md
├── governed_desktop_runs/
│   └── reference to future/governed_desktop_runs/
├── market_sandbox/
│   └── reference to future/market_sandbox/
└── youtubelis/
    └── reference to future/youtubelis/
```

---

## Domain Roles

### Governed Desktop Runs

Role:

> How future Brain plans become safe desktop/browser/OpenClaw actions.

Relationship:

- Brain proposes task envelope.
- Policy evaluator checks envelope/action.
- User approves if required.
- Governor remains authority.
- Execution stops on completion, timeout, cancellation, uncertainty, or scope violation.

### Market Sandbox

Role:

> How future Brain learning works in a high-risk domain without becoming authority.

Relationship:

- Brain analyzes market data, news, paper results, and lessons.
- Learning records remain structured and reviewable.
- Strategy changes require user approval.
- Real-money action remains blocked unless separately implemented and governed.

### YouTubeLIS

Role:

> How future Brain planning could support a content-production workflow.

Relationship:

- Brain helps plan ideas, scripts, voice workflows, and asset steps.
- Governed desktop runs would be required for browser/tool execution.
- Publishing remains a separate high-risk action requiring final human approval.

---

## What Feeds The Brain

Future Brain context may include:

- approved plans
- explicit memories
- domain learning records
- completed run receipts
- user-approved rule changes
- capability contracts
- current task state
- known failure patterns

---

## What Does Not Feed Authority

These must not grant authority by themselves:

- learning records
- repeated success
- paper-trading performance
- content workflow history
- convenience
- user trust over time
- model confidence

Authority changes require explicit governance, tests, implementation, and runtime truth updates.

---

## Migration Direction

Current state:

```text
future/brain/ = umbrella/navigation layer
future/governed_desktop_runs/ = source docs
future/market_sandbox/ = source docs
future/youtubelis/ = source docs
```

Possible later state:

```text
future/brain/governed_desktop_runs/ = source docs
future/brain/market_sandbox/ = source docs
future/brain/youtubelis/ = source docs
```

Only migrate after references are checked and duplicate docs are reconciled.
