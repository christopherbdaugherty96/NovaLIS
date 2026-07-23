# Grounded Brief/Category Routing Closeout - 2026-07-23

## Status

The highest-ROI finding from the seven-morning observation phase is implemented, merged, and
verified on fresh `main`.

- PR: #312
- Reviewed head: `f34795c3ba4f8f48eca2cb761fecb3c8da36c3ca`
- Merge commit: `5c2eda634aa0c0cb3f5dd15fa485ed522d7ca997`
- Independent review: PASS
- GitHub CI: non-executing because of the recorded account billing/spending-limit restriction
- Local validation before merge: 205 focused tests, Ruff PASS, runtime structural proof PASS

## Fresh-main live verification

Nova was restarted from clean `main` at the merge commit. The following workflow was repeated in a
new dashboard session:

1. `show me global security news`
2. `Tell me more about the second story.`
3. `What matters most?`
4. `today's news`

Observed outcome:

- The explicit category request returned governed `CATEGORY SUMMARY - Global News` output.
- The second-story follow-up stayed attached to the second story on the visible category surface.
- `What matters most?` answered from the active category surface rather than an older brief or
  broad weather/calendar/runtime state.
- The fallback intelligence brief rendered `Confidence: Low` in the brief body and `Confidence:
  Low` in the Trust strip.
- Placeholder summaries remained explicitly marked `[Fallback]` and directed the user to review
  linked source pages; no synthesized facts were fabricated.
- The interface remained healthy and usable through the workflow.

## Closed boundary

PR #312 closes the evidence-defined grounded brief/category routing lane:

- category requests route to the governed news capability;
- rendered brief and active category/story state are the grounding source;
- numeric and vague follow-ups do not leak back to stale brief state;
- targeted deterministic answers replace broad dashboard fact dumps;
- brief and Trust confidence use the same response value;
- fallback/pending behavior remains source-bounded.

## Explicit exclusions

This closeout does not authorize or begin:

- connection-truth repair;
- runtime-generator reconciliation;
- corruption-safe loading;
- provider/model changes;
- capability or authority expansion.

Those remain separate decisions.
