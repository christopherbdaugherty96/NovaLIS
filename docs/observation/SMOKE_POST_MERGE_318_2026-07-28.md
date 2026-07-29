# Post-Merge Smoke + Diagnosis — PR #318 (governed-surface routing guard) — 2026-07-28

**Status:** recorded evidence (a verification smoke + read-only diagnosis), not a plan and not the
owner's acceptance morning. It does not authorize a build.

## Run context

- Fresh checkout of merged `main` `69e0b4f2` (PR #318 squash of reviewed head `1f02a1dd`).
- Live runtime: backend started server-only (`start_daemon.py --no-browser`, backend venv,
  User-scope env `OLLAMA_MODEL=gemma2:2b`, real calendar `.ics`). Ollama up; port 8000 clean start.
- Driven through the real `/ws` in one session (state persists brief -> follow-up), exact prompts.
- Server stopped after the run; port 8000 freed. No repository files were changed by the smoke.

## Result (mixed)

| Prompt | Observed | Verdict |
| --- | --- | --- |
| "Give me my Daily Awareness Brief." | `awareness_brief` widget + "your daily awareness brief is ready — 5 of 8 sections have live data"; no timeout; no GeneralChat escape | PASS |
| "Show me Auralis Today" | `awareness_brief` widget + "Your Auralis Today section is ready in the Daily Awareness Brief"; no `@auralis_digital`; no GeneralChat | PASS |
| "Let's discuss the awareness brief design" (mention) | Streamed GeneralChat response; not guarded; not a brief | PASS (false-positive protection holds) |
| "What matters most?" (after the brief) | Streamed generic local-model output ("Meaningful stuff. For you? What's important to you right now?"); did NOT bind to the brief | **FAIL (live)** |

Net: PR #318's trust-critical repair is validated on the live runtime (routing + hallucination
prevention + mention protection). One residual grounding failure remains.

## Diagnosis (read-only; grounded at file:line)

Root cause of the "What matters most?" failure — **not** a regression, **not** a hallucination:

- `last_brief_clusters` is assigned in only two places, both the Cap 50 **intelligence-brief**
  path: `session_handler.py:55` and `session_handler.py:4172`.
- The **awareness-brief route** (`session_handler.py:~3508-3607`) sets `brief_weather`,
  `news_cache`, `news_categories`, `brief_calendar`, `last_calendar_events` (via
  `store_brief_widget`) and `active_brief_item="awareness_brief"` — but it does **not** set
  `last_brief_clusters`.
- The grounded-followup gate `is_discussion_shaped_brief_followup`
  (`brief_followup_grounding.py:118`) admits "What matters most?" only via one of two paths, and
  the phrase satisfies neither after the awareness brief:
  1. Explicit-key path `_select_explicit_item_key` (`:331`) routes "what matters most" to
     `awareness_brief` **only if `last_brief_clusters` is set** — it is not.
  2. Active-key path (`:130`) requires `_has_active_reference_shape` -> `_has_reference_shape`
     (`:426`), which needs a "that/this/it"-style reference. "What matters most?" has none, so it
     returns False.
- With both paths False, the follow-up falls through to the general-chat fallback and the local
  model produces the weak, ungrounded reply.

So `active_brief_item="awareness_brief"` alone (what PR #318 established) is insufficient: the
awareness-brief follow-up grounding keys off `last_brief_clusters`, which only the Cap 50
intelligence brief populates. `_answer_awareness_followup` (`:820`) already knows how to answer
"what matters most" from `last_brief_clusters`; it never gets the chance because that state is
absent on the awareness surface.

## Test-fidelity note

The WS-boundary test `test_daily_awareness_request_..._grounds_followup` asserts only that
`generate_chat` is not called, and it passes — but the live runtime still produced a weak model
answer for the same follow-up. The assertion proves "no escape to that specific fallback," not
"grounded content." A faithful test must assert the follow-up returns grounded brief content.

## Classification and next candidate

- Severity: grounding/reasoning-**quality** miss (generic deflection, no fabricated facts). Lower
  than the PR #318 trust-boundary items. Not a rollback trigger.
- Candidate (owner-gated, not warranted here): make the awareness-brief route populate an
  awareness-cluster state (`last_brief_clusters` or equivalent, in the shape
  `_answer_awareness_followup` reads) so "What matters most?" grounds over the awareness brief;
  strengthen the WS-boundary test to assert grounded content, not just no-escape.
- Separate, still-open items untouched: `Sources: n/a` Trust display; first-brief latency.

## Resolution — post-#319 re-verification (loop CLOSED, 2026-07-28)

Warrant v3.1 was implemented, independently reviewed (PASS), and merged as PR #319 (squash
`b6956d39`). A live post-merge smoke on fresh `main` `b6956d39` (server-only, real Ollama
`gemma2:2b`, real `/ws`) re-ran the exact flow. All checks pass:

| Prompt | Observed | Verdict |
| --- | --- | --- |
| "Give me my Daily Awareness Brief." | `awareness_brief` widget + "brief is ready"; no timeout; no GeneralChat | PASS |
| "What matters most?" | Deterministic non-model reply: "Lead sourced item from the rendered Awareness Brief: - Weather: ... 77 degrees F and Partially cloudy in Ann Arbor. [source: weather; status: ok]" | PASS — residual FIXED |
| "Show me Auralis Today" | Honest "Auralis Today section is ready"; no `@auralis_digital` | PASS |
| "Let's discuss the awareness brief design" (mention) | Normal GeneralChat reply; not guarded, not a brief | PASS |
| "Show me global security news" | Governed `CATEGORY SUMMARY - Global News` (Story 1 BBC, Story 2 Al Jazeera) | PASS (Cap 50 category intact) |
| "Tell me more about the second story" | Deterministic "Sourced headline ... - 2. Yemen's Houthis ... (Al Jazeera)" | PASS — Cap 50 numeric isolation intact live |

Key confirmations:

- v3.1 DoD met: "What matters most?" returns a concrete rendered fact (the Weather section) plus a
  `[source: weather; status: ok]` label, produced deterministically (no `chat_stream`/model
  tokens). The pre-#319 weak deflection is gone.
- Cap 50 isolated live: after an Awareness Brief was rendered earlier in the session, "second
  story" still resolved correctly to story 2 on the loaded news surface.
- No repository files changed by the smoke; server stopped, port 8000 freed.

The #318 -> smoke -> diagnosis -> #319 -> smoke repair loop is **CLOSED**. Still-separate open
items (not part of this loop): `Sources: n/a` Trust display; first-brief latency; two non-hermetic
news-cache tests.
