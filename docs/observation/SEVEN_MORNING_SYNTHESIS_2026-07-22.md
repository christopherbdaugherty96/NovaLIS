# Seven-Morning Observation Synthesis - 2026-07-22

## Decision

The seven-morning evidence threshold is complete. Nova has crossed the interaction-reliability
floor for continued product work: deterministic weather and valid-empty calendar behavior are
useful, governed outcomes are inspectable, degraded outcomes are honest, and a timed-out model
turn no longer blocks the next deterministic request.

Nova is not yet daily-reliance-ready. The highest-return next lane is a narrow grounded-routing
repair over the rendered news brief and active story surface. It should not be expanded into a
general conversation rewrite, model change, provider change, or capability lane.

## Method

This synthesis reads Morning 1 through Morning 7 as an evolving system, not seven identical test
runs. Frequency below is morning-level occurrence: multiple examples in one log count once, and a
later addendum counts with its parent morning. Some conditions were not exercised every morning,
so denominators are stated where a universal `of 7` would be misleading.

Findings are classified as:

- **Current:** reproduced in the latest relevant mornings and still open.
- **Closed/preserve:** observed earlier, repaired, and validated after repair.
- **Secondary:** real but narrower or less directly tied to daily usefulness.
- **Parked:** insufficient evidence or explicitly outside the next lane.

## What became reliable enough to preserve

| Boundary | Evidence across the phase | Current conclusion |
| --- | --- | --- |
| Weather | Working brief/chat weather was observed repeatedly; Mornings 4, 6, and 7 returned useful Ann Arbor conditions. Morning 7's governed weather action completed in 0.468 seconds after an abandoned model turn. | Preserve the deterministic governed path. |
| Empty calendar | The connected local `.ics` source repeatedly returned `Nothing on your calendar today`; PR #310 preserved valid-empty as success and Morning 6 recorded a successful Cap 57 receipt. | Preserve successful-empty semantics. Improve source labeling separately. |
| Receipts and outcome truth | Successful weather/calendar receipts were visible in Morning 6. Forced degraded contracts were covered by PR #310 tests; live sessions did not fabricate a natural outage. | Preserve receipt truth and visible degraded sections. |
| Manual recovery | Mornings 1-3 exposed reconnect/Gotcha/stuck-turn failures. By Morning 4, the Gotcha loop and false status-frame failure were absent; Stop remained honest and usable. | Closed; guard against regression. |
| Automatic timeout isolation | Morning 6 exposed cross-turn blocking. PR #311 repaired it; Morning 7 reproduced the same 90-second failure pattern and the following weather turn remained isolated. | Closed; guard against regression. |

## Ranked current defects

| Rank | Defect | Observed frequency | User impact | Bounded repair scope | Status |
| ---: | --- | --- | --- | --- | --- |
| 1 | Brief/category requests and follow-ups do not consistently bind to the rendered brief or active story surface | Present in all seven mornings at the broad conversational-use level; directly reproduced in Mornings 4-7 after basic interaction repairs | **Critical for habit formation.** Nova can show useful facts but often cannot answer the next natural question about what it just showed. Users must reopen another app. | Deterministic intent routing; rendered Cap 50 cluster facts; active-surface/stable-story identity; narrow-answer precedence over broad dashboard state | **Current; authorize first** |
| 2 | News synthesis/relevance remains fallback, pending, stale, or category-incoherent | Material news-quality failure in Mornings 1, 2, 4, 5, 6, and 7; Morning 3's loaded-headline summary worked but broader follow-ups still failed | **High.** News is visible but frequently not decision-useful; irrelevant or placeholder content damages trust more than an honest unavailable state | Retain deterministic fallback; route category fetches correctly; consume only current rendered clusters; reject unrelated category items; no provider/model change | **Current; include only where inseparable from rank 1** |
| 3 | Response confidence and Trust confidence have separate truth sources | Explicit contradiction in Mornings 5 and 6; Morning 4 also overclaimed confidence on all-fallback synthesis | **High trust impact.** The same response can tell the user both `Low/Medium-Low` and `Standard/Medium-High` | Derive one response-level confidence outcome and render it consistently in body and Trust strip | **Current; include in narrow lane** |
| 4 | Settings/runtime connection truth and local source labels disagree | False configuration truth appeared in Morning 1; later settings contradiction reproduced in Mornings 6 and 7. Morning 6 labeled local `.ics` as `Mode: Online` | **Medium-high.** Users cannot tell whether a source is configured or local, even when it works | Recognize operative User-scope environment configuration; label `.ics` as local; do not alter connector authority | **Secondary lane** |
| 5 | Generated runtime fingerprints drift after startup/code changes | Recorded in Mornings 4, 6, and 7; generated deltas were intentionally excluded from observation commits | **Medium repository-truth impact, low immediate user impact.** Fresh main can disagree with committed generated truth | Parked PR 2 generator reconciliation only; no coupling to routing work | **Secondary lane** |
| 6 | Stale business-context presentation (`Watch: July 9...`) persists without tense or freshness | Present in every full-brief observation that recorded the Auralis section (Mornings 1-6) | **Medium trust/noise impact.** Past-dated context appears current and competes with more useful information | Freshness/tense rule for surfaced memory-derived status; no business action or external write | **Secondary candidate; separately authorize** |

