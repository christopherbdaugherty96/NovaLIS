# Nova News Experience And Reasoning Plan
Date: 2026-03-21
Status: Planning packet with core inline-summary/category improvements now partially implemented on `main`
Scope: Improve the news page experience, timeout behavior, category labeling, and source-grounded news reasoning without widening authority

## Purpose
This packet captures a specific product goal:

Nova's news experience should feel more useful, more readable, more grounded in real source material, and less interruptive.

The user goals behind this packet are:
- inline summaries should happen on the news page itself
- the user should not need to bounce to another page just to read a summary
- news and brief flows should stop failing so often with timeout-style dead ends
- category labels should be simpler and more natural
- Nova should read source content more fully and reason from the actual material before answering

This is not runtime truth.
It is a product and design roadmap for improving the news surface and the reasoning quality behind it.

## Implemented Foundation On `main` (2026-03-25)
The current runtime now includes:
- inline news summary rendering on the News page
- in-place summary actions instead of bouncing to chat for the main payoff
- cleaner visible category language:
  - Politics news
  - Global news
  - Local news
  - Tech news
  - Crypto news

Remaining items in this packet should be read as the next quality-improvement layer, not as untouched future-only ideas.

## Current Problems To Fix

### 1. Summary Flow Is Too Interruptive
Right now, the news experience appears to push the user away from the headline card instead of letting the payoff happen in place.

The better product shape is:
- click `Summarize`
- the summary appears inside that headline card
- the user stays on the news page

That creates better continuity and less UI friction.

### 2. Timeout Behavior Still Hurts The Experience
Even when Nova stays honest about timeouts, the experience is still weak if the user only gets:
- `The request took too long and was cancelled.`

That is truthful, but not very helpful.

The news experience needs:
- quicker first payoff
- better degraded paths
- clearer fallback behavior

### 3. News Labels Feel Too Framed Or Awkward
Labels like:
- left politics
- right politics

do not match the cleaner product feel you want.

The categories should feel simpler and more user-friendly, for example:
- Politics news
- Global news
- Local news
- Tech news
- Crypto news

### 4. Source Reading Is Not Deep Enough Yet
The system can still behave too much like:
- headline summary
- snippet summary
- partial-page synthesis

instead of:
- read the source
- understand the article
- reason from the material
- then answer

That is one of the biggest quality gaps if you want the news experience to feel much stronger.

## Best Product Recommendation
The best overall direction is:

### Keep The News Page As The Place Where News Is Worked With
Do not make the user leave the news page to get the main payoff.

The news page should become a working surface where the user can:
- browse headlines
- expand a summary inline
- ask for deeper explanation
- compare sources
- open the source article if wanted

That is better than bouncing the user between pages or between dashboard and chat for simple news actions.

## Best UX Shape

### Inline Headline Cards
Each headline card should support:
- `Summarize`
- `Expand`
- `Compare sources` (later)
- `Open source`

The `Summarize` action should:
- load inside the same card
- preserve the user's place on the page
- show clear loading and fallback states

### Better Loading States
Instead of only failing with a timeout message, the news card should be able to say:
- `Loading summary...`
- `Still reading sources...`
- `Quick summary available now`
- `Full source-based summary took too long; showing a shorter version`

This makes the experience feel alive and honest without feeling broken.

### Cleaner Category Labels
Recommended visible category names:
- Politics news
- Global news
- Local news
- Tech news
- Crypto news

These are simpler, easier to scan, and less awkward than ideological-direction labels.

## Best Reasoning Recommendation

### Read First, Summarize Second
The strongest improvement is this:

Nova should not summarize only from:
- the headline
- the short snippet
- a weak first source signal

Nova should summarize from:
- the full article text when available
- a cleaned and extracted article body
- multiple source bodies when comparison is requested

That gives a much better answer.

### Separate Headline Snapshot From Article Reasoning
These should be two different layers:

1. headline/news snapshot
2. article reading and reasoning

That separation matters because the first one should be:
- fast
- light
- dashboard-friendly

And the second one should be:
- slower
- more grounded
- source-text based
- higher quality

### Single-Article Summary First
The best first reasoning improvement is:
- when the user clicks `Summarize` on a headline
- Nova reads that article
- Nova summarizes that article specifically

This is better than trying to jump straight to giant multi-source synthesis everywhere.

### Multi-Source Reasoning As A Later Layer
After single-article reading is solid, then add:
- compare multiple articles on the same story
- identify shared facts
- identify disagreement or uncertainty

That should come after article-reading quality is reliable.

## Technical Recommendation

### Current Product Track
These improvements belong in the current product improvement track, not later autonomy phases:

- inline card summaries on the news page
- better loading and degraded states
- timeout fallback improvements
- cleaner category labels
- single-article source reading before summarizing
- better source-grounded summaries for news cards

These are current product improvements.
They do not require new authority.

### Phase 7 Extensions
These belong later in Phase 7 governed external reasoning:

- stronger long-form article synthesis when the local model is weak
- more nuanced cross-source reasoning
- optional second-opinion review of a news summary
- harder ambiguity handling on complex current-events questions

