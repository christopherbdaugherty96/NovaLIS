# Brain Mode Proof

Status: **PASS** — Stage 5 brain mode contracts and trace implemented and proven, 2026-05-02.

## Runtime Claim

Brain mode contracts and BrainTrace are implemented as non-authorizing, read-only
planning vocabulary.

They do not:

- execute any action
- authorize any capability
- call an LLM
- mutate session state
- expose private LLM reasoning

## Seven Registered Modes

| Mode | may_mutate_repo | requires_context | may_produce_code |
|---|---|---|---|
| `brainstorm` | False | False | False |
| `repo_review` | False | **True** | False |
| `implementation` | **True** | **True** | **True** |
| `merge` | **True** | **True** | False |
| `planning` | False | False | False |
| `action_review` | False | **True** | False |
| `casual` | False | False | False |
| `unknown` | False | False | False |

## Four Required Invariants

**1. Brainstorm mode never mutates repo**

- `ModeContract.may_mutate_repo = False` for brainstorm
- `cannot` list includes write/modify files, commit, push, authorize capabilities
- brainstorm output explicitly cannot be treated as a confirmed plan
- Only `implementation` and `merge` have `may_mutate_repo=True` — verified across all modes

**2. Repo-review mode requires context before recommending**

- `ModeContract.requires_context_before_recommending = True` for repo_review
- `cannot` list includes "recommend changes without first reading current state"
- Cannot treat prior session context as current repo truth without verifying
- Also true for: action_review, implementation, merge

**3. Implementation mode stays focused (no scope creep)**

- `cannot` list includes expanding scope without explicit user approval
- `cannot` list includes merging PRs or pushing to main unilaterally
- `cannot` list includes features, refactors, or abstractions beyond the stated task
- merge mode: cannot force-push main, cannot bypass review hooks

**4. BrainTrace never exposes private reasoning or authorizes action**

- `execution_performed=False` enforced in `__post_init__` via `object.__setattr__`
- `authorization_granted=False` enforced in `__post_init__` via `object.__setattr__`
- `private_reasoning_exposed=False` enforced in `__post_init__` via `object.__setattr__`
- All three fields cannot be overridden by callers (frozen dataclass + `__post_init__`)
- Trace records: mode, context_sources (authority labels), decision_notes (structural), warnings
- Trace does NOT record: LLM prompt text, chain-of-thought, internal reasoning

## Mode Classification

`classify_mode(query: str) -> ModeClassification` — lightweight regex, no LLM call.

- Brainstorm signals: "brainstorm", "what if", "ideas for", "explore", "alternatives"
- Repo-review signals: "review", "audit", "check", "explain the code"
- Implementation signals: "implement", "build", "fix", "refactor", "create"
- Merge signals: "merge", "pull request", "PR #N", "ready to merge"
- Planning signals: "plan", "roadmap", "design", "spec", "how should we"
- Action-review signals: "should I run/push/delete", "is it safe to", "blast radius"
- Casual signals: exact match on "hi", "thanks", "ok", etc.
- Unknown: no pattern matched, confidence = 0.0

## BrainTrace Fields

```
trace_id: str              — unique "BT-XXXXXXXX" identifier
mode: BrainMode            — mode active when trace was composed
composed_at: str           — ISO UTC timestamp
context_sources: tuple     — authority labels from ContextPack items used
decision_notes: tuple      — structural decisions (scope, approach, constraints)
warnings: tuple            — structural concerns about the turn
execution_performed: False — enforced, not settable
authorization_granted: False — enforced, not settable
private_reasoning_exposed: False — enforced, not settable
```

## Validation

Commands run on `brain-mode-v1`:

```text
python -m py_compile nova_backend/src/brain/brain_mode.py
python -m py_compile nova_backend/tests/brain/test_brain_mode.py
python -m pytest nova_backend/tests/brain/test_brain_mode.py -q
python -m pytest nova_backend/tests/brain/ -q
python scripts/check_runtime_doc_drift.py
git diff --check
```

Results:

```text
compile check (brain_mode.py):      PASS
compile check (test_brain_mode.py): PASS
brain mode suite:                   PASS  79 passed  (original proof run)
full brain suite:                   PASS  219 passed (original proof run)

Post-merge additions (second pass + Stage 6 fixes, 2026-05-03):
brain mode suite:                   PASS  87 passed
full brain suite:                   PASS  231 passed
runtime doc drift:                  PASS
git diff --check:                   PASS  clean
```

## Boundary

This proof does not claim:

- brain mode surfaced per-turn in the UI (classification runs; not yet visible to the user)

Stage 6 update (2026-05-03): classify_mode() and compose_brain_trace() are now wired into
general_chat_runtime.py. A BrainTrace is recorded in session_state["last_brain_trace"] on
every general-chat turn. Brain mode does not gate or affect routing — trace only.
- Routine surfaces (Stage 6)
- BrainTrace stored persistently or surfaced in the UI (Stage 6)
