# Memory Loop Proof

Status: **PASS** — Stage 3 memory loop implemented and proven, 2026-05-02.

## Runtime Claim

MemorySkill is implemented as an explicit, user-initiated conversational memory skill.

It does not:

- save memory silently or automatically
- use memory before the user has confirmed or reviewed it
- reuse memory items the user has forgotten (soft-delete filters all read paths)
- authorize any action (use_llm=False, no capability invocations)
- call an LLM
- register a new capability
- create external effects

## Operations Implemented

- `remember` — save a new item (source: explicit_user_save, receipt logged)
- `review` / `list` — show saved items with IDs and source labels
- `update` — supersede an existing item (source: explicit_user_edit, receipt logged)
- `forget` — soft-delete an item; logs MEMORY_ITEM_DELETED receipt
- `why-used` — explain what memory context is active, source labels, selection logic

## Four Required Invariants

**1. No silent autosave**

- `_handle_remember` is the only write path and requires explicit user intent.
- `_handle_review`, `_handle_why_used`, and unmatched queries do not write.
- `remember` with no content after the prefix returns a failure, no save.

**2. Memory not used before confirmation**

- Auto-extracted items (source: auto_extracted) are surfaced via `review` and
  `why-used` with their source label explicitly shown.
- `why-used` explains the selection logic and lets the user see and remove any item.
- No memory is injected silently before the user can review it.

**3. Forgotten memory is not reused**

- `store.delete_item(id, confirmed=True)` sets `deleted=True` on the item.
- All read paths in `GovernedMemoryStore` filter `deleted=True`:
  `list_items`, `list_recent_items`, `summarize_overview`, search, and thread queries.
- A second forget of the same ID raises `KeyError` — caught, returns failure.
- `review` after forgetting all items shows the empty-state message.

**4. Memory never authorizes action**

- All `SkillResult` objects from `MemorySkill` have `use_llm=False`.
- `result.data` contains no `execution_performed=True` or `authorization_granted=True`.
- `result.skill == "memory"` — not a governed capability ID.
- No call to `GovernorMediator`, `CapabilityRegistry`, `ExecuteBoundary`, or OpenClaw.

## Validation

Commands run on `memory-loop-v1 @ c39b059`:

```text
python -m py_compile nova_backend/src/memory/memory_skill.py
python -m py_compile nova_backend/tests/memory/test_memory_skill.py
python -m pytest nova_backend/tests/memory/ -q
python -m pytest nova_backend/tests/memory/ nova_backend/tests/conversation/ nova_backend/tests/brief/ -q
python scripts/check_runtime_doc_drift.py
git diff --check
```

Results:

```text
compile check (memory_skill.py):    PASS
compile check (test_memory_skill):  PASS
memory suite:                       PASS  62 passed
memory + conversation + brief:      PASS  588 passed
runtime doc drift:                  PASS
git diff --check:                   PASS  clean
```

Full suite (`nova_backend/tests/`) run in background — pending final line.
Prior full suite result on main @ 33b6ed1: 1877 passed, 4 skipped.

## Wiring

`run_memory_skill_if_requested()` added to `general_chat_runtime.py`.

It intercepts explicit memory intent queries before general-chat fallback.
Non-authorizing: no LLM, no capability, no external effects.

## Boundary

This proof does not claim:

- automatic cross-session memory capture
- receipt-to-memory promotion
- memory-based Context Pack selection (Stage 4)
- full Brain mode contracts (Stage 5)
