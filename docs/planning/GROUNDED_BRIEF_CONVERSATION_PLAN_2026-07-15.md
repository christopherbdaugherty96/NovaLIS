# Grounded Brief Conversation Plan

Date: 2026-07-15

Status: active plan. Slice 0 landed in PR #307; Slices 1-3 remain unstarted.
No implementation beyond the named slice is authorized by this document.

Current shipped state:

- Main: `842ae9ee` after PR #307.
- Slice 0 complete:
  - `compare story 1 and story 2` reaches the governed Cap 50 compare path.
  - `news_synthesis_ready.message` is concise; the full completed brief is preserved in
    `brief_report` / widget data instead of being dumped into chat.
  - Remaining validation: Morning 5's strange local-model greeting may have come through a separate
    advisory path rather than the backend `news_synthesis_ready` payload. Slice 0 corrected the
    known backend message contract; a post-merge live check is still required to confirm the
    unrelated greeting no longer appears.
- Next safe slice, if explicitly approved: Slice 1 (deterministic routing + rendered-brief fact
  unification + active-surface/stable-story identity mapping, no model, no contract change).

## Problem

Morning 5 showed async synthesis made the brief *content* useful, but the bottleneck moved to
**conversing about the brief**. Every follow-up over the brief is weak:

- `what matters most from this brief?` / `is this brief complete or partial?` →
  [`_answer_awareness_followup`, brief_followup_grounding.py:695](../../nova_backend/src/conversation/brief_followup_grounding.py)
  returns a **deterministic facts-dump** + a canned "I should not add facts" disclaimer. It never
  reads the question and never answers. Confirmed: zero model involvement in this layer.
- `show me global security news` / `compare story 1 and story 2` → *miss* the grounded path and fall
  to advisory, which hallucinates (a fabricated aggregator link; a chatty deflection).
- Follow-up facts come from the raw loaded headline cache (`_news_lines`), not the rendered Cap 50
  clusters, so they can disagree with the brief on screen (Jay Clayton vs. US–Iran airstrikes).
- Numeric story commands can resolve against the wrong active surface: after a two-story Global
  News/Security category summary, `track story 2` resolved to `Technology` from the older
  intelligence brief instead of story 2 from the active category result.
- The same response can show conflicting confidence labels (`Medium-Low` in the brief body vs.
  `Standard` in the message trust strip). That is a presentation/trust defect, not a generation
  problem.

Root cause is plumbing, not model: the grounded layer is an anti-hallucination *guardrail* (echo
only loaded facts) that is too safe to be useful — it cannot answer because it never tries.

## The contract change (why this is plan-first)

Today's contract: **echo only sourced facts.** This lane changes it to: **generate an answer
constrained by sourced facts.** That safety boundary is the whole reason to write it down before
code — done wrong, it reopens the hallucination door this guardrail was built to close.

## Goal

Let Nova answer natural follow-ups *about the current brief*, grounded strictly in the rendered
brief facts, fast, without hallucinating and without dumping raw facts.

## Non-Goals

- No general web search broadening; no new news providers.
- No new execution authority, external writes, or paid provider.
- No autonomous work.
- Do not let the model introduce facts beyond the supplied brief facts.
- Do not spend the model-gate up front — earn it only if the interactive probe fails.

## Design

### 1. Unified fact source
Follow-ups must read the **rendered Cap 50 `brief_clusters`** (stored in
`session_state["last_brief_clusters"]`, already populated at
[session_handler.py:3854](../../nova_backend/src/websocket/session_handler.py)), NOT the raw
headline cache. One source of truth = the brief on screen. This alone fixes the stale/inconsistent
follow-up facts.

### 1a. Active surface and story-map contract
Slice 1 must define the current news surface before relying on numeric story references. The
surface contract should include:

- `surface_type`: main brief, category result, search result, tracking view, or other governed news
  surface.
- `surface_id` / version: a stable identifier that changes atomically when the visible story
  collection changes.
- Stable story identities for every rendered item.
- A versioned `index_to_story` map for the currently active surface.
- Replacement rules for synthesis updates: when async synthesis updates a brief in place, the story
  identities should remain stable if the collection is the same; if the collection changes, the
  surface version must change.

Commands like `track story 2`, `compare story 1 and story 2`, and `summarize story 1` must resolve
against the active surface/version, not whichever broad story list was last written. If the active
surface is ambiguous, Nova should clarify rather than silently using an older story collection.

### 2. Routing scope
Extend `is_discussion_shaped_brief_followup`
([brief_followup_grounding.py:111](../../nova_backend/src/conversation/brief_followup_grounding.py))
to catch the phrasings Morning 5 missed, routing them to the grounded path instead of advisory:

- `what matters most` / `what stands out`
- `what should I watch` / `keep an eye on later today`
- `is this (brief) complete / partial / done`
- `show me <category> news` (e.g. global security) — must reach governed news/category, never advisory
- compare phrasing (see Slice 0 regex fix)

Guardrail: only route to grounded generation when a brief is actually loaded; otherwise the existing
paths apply. Never silently send a brief follow-up to freeform advisory.

