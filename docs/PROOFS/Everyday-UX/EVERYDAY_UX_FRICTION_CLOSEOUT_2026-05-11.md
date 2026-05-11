# Everyday UX Friction — Workstream Closeout

**Date:** 2026-05-11
**Lock set:** 2026-05-10
**Final commit on main:** `ae0fba5`
**Driving question:** Can a normal person use Nova every day without confusion?

---

## PR chain — full record

| PR | Branch | Type | Merged | Summary |
|---|---|---|---|---|
| #135 | `docs/everyday-ux-friction-priority-lock` | docs | ✓ | Priority lock + live workflow test plan |
| #136 | `proof/everyday-ux-live-workflow-baseline` | proof | ✓ | 13-scenario live baseline; established pre-fix routing truth |
| #137 | `docs/nova-conversation-response-contract` | docs | ✓ | Response shape contract — calm, bounded, premium output style |
| #138 | `fix/everyday-ux-friction-slices-1-8` | fix | ✓ | Routing gaps fixed across 8 slices; 20 unrouted phrases resolved |
| #139 | `proof/everyday-ux-friction-slice-1-verification` | proof | ✓ | Post-merge verification; 26/26 scenarios pass; `what can u do` fix |
| #140 | `fix/everyday-ux-friction-slice-9` | fix | ✓ | RC-7 normalization fix; dead code removed; 98 full-pipeline tests |

---

## What was fixed

### Routing corrections (RC-1 through RC-7)

| RC | Phrase example | Before | After |
|---|---|---|---|
| RC-1 | `open my email` | Cap 17 (wrong) | EMAIL_INBOX |
| RC-2 | `tell me more about that` | LLM timeout | AMBIENT_CLARIFICATION |
| RC-3 | `what went wrong` | LLM nonsense | AMBIENT_CLARIFICATION |
| RC-4 | `what should I do today` | Cap 16 (wrong) | AMBIENT_CLARIFICATION |
| RC-5 | `idk what to do` | LLM timeout | AMBIENT_CLARIFICATION |
| RC-6 | `i'm lost` / `i'm stuck` | LLM timeout | AMBIENT_CLARIFICATION |
| RC-7 | `help me` / `i need help` | CAPABILITY_HELP (wrong) | HELP_ORIENT |

RC-7 had a second-layer bug: `PHRASE_NORMALIZATION` in `InputNormalizer` was silently
rewriting the phrases to `"what can you do"` before session-layer patterns ran, making
`HELP_ORIENT_RE` permanently unreachable for its most natural triggers. Fixed in slice-9
by removing three conflicting `PHRASE_NORMALIZATION` entries and narrowing one.

### New routing coverage (slices 1–8)

Phrases newly routed that were previously unhandled:

| Phrase | Route |
|---|---|
| `catch me up` | Cap 56 |
| `will it snow tomorrow` | Cap 55 |
| `should i bring an umbrella` | Cap 55 |
| `send an email` | Cap 64 |
| `what have you saved for me` | Cap 61 |
| `how is the AI story doing` | Cap 52 |
| `today's news` | Cap 50 (previously scooped by Cap 56) |
| `find me a recipe for pasta` | Cap 16 |
| `what day is it` | TIME_QUERY |
| `remind me to call mom` (no time) | REMIND_TIMELESS → clarification |
| `what can u do` | CAPABILITY_HELP |
| `i want help` / `i want some help` | HELP_ORIENT |

### Dead code removed (slice-9)

Three pattern checks in `governor_mediator.py` were unreachable — early unconditional
pre-checks at L902, L986, and L1014 returned before the downstream copies at L1164,
L1263, and L1412 could run. Downstream copies removed; comments point to active lines.

### Full-pipeline test methodology (slice-9)

Previous routing tests bypassed `InputNormalizer` — they tested raw strings against
session-layer patterns directly. This approach would not have caught the RC-7 bug.

New file: `tests/websocket/test_session_layer_pipeline.py` — 98 assertions through the
full production path: `InputNormalizer.normalize()` → trailing punct strip → session-layer
patterns → governor. Future `PHRASE_NORMALIZATION` changes will be caught immediately if
they conflict with session-layer routing.

---

## Final test counts

| Suite | Count | Status |
|---|---|---|
| Websocket + conversation (full) | 536 | pass |
| New full-pipeline tests | 98 | pass |
| Verification sweep (post-PR #139) | 26/26 scenarios | pass |

---

## Deferred items — carried forward as GitHub issues

These were found during the workstream but are not resolved here.
Each needs its own scoped investigation:

1. **Search widget not surfacing in live WebSocket sessions** — Cap 16 routing is correct
   (confirmed in P1–P5 certification); the widget surface is a WS transport/render issue.
   Needs live WS session debugging with the frontend.

2. **RS-2 capability list truncation** — message ends cleanly in all test runs; may be
   context-length dependent in live sessions. Root cause unknown.

3. **`"tell me more"` with prior context** — intentional LLM fallthrough in production
   (AMBIENT_CLARIFICATION only fires when `session_state["last_response"]` is empty).
   Needs a dedicated session-state-aware test to exercise the `with-context` path.

---

## What this workstream did not do

Explicitly out of scope — none of the following were touched:

- No new capabilities added
- No OpenClaw expansion
- No authority changes
- No external writes
- No autonomous workflows
- No browser/computer-use
- No Cap 64 P5 (queued, needs own lock)
- No UI simplification implementation (queued, needs own lock)

---

## Recommended next sequence

```text
1. Interface Personality Layer MVP
   — response shaping only; no tools, no execution, no memory writes

2. Google read-only connector foundation
   — Calendar/Gmail metadata read + draft; Drive/Docs read; no sends, no edits

3. Piper / local TTS voice upgrade
   — local-first; ElevenLabs as optional cloud provider only, behind NetworkMediator

4. ElevenLabs (optional, later)
   — visible cost/setup truth; not default
```

---

## Verdict

Everyday UX Friction workstream is **closed**.

The driving question — *can a normal person use Nova every day without confusion?* — has
measurable answers now that it did not have at lock time. Seven baseline friction points
resolved, 12 previously unrouted phrases now route correctly, one normalization-layer bug
that silently bypassed a handler in production has been fixed, and the test suite now
covers the full production routing pipeline for the first time.
