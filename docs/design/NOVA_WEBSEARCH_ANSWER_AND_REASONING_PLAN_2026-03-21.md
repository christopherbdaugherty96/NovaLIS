# Nova Web Search Answer And Reasoning Plan
Date: 2026-03-21
Status: Planning packet with answer-first search foundation now partially implemented on `main`
Scope: Improve Nova's web-search answer quality, presentation style, source reading, and evidence surfacing without widening authority

## Purpose
This packet captures a clear product goal:

Nova's web search should feel less like a visible search breakdown tool and more like a capable assistant that:
- understands the user's question
- searches for the right information
- reads the relevant source material
- reasons with that information
- answers directly first
- still shows sources when the user wants them

This is not runtime truth.
It is a design and product roadmap for improving the search experience and search-based answering quality.

## Implemented Foundation On `main` (2026-03-25)
The current runtime now includes:
- answer-first search response copy
- hidden-by-default source lists in the search widget
- cleaner evidence-on-demand behavior for normal search use

The remaining items in this packet are the deeper reasoning and retrieval-quality extensions beyond that first product slice.

## Core Product Direction
The best default shape is:

1. understand the user's request
2. search for it
3. read the relevant source material
4. reason with the gathered information
5. answer directly
6. keep evidence and source detail available on click

That means Nova should feel more like:
- "Here is the answer."

and less like:
- "Here is a big visible breakdown of how I searched."

## Current Problems To Fix

### 1. Search Results Are Too Breakdown-Heavy
Right now the product can surface too much of the machinery:
- result counts
- search latency
- visible process narration
- visible source-page breakdowns
- dashboard-style evidence before the answer

That can be useful in some cases, but it should not be the default feel.

The better default is:
- answer first
- evidence second
- source details on demand

### 2. Nova Does Not Always Feel Like It Understood The Question First
The ideal user experience is not:
- literal query forwarding
- shallow search phrase repetition

The ideal experience is:
- Nova interprets the user's meaning
- chooses the right search intent
- retrieves information for that intent
- answers the actual question

Examples:
- "who won the super bowl 2026" should become a direct factual answer
- "what happened with the fed today" should become a current-events answer
- "compare the two" after a search should stay anchored to the current search context

### 3. Source Reading Is Still Too Shallow
The system can still lean too much on:
- titles
- snippets
- weak first-result signals
- visible intermediate scaffolding

The stronger version is:
- read the source page body when needed
- extract useful content
- reason from the material
- then answer

### 4. Source Visibility Should Be There, But Not In The Way
You still want:
- sources
- transparency
- traceability

But the user should not need to wade through source mechanics just to get a straightforward answer.

The better pattern is:
- direct answer shown by default
- `Sources` or `Show sources` on click
- optional deeper evidence view if the user wants it

## Best Product Recommendation

### Answer First, Evidence On Demand
The best default search UX is:
- Nova gives the answer first
- Nova gives a short confidence framing only when useful
- sources live behind a click or expand affordance

This keeps Nova useful and conversational without losing transparency.

### Use Search As Hidden Retrieval, Not Visible Personality
Search should feel like a support layer.

Nova should not sound like a search engine UI unless the user explicitly asks for:
- source analysis
- reliability review
- research brief
- full evidence comparison

Normal search answers should feel like assistant answers.

### Keep Rich Search Detail Available For Power Use
Do not remove the breakdown entirely.

Instead, move it behind explicit affordances such as:
- `Sources`
- `Why this answer`
- `Compare sources`
- `Open evidence`

That keeps the interface clean while preserving trust and auditability.

## Best UX Shape

### Default Search Answer Card
The default search answer should show:
- direct answer
- very short support summary
- optional quick caveat if uncertainty matters
- collapsed source affordance

Recommended actions:
- `Show sources`
- `Open source`
- `Compare sources` (later)
- `Research deeper` (later)

### Source Panel On Click
When the user clicks `Show sources`, the card can reveal:
- source names
- source domains
- article titles
- one-line source notes

This keeps source visibility available without making every answer feel cluttered.

### Deeper Search Modes Should Be Explicit
There should be a distinction between:

1. answer mode
2. research mode
3. compare-sources mode

Answer mode should stay lightweight.
Research mode can show more process detail.
Compare mode can show overlap and disagreement.

## Best Reasoning Recommendation

### Understand The User Question Before Searching
Before Nova searches, it should classify the question shape.

Examples:
- direct fact lookup
- current-events question
- comparison question
- explanatory question
- follow-up on an earlier search
- request for a research-style answer

That lets Nova shape both retrieval and answer form more intelligently.

### Read Relevant Source Material Before Answering
The strongest answer improvement is:
- retrieve
- read
- reason
- answer

That is better than:
- retrieve
- surface snippets
- guess from first-result metadata

### Separate Retrieval, Reading, And Answering
These should be treated as different layers:

