# Nova — Memory Tier System Design
Status: PLANNED — not yet started
Updated: 2026-04-02

---

## Goal

Give Nova two distinct kinds of memory:

1. **Rolling memory** — accumulates across sessions, persists for a while, but automatically
   clears when it gets too large. Everyday context, conversation history, things said in passing.

2. **Permanent memory** — explicitly important things that never auto-delete. Protected from
   the rolling purge. The user decides what goes here.

---

## What Already Exists (current state)

Nova's `governed_memory_store` already has a three-tier system:

| Tier | Current meaning | Included in recall |
|---|---|---|
| `active` | Current working memory | Yes (+2 score boost) |
| `locked` | Important, protected | Yes |
| `deferred` | Archived, out of sight | No |

There is **no TTL or automatic expiry** today. Items persist until explicitly deleted.
There is **no rolling purge** — the store grows indefinitely.

The recall system (`_select_relevant_memory_context` in `brain_server.py`) loads up to 3
relevant items per query via relevance scoring. It does not distinguish between "just said
this session" vs "saved six months ago."

---

## Proposed Design

### Two Memory Classes

Map onto the existing tier system with new semantics and automatic lifecycle management:

| Class | Store Tier | Auto-purge | User label | Who manages |
|---|---|---|---|---|
| **Rolling** | `active` | Yes — when count exceeds threshold | "Session memory" | Nova manages automatically |
| **Permanent** | `locked` | Never | "Saved memories" | User explicitly promotes |

The `deferred` tier stays as-is — a manual archive bucket the user can move things to.

---

### Rolling Memory

**What it is:**
Everything Nova picks up during normal conversation — things you mention, context from
this session, follow-ups from the last few sessions, preferences stated in passing.
Nova saves these automatically as `active` tier records.

**Lifecycle:**
- Nova saves rolling entries during conversation (already partially does this)
- When the `active` tier count exceeds the rolling limit (proposed: **100 items**),
  the oldest active items are automatically purged — soft-deleted in order of `created_at` ascending,
  skipping any item that has been explicitly user-confirmed or has a high recall score
- Purge runs at session start or when a new save would push over the limit
- Items in `active` that have been recalled frequently (high score hits) are preserved longer

**User visibility:**
- "Session memory" section in the Memory panel shows recent active items
- User can see what's in rolling memory, promote any item to permanent, or manually clear any item
- Rolling memory shows a count: "42 of 100 session memories used"

**What Nova saves here automatically:**
- Topics discussed this session
- Preferences or facts the user states in passing ("I'm working on a deadline today")
- Follow-up context ("last time we talked about X")
- Anything Nova would currently save via the existing implicit memory path

---

### Permanent Memory

**What it is:**
Things that should never disappear. Explicitly important. Protected from the rolling purge.

**Lifecycle:**
- Only promoted to permanent by the user — either:
  - User says "remember this permanently" / "save this" in chat
  - User clicks "Save permanently" on any rolling memory card in the UI
  - Profile setup data (name, nickname, rules) is written here automatically as `user_identity`
- Stored as `locked` tier — already protects against casual deletion
- **Never touched by the auto-purge** — the purge only targets `active` tier
- Can only be deleted by explicit user action with a confirmation step ("Are you sure? This is a permanent memory.")

**User visibility:**
- "Saved memories" section — always visible, always loaded
- Always injected into Nova's context at session start regardless of relevance score
  (unlike rolling memory which is relevance-ranked)
- Shown with a lock indicator in the UI

**Examples of what goes here:**
- User's name, nickname, email, rules (from profile setup — written automatically)
- "I have a dog named Max"
- "My work hours are 9am–6pm"
- "I'm building a project called Nova"
- "I prefer metric units always"
- Important decisions or commitments

---

### Memory Injection at Session Start

Current behavior: `_select_relevant_memory_context()` loads 3 relevance-scored items per query.

Proposed behavior:

```
Session start:
  1. Load ALL permanent (locked) items → always injected into system context
     (these are always true, always relevant)
  2. Load top 3–5 relevant rolling (active) items per query via existing scoring
     (these are situationally relevant)

Result injected into prompt:
  [Permanent context block]   ← always present
  [Rolling context block]     ← query-relevant items only
```

This means Nova always "knows" permanent facts without needing to be reminded,
and also pulls in relevant rolling context per conversation turn.

