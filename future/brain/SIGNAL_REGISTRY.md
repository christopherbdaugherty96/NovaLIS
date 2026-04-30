# Signal Registry

Defines approved triggers that NovaLIS may respond to in a controlled way.

---

## Core Principle

> NovaLIS should not react to everything. Only approved signals should trigger behavior.

---

## Signal Types

- scheduled (time-based)
- user-requested
- file/folder changes
- external data updates
- domain-specific signals (market, workflow)

---

## Signal Definition

```text
Signal
- name
- source
- frequency
- allowed_actions
- blocked_actions
- required_approval
- risk_level
- max_runtime
```

---

## Frequency Rules

- must be explicitly defined
- must respect rate limits
- must avoid infinite loops

---

## Safety Rules

Signals must:

- be bounded
- be stoppable
- produce receipts
- respect domain permissions

---

## Anti-Patterns

- reacting to all events
- unlimited polling
- recursive triggers
- unbounded automation

---

## Status

Planning only