1. query understanding
2. search retrieval
3. source reading
4. answer synthesis
5. evidence display

That separation makes it easier to:
- improve quality
- control cost/latency
- preserve a cleaner user experience

### Use Short Answers First
The default answer should usually be:
- direct
- concise
- grounded

Then the user can expand into:
- more detail
- sources
- comparison
- reliability analysis

### Multi-Source Reasoning Comes After Single-Question Quality
First make one-question search answers strong.
Then add better:
- cross-source comparison
- contradiction detection
- uncertainty handling
- evidence-weighted synthesis

That should be a later layer, not the first thing the user sees.

## Technical Recommendation

### Current Product Track
These improvements belong in the current product-improvement track:
- answer-first web-search presentation
- collapsed source display by default
- better query understanding before retrieval
- source reading before summary for normal search answers
- less visible process clutter
- better degraded behavior when reading is slow

These are product-quality and answer-quality improvements.
They do not require new authority.

### Phase 7 Extensions
These belong later in Phase 7 governed external reasoning:
- stronger provider-backed long-form synthesis for difficult web questions
- deeper multi-source reasoning and contradiction handling
- optional second-opinion review of a search answer
- harder ambiguity handling on complex or contested topics

Why they belong in Phase 7:
- they are reasoning-quality extensions
- they remain text-only
- they do not add execution authority

### Phase 8 Boundary
This packet is not about execution.

For Phase 8, the interpretation boundary should stay:
- web search remains read-only
- no search result becomes execution authority
- no provider-backed answer becomes approval authority

### Much Later
Only much later should Nova consider:
- durable search preference learning
- adaptive source weighting based on long-term user preference
- persistent topic tracking across sessions

That belongs later because it begins to touch lasting learning and personalization.

## Recommended Architecture

### 1. Query Understanding Layer
This layer should:
- interpret what the user is asking
- classify search intent
- identify whether the request is:
  - fact lookup
  - current-events search
  - compare request
  - explanation request
  - follow-up request

This is where Nova becomes more assistant-like before retrieval even begins.

### 2. Retrieval Layer
This layer should:
- perform the search
- gather candidate results
- choose likely relevant sources
- avoid over-surfacing raw retrieval mechanics by default

### 3. Source Reader Layer
This layer should:
- fetch the selected source page
- extract meaningful article/page text
- prepare clean content for reasoning

This is the main answer-quality upgrade.

### 4. Answer Synthesis Layer
This layer should:
- reason from the read source material
- answer the question directly
- keep the answer concise first
- preserve uncertainty when needed

### 5. Evidence Display Layer
This layer should:
- hide heavy breakdowns by default
- reveal sources only when clicked
- support later:
  - compare sources
  - reliability review
  - evidence expansion

Likely implementation surfaces:
- [web_search_executor.py](C:\Nova-Project\nova_backend\src\executors\web_search_executor.py)
- [news_intelligence_executor.py](C:\Nova-Project\nova_backend\src\executors\news_intelligence_executor.py)
- [dashboard.js](C:\Nova-Project\nova_backend\static\dashboard.js)
- [intelligence_brief_renderer.py](C:\Nova-Project\nova_backend\src\rendering\intelligence_brief_renderer.py)

## Best Implementation Order

### Stage 1 - Answer-First Search Presentation
Goal:
- make web search answers feel like Nova answers instead of search dashboards

Best scope:
- direct answer first
- collapse source details by default
- keep source display on click
- reduce visible process clutter

Suggested branch:
- `codex/websearch-stage1-answer-first-ui`

### Stage 2 - Query Understanding Before Retrieval
Goal:
- improve how Nova interprets the user's question before searching

Best scope:
- classify basic search intents
- improve follow-up anchoring for search questions
- shape the answer by question type

Suggested branch:
- `codex/websearch-stage2-query-understanding`

### Stage 3 - Source-Reader Grounded Answers
Goal:
- answer from source content, not just titles and snippets

Best scope:
- fetch and clean source page text
- synthesize from the actual article/page body
- keep answers concise first

Suggested branch:
- `codex/websearch-stage3-source-reader-grounding`

### Stage 4 - Better Degraded Behavior
Goal:
- make search still useful when full source reading is slow or partial

Best scope:
- short grounded fallback
- clearer uncertainty language
- avoid dead-end timeout feel
- keep user-facing wording clean

Suggested branch:
- `codex/websearch-stage4-degraded-flow`

### Stage 5 - Multi-Source Compare Mode
Goal:
- support deeper, more analytical search questions

Best scope:
- explicit compare mode
- overlap and disagreement
- confidence framing
- evidence expansion on click

Suggested branch:
- `codex/websearch-stage5-compare-mode`

## Recommended Product Rule
The anchor rule for Nova web search should be:

Answer first. Reason from sources. Show evidence when asked.

That keeps Nova conversational, useful, and grounded at the same time.
