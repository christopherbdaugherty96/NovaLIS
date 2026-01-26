\# NovaLIS Architectural Contract (LOCKED)



NovaLIS is a governed household system, not an autonomous AI assistant.



NovaLIS is designed to be trusted:

\- predictable

\- refusal-safe

\- silence-first

\- explicitly controlled



This contract is LOCKED. Changes require an explicit unlock.



---



\## Non-Negotiable Principles



\### 1) Governor Model

\- There is a single authoritative brain / router.

\- Skills do not decide what happens next.

\- UI does not decide what happens next.

\- LLM output never decides what happens next.



\### 2) Silence-First Behavior

\- NovaLIS does nothing unless explicitly invoked.

\- Silence is a correct outcome.

\- No follow-ups unless requested.



\### 3) Event-Driven Only

Allowed triggers:

\- user message

\- explicit UI action

\- explicit schedule (ask-first prompts only)



Forbidden:

\- background loops

\- polling

\- silent fetches

\- auto-refresh on load/reconnect



\### 4) Permission \& Confirmation

\- Actions require explicit user permission and confirmation.

\- Confirmation is ephemeral. No “remembered” consent.

\- Denial or no-response ends the interaction cleanly.



\### 5) LLM as Helper Only

LLM may:

\- clarify user-provided text

\- answer bounded informational questions

\- support explicit reflective reasoning mode



LLM may NOT:

\- route

\- plan

\- infer intent

\- select actions

\- execute actions

\- retry or auto-escalate



If removing the LLM would make Nova unsafe, Nova is already broken.



\### 6) Deterministic Skills

\- Skills are deterministic, bounded, and stateless.

\- Same input should produce the same outcome (within external API variability).

\- Skills must fail safely and finitely.



\### 7) Deterministic News \& Weather Contracts

News:

\- fixed whitelist of trusted sources

\- headlines only by default

\- no summaries unless explicitly requested (and only via explicit permission escalation if needed)

\- never speak headlines if none exist



Weather:

\- current conditions only (Phase-1/2 baseline)

\- no forecast creep



\### 8) System Acknowledgment Layer (SAL)

\- fixed strings only (no LLM generation)

\- text-only forever

\- no follow-ups, no questions, no escalation

\- ACK-BOUNDARY ends interaction immediately



\### 9) Truthful UI

\- UI is observer-only.

\- UI must not imply thinking/listening/intent/mood.

\- Orb visuals are presentation-only and non-semantic.



\### 10) Phase Discipline

\- Phase boundaries are enforced.

\- No feature jumps across phases.

\- UX polish comes after stability and governance are proven.



---



\## Forbidden (Hard Line)

\- background refreshes, auto-updates, silent fetches

\- autonomous retries or “helpful” guessing

\- anthropomorphic drift (emotion/attention cues)

\- LLM-driven routing, planning, or action inference

\- UI state that misrepresents backend truth



