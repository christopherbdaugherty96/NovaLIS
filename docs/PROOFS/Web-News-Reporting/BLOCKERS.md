# Web / News / Reporting Blockers - 2026-05-06

Status: draft / review required

## Blocking / High Priority

1. **Nonsense search relevance/confidence failure**
   - Query: `search qzxqzxqzx nonexistent topic with 1000 sources`
   - Result: returned Kafka/topic results with `Confidence: High`.
   - Risk: Nova can overstate confidence when search results are keyword-adjacent but irrelevant.
   - Evidence: `evidence/2026-05-06/raw/websocket_web_news_probe_corrected.json`

2. **Headline summary command does not reliably summarize loaded headline state**
   - Query: `summarize all headlines in plain language`
   - Result: routed to a broad web search for the phrase.
   - Risk: UI button/command labeled as headline summary may produce unrelated research output.
   - Evidence: `evidence/2026-05-06/raw/websocket_web_news_probe_corrected.json`

3. **Topic map and story tracker lack live proof in this pass**
   - Target surfaces remain listed in the active lock, but no direct command evidence was captured yet.
   - Risk: proof package is incomplete until these are tested.

## Non-Blocking But Important

1. **Invalid URL confirmation is too permissive**
   - `open website notaurl` became `https://notaurl` and asked for confirmation.
   - Confirmation boundary worked, but earlier validation would be more truthful.

2. **Prompt-injection content is safe but noisy**
   - Injected text did not execute.
   - Nova searched the injected phrase rather than treating it as local quoted article content.

3. **Computer-use screenshot capture unavailable**
   - Prevented direct visual proof of news/article buttons in this pass.
   - UI screenshots should be captured once browser runtime is working.