## Rank 1 evidence trace

The highest-ranked defect is not a general statement that conversation quality is poor. It is a
specific repeated boundary failure:

- **Morning 1:** Nova felt like a status panel, not an assistant that could discuss its brief.
- **Morning 2:** natural headline phrasing failed while a rigid loaded-headline summary worked;
  category-specific politics phrasing reused mixed context.
- **Morning 3:** schedule, heat-alert, and `on what weekday?` follow-ups did not use the already
  visible source/result context.
- **Morning 4:** an Iran follow-up ignored the current loaded headline and returned stale,
  unsourced model context; category summary relevance also failed.
- **Morning 5:** `what matters most`, `what should I keep an eye on`, compare, completeness, and
  global-security requests escaped the rendered brief. Numeric story identity resolved against an
  older surface.
- **Morning 6:** `what matters most from this brief?` produced a broad state dump; `show me global
  security news` missed the governed category path and timed out.
- **Morning 7:** the exact category miss was reproduced to validate timeout containment. Isolation
  passed, but the late placeholder confirms the request still entered the wrong model-shaped path.

This sequence shows a stable product defect after the older transport/recovery problems were
removed: the active rendered object is not consistently the conversation's grounding object.

## Authorized shape of the next repair

The evidence supports authorizing one narrow grounded-routing repair with these outcomes:

1. Explicit category wording such as `show me global security news` reaches the governed
   news/category path and never falls through to advisory general chat.
2. Brief-relative follow-ups such as `what matters most?`, `what should I watch?`, compare, and
   completeness questions bind to the current rendered brief or active category/story surface.
3. When a narrower active surface exists, its facts take precedence over broad weather/calendar/
   dashboard state; broad `Sourced brief facts` dumps are not used as a substitute answer.
4. Numeric story commands resolve against a stable active-surface identity, not an older story
   collection.
5. Response and Trust presentation consume one confidence value.
6. If synthesis is unavailable, Nova returns deterministic sourced headlines or an explicit
   fallback/partial state. It does not invent links, silently switch to generic search, or present
   model memory as current news.

### Non-goals

- No model/provider change.
- No capability, Governor, authority, connector, or external-write expansion.
- No broad conversation rewrite or full historical Slice 1 by default.
- No connection-settings repair in the same PR.
- No runtime-fingerprint reconciliation in the same PR.
- No corruption-safe loading work without separate evidence and authorization.

## Acceptance evidence for the next lane

A focused implementation should not be considered complete until tests demonstrate:

- category-routing positives for `global security news` and close natural variants;
- negative routing cases that must remain ordinary conversation;
- rendered-brief follow-ups answer from the current cluster object;
- active category/story identity survives refresh or is explicitly cleared;
- broad dashboard facts cannot override a narrower active surface;
- fallback/pending synthesis remains deterministic and source-bounded;
- body and Trust confidence are identical for success, partial/fallback, and failure outcomes;
- existing weather, calendar, receipts, Stop, and timeout-isolation contracts remain unchanged.

## Secondary sequencing

After the narrow grounded-routing repair is independently reviewed and live-verified:

1. Decide separately whether to authorize connection-truth repair.
2. Decide separately whether to publish the parked runtime-generator reconciliation lane.
3. Keep corruption-safe loading parked unless an actual corruption/loading failure is observed.

No additional open-ended morning cycle is required to justify the first lane. Future live use
should verify the shipped repair, not restart evidence collection from zero.
