\# NovaLIS Pre-Commit Checklist (LOCKED PROCESS)



Rule: If any item fails → do not commit.



---



\## 1) Phase \& Scope Guard

\- Does this change belong to the current phase?

\- Is it completing/hardening existing behavior (not novelty)?

\- Does it avoid unlocking future phases implicitly?



Fail if you are “sneaking in” convenience or polish.



---



\## 2) Governor Model Integrity

\- Brain remains sole authority.

\- Skills remain deterministic and non-authoritative.

\- No action occurs without explicit confirmation (Phase-2+).



Fail if anything infers, retries, escalates, or chains.



---



\## 3) Event-Driven Only

\- No background loops.

\- No polling.

\- No auto-refresh on load/reconnect.



Fail if code runs “just because the app started.”



---



\## 4) LLM Boundary Check (Critical)

\- LLM is not a router, actor, planner, retry engine.

\- LLM output cannot directly cause execution.

\- LLM failure fails closed (calm refusal).



Fail if removing the LLM would break safety.



---



\## 5) Determinism \& Failure Safety

\- Same input → same result (within external API variability).

\- Failures are calm, finite, and silence-safe.

\- No retries without user re-invocation.



Fail if the system “tries again” on its own.



---



\## 6) News \& Weather Contracts

News:

\- headlines only

\- whitelist only

\- no summaries by default

\- no speaking if zero headlines



Weather:

\- current conditions only

\- no forecast creep



Fail if inference/enrichment sneaks in.



---



\## 7) Cache \& State Rules

If cached data is displayed:

\- label as cached

\- show timestamp

\- refresh only on explicit user action

\- never silently refresh



Fail if cached can be mistaken for live.



---



\## 8) UI Truthfulness

\- UI reflects backend truth only.

\- No visuals implying thinking/listening/intent.

\- Orb is non-semantic.



Fail if UI “guesses” system state.



---



\## 9) Single Source of Truth

\- One dashboard.js

\- One CSS entrypoint

\- No duplicate active assets



Fail if you are unsure what file is running.



---



\## 10) Acceptance Test (Mandatory)

Manually verify:

\- stop works immediately

\- confirmation gate blocks execution

\- no background actions occur

\- failure responses are calm and finite

\- silence is respected



If not tested → do not commit.



