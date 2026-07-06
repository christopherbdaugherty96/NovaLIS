# Auralis Today — C1 Design

Status: design-only (not runtime authorised until implemented, tested, and reflected in
generated runtime truth). Governed by `docs/design/DESIGN_AUTHORITY.md`.
Roadmap: Lane C / C1 in `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`.

## Product goal (North Star, not a pass/fail test)

> Does Nova help decide the best move today for the Auralis / Lucid Creations business in
> under 30 seconds?

C1 is the first experiment answering the project's central open question: will the owner
actually open Nova every day? It is a **decision surface, not a dashboard**. If it becomes a
screen full of metrics, it has failed regardless of code quality.

## Trusted input set (FIXED before implementation)

C1 bases its recommendation on exactly these inputs and no others. "Could read" is not
"trusts." Anything not in this list is out of scope for v1.

| Input | Source | Read path |
|---|---|---|
| Order + revenue snapshot | Shopify Admin API (cap 65, read-only) | existing `shopify_connector` |
| Public vs family/proof split | Shopify order **tags** | connector extension (new) |
| WELCOME10 usage | Shopify `discountCodes` | connector extension (new) |
| Per-channel publish counts | Shopify `publications` | connector extension (new) |
| Settled decisions | GovernedMemoryStore, tier=`locked` | existing memory read |
| Owner-action queue | GovernedMemoryStore items tagged `needs_chris` / `agent_doable` / `scheduled` / `blocked` | existing memory read |
| Promotion queue (static, ordered) | GovernedMemoryStore tagged list | existing memory read |

**Explicitly NOT trusted in v1:** Google Merchant / Meta / TikTok APIs (no connector),
live catalog-drift output (lives in the Auralis repo; a bounded local-read is a later
iteration), anything requiring a write, and any LLM-invented fact. The "why this?" line and
best-move selection are deterministic, not model-generated.

## Output contract (exactly five lines)

Rendered as one `AwarenessSection` in `src/brief/awareness_brief.py`, following the existing
section pattern (bounded item tuple, `status`, `source`).

```
Auralis Today
Status:        <store live? · N products · channel status · known blocker>
Revenue:       <public sales vs family/proof proof-order · WELCOME10 uses · top-margin product>
Owner blocker: <the single needs_chris item that most gates revenue>
Best move:     <ONE action> — <why this?>
Watch:         <top scheduled/waiting item, e.g. July 9 Google review>
```

## Deterministic best-move logic

Stable across reruns with unchanged inputs (acceptance criterion 2):

```
if an owner blocker exists that gates revenue:
    best move = the smallest next step for that blocker
else:
    best move = top unblocked item of the static promotion queue
"why this?" = the one-clause reason tied to the selected item's input
```

No randomness, no model choice. Same inputs → same line.

## Degradation (acceptance criterion 4)

If a trusted input is unavailable (e.g. Shopify not reachable), C1 states so explicitly on the
affected line and **does not invent a recommendation**: e.g. `Revenue: not enough to
recommend today (Shopify unavailable).` A missing input never produces a fabricated best move.

**Input status (internal, makes the honesty rule testable).** The builder computes one of:
`inputs_complete` (all trusted inputs present) / `inputs_partial` (some present, some missing —
degrade the affected lines, still recommend from what is present) / `not_enough_trusted_inputs`
(no trusted revenue/queue signal — the best-move line becomes an explicit "not enough to
recommend today", never a fabricated action). Exposed on the section result for tests; may be
surfaced subtly in UI but is not a prominent metric.

## Memory seeds (no schema change)

Seeds map onto the existing `GovernedMemoryStore` schema (per
`docs/design/MEMORY_SYSTEM_REFERENCE.md`): decisions = items at tier `locked`; ownership
dimension = tags; promotion order = a tagged ordered list. Do **not** build on
`NovaSelfMemoryStore` (dead writes) or `quick_corrections` (no consumer).

## Acceptance criteria (all five required)

1. Within 30s of opening, the user identifies ONE recommended next action with no follow-up
   questions.
2. Deterministic: same inputs → same recommendation.
3. Includes a brief "why this?" explanation.
4. When there isn't enough information, says so explicitly — never fabricates.
5. Surface stays small; adding any line/metric requires clear justification.

## Validation protocol (after build, before deciding what is next)

Owner dogfoods for one week: open Nova each morning **before** email / Shopify / GitHub /
social. Log per day: did you follow the recommendation? was it actually highest-value? if
ignored, why? This real-usage log — not another design review — drives the next iteration.

## Not in v1

Meta/TikTok/Google connectors; product-readiness scoring engine; content CRM; OpenClaw/
Telegram delivery (that is C3, gated on token rotation + scheduler repair); Friday Risk Loop
(C4); any new page. C1 is one section in the existing Daily Brief.

## Build order (as built)

1. This design doc (fixes the trusted input set). ✓
2. `build_auralis_today_section(...)` + `auralis_today_input_status` — deterministic
   best-move + honest degradation. ✓ (built first: fully verifiable, encodes all criteria)
3. Governed-memory seed loader (`auralis_seeds.py`) — locked decisions, owner-action queue,
   promotion queue; deterministic ordering. ✓
4. Conditional wiring into `compose_awareness_brief` + session-handler on-open path. ✓
   (renders when seeds or a snapshot exist; default composition unchanged at 7 sections)
5. Connector enrichment (`shopify_auralis_enrichment.py`) — pure tested parsers for order
   split / WELCOME10 / channels. ✓ **Live GraphQL round-trip gated on Cap 65 P5
   (owner-paused): no network call added to the on-open path; the section degrades honestly
   until P5 is unpaused, at which point a thin fetch feeds `parse_enrichment`.**
6. Tests: all five acceptance criteria + determinism-across-reruns + non-authorizing shape +
   seed classification + enrichment parsing. ✓ (27 C1 tests; 225 green incl. regression)
