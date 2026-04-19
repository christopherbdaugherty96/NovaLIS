# Nova Memory System — Complete Reference

**Status:** Verified against source code (2026-04-18)
**Audience:** Christopher Daugherty / Core development

---

## Overview

Nova has four distinct memory stores. Each serves a different purpose, operates independently, and persists separately to disk. They are not a unified system — they were built at different times and have different maturity levels.

| Store | Purpose | File | Status |
|---|---|---|---|
| `GovernedMemoryStore` | Explicit saves — "remember this" | `data/nova_state/memory/governed_memory.json` | Fully wired |
| `UserMemoryStore` | Auto-extracted user facts | `data/nova_state/memory/user_memory.json` | Fully wired |
| `NovaSelfMemoryStore` | Nova's relationship notes + topic log | `data/nova_state/memory/nova_self_memory.json` | Reads wired, writes mostly dead |
| `quick_corrections.py` | Conversation correction log | `data/nova_state/memory/quick_corrections.jsonl` | Writes only, no consumer |

---

## 1. GovernedMemoryStore

**File:** `nova_backend/src/memory/governed_memory_store.py`
**Data file:** `nova_backend/src/data/nova_state/memory/governed_memory.json`

### What It Stores

Explicit knowledge items — things Nova or the user directly told it to remember. Each item has governance metadata: a tier (active/locked/deferred), a confirmation requirement, lineage links, and tags.

### Schema (one item)

```json
{
  "id": "GM-a1b2c3d4",
  "title": "Deploy checklist for Pour Social",
  "content": "Always test the POS integration before pushing to prod.",
  "tags": ["pour-social", "ops", "checklist"],
  "thread_name": "pour-social",
  "lock": {
    "tier": "active",
    "requires_confirmation": false,
    "confirmed_by": null,
    "locked_at": null,
    "superseded_by": null
  },
  "lineage": [],
  "created_at": "2026-04-10T14:22:00Z",
  "updated_at": "2026-04-10T14:22:00Z",
  "source": "explicit"
}
```

### Tiers

- **active** — normal, injectable into prompts, searchable
- **locked** — protected; requires `confirmed=True` to delete or supersede
- **deferred** — low-priority, excluded from active retrieval unless directly queried

### Key Methods

| Method | Description |
|---|---|
| `save_item(title, content, tags, thread_name, ...)` | Create or update a governed item |
| `find_relevant_items(query, thread_name, limit)` | Token-scored search — returns items ranked by match quality |
| `list_items(thread_name, tier)` | List all items, optionally filtered |
| `lock_item(item_id)` | Escalate to locked tier |
| `defer_item(item_id)` | Move to deferred tier |
| `delete_item(item_id, confirmed)` | Remove item; locked items require `confirmed=True` |
| `supersede_item(item_id, new_item_id, confirmed)` | Mark old item as superseded by new one |
| `export_payload()` | Full export for the `/api/memory/export` endpoint |

### Search Scoring

`find_relevant_items()` uses token scoring, not semantic search:

| Match type | Points |
|---|---|
| Active thread match (thread_name == current thread) | +8 |
| Exact query string in title | +8 |
| Query token in title | +5 each |
| Query token in tags | +4 each |
| Query token in content | +2 each |
| Active tier bonus | +2 |

**Implication:** Keyword-rich titles and accurate tags matter a lot. Semantic relevance is not captured.

### How It Gets Written

Two paths:
1. **Conversation commands** — user says "remember that..." or "save this" → processed by `memory_governance_executor.py` via the capability system
2. **Memory API** (`POST /api/memory/governed`) — dashboard or direct API call

### How It Gets Read Into Conversations

`_select_relevant_memory_context()` in `brain_server.py` (lines 385–452):
- Called on every incoming message
- Fetches up to 3 items using `find_relevant_items(query, active_thread)`
- Stores results in `session_state["relevant_memory_context"]`
- Skipped for memory management commands themselves (save, list, delete, etc.)

`general_chat.py` (line 765):
- Reads `state.get("relevant_memory_context")`
- Appends each item as a `Relevant explicit memory {ID}` hint in the conversational prompt
- Limited to 3 items

**This is fully functional.**

### Atomic Writes

All writes go through `write_json_atomic()` + `shared_path_lock()`:
- Writes to a temp file first, then renames atomically
- Per-path `RLock` prevents concurrent writes
- Zero risk of partial writes corrupting the JSON file

---

## 2. UserMemoryStore

**File:** `nova_backend/src/memory/user_memory_store.py`
**Data file:** `nova_backend/src/data/nova_state/memory/user_memory.json`

### What It Stores

Facts about the user extracted from conversation or explicitly saved. Keyed by `(category, key)` — upsert on match, so the same fact is never duplicated.

### Categories (priority order for rendering)

1. `personal` — name, location, age, etc.
2. `preferences` — likes, dislikes, settings
3. `work` — job, company, role
4. `communication_style` — how the user likes to be addressed
5. `relationships` — people they mention
6. `important_dates` — anniversaries, deadlines

### Schema (one entry)

