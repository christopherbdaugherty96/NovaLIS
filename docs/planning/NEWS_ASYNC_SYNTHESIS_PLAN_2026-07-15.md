# News Async Synthesis Plan

Date: 2026-07-15

Status: **IMPLEMENTED. Slices 1 and 2 shipped.** No implementation beyond the named slices is
authorized by this document.

Current shipped state:

- Slice 1 (cache data model + read-through) — SHIPPED, PR #305 (main `e1236933`): `NewsSynthesisCache`
  with volatile-text/tracking-URL-normalized cluster fingerprints, atomic writes, fresh-hit skips
  the LLM, miss keeps the honest placeholder path, opportunistic put on successful synchronous
  synthesis.
- Slice 2 (user-triggered async fill) — SHIPPED, PR #306 (main `923e306c`): single-worker fill
  queue, foreground-model pause guard, 30m fresh / 2h stale, `news_synthesis_ready` push (widget
  refresh always, chat post gated on no active turn). Live quality gate: `gemma2:2b` produced usable
  grounded synthesis for 2/3 clusters given 45s — **model-gate probe negative, gate stays parked.**
- Slice 3 (freshness disclosure) — largely already landed as Pending/Stale/Partial states +
  `synthesized_at`/`model_label`; only a tightening pass remains if the presentation is unclear.

The original draft text is retained below for the design record.

## Problem

Morning 4 showed that the daily intelligence brief is now honest but not yet useful when source-grounded synthesis times out. The current request path tries to fetch sources, cluster them, and synthesize each cluster inside one interactive brief request:

- whole brief budget: `BRIEF_REQUEST_TIMEOUT_SECONDS = 8.5`
- per-cluster synthesis budget: `CLUSTER_ANALYSIS_TIMEOUT_SECONDS = 2.2`
- cluster output target: up to 380 tokens per cluster

On the current local CPU + `gemma2:2b` setup, structured source synthesis cannot reliably finish inside that budget. The confidence fix now labels placeholder clusters truthfully, but it does not produce useful synthesized briefs.

## Goal

Make the daily news brief useful without making the chat turn slow or spending the model-gate decision.

The target behavior:

- the interactive brief returns quickly
- source-grounded cluster synthesis is real when available
- stale or unavailable synthesis is disclosed plainly
- placeholders remain honest fallbacks, not hidden failures
- no new execution authority, external writes, paid-provider use, or autonomous background operation

## Non-Goals

- Do not raise the synchronous per-cluster timeout as the primary fix.
- Do not switch models or spend the DeepSeek/model-gate decision.
- Do not add new news providers or external write paths.
- Do not create autonomous background work that runs without an explicit user/session trigger.
- Do not claim cached synthesis is "current" unless its freshness is shown.

## Recommended Design

Use a session-scoped, read-through synthesis cache with stale-while-revalidate semantics.

The synchronous brief path should:

1. Build the current headline/source packet set exactly as it does today.
2. Compute stable cluster fingerprints from normalized cluster title + source URLs + source excerpts.
3. Look for synthesized clusters in a local cache.
4. Render cached synthesized clusters immediately when fresh enough.
5. Render honest placeholders for cache misses.
6. Queue cache-miss synthesis work for the same local process to complete after the response.
7. On the next brief request, reuse completed synthesis if the fingerprints still match.

This keeps user-facing latency bounded while allowing the local model to spend tens of seconds synthesizing in the background after an explicit news/brief request.

## First-Open Warming Decision

This is the load-bearing product decision for the lane.

The basic read-through cache improves the second request. The daily brief's highest-value moment is usually the first open of the day. If a cold cache only produces placeholders and requires the user to ask again, the architecture is honest but not useful enough.

Decision to make before Slice 2:

**Does the dashboard's automatic open-brief count as a session trigger?**

Recommended answer: yes, if the user opened the dashboard/session and Nova is already rendering the brief as part of that session. That keeps synthesis user/session-triggered rather than autonomous scheduled work.

If yes:

- the open-brief request may enqueue cache-miss synthesis
- synthesis may continue after the initial placeholder brief renders
- when synthesis completes, Nova should be able to push a `synthesis ready` update for the visible brief
- the user should not need to manually ask for the same brief again to benefit

If no:

- the lane only improves repeated requests
- the first-open Morning 4 experience remains mostly unchanged
- this should be called out as a deliberate product trade-off before implementation

