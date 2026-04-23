# Live Dashboard Basic User Smoke - 2026-04-23

## Scope

Basic live dashboard smoke test using Playwright against local runtime at `http://127.0.0.1:8000`.

## Final Status

Status: IMPROVED

Core first-user chat reliability materially improved after turn-correlation fixes, overlapping-send guards, and widget-refresh discipline.

## Verified Wins
- Dashboard loads cleanly.
- Chat opens successfully.
- Normal prompts receive visible in-turn answers.
- Confirmation flows render correctly.
- Browser console and local HTTP path were clean during the passing run.
- Manual user turns are protected from background widget noise.

## Key Engineering Fixes Already Applied
- Manual turns tracked with active turn state.
- Silent widget refresh suppressed during user turns.
- Overlapping sends blocked while assistant reply is in flight.
- Explicit `turn_id` correlation added across WebSocket frames.
- Repeated identical assistant text deduplicated.
- Delayed or unrelated frames filtered during active manual turns.

## Remaining Opportunity
The next layer is no longer basic reliability. The next layer is premium feel:
- faster perceived response pacing
- clearer blocked-send messaging
- preserve unsent draft text during waits
- reduce unnecessary background frames at the source
- stronger first-use capability guidance

## Diamond Readiness Interpretation
The dashboard appears to have moved beyond broken-first-impression risk.
The next bar should be showcase readiness, not just technical pass/fail.

Recommended acceptance standard:
- reliable core chat
- coherent transcript behavior
- polished first-use flow
- visible user value in first session

See: `docs/TODO/DIAMOND_PREVIEW_RELEASE_STANDARD_2026-04-23.md`

## Recommended Next Test
1. Fresh launch.
2. Open Chat.
3. Ask three ordinary questions.
4. Trigger one governed action.
5. Confirm no transcript confusion.
6. Judge premium feel, not only technical success.

## Cleanup
- Backend stopped after smoke.
- Runtime-generated files restored after test pass.
