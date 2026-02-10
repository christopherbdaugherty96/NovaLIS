\# NovaLIS Repo Annotation Map (Rules → Files)



This maps governance rules to the most likely folders/files where they are enforced or violated.



---



\## Backend: Governor Core

Typical location:

\- Nova-Backend-AI-Brain\\brain\_server.py

\- Nova-Backend-AI-Brain\\router.py

Rules:

\- routing priority (Stop → Confirmation → Skills → Recency Guard → LLM → Failure)

\- no autonomy, no retries, no background behavior

\- LLM cannot become router/actor



Red flags:

\- “guess intent”

\- auto-escalation

\- implicit chaining



---



\## Backend: Gates

Typical location:

\- Nova-Backend-AI-Brain\\gates\\confirmation\_gate.py

Rules:

\- explicit permission/confirmation

\- ephemeral consent only



Red flags:

\- auto-confirm

\- stored consent

\- proceed on reconnect



---



\## Backend: Skills

Typical location:

\- Nova-Backend-AI-Brain\\skills\\news.py

\- Nova-Backend-AI-Brain\\skills\\weather.py

Rules:

\- deterministic, bounded, stateless

\- no inference, no autonomy



Red flags:

\- multiple queries/retries

\- default summaries

\- background refresh



---



\## Backend: LLM Helper

Typical location:

\- Nova-Backend-AI-Brain\\llm\\llm\_manager.py

Rules:

\- helper only

\- fail closed



Red flags:

\- LLM output triggers actions

\- retries/fallback chains



---



\## Backend: SAL

Typical location:

\- Nova-Backend-AI-Brain\\sal\\sal.py

Rules:

\- fixed strings only

\- text-only



Red flags:

\- dynamic variants

\- LLM usage



---



\## Frontend: Dashboard

Typical location:

\- Nova-Frontend-Dashboard\\dashboard.js

\- Nova-Frontend-Dashboard\\style.phase1.css

Rules:

\- observer-only UI

\- no auto-fetch, no implied intent



Red flags:

\- fetch on load

\- background refresh

\- UI state guessing backend state



---



\## Orb / Visual Layer

Typical location:

\- Nova-Frontend-Dashboard\\orb\_canvas.js (Phase-2+)

Rules:

\- time-based, non-semantic visuals

\- no coupling to backend state



Red flags:

\- listening/thinking cues

\- event-driven animation



