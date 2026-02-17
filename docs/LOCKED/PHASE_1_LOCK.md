\# NovaLIS Phase-1 Lock (FROZEN)



Phase-1 theme: Information-only, calm presence, deterministic skills.

Phase-1 is FROZEN. No new features are added here.



---



\## Phase-1 Allowed

\- Chat-first UI (observer-only)

\- Weather: current conditions only

\- News: headlines-only, fixed whitelist, source attribution

\- Deterministic routing and safe failures

\- SAL fixed-string acknowledgments (text-only)

\- Basic UI readability/accessibility improvements that do NOT change behavior



---



\## Phase-1 Forbidden

\- Any autonomous behavior

\- Any background refresh (news/weather/UI)

\- Any “smart” summaries by default

\- Any LLM-driven routing/planning/acting

\- Any UI implying thinking/listening/intent

\- Any execution actions (system/file/app control)

\- Any memory writes or learning



---



\## Phase-1 Cache Rule (If used)

If cached headlines/weather are displayed:

\- Must be labeled “Cached”

\- Must show timestamp

\- Must not refresh automatically

\- Refresh only on explicit user action



---



\## Phase-1 Exit Criteria (Must all be true)

\- Deterministic routing order is enforced.

\- News returns expected count under normal conditions; zero headlines do not trigger speech.

\- Weather shows current conditions correctly for stored location.

\- Failures are calm and finite (“I’m not sure right now.”), no retries.

\- UI loads cleanly, no duplicate active assets.

\- Manual acceptance test script passes.