```json
{
  "id": "UM-a1b2c3d4",
  "category": "personal",
  "key": "name",
  "value": "Chris",
  "context": "User said 'my name is Chris' during onboarding",
  "created_at": "2026-04-01T10:00:00Z",
  "updated_at": "2026-04-01T10:00:00Z",
  "source": "observed",
  "confidence": 0.85
}
```

### Limits

- Max 200 entries
- When limit hit: drops oldest low-confidence `observed` entries first; `explicit` entries are protected
- Values capped at 300 chars

### Key Methods

| Method | Description |
|---|---|
| `save(category, key, value, ...)` | Upsert by (category, key) |
| `get_all(limit)` | List all entries sorted by recency |
| `get_by_category(category, limit)` | Filter by category |
| `search(query, limit)` | Token-match search across key+value+context |
| `remove(entry_id)` | Delete by ID |
| `render_context_block(max_chars)` | Compact string for prompt injection |

### How It Gets Written

**Automatic extraction** — `_extract_and_save_memories()` in `general_chat.py` (line 1595):
- Called on every successful response
- Runs regex patterns against the normalized user query
- Detects patterns like "my name is X", "I live in X", "I prefer X", "I like X"
- Saves as `source="observed"`, `confidence=0.85`

**API** — `POST /api/memory/user` saves as `source="explicit"`, `confidence=1.0`

**Memory API** — `memory_api.py` line 64 handles explicit saves from the dashboard

### How It Gets Read Into Conversations

`_build_memory_context()` in `general_chat.py` (line 368):
- Calls `render_context_block(max_chars=300)`
- Output appended to the LLM system prompt under `"What you know about the user:"`
- Present every turn

**This is fully functional.**

---

## 3. NovaSelfMemoryStore

**File:** `nova_backend/src/memory/nova_self_memory_store.py`
**Data file:** `nova_backend/src/data/nova_state/memory/nova_self_memory.json`

### What It Stores

Nova's self-knowledge about the relationship with this specific user. Three sub-stores:

| Sub-store | Cap | Purpose |
|---|---|---|
| `relationship_insights` | 20 entries | Notes like "user prefers direct answers", "user gets frustrated with caveats" |
| `session_summaries` | 10 entries | End-of-session narrative summaries |
| `topic_patterns` | 30 entries | Topics frequently discussed, with recency tracking |

### Schema

```json
{
  "schema_version": "1.0",
  "relationship_insights": [
    {
      "id": "NS-a1b2c3d4",
      "insight": "User prefers bullet points over prose",
      "source": "observed",
      "created_at": "2026-04-10T14:22:00Z",
      "updated_at": "2026-04-10T14:22:00Z"
    }
  ],
  "session_summaries": [
    {
      "id": "SS-a1b2c3d4",
      "summary": "Discussed Pour Social POS integration, decided to defer API work to next sprint.",
      "session_id": "abc123",
      "created_at": "2026-04-10T18:00:00Z"
    }
  ],
  "topic_patterns": [
    {
      "topic": "pour social",
      "count": 7,
      "last_seen": "2026-04-18T09:00:00Z"
    }
  ],
  "updated_at": "2026-04-18T09:00:00Z"
}
```

### Key Methods

#### Write methods

| Method | Description |
|---|---|
| `record_insight(insight, source)` | Save a relationship observation (deduplicates by substring match) |
| `record_session_summary(summary, session_id)` | Save end-of-session summary |
| `record_topic(topic)` | Increment topic count; creates or updates the topic entry |

#### Read methods (wired and working)

| Method | Description |
|---|---|
| `get_relationship_context(max_chars)` | Compact string of top insights for prompt injection |
| `get_recent_summaries(limit)` | Most recent session summaries |
| `get_top_topics(limit)` | Topics sorted by count descending |
| `snapshot()` | Stats for the memory dashboard |

### How It Gets Read Into Conversations

`_build_memory_context()` in `general_chat.py` (line 374):
- Calls `get_relationship_context(max_chars=150)`
- Output appended to the LLM system prompt under `"Relationship context:"`

`memory_api.py` (lines 106–112):
- Exposes insights, summaries, and topics via `GET /api/memory/nova`

### Write path — wired (2026-04-19)

All three write methods are now called in conversation flow:

**`record_topic()`** — called after every successful response in `_run_local_model()`. Takes the first 5 stopword-filtered words of the user query as the topic string. Implemented via `_record_query_topic()` in `general_chat.py`.

**`record_insight()`** — called after every successful response via `_extract_relationship_signals()` in `general_chat.py`. Runs conservative regex patterns against user messages shorter than 200 chars. Detects explicit preference/feedback signals only (length, formatting, directness, caveats, examples). Maps matches to normalized insight strings so deduplication works. One insight per query maximum.

**`record_session_summary()`** — called in the `finally` block of `session_handler.py` (WebSocket disconnect). Only fires if the session had >= 3 turns. Builds a compact text summary from `session_state`: turn count, active project thread, topic, last response excerpt.

---

## 4. quick_corrections.py

**File:** `nova_backend/src/memory/quick_corrections.py`
**Data file:** `nova_backend/src/data/nova_state/memory/quick_corrections.jsonl`

