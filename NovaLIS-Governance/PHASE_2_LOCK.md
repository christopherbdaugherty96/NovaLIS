\# NovaLIS Phase-2 Lock (INTENTIONAL ACTION — NO AUTONOMY)



Phase-2 theme: Explicit Action Mode with mandatory confirmation.

Actions are user-invoked only, single-step only, no chaining.



---



\## Phase-2 Entry Criteria (Must already be true)

\- Phase-1 is frozen and reproducible.

\- Governor routing order is enforced.

\- Skills are deterministic and bounded.

\- Confirmation gate is functional and blocks execution.

\- UI remains observer-only (no implied intent).



---



\## Phase-2 Core Mechanism (LOCKED)

\- Introduce explicit ActionRequest objects.

\- Mandatory confirmation before any action executes.

\- One action at a time. No chaining. No background work.

\- Clear completion or refusal response, then interaction ends.



---



\## Phase-2 Allowed Actions (V1 scope)

A) Deterministic system launch actions:

\- open explicit folder/file

\- launch pre-approved apps

(only via trusted executor model; no remote shell; no filesystem crawling)



B) Read-only predefined views:

\- open static “News Views” / dashboards / websites



C) Media routing (where playback occurs):

\- local files only

\- stop always works



D) Deterministic info actions:

\- time/date

\- reminders read/cancel/list (deterministic objects)



---



\## Phase-2 Forbidden

\- Automation, routines, multi-step plans

\- Background monitoring, background refresh, or silent fetches

\- Device discovery, scanning, or crawling

\- File searching across client machines

\- LLM-driven action selection or planning

\- Any “helpful” default behavior that executes without explicit confirmation



---



\## Phase-2 UI Rules

\- UI may show confirmation prompts and completion/errors.

\- UI must not imply system cognition or attention.

\- Orb remains non-semantic.



---



\## Phase-2 Exit Criteria

\- ActionRequest + confirmation enforced everywhere.

\- “Stop” always halts immediately.

\- No background execution.

\- Trusted executor capability checks are enforced.

\- Documentation frozen for Phase-2 behavior and exclusions.



