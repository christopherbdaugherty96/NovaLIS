# Issue #214 — Deterministic Continuity Investigation

Date: 2026-05-23
Branch: `investigate/issue-214-deterministic-continuity`

---

## CURRENT TRUTH

The multi-turn context simulation (22/36, 61.1%) breaks down as:

```text
LLM/hardware-bound failures:    10  (Ollama throughput)
Ambient clarification design:    2  (context-gate edge case)
External dependency:             2  (token budget exhaustion)
Preamble routing:                0  (listed as 1 in issue, actually 0 isolated — the preamble
                                     failure in the simulation was Zara T4 which also hit LLM
                                     fallback, but the preamble stripping gap is independently
                                     confirmed below)
```

None of the 14 simulation failures are pure deterministic
routing bugs. However, **preamble-tolerant routing is a confirmed
deterministic gap** that silently drops users into LLM fallback
instead of deterministic handlers.

---

## REPRODUCTION CASES

### Area 1: Preamble-tolerant routing

All 15 tested preamble variants × 4 deterministic governor
targets = 60/60 broken (100% failure rate):

```text
Preambles tested:
  "also, "  "also "  "by the way, "  "by the way "  "anyway, "
  "anyway "  "oh and "  "one more thing, "  "and also "  "plus "
  "oh, "  "hey, "  "so, "  "ok so "  "alright, "

Governor targets tested:
  "what is the weather"           → cap 55 (works bare, broken with preamble)
  "latest news"                   → cap 56 (works bare, broken with preamble)
  "search for AI news"            → cap 16 (works bare, broken with preamble)
  "open my downloads folder"      → cap 22 (works bare, broken with preamble)

Session-layer targets also broken:
  "what can you do"               → CAPABILITY_HELP (broken with preamble)
  "what time is it"               → TIME_QUERY (broken with preamble)
```

Root cause: `InputNormalizer.POLITE_PREFIX_RE` strips polite
prefixes ("hey nova", "can you", "please") but does not strip
conversational preambles ("also,", "by the way,", "anyway,").

Fix location: `src/conversation/response_style_router.py` line
153, `POLITE_PREFIX_RE`.

### Area 2: Post-clarification ambient follow-up

Simulation failures (Ravi T2/T3): after clarification sets
`last_response`, subsequent ambiguous inputs ("what went wrong?",
"i'm confused") bypass the ambient clarification guard and fall
through to LLM.

Analysis: **this is correct behavior, not a bug.**

The context guard (`if not last_response`) exists to avoid
re-firing clarification when the user has prior context. With
`last_response` set, "what went wrong?" should be interpreted
as a follow-up to the prior response, not a new context-free
confusion phrase. The failure is that the LLM cannot produce
a useful response — not that the routing is wrong.

PR #223 confirmed this behavior with 11 dedicated tests in
`TestAmbientContextGuard`.

---

## FIXABLE DETERMINISTIC CASES

```text
1. Preamble-tolerant routing — YES, fixable
   Location: InputNormalizer.POLITE_PREFIX_RE
   Scope: add conversational preamble patterns
   Risk: low (additive regex change, existing strip loop handles it)
   Impact: prevents silent fallthrough to LLM for preamble + command
```

---

## LLM/HARDWARE-BOUND CASES

```text
1. General-chat LLM fallback (10 failures) — NOT fixable without
   better hardware or model. Same bottleneck as reliability cycle.

2. Post-clarification follow-up (2 failures) — routing is correct,
   LLM cannot produce response. NOT a deterministic fix target.

3. External token budget (2 failures) — infrastructure state,
   not code defect.
```

---

## PATCH RECOMMENDATION

```text
Create a small follow-up PR:
  fix/preamble-tolerant-routing

Scope:
  - Add conversational preamble patterns to POLITE_PREFIX_RE
  - Add targeted routing tests for preamble variants
  - No GovernorMediator changes
  - No session handler changes
  - No capability changes

Patterns to add:
  also[, ]+
  by the way[, ]+
  anyway[, ]+
  oh and[, ]+
  one more thing[, ]+
  and also[, ]+
  plus[, ]+
  oh[, ]+
  so[, ]+
  ok so[, ]+
  alright[, ]+
```

---

## DO-NOT-TOUCH LIST

```text
- GovernorMediator routing logic
- ExecuteBoundary
- capability_locks.json
- OpenClaw
- session handler ambient clarification gate
- LLM/Ollama configuration
- Memory writes
- Generated runtime docs
- Scheduler/autonomy
```

---

## ISSUE #214 DISPOSITION

After the preamble routing fix:

```text
Deterministic continuity gaps: CLOSED (preamble routing fixed)
LLM-dependent continuity:     OPEN (hardware/model backlog)
Ambient clarification design:  CLOSED (correct behavior, PR #223 tested)
External dependency:           CLOSED (infrastructure, not code)
```

Recommendation: leave #214 open as hardware/model backlog with
a comment noting the deterministic fix. Do not close until LLM
throughput improves enough to address the remaining 10 failures.