Why they belong in Phase 7:
- they are reasoning-quality upgrades
- they stay text-only
- they do not add execution authority

### Phase 8 Boundary
This packet is not about execution.

Phase 8 should only matter insofar as:
- news remains read-only
- no article action or provider result becomes execution authority

### Much Later
Only much later should Nova consider:
- durable personalized topic preferences
- adaptive source-style preference learning
- implicit topic ranking based on repeated behavior

That belongs much later because it starts to touch lasting preference learning and personalization behavior.

## Recommended Architecture

### 1. News Snapshot Layer
This layer gathers and renders:
- headline
- source
- category
- timestamp
- quick metadata

It should stay fast and lightweight.

Likely surfaces:
- [news_intelligence_executor.py](C:\Nova-Project\nova_backend\src\executors\news_intelligence_executor.py)
- [dashboard.js](C:\Nova-Project\nova_backend\static\dashboard.js)
- [intelligence_brief_renderer.py](C:\Nova-Project\nova_backend\src\rendering\intelligence_brief_renderer.py)

### 2. Article Reader Layer
This layer should:
- fetch the source page when needed
- extract cleaned article text
- prepare a summary-ready article body
- separate article text from headline metadata

This is the main quality improvement layer.

### 3. Summary Layer
This layer should:
- summarize from article text, not just headline/snippet
- keep the answer short at first
- allow deeper expansion later
- surface source grounding clearly

### 4. Multi-Source Reasoning Layer
Later, for deeper news questions, Nova should:
- compare multiple articles
- identify overlap
- identify disagreement
- note confidence and uncertainty

This should be layered on top of article-reading quality, not used as a substitute for it.

## Best Implementation Order

### Stage 1 - Inline News Card Summaries
Goal:
- make the `Summarize` button work inside the headline card on the news page

Best scope:
- stay on the same page
- render loading and result inline
- no forced bounce back to the other page

Primary files:
- [dashboard.js](C:\Nova-Project\nova_backend\static\dashboard.js)
- [style.phase1.css](C:\Nova-Project\nova_backend\static\style.phase1.css)

Suggested branch:
- `codex/news-ui-stage1-inline-card-summary`

### Stage 2 - Timeout And Degraded Flow Improvements
Goal:
- stop the news experience from feeling like a dead-end timeout system

Best scope:
- better loading states
- truthful degraded summary fallback
- headline-only fallback when full reading is too slow
- retry guidance only when useful

Primary files:
- [news_intelligence_executor.py](C:\Nova-Project\nova_backend\src\executors\news_intelligence_executor.py)
- [dashboard.js](C:\Nova-Project\nova_backend\static\dashboard.js)

Suggested branch:
- `codex/news-stage2-timeout-degraded-flow`

### Stage 3 - Single-Article Reader Grounded Summary
Goal:
- summarize from the actual article text rather than weak headline/snippet signals

Best scope:
- read one article body
- extract meaningful text
- produce one grounded summary
- keep the first version limited to article-specific summaries

Primary files:
- [news_intelligence_executor.py](C:\Nova-Project\nova_backend\src\executors\news_intelligence_executor.py)
- [web_search_executor.py](C:\Nova-Project\nova_backend\src\executors\web_search_executor.py)

Suggested branch:
- `codex/news-stage3-article-reader-grounded-summary`

### Stage 4 - Category Taxonomy Cleanup
Goal:
- make news categories cleaner and more user-facing

Best scope:
- rename visible categories to:
  - Politics news
  - Global news
  - Local news
  - Tech news
  - Crypto news

This can happen earlier if it is a trivial surface change, but conceptually it belongs as a bounded UI taxonomy pass.

Suggested branch:
- `codex/news-stage4-taxonomy-cleanup`

### Stage 5 - Multi-Source Reasoning And Deeper Explanation
Goal:
- let Nova reason across multiple sources once article-reading quality is already solid

Best scope:
- compare at least two sources
- identify shared facts
- identify disagreements or uncertainty
- return cleaner multi-source summaries

This may remain in the local/current track for modest improvements, but stronger versions of it fit naturally into Phase 7 governed external reasoning.

## What To Avoid
Do not:
- summarize from headlines alone when the user asked for a real summary
- hide timeouts without a useful fallback
- make the user leave the news page for the basic payoff
- overcomplicate the category labels
- pretend weakly grounded synthesis is deeply reasoned
- jump straight to giant multi-source reasoning before article reading is solid

## Definition Of Success
The news experience is in a much better place when:
- `Summarize` works inside the news card
- the user can stay on the news page
- timeout behavior gives useful fallback instead of dead ends
- category names are cleaner
- article summaries are clearly grounded in source text
- multi-source reasoning is introduced only after single-article reading is reliable

## One-Sentence Recommendation
The best way to improve Nova's news experience is to make news cards interactive on-page, separate fast headline snapshots from deeper article-reading summaries, clean up category labels, and make Nova read source text more fully before reasoning or summarizing.
