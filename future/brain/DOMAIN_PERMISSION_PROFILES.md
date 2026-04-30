# Domain Permission Profiles

Defines risk and permission models across domains.

---

## Core Principle

> Different domains have different risk levels and must be governed consistently.

---

## Example Profiles

### Market Sandbox

- read data: low
- paper trade: medium
- real trade: critical

### YouTubeLIS

- script planning: low
- asset generation: medium
- publishing: high

### Desktop Runs

- read page: low
- file creation: medium
- account change: high

---

## Fields

```text
DomainProfile
- domain
- action
- risk_level
- approval_required
```

---

## Status

Planning only