### What It Stores

Append-only log of corrections the user gave Nova mid-conversation. Each line is a JSON object:

```json
{
  "id": "QC-a1b2c3d4",
  "original": "Nova said Paris is the capital of Germany",
  "correction": "Berlin is the capital of Germany",
  "turn": 12,
  "recorded_at": "2026-04-18T10:00:00Z",
  "consumed": false
}
```

### Key Method

`record_correction(original, correction, turn)` — appends a record. Always writes `"consumed": false`.

### Consumer wired (2026-04-19)

The file now has a complete read/write/consume cycle:

- **`record_correction(content)`** — unchanged, appends with `consumed: false`
- **`load_unconsumed(limit)`** — reads entries where `consumed` is False, returns content strings
- **`mark_all_consumed()`** — rewrites the log marking all entries consumed

At session init in `session_handler.py`, `load_unconsumed(limit=5)` fetches any pending corrections, stores them in `session_state["pending_corrections"]`, then calls `mark_all_consumed()`. In `_build_conversational_prompt()` in `general_chat.py`, pending corrections are injected as `"User previously corrected Nova: ..."` hints and then cleared from session_state so they only appear on the first turn of that session.

---

## Memory Flow Diagram

```
User message arrives
        │
        ▼
brain_server.py: _select_relevant_memory_context()
  → GovernedMemoryStore.find_relevant_items(query, thread)
  → stores up to 3 items in session_state["relevant_memory_context"]
        │
        ▼
general_chat.py: _build_memory_context()
  → UserMemoryStore.render_context_block(300 chars)
  → NovaSelfMemoryStore.get_relationship_context(150 chars)
  → combined into LLM system prompt
        │
        ▼
general_chat.py: _build_conversational_prompt()
  → reads session_state["relevant_memory_context"]
  → appends governed memory items as "Relevant explicit memory" hints
        │
        ▼
LLM generates response
        │
        ▼
general_chat.py: _extract_and_save_memories(query)
  → regex match → UserMemoryStore.save() if personal info detected
        │
        ▼
general_chat.py: _record_query_topic(query)
  → NovaSelfMemoryStore.record_topic() with first 5 words of query
        │
        ▼
general_chat.py: _extract_relationship_signals(query)
  → conservative regex → NovaSelfMemoryStore.record_insight() if feedback signal detected
        │
        ▼
session end (WebSocket disconnect)
        │
        ▼
session_handler.py finally block
  → NovaSelfMemoryStore.record_session_summary() if turn_count >= 3
```

**Session start (corrections):**
```
session_handler.py: session init
  → load_unconsumed() → session_state["pending_corrections"]
  → mark_all_consumed()

Turn 1: _build_conversational_prompt()
  → injects pending_corrections as hints
  → clears session_state["pending_corrections"]
```

---

## Atomic Write Pattern

Both `GovernedMemoryStore` and `UserMemoryStore` use the same safe write pattern:

```python
# write_json_atomic in src/utils/persistent_state.py
# 1. Write to temp file (same directory)
# 2. os.replace() — atomic rename on all major OS
# 3. Per-path RLock from shared_path_lock() prevents concurrent writes
```

`NovaSelfMemoryStore` also uses `write_json_atomic()` via the same utility.

---

## What Works vs. What Doesn't

### Working
- Governed memory retrieval per turn (keyword-scored, up to 3 items)
- User memory extraction from conversation (regex patterns)
- User memory injection into system prompt
- Relationship context injection — insights now accumulate from conversation
- Session summaries written on disconnect (>= 3 turns)
- Topic patterns accumulate every turn
- Quick corrections injected at next session start, then marked consumed
- All memory dashboard API endpoints
- Atomic writes across all three stores

### Known Limitations
- Governed memory search is keyword-only — no semantic similarity
- `NovaSelfMemoryStore` dedup uses substring match (can miss near-duplicates)
- No governed memory deduplication on save (unlike `UserMemoryStore`)
- Thread snapshot/decision actions in `memory_governance_executor.py` are stubbed
- Relationship insight extraction is regex-only — won't catch signals in non-standard phrasing

---

## File Locations Summary

```
nova_backend/src/
├── memory/
│   ├── governed_memory_store.py    # GovernedMemoryStore class
│   ├── user_memory_store.py        # UserMemoryStore class
│   ├── nova_self_memory_store.py   # NovaSelfMemoryStore class
│   └── quick_corrections.py        # record/load_unconsumed/mark_all_consumed
├── api/
│   └── memory_api.py               # REST endpoints for all stores
├── skills/
│   └── general_chat.py             # _build_memory_context(), _extract_and_save_memories(),
│                                   # _record_query_topic(), _extract_relationship_signals()
└── brain_server.py                 # _select_relevant_memory_context()

nova_backend/src/data/nova_state/memory/
├── governed_memory.json            # GovernedMemoryStore persistence
├── user_memory.json                # UserMemoryStore persistence
├── nova_self_memory.json           # NovaSelfMemoryStore persistence
└── quick_corrections.jsonl         # Append-only corrections log
```
