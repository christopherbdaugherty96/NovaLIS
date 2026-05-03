# Context Pack Proof

Status: **PASS** — Stage 4 Context Pack implemented and proven, 2026-05-02.
Corrections applied 2026-05-02: budget_used edge case fix, test logic fix, assumption label clarification.

## Runtime Claim

ContextPack is implemented as a bounded, labeled context bridge between Memory/Search/Project
and Brain.

It does not:

- authorize any action
- treat candidate items as confirmed
- override runtime truth with memory
- silently hide conflicts or budget overruns
- call an LLM
- create external effects
- persist state

## Dataclass Invariants

- `execution_performed=False` enforced in `__post_init__` via `object.__setattr__`
- `authorization_granted=False` enforced in `__post_init__` via `object.__setattr__`
- Callers cannot override either field — frozen dataclass, `__post_init__` re-sets them

## Source and Authority Labels

| Source label | Meaning | Produced by builder? |
|---|---|---|
| `runtime_truth` | Live data from connectors / session state | Yes |
| `confirmed_memory` | Explicitly saved by user (explicit_user_save, explicit_user_edit) | Yes |
| `candidate_memory` | Auto-extracted, observed, or unknown source — not confirmed | Yes |
| `assumption` | Fallback when no source evidence available — reserved for Stage 5+ callers | No (reserved) |

| Authority label | Rank | Meaning | Produced by builder? |
|---|---|---|---|
| `runtime_truth` | 0 | Highest — live data always listed first | Yes |
| `confirmed_project_memory` | 1 | User-confirmed memory items | Yes |
| `candidate_memory` | 2 | Unconfirmed — surfaced as suggestions only | Yes |
| `assumption` | 3 | Lowest authority — reserved for Stage 5+ callers | No (reserved) |

Note: `assumption` is defined as a constant and rank entry so Stage 5+ callers that build
`ContextItem` directly (e.g. search evidence with no retrievable source) can use it.
`compose_context_pack()` does not currently produce assumption items.

## Four Required Invariants

**1. Candidate items are never treated as confirmed**

- `auto_extracted`, `observed`, and unknown sources → `AUTHORITY_CANDIDATE_MEMORY`
- `explicit_user_save` and `explicit_user_edit` → `AUTHORITY_CONFIRMED_PROJECT_MEMORY`
- `ContextPack.candidate_items` property returns only candidate-authority items
- `render_context_block()` flags candidates with "unconfirmed — treat as suggestion only"
- `why_selected` string explicitly says "treat as suggestion only" for candidates

**2. Runtime truth outranks memory**

- Items sorted by `authority_rank` — runtime truth (rank 0) always appears first
- Runtime truth items: TRUNCATED to budget, never dropped
- Memory items: DROPPED with `budget_exceeded` warning when budget exhausted
- When budget is already zero, runtime truth gets a minimum 200-char excerpt

**3. Budgets are enforced**

- `budget_chars` (default 4000) tracked with `budget_remaining` counter
- `budget_used` tracks actual chars added (independent of budget floor) — accurate even at
  `budget_chars=0` where a minimal 200-char RT excerpt makes `within_budget` correctly False
- Runtime truth items consumed first; remaining budget shared by confirmed then candidates
- `max_confirmed` (default 5): excess confirmed items emit `budget_exceeded` warning
- `max_candidate` (default 2): excess candidate items emit `budget_exceeded` warning
- `within_budget` property reports whether total content fits
- `budget_used` and `budget_remaining` reported in `to_dict()`

**4. Non-authorizing frozen dataclass**

- `execution_performed=False` always — enforced, not settable
- `authorization_granted=False` always — enforced, not settable
- Both `ContextPack` and `ContextItem` are `frozen=True` dataclasses
- No calls to Governor, GovernorMediator, ExecuteBoundary, or any capability

## Additional Behaviors Proven

**Stale detection**

- Items with `updated_at` or `created_at` older than `stale_threshold_days` (default 30)
  flagged with `is_stale=True` and `stale_reason` string
- `stale_memory` warning emitted for each stale item included
- `render_context_block()` notes stale items inline

**Conflict detection**

- Items sharing the same 40-char title prefix get a `conflicting_sources` warning
- Only fires for items actually selected — dropped items are not checked

**Warning cap**

- Raw warnings capped at `max_warnings` (default 2)
- When raw warnings exceed cap: first `max_warnings` kept, `WARN_TOO_MANY_WARNINGS`
  appended explaining how many were suppressed

**Backwards compatibility**

- `to_legacy_format()` returns `list[dict[str, str]]` matching the shape expected by
  `_select_relevant_memory_context` in brain_server.py

**Deleted item filtering**

- Memory items with `deleted=True` are filtered out defensively before classification

## Validation

Commands run on `claude/review-stage-4-context-4tbIn` (corrections applied):

```text
python -m py_compile nova_backend/src/brain/context_pack.py
python -m py_compile nova_backend/tests/brain/test_context_pack.py
python -m pytest nova_backend/tests/brain/test_context_pack.py -q
python -m pytest nova_backend/tests/brain/ -q
python scripts/check_runtime_doc_drift.py
git diff --check
```

Results:

```text
compile check (context_pack.py):        PASS
compile check (test_context_pack.py):   PASS
context pack suite:                     PASS  68 passed  (67 original + 1 new, original proof run)
full brain suite:                       PASS  140 passed (original proof run)

Post-merge additions (second pass + edge case tests, 2026-05-03):
context pack suite:                     PASS  72 passed
full brain suite:                       PASS  231 passed
runtime doc drift:                      PASS
git diff --check:                       PASS  clean
```

Note: CI jobs on the PR branch show failures for `lint-and-test`, `runtime-docs`, `governance`,
and related checks. These are pre-existing environment failures (missing fastapi/uvicorn in the
CI runner) that affect all branches and are unrelated to Stage 4 code. The brain test suite
(the subset that does not require fastapi) is 141/141 green.

## Boundary

This proof does not claim:

- context pack injection into live brain_server.py prompts (Stage 5)
- automatic context pack assembly from live memory store (Stage 5)
- brain mode contracts (Stage 5)
- routine surfaces (Stage 6)
