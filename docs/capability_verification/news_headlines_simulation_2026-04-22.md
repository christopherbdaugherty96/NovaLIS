# News and Headlines Verification - 2026-04-22

## Scope

Live WebSocket and automated verification for Nova's news surfaces:

- Current headline fetching
- Headline widget payloads
- Follow-up headline summaries
- Category summaries
- Daily intelligence brief
- Headline comparison
- Routing for common first-user news phrases
- RSS title/entity cleanup

Backend was started with:

```powershell
python scripts/start_daemon.py --no-browser
```

Model status was already confirmed after restart:

```text
POST /api/settings/model/confirm -> No model update is pending.
```

## Automated Result

Status: PASS

Command:

```powershell
python -m pytest nova_backend/tests/test_rss_fetch.py nova_backend/tests/test_governor_mediator_phase4_capabilities.py nova_backend/tests/test_news_skill.py nova_backend/tests/executors/test_news_intelligence_executor.py nova_backend/tests/executors/test_info_snapshot_executor.py -q
```

Result:

```text
42 passed in 3.08s
```

Coverage confirmed:

- RSS/Atom parsing, summaries, published timestamps, video URLs
- RSS title entity decoding
- News skill multi-feed fallback and category buckets
- News unavailable behavior when feeds return nothing
- News snapshot executor payloads
- Headline summary, category summary, topic/source filters, comparisons
- Daily brief behavior with and without cached headlines
- Routing for `news`, `what's the news today`, `latest headlines`, and `current headlines`

## Live Runtime Result

Status: PASS after correction

Passing live probes:

- `news` fetched 5 current headlines from 5 sources and emitted a `news` widget.
- `latest headlines` fetched current headlines after routing correction.
- `current headlines` fetched current headlines after routing correction.
- `summarize headline 1` produced a `news_summary` payload.
- `summarize tech news` produced a category summary and no raw HTML entities in chat or payload.
- `today's news` produced an `intelligence_brief` payload.
- `daily brief` produced a daily intelligence brief.
- `compare headlines 1 and 3` produced a headline comparison.

Representative live smoke:

```text
latest headlines -> Loaded 5 sources. Themes: global security and policy and government...
current headlines -> Loaded 5 sources. Themes: global security and policy and government...
summarize tech news -> CATEGORY SUMMARY - Tech News ...
```

## Issues Found And Corrected

1. `latest headlines` fell through to generic fallback.
   - Cause: `NEWS_RE` handled `headlines`, `latest news`, and `top news`, but not `latest headlines`.
   - Fix: Added routing for `latest headlines`, `current headlines`, `recent headlines`, and `top headlines`.
   - Verification: live `latest headlines` and `current headlines` now return news widgets.

2. Raw HTML entities leaked into user-facing headline summaries.
   - Example: `&#8216;` appeared in a tech-news summary before correction.
   - Cause: RSS summaries were cleaned, but RSS titles were not passed through the same text cleanup path.
   - Fix: Clean RSS titles with `_clean_text()`.
   - Verification: focused RSS test and live `summarize tech news` showed no raw `&#` entities in chat or structured payload.

## Remaining Follow-Up

- Some live brief outputs use fallback/placeholder source-grounded summaries when local synthesis or source reads are unavailable. This is acceptable degradation, but future work should make the UI label "headline-only" versus "source-grounded" even more obvious.
- Console output on Windows can display smart punctuation as `?` in ASCII-only test scripts; the structured WebSocket payload no longer contains raw HTML entities.
