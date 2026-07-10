# docs/observation — Morning observation logs

**Status:** ACTIVE — this is the current phase's primary evidence stream.
**Authority:** observation logs are recorded evidence (facts about usage), not plans or designs.
They feed the roadmap; they do not authorize builds by themselves.

## Why this folder exists

Phase 3 is closed and engineering is frozen behind the observation gate: **at least 7 real
mornings of logged use before any new feature building.** Behavior generates the roadmap — not
specs, not reference repos, not theory. This folder is where that behavior gets recorded.

The single success metric: **did Nova eliminate at least one uncertainty before you reached for
another app?**

## Protocol

1. One file per morning: `YYYY-MM-DD.md`, copied from
   [MORNING_LOG_TEMPLATE.md](MORNING_LOG_TEMPLATE.md).
2. Fill it in **right after** using the Morning Brief, while the experience is fresh.
   Target: under 5 minutes. Short honest answers beat long polished ones.
3. **Collect before analyzing.** No trend analysis, no roadmap decisions, no builds until at
   least 7 logs exist. A single morning is an anecdote; seven are evidence.
4. Exceptions to the freeze: only critical bugs. If Nova acts without asking, or presents an
   inference as fact, that is a critical bug — log it and it may be fixed immediately.
5. After 7+ logs: analyze for repetition. A wish repeated 3+ mornings is a roadmap candidate.
   A wish appearing once is noise.

## What happens to the results

- Repeated friction/wishes → candidates for the master roadmap
  (`docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`), filtered by decision-relevance
  ("does this change what I should know, decide, or do?") and app-elimination
  ("does this remove another app from my morning?").
- Trust-class violations (inference shown as fact) → Phase-4 candidates for the
  Fact / Reasoning / Inference UI.
- Latency problems → evidence for the model-preset/budget direction.

Related: `docs/CANONICAL/00_INDEX.md` (how to read truth),
`docs/product/PRODUCT_DEFINITION.md` (identity and phases).
