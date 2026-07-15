# Morning 4 — News Synthesis Fallback Trace (findings note)

Companion to `MORNING_04_2026-07-15.md`. Read-only code trace of Morning 4's #1 trust issue: the
daily news brief returned `[Fallback] … I could not complete a source-grounded synthesis` for every
cluster. This note records the mechanism; no code changed.

## Root cause: request-time budget vs. CPU inference speed (NOT plumbing, NOT proven model-quality)

The daily brief synthesizes each topic cluster with the local LLM, then parses a `Summary` /
`Implication` structure. Empty or unparseable output becomes the `[Fallback]` placeholder.

Chain, in `nova_backend/src/executors/news_intelligence_executor.py`:

- Each cluster synthesis calls `_llm_or_fallback(_cluster_prompt(cluster), "", timeout_seconds=
  _bounded_timeout(deadline, CLUSTER_ANALYSIS_TIMEOUT_SECONDS), max_tokens=380)` (line ~1406).
- `CLUSTER_ANALYSIS_TIMEOUT_SECONDS = 2.2` (line 26) — each cluster gets **≤2.2s** to produce up to
  **380 tokens** of structured synthesis (often less: `_bounded_timeout` caps it by the remaining
  overall deadline).
- `_llm_or_fallback` runs `generate_chat` in a thread and does `future.result(timeout=…)`; on
  `FuturesTimeoutError` it returns the empty fallback immediately (lines 388–410).
- Empty text → `_parse_summary_and_implication("")` → `_cluster_fallback` → the placeholder
  (lines 616–654).
- The whole brief shares `BRIEF_REQUEST_TIMEOUT_SECONDS = 8.5` across source-fetch **plus** all four
  cluster syntheses.

`gemma2:2b` on CPU cannot generate ~380 structured tokens in ~2.2s (it is tens of seconds), so every
cluster times out and falls back. Structurally, real CPU synthesis can never fit an 8.5s whole-brief
budget — **the brief is architected for a fast model or async precompute; on the current CPU +
gemma2:2b setup it will always fall back.**

What this rules in/out:
- **Not plumbing.** Source excerpts are in the prompt (`_cluster_prompt`, line 597).
- **Not proven model-*quality*.** The model never finishes, so Morning 4 says nothing about whether
  `gemma2:2b` could synthesize well — only that it can't in 2.2s on CPU. **The model-gate is not
  earned by this evidence.** (Consistent with the earlier "LLM wasn't receiving facts / plumbing not
  model" trace.)

## Secondary bug: confidence label does not reflect synthesis success

The brief rendered `Confidence: Medium-High` while every cluster was a placeholder. Confidence is
derived mostly from source count, not synthesis success. Fix target: if placeholder clusters > 0,
confidence must degrade; if all clusters are placeholders, it must be low/degraded — never
Medium-High. Independent, cheap, trust-critical.

## Secondary bug (separate path): category-summary relevance

`summarize the war between the US and Iran` led with a World Cup headline. The category/story
summarizer returns loaded headlines without filtering by the query. Distinct from the timeout issue;
own trace when prioritized.

## Recommended path (owner-confirmed 2026-07-15)

1. Fix the confidence lie first (no trade-off, pure trust fix).
2. Scope brief synthesis as **async / precompute / cache** so the LLM gets minutes, not 2.2s —
   keeping the brief fast *and* real.
3. Do NOT simply raise the 2.2s timeout (makes the brief slow and still brittle).
4. Do NOT spend the model-gate yet — this is a budget/architecture problem, not a quality verdict.

## Related want surfaced same day

Owner asked for visibility: **which local model is active**, and **token usage (especially for paid
models when active)**. Same trust-transparency theme as the confidence fix — Nova should show what
is running and what it costs. Scope separately.