First-slice recommendation: implement the cache/read-through model first, then decide whether Slice 2 includes a push update or only fills for the next request. Do not bury this as a minor implementation detail.

## Freshness Model

Each synthesized cluster should carry:

- `cluster_fingerprint`
- `source_fingerprints`
- `source_count`
- `synthesized_at`
- `source_packet_collected_at`
- `model_label`
- `summary`
- `implication`
- `sources`
- `status`: `fresh`, `stale`, `pending`, `placeholder`, or `failed`

Freshness policy:

- Fresh: fingerprint match and synthesized within a short TTL, proposed 30 minutes.
- Stale but usable: fingerprint match and within a longer TTL, proposed 4 hours, rendered with "Synthesized X min/hr ago."
- Invalid: fingerprint mismatch, no cache entry, or source packet materially changed.
- Failed: synthesis attempted and failed; retry with backoff, do not spin.

Fingerprinting is a first-class design choice. Fingerprints must be stable enough to hit the cache but strict enough not to reuse synthesis for materially different stories.

Risk: source excerpts often include volatile text such as timestamps, live-update labels, tracking fragments, and ad boilerplate. Fingerprinting raw excerpts can cause constant misses.

Recommended first-slice fingerprint:

- required: normalized title, canonical URL, source label
- optional: normalized excerpt content after boilerplate/time-marker removal, capped to stable article text
- excluded: fetch timestamp, relative time strings, ad/tracking text, live-update counters

Tests must prove both sides:

- equivalent packets with reordered sources or volatile timestamp text still hit
- materially different article text or URL changes miss

The UI/report should disclose:

- "Synthesized from source pages X minutes ago" for cached real synthesis.
- "Synthesis is still running; this cluster is a placeholder for now" for misses.
- "Cached synthesis is stale" when stale-but-usable data is shown.

## Execution Model

Start with in-process, user-triggered work only.

When a user asks for today's news or a daily intelligence brief with source reads:

- the request may enqueue synthesis jobs for cache misses
- those jobs run locally, bounded by concurrency and duration limits
- no work starts before a user-triggered news/brief request
- no external writes occur
- the cache is a local runtime artifact, not memory authority

Suggested first-slice constraints:

- one synthesis worker per process
- maximum one active news synthesis batch per session
- maximum four clusters per batch
- maximum 90 seconds per batch
- retry failed clusters no more than once per fingerprint within 15 minutes
- cancel/ignore results when process exits; persistence can come later if needed

Foreground inference wins:

- pause or skip synthesis when an interactive advisory/model turn is active
- do not start a new cluster synthesis while a foreground turn is waiting on the local model
- if the local model is busy, leave clusters as pending/placeholder rather than degrading chat responsiveness
- record this as `synthesis_status: "pending"` or `"paused"`; do not hide contention

This is necessary because async synthesis and ordinary advisory chat share the same local model. A single background worker is not enough if it competes with foreground inference.

## Cache Location

First slice: local runtime cache file under runtime state, not tracked docs.

Candidate path:

`runtime data / nova_state / news_synthesis_cache.json`

The cache should be treated as ephemeral runtime truth:

- safe to delete
- rebuilt from current headlines/source packets
- not committed
- not evidence by itself

Persistence must use atomic read/write behavior:

- write to a temp file and replace atomically
- tolerate partial/corrupt cache by ignoring it and rebuilding
- guard concurrent read/write with the existing shared path lock pattern where practical

## Rendering Contract

The existing `_render_daily_brief_v2` path can remain the renderer, but clusters should distinguish:

- real synthesized cluster: `placeholder: false`, `synthesis_status: "fresh"` or `"stale"`
- pending/missing cluster: `placeholder: true`, `synthesis_status: "pending"`
- failed cluster: `placeholder: true`, `synthesis_status: "failed"`

Confidence should continue to degrade when placeholders exist.

Suggested confidence rule:

- all fresh/stale synthesized: current source-count behavior
- mixed synthesized + placeholder: `Medium-Low`
- all placeholder/pending/failed: `Low`

Add a report note whenever cached synthesis is used:

`Synthesis: 3 fresh, 1 pending. Fresh synthesis generated 12 minutes ago from 4 source pages.`

## Minimal Implementation Slices

### Slice 1: Cache Data Model + Read-Through Rendering — SHIPPED (PR #305)