### 3. Answer mode (the constrained-generation contract)
The model may synthesize an answer **only from the supplied brief facts**:

- Prompt carries the rendered `brief_clusters` (title/summary/implication/sources) as the sole
  allowed facts.
- The model answers the user's actual question over those facts.
- Unsupported gaps are stated explicitly ("The loaded brief does not cover X"), never invented.
- Output is labeled as inference where it connects facts, consistent with the trust-class posture.
- No external fact addition, no fabricated links, no web fetch.

### 4. Latency budget
Interactive, **separate from async synthesis**. Follow-ups need an answer in a couple of seconds on
CPU, not 45s. The proposed 4–6s budget is a benchmarking hypothesis, not an implementation contract.
Before Slice 2 fixes the cap, benchmark the actual constrained prompt on the current CPU-only setup;
otherwise deterministic fallback may trigger almost every time and mask the interactive-model probe.

### 5. Fallback
If the model is slow or times out, return a **concise deterministic answer** (e.g. a one-line "top
item" derived from the brief), NOT the current raw facts-dump. Honest, short, useful — never a wall
of facts and never a fabricated answer.

## Slices

### Slice 0 — cheap correctness fixes (no contract change) — COMPLETE
- **Compare regex**: `compare story 1 and story 2` now parses alongside the existing
  `compare story 1 and 2` / `compare 1 and 2` forms. The headline compare path is preserved.
- **`news_synthesis_ready` copy**: the chat-facing `message` is now a concise announcement, while
  the full brief report remains available separately for the widget. The frontend keeps using the
  structured widget payload for the rendered brief.
- **Validation still needed**: Slice 0 corrected the known backend message contract, but Morning 5's
  local-model greeting had a usage strip and may have come through another advisory path. Post-merge
  live validation should confirm the strange greeting no longer appears.
- Landed in PR #307 at `842ae9ee`.

### Slice 1 — unified fact source + routing (deterministic, no model yet)
- Point brief follow-ups at `last_brief_clusters`.
- Add the active-surface/story-map contract (surface type, surface version, stable story identities,
  active `index_to_story` map, and atomic replacement rules).
- Extend routing (§2) so the missed phrasings reach the grounded path.
- Keep answers deterministic for now (improved, question-aware facts selection — still no fabrication).
- Exit: `show me global security news` no longer hits advisory; follow-up facts match the rendered
  brief; numeric story commands resolve against the active visible surface; no hallucinated links.

### Slice 2 — constrained grounded generation
- Add the grounded-answer prompt (§3) with the interactive budget (§4) and deterministic fallback (§5).
- Exit: `what matters most?` returns an actual answer grounded in the brief; unsupported gaps stated;
  no invented facts; falls back cleanly under the latency cap.

### Slice 3 — quality/latency gate (the interactive-model probe)
- Live: judge whether `gemma2:2b` answers grounded follow-ups *well and fast* interactively.
- This is distinct from the synthesis probe (which had 45s). Async proved the model synthesizes well
  given time; this proves — or disproves — that it converses well *fast*.
- If it is too slow or too weak here, THAT is the first earned evidence for a narrow
  interactive-model-gate. Earn it after the plumbing is right; do not assume it.

## Tests

- Routing: each target phrasing routes to grounded, not advisory (incl. `show me <category> news`).
- Fact source: follow-up facts equal the rendered `brief_clusters`, not the raw headline cache.
- Grounded answer stays within facts: answer contains no entity/claim absent from supplied clusters.
- Hallucination negatives: no fabricated URLs; unsupported question → explicit "not covered."
- Fallback: model timeout → concise deterministic answer, not a facts-dump, not empty.
- Latency: benchmark the constrained prompt on the current CPU-only setup before fixing the
  interactive cap; fallback enforces the final chosen cap once measured.
- Contract: no web search, no external write, no paid budget from a brief follow-up.
- Slice 0: `compare story 1 and story 2` parses; `news_synthesis_ready` posts a concise announcement.
- Active surface: `track story 2` after a category result resolves against that active category
  surface, not an older intelligence brief.
- Confidence presentation: brief-body confidence and message trust-strip confidence do not conflict
  for the same response.

## Open Decisions

1. Interactive latency budget: proposed 4–6s only as a benchmark hypothesis. Measure the constrained
   prompt on the current CPU-only setup before making it the implementation cap.
2. Fallback shape: one-line top item vs. short 2–3 bullet deterministic summary.
3. `show me <category> news`: route to the existing news/category executor, or to grounded generation
   over the already-loaded clusters? Recommendation: existing news/category path first.
4. How strict is "within facts"? Recommendation: entities/claims must trace to supplied clusters;
   connective inference allowed but labeled.

## Recommendation

Slice 0 is landed. Next, if the owner approves more build work, land Slice 1: deterministic routing,
rendered-brief fact unification, and active-surface/stable-story identity mapping against the
rendered Cap 50 brief clusters. Keep `show me <category> news` on the existing governed
news/category path unless the owner chooses otherwise. Only then consider Slice 2's constrained
generation, behind the tests above. Slice 3 is the live interactive-model probe. Do not change the
safety boundary without the hallucination-negative tests in place.