---

### Purge Logic (Rolling Memory)

Triggered: at session start, or when a new `active` save would exceed the limit.

```
ROLLING_MEMORY_LIMIT = 100  (proposed default, configurable in settings)

Algorithm:
  1. Count active (non-deleted) items
  2. If count <= limit: no action
  3. If count > limit:
     a. Sort active items by created_at ascending (oldest first)
     b. Skip items that are: recently recalled (last 7 days), user-confirmed saves,
        or have recall_score above threshold
     c. Soft-delete oldest items until count == limit - 10
        (purge to 90, not exactly 100, to avoid purge on every new save)
  4. Log purge event to ledger (how many removed, date range of removed items)
```

The user can also manually trigger "Clear session memory" from the UI — wipes all `active` items
except any that the user has explicitly confirmed.

---

### UI — Memory Panel

A new or expanded Memory section in the dashboard showing both tiers:

```
┌──────────────────────────────────────────────────┐
│  Memory                                          │
│                                                  │
│  🔒 Saved Memories  (permanent, never delete)    │
│  ┌────────────────────────────────────────────┐  │
│  │  user_identity — Chris / "Boss" / rules    │  │
│  │  My project is called Nova                 │  │
│  │  I prefer metric units always              │  │
│  │                          [+ Add]  [Manage] │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  💬 Session Memory  (42 / 100)  [Clear all]     │
│  ┌────────────────────────────────────────────┐  │
│  │  Working on connection UI redesign  [🔒]   │  │
│  │  Mentioned deadline is Thursday     [🔒]   │  │
│  │  Asked about Brave API key          [🔒]   │  │
│  │  ...                                       │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

- `[🔒]` on a rolling item = "Promote to permanent" button
- `[+ Add]` on permanent = open a free-text field to manually save a permanent memory
- `[Clear all]` on session memory = wipe all active items (with confirmation)
- `[Manage]` on permanent = list view with delete option (with confirmation per item)
- Count indicator on session memory: "42 / 100" — user knows how full the rolling buffer is

---

## Backend Work Required

| Component | Work |
|---|---|
| `governed_memory_store.py` | Add `recall_count` and `last_recalled_at` fields to track recall frequency for purge scoring |
| `governed_memory_store.py` | Add `purge_old_active()` method implementing the purge algorithm |
| `memory_governance_executor.py` | Add `promote` action: moves `active` item to `locked` tier (permanent) |
| `brain_server.py` | Update `_select_relevant_memory_context()` to always load locked items + scored active items separately |
| `brain_server.py` | Call `purge_old_active()` at session start |
| `settings_api.py` | Expose `ROLLING_MEMORY_LIMIT` as a configurable setting |
| `memory_api.py` | New endpoint: `POST /api/memory/{id}/promote` — promote to permanent |
| `memory_api.py` | New endpoint: `DELETE /api/memory/rolling/clear` — clear all active items |

---

## Constants (proposed defaults, all configurable)

| Constant | Default | Purpose |
|---|---|---|
| `ROLLING_MEMORY_LIMIT` | 100 items | Max active items before purge triggers |
| `PURGE_TARGET` | 90 items | Purge down to this count (not exactly limit) |
| `RECALL_RECENCY_DAYS` | 7 | Items recalled within N days are spared from purge |
| `MAX_PERMANENT_ITEMS` | None (unlimited) | No cap on permanent memories |
| `PERMANENT_ALWAYS_INJECT` | True | All locked items always in session context |
| `ROLLING_RECALL_LIMIT` | 5 | Max rolling items injected per query turn |

---

## Open Questions / Things to Add

- [ ] Should Nova suggest promoting a rolling item to permanent? ("You've referenced this a lot — want to save it permanently?")
- [ ] Should there be a "importance score" the user can set on rolling items to protect them from purge without making them permanent?
- [ ] What happens to rolling memory if the user is offline / local-only — does the purge still run the same way?
- [ ] Should the rolling limit be visible and adjustable in the Settings UI?
- [ ] Should deferred items count toward the rolling limit or be excluded from the count?
- [ ] Should permanent memories have categories or tags visible in the UI (work, personal, preferences, etc.)?
- [ ] Should Nova confirm before auto-saving something to rolling memory, or always silent?

---