- Add a small cache module for cluster fingerprints and cached synthesis records.
- Add tests for fingerprint stability and invalidation when URL/excerpt changes.
- Teach `execute_brief(read_sources=True)` to prefer fresh cached clusters.
- Keep current placeholder behavior for misses.

Exit criteria:

- cached synthesized clusters render without calling the LLM
- cache misses remain honest placeholders
- confidence behavior remains truthful

### Slice 2: User-Triggered Async Fill — SHIPPED (PR #306; live quality gate passed, 2/3 clusters)

- After a brief/news request, enqueue synthesis for cache misses.
- Run locally with strict concurrency and timeout bounds.
- Store completed records in the cache.
- Do not block the original request.
- Pause or defer local-model synthesis while foreground advisory/model turns are active.
- Decide whether first-open dashboard brief is a valid session trigger.
- If first-open warming is allowed, send a `synthesis ready` update or equivalent visible refresh signal when the active brief's synthesis completes.

Exit criteria:

- first request can return placeholders quickly
- second request can render real synthesized clusters from the completed cache
- failed jobs do not loop indefinitely
- foreground chat responsiveness is not worsened by background synthesis
- the user can tell whether synthesis is pending, paused, fresh, stale, or failed
- synthesized output passes a relevance/usefulness check against the source packet

Quality gate:

Slice 2 is the first real probe of whether the current local model can produce useful news synthesis when given enough time. Morning 4 proved only that `gemma2:2b` cannot finish in 2.2 seconds; it did not prove model quality.

Before considering the lane successful, inspect completed synthesis for:

- source grounding: summary reflects the linked source packets
- relevance: cluster title and summary match the user-visible story set
- usefulness: implication is specific enough to be worth showing
- hallucination control: no unsupported claims beyond the source excerpts

If async synthesis completes but remains low-quality, that is legitimate evidence for reopening the model-gate decision.

### Slice 3: Freshness Disclosure

- Add visible report notes for fresh/stale/pending synthesis counts.
- Include `synthesized_at` and `model_label` in structured data.
- Add speakable text that does not overclaim.

Exit criteria:

- user can tell whether the brief is current, cached, pending, or degraded
- stale cached synthesis never reads as live synthesis

## Tests

Unit tests:

- fingerprint stays stable for equivalent source packet order
- fingerprint stays stable across volatile timestamp/live-update text
- fingerprint changes when canonical URL or material article content changes
- cache returns fresh hits and rejects invalid/stale misses
- cached clusters render as non-placeholder
- pending/failed clusters render as placeholders
- confidence degrades with mixed/all-placeholder clusters

Executor tests:

- first `execute_brief(read_sources=True)` returns quickly with placeholders when cache is empty
- async worker fills the cache with synthesized clusters
- second `execute_brief(read_sources=True)` uses cached synthesis without calling the LLM
- stale cache is disclosed and optionally used only within stale-usable TTL
- failed synthesis records do not retry immediately
- background synthesis pauses or defers when foreground local inference is active
- first-open warming either pushes a completion update or is explicitly not part of the slice
- completed synthesis fails the quality gate when it is off-topic or unsupported by source packets

Contract tests:

- no provider budget usage is recorded for local async synthesis
- no new Governor authority or external write path is introduced
- generated runtime docs do not become the cache

Optional live smoke:

- start fresh server
- ask for today's news / daily intelligence brief
- confirm first result is honest if pending
- wait for synthesis completion
- ask again and confirm real synthesized clusters appear with freshness note

## Decision Outcomes

1. Fresh TTL: shipped as 30 minutes.
2. Stale-but-usable TTL: shipped as 2 hours for news, shortened from the draft's 4-hour proposal.
3. Persistence: shipped as a local runtime cache with atomic writes, not a tracked doc artifact.
4. First-open warming: shipped as session-triggered work; the dashboard/open brief may enqueue synthesis
   because the user opened the session and Nova is already rendering the brief.
5. Update mechanism: shipped as `news_synthesis_ready`; the widget refreshes from structured data and
   chat copy is gated/concise.
6. Scope: shipped for Cap 50 intelligence briefs first. Category-summary relevance remains a separate
   open bug/path.

## Recommendation

Slices 1 and 2 are shipped. The lane proved the important product bet: async/background time makes
the local model useful for source-grounded brief synthesis, so the model-gate remains parked. The
remaining work is a small Slice 3 tightening pass only if Morning use shows the freshness/pending/
partial presentation is unclear.

Do not alter the model choice, paid provider policy, or synchronous timeout budget from this plan.
