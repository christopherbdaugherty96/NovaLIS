# NOVA: DEEP MEMORY (Saved → Unlock Required)
## Memory Governance Design Intent (v1.0)

**Authority:** SAVED → UNLOCK REQUIRED  
**Effective:** 2026-01-29T01:19:02+00:00

> This document preserves intended memory semantics and structures.
> It is **not** runtime truth until explicitly unlocked, implemented, and verified.

---

## Core Principle
Memory is a filing system, not a learning system.

- No inference
- No personalization drift
- No behavior adaptation
- No unsolicited suggestions driven by memory contents

## Tiers
- **Locked:** canonical truth; immutable without explicit unlock
- **Active:** working set; modifiable via governed operations
- **Deferred:** parked ideas; non-binding; can be discarded

## Access Rules
- Readable only by explicit user request or explicit reference
- Not automatically searched for “relevant context”
- Not used to infer preferences, habits, priorities, or importance
- Not allowed to influence tone

## Proposed Local Layout (Design Intent)
```
/nova_state/
├── memory/
│   ├── locked/
│   ├── active/
│   └── deferred/
├── state_machine/
│   ├── phase_state.json
│   └── blockers.json
├── audit/
│   └── events.jsonl
└── snapshots/
```

## Operations (Design Intent)
| Operation | Effect | Requires Confirmation |
|---|---|---|
| SAVE | create active item | No |
| LOCK | active → locked | No |
| DEFER | active → deferred | No |
| UNLOCK | locked → active | Yes |
| DELETE | tombstone item | Yes |
| SUPERSEDE | new locked replaces old | Yes |

## Item Schema (Design Intent)
```json
{
  "id": "MEM-YYYYMMDD-HHMMSS-XXXX",
  "title": "Short title",
  "tier": "locked|active|deferred",
  "scope": "nova_core|project|ops",
  "created_at": "2026-01-29T01:19:02+00:00",
  "updated_at": "2026-01-29T01:19:02+00:00",
  "version": 1,
  "lock": {
    "is_locked": true,
    "unlock_policy": "explicit_user_unlock_only",
    "supersedes": []
  },
  "tags": [],
  "body": "Text..."
}
```
