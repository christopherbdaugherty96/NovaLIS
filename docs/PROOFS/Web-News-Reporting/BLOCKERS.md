# Web / News / Reporting Blockers - 2026-05-06

Status: draft / review required

## Blocking / High Priority

1. **Prompt-injection content is safe but noisy**
   - Injected text did not execute.
   - Nova searched the injected phrase rather than treating it as local quoted article content.
   - Evidence: `evidence/2026-05-06/raw/websocket_web_news_probe_corrected.json`

2. **Computer-use screenshot capture unavailable**
   - Prevented direct visual proof of news/article buttons in this pass.
   - UI screenshots should be captured once browser runtime is working.
   - Evidence: `../UI-Commands/evidence/2026-05-06/raw/browser_use_failure.txt`

## Resolved In 2026-05-07 Fix Pass

1. **Nonsense search relevance/confidence failure**
   - Query: `search qzxqzxqzx nonexistent topic with 1000 sources`
   - Fix validation: result now reports `Confidence: Low` and says results may be weak or unrelated.
   - Evidence: `evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/brain/test_search_synthesis.py`

2. **Headline summary command did not reliably summarize loaded headline state**
   - Query: `news`, then `summarize all headlines in plain language`
   - Fix validation: response summarized the loaded headlines and stated no web search or external action was performed.
   - Evidence: `evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`
   - Regression: `nova_backend/tests/websocket/test_session_handler_proof_blockers.py`

3. **Topic map and story tracker lacked live proof**
   - Fix validation: `show topic map`, `track story global security`, and `show story tracker` now have direct proof evidence.
   - Evidence: `evidence/2026-05-07/raw/web_news_blocker_fix_probe.json`

## Non-Blocking But Important

1. **Invalid URL confirmation is too permissive**
   - `open website notaurl` became `https://notaurl` and asked for confirmation.
   - Confirmation boundary worked, but earlier validation would be more truthful.

2. **Open website/article visual proof remains blocked by browser-use runtime**
   - Article/open behavior remains proven through WebSocket confirmation evidence, not screenshots.
